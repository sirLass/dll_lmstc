import logging
import re
from typing import Any, Iterable, List, Sequence
import difflib

from .models import ApplicantPasser, SavedJobMatch

logger = logging.getLogger(__name__)

SYMBOL_PATTERN = re.compile(r"[^a-z0-9\s]+")
# Cap the denominator to avoid low percentages when there are many program keywords
KEYWORD_DENOMINATOR_CAP = 20

def singularize_word(word: str) -> str:
    """
    Naively convert plural English words to singular to improve matching.
    Keeps it lightweight (no external NLP deps).
    """
    if not word:
        return word
    w = word.strip().lower()
    # Common plural -> singular rules
    if len(w) > 4 and w.endswith("ies"):
        # companies -> company
        return w[:-3] + "y"
    if len(w) > 3 and (w.endswith("ses") or w.endswith("xes") or w.endswith("zes") or w.endswith("ches") or w.endswith("shes")):
        # classes -> class, boxes -> box, churches -> church
        return w[:-2]
    if len(w) > 2 and w.endswith("s") and not w.endswith("ss"):
        # resources -> resource, skills -> skill
        return w[:-1]
    return w


def singularize_text(text: str) -> str:
    """
    Apply singularization to each token in the already cleaned text.
    """
    if not text:
        return ""
    return " ".join(singularize_word(tok) for tok in text.split() if tok)


def clean_text(text: str | None) -> str:
    """
    Normalize text by lowercasing, removing symbols, and collapsing whitespace.
    """
    if not text:
        return ""
    lowered = str(text).lower()
    without_symbols = SYMBOL_PATTERN.sub(" ", lowered)
    return re.sub(r"\s+", " ", without_symbols).strip()


def _normalize(text: str) -> str:
    """
    Clean and singularize text to make comparisons robust to punctuation and pluralization.
    """
    return singularize_text(clean_text(text))


def _token_set(text: str) -> set:
    """
    Convert text into a set of normalized tokens for order-insensitive comparison.
    """
    norm = _normalize(text)
    return set(norm.split()) if norm else set()


def extract_keywords(text: Iterable[str] | str | None) -> List[str]:
    """
    Convert provided text or iterable of text into a unique list of keywords.
    """
    if not text:
        return []

    chunks: Sequence[str]
    if isinstance(text, str):
        chunks = [text]
    else:
        chunks = list(text)

    keywords: List[str] = []
    seen = set()
    for chunk in chunks:
        normalized = clean_text(chunk)
        if not normalized:
            continue
        for token in normalized.split():
            base = singularize_word(token)
            if base and base not in seen:
                keywords.append(base)
                seen.add(base)
    return keywords


def calculate_match_score(program_keywords: List[str], job_text: str) -> float:
    """
    Percentage score based on keyword coverage in the job text.
    """
    if not program_keywords:
        return 0.0

    normalized_job_text = clean_text(job_text)
    if not normalized_job_text:
        return 0.0
    # Singularize both the job text and the program keywords to reduce pluralization mismatch
    normalized_job_text = singularize_text(normalized_job_text)
    normalized_keywords = [singularize_word(k) for k in program_keywords if k]

    matches = sum(1 for keyword in normalized_keywords if keyword and keyword in normalized_job_text)
    denom = min(len(program_keywords), KEYWORD_DENOMINATOR_CAP) if program_keywords else 0
    if denom == 0:
        return 0.0
    score = (matches / denom) * 100
    return round(score, 2)


def save_high_match_jobs(user, job_data: dict[str, Any], score: float) -> None:
    """
    Persist jobs whose score meets the saving threshold for the given applicant.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return

    job_url = job_data.get("url") or job_data.get("job_url")
    if not job_url and job_data.get("id"):
        job_url = f"https://philjobnet.gov.ph/job/{job_data['id']}"

    if not job_url:
        return

    try:
        SavedJobMatch.objects.update_or_create(
            user=user,
            job_url=job_url,
            defaults={
                "job_title": job_data.get("title") or "Job Opportunity",
                "job_company": job_data.get("company") or "",
                "match_score": round(score, 2),
            },
        )
    except Exception as exc:
        logger.warning("Unable to save high-match job for %s: %s", getattr(user, "id", None), exc)


def _extract_competency_chunks(program_competencies: dict[str, Any] | None) -> List[str]:
    chunks: List[str] = []
    if not program_competencies:
        return chunks

    job_opportunities = program_competencies.get("job_opportunities", [])
    if isinstance(job_opportunities, list):
        chunks.extend([str(item) for item in job_opportunities])

    return chunks


def _combine_job_text(job: dict[str, Any]) -> str:
    job_sections: List[str] = []
    for key in ("title", "description", "requirements", "qualifications"):
        value = job.get(key)
        if value:
            job_sections.append(str(value))

    skills = job.get("skills") or job.get("skill_requirements")
    if isinstance(skills, list):
        job_sections.extend([str(skill) for skill in skills])
    elif isinstance(skills, str):
        job_sections.append(skills)

    return " ".join(job_sections)


def _get_program_keywords_for_user(user) -> List[str]:
    if not user or not getattr(user, "is_authenticated", False):
        return []

    passers = ApplicantPasser.objects.filter(applicant=user).select_related("program")
    if not passers.exists():
        return []

    chunks: List[str] = []
    for passer in passers:
        program = getattr(passer, "program", None)
        if program and program.program_competencies:
            chunks.extend(_extract_competency_chunks(program.program_competencies))

    return extract_keywords(chunks)


def _get_program_opportunity_phrases_for_user(user) -> List[str]:
    """
    Return the raw career opportunity phrases (e.g., "Accounting Staff") for all
    programs the user has passed. Used for phrase-level fuzzy matching/boost.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return []

    passers = ApplicantPasser.objects.filter(applicant=user).select_related("program")
    if not passers.exists():
        return []

    phrases: List[str] = []
    for passer in passers:
        program = getattr(passer, "program", None)
        if program and program.program_competencies:
            job_ops = program.program_competencies.get("job_opportunities", [])
            if isinstance(job_ops, list):
                phrases.extend([str(p) for p in job_ops if p])
    return phrases


def _max_phrase_similarity(phrases: List[str], job_title: str, job_text: str) -> float:
    """
    Compute the maximum similarity between any provided phrase and either the job title
    or the combined job text. Returns a value in [0,1].

    Enhancements:
    - Exact/near-exact match via direct containment after normalization.
    - Order-insensitive token subset check (all phrase words present in title/text) -> treat as 1.0.
    - Fallback to difflib fuzzy ratio against both title and combined text.
    """
    if not phrases:
        return 0.0

    title_norm = _normalize(job_title)
    text_norm = _normalize(job_text)
    title_tokens = _token_set(job_title)
    text_tokens = _token_set(job_text)
    best = 0.0

    for phrase in phrases:
        p = _normalize(phrase)
        if not p:
            continue

        # 1) Direct containment (perfect match)
        if (p in title_norm) or (title_norm and title_norm in p):
            return 1.0
        if (p in text_norm) or (text_norm and text_norm in p):
            return 1.0

        # 2) Order-insensitive subset match of tokens (treat as perfect)
        p_tokens = set(p.split()) if p else set()
        if p_tokens and title_tokens and p_tokens.issubset(title_tokens):
            return 1.0
        if p_tokens and text_tokens and p_tokens.issubset(text_tokens):
            return 1.0

        # 3) Fuzzy ratio against title and full text (keep the best)
        if title_norm:
            best = max(best, difflib.SequenceMatcher(None, p, title_norm).ratio())
        if text_norm:
            best = max(best, difflib.SequenceMatcher(None, p, text_norm).ratio())

    return best


def match_jobs_for_user(user, jobs: List[dict[str, Any]], min_threshold: float = 0.0) -> List[dict[str, Any]]:
    """
    Score each job against the applicant's program keywords and optionally save high matches.
    """
    program_keywords = _get_program_keywords_for_user(user)
    opportunity_phrases = _get_program_opportunity_phrases_for_user(user)
    matched_jobs: List[dict[str, Any]] = []

    for job in jobs:
        job_text = _combine_job_text(job)
        score = calculate_match_score(program_keywords, job_text) if program_keywords else 0.0

        # Helper: token coverage of any opportunity phrase inside the job title/text
        # (avoids dilution when overall keyword set is large)
        def _max_phrase_token_coverage(phrases: List[str], text: str) -> float:
            if not phrases:
                return 0.0
            job_tokens = _token_set(text)
            if not job_tokens:
                return 0.0

            def _best_token_similarity(p_tok: str) -> float:
                # Best character-level similarity for this phrase token against any job token
                return max((difflib.SequenceMatcher(None, p_tok, j_tok).ratio() for j_tok in job_tokens), default=0.0)

            best_cov = 0.0
            for phrase in phrases:
                p_tokens = _token_set(phrase)
                if not p_tokens:
                    continue
                matched = 0
                for pt in p_tokens:
                    if pt in job_tokens:
                        matched += 1
                        continue
                    # Fuzzy token match: count as matched if sufficiently similar to any job token
                    if _best_token_similarity(pt) >= 0.80:
                        matched += 1
                cov = matched / len(p_tokens)
                best_cov = max(best_cov, cov)
            return best_cov

        # Phrase-level boost: if any career opportunity phrase closely matches the
        # PESO job title/text (tolerant to small typos), elevate score accordingly.
        if opportunity_phrases:
            title = job.get("title") or ""
            phrase_sim = _max_phrase_similarity(opportunity_phrases, title, job_text)
            # Token coverage boost (e.g., job contains most words from a phrase)
            token_cov = _max_phrase_token_coverage(opportunity_phrases, f"{title} {job_text}")
            if token_cov >= 0.99:
                score = 99.0
                logger.info("Token coverage ~100%% for job '%s' (coverage=%.2f) -> capped at 99%%", title, token_cov)
            else:
                coverage_boost = round(token_cov * 100, 2)
                # Add small token-based boosts in common ranges
                if 20.0 <= coverage_boost < 50.0:
                    coverage_boost += 10.0
                elif 50.0 <= coverage_boost < 100.0:
                    coverage_boost += 5.0
                coverage_boost = min(coverage_boost, 99.0)
                if coverage_boost > score:
                    logger.info("Token coverage boost for job '%s': %.2f -> %.2f", title, score, coverage_boost)
                score = max(score, coverage_boost)
            # Exact/near-exact match -> cap at 99%
            if phrase_sim >= 0.95:
                score = 99.0
                logger.info("Fuzzy phrase match ~100%% for job '%s' (sim=%.2f) -> capped at 99%%", title, phrase_sim)
            # Close match -> boost to at least the fuzzy similarity percentage
            elif phrase_sim >= 0.85:
                boosted = round(phrase_sim * 100, 2)
                boosted = min(boosted, 99.0)
                if boosted > score:
                    logger.info("Fuzzy phrase boost for job '%s': %.2f -> %.2f", title, score, boosted)
                score = max(score, boosted)

        # Cap maximum at 99% and round before saving/returning
        if score > 99.0:
            score = 99.0
        score = round(score, 2)

        job_copy = job.copy()
        job_copy["match_percentage"] = score

        if score >= 50:
            save_high_match_jobs(user, job, score)

        if score >= min_threshold:
            matched_jobs.append(job_copy)

    matched_jobs.sort(key=lambda item: item.get("match_percentage", 0), reverse=True)
    return matched_jobs

