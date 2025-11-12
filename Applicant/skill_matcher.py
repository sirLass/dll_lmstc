"""
Skill Matching Utility using difflib (lightweight alternative to scikit-learn)
Matches PESO job post skills with program competencies
"""
import difflib
import logging

logger = logging.getLogger(__name__)


class SkillMatcher:
    """
    Match job skills with user competencies using difflib SequenceMatcher
    """
    
    def __init__(self):
        # No initialization needed for difflib
        pass
    
    def extract_competencies_text(self, program_competencies):
        """
        Extract all competencies from a program's competencies dictionary
        Returns a single text string of all competencies
        """
        if not program_competencies or not isinstance(program_competencies, dict):
            return ""
        
        all_competencies = []
        
        # Extract Basic Competencies
        basic = program_competencies.get('basic', [])
        if isinstance(basic, list):
            for comp in basic:
                if isinstance(comp, dict):
                    all_competencies.append(comp.get('name', ''))
                    # Also include learning outcomes as they often contain skill keywords
                    outcomes = comp.get('learning_outcomes', [])
                    if isinstance(outcomes, list):
                        all_competencies.extend([str(o) for o in outcomes])
                elif isinstance(comp, str):
                    all_competencies.append(comp)
        
        # Extract Common Competencies
        common = program_competencies.get('common', [])
        if isinstance(common, list):
            for comp in common:
                if isinstance(comp, dict):
                    all_competencies.append(comp.get('name', ''))
                    outcomes = comp.get('learning_outcomes', [])
                    if isinstance(outcomes, list):
                        all_competencies.extend([str(o) for o in outcomes])
                elif isinstance(comp, str):
                    all_competencies.append(comp)
        
        # Extract Core Competencies
        core = program_competencies.get('core', [])
        if isinstance(core, list):
            for comp in core:
                if isinstance(comp, dict):
                    all_competencies.append(comp.get('name', ''))
                    outcomes = comp.get('learning_outcomes', [])
                    if isinstance(outcomes, list):
                        all_competencies.extend([str(o) for o in outcomes])
                elif isinstance(comp, str):
                    all_competencies.append(comp)
        
        # Extract Job Opportunities (these are direct skill matches)
        job_opportunities = program_competencies.get('job_opportunities', [])
        if isinstance(job_opportunities, list):
            all_competencies.extend([str(jo) for jo in job_opportunities])
        
        # Join all competencies into a single text
        competencies_text = ' '.join([str(c) for c in all_competencies if c])
        return competencies_text
    
    def extract_job_skills_text(self, job_skills, job_title='', job_description=''):
        """
        Extract all skills from a job post
        Returns a single text string combining skills, title, and description
        """
        skills_list = []
        
        # Add job title (important for matching)
        if job_title:
            skills_list.append(str(job_title))
        
        # Add job skills
        if job_skills:
            if isinstance(job_skills, list):
                skills_list.extend([str(skill) for skill in job_skills])
            elif isinstance(job_skills, str):
                skills_list.append(job_skills)
        
        # Add job description (contains many skill keywords)
        if job_description:
            skills_list.append(str(job_description))
        
        # Join all into a single text
        skills_text = ' '.join([s for s in skills_list if s])
        return skills_text
    
    def calculate_match_percentage(self, user_competencies_text, job_skills_text):
        """
        Calculate match percentage between user competencies and job skills
        Uses difflib SequenceMatcher for text similarity
        
        Returns:
            float: Match percentage (0-100)
        """
        try:
            # Handle empty inputs
            if not user_competencies_text or not job_skills_text:
                return 0.0
            
            if not user_competencies_text.strip() or not job_skills_text.strip():
                return 0.0
            
            # Normalize text (lowercase and strip)
            user_text = user_competencies_text.lower().strip()
            job_text = job_skills_text.lower().strip()
            
            # Use difflib SequenceMatcher to calculate similarity
            matcher = difflib.SequenceMatcher(None, user_text, job_text)
            similarity_score = matcher.ratio()
            
            # Also check for word-level matching (more granular)
            user_words = set(user_text.split())
            job_words = set(job_text.split())
            
            if user_words and job_words:
                # Calculate intersection ratio
                intersection = user_words.intersection(job_words)
                word_match_ratio = len(intersection) / max(len(user_words), len(job_words))
                
                # Combine character-level and word-level matching
                # Give more weight to word-level matching (70%) as it's more meaningful
                final_score = (similarity_score * 0.3) + (word_match_ratio * 0.7)
            else:
                final_score = similarity_score
            
            # Convert to percentage (0-100)
            match_percentage = float(final_score * 100)
            
            return round(match_percentage, 2)
            
        except Exception as e:
            logger.error(f"Error calculating match percentage: {e}")
            return 0.0
    
    def match_jobs_with_competencies(self, jobs, user_programs_competencies, min_match_threshold=10.0):
        """
        Match a list of jobs with user's program competencies
        
        Args:
            jobs (list): List of job dictionaries with 'skills', 'title', 'description'
            user_programs_competencies (list): List of program competencies dictionaries
            min_match_threshold (float): Minimum match percentage to include (default 10%)
        
        Returns:
            list: Jobs with added 'match_percentage' field, filtered and sorted by match
        """
        # Combine all user's program competencies into one text
        all_user_competencies = []
        for program_comp in user_programs_competencies:
            comp_text = self.extract_competencies_text(program_comp)
            if comp_text:
                all_user_competencies.append(comp_text)
        
        if not all_user_competencies:
            return []  # No competencies to match against
        
        user_competencies_text = ' '.join(all_user_competencies)
        
        # Calculate match percentage for each job
        matched_jobs = []
        for job in jobs:
            job_skills_text = self.extract_job_skills_text(
                job.get('skills', []),
                job.get('title', ''),
                job.get('description', '')
            )
            
            match_percentage = self.calculate_match_percentage(
                user_competencies_text,
                job_skills_text
            )
            
            # Only include jobs that meet minimum threshold
            if match_percentage >= min_match_threshold:
                job_copy = job.copy()
                job_copy['match_percentage'] = match_percentage
                matched_jobs.append(job_copy)
        
        # Sort jobs by match percentage (highest first)
        matched_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return matched_jobs
    
    def get_top_matching_skills(self, user_competencies_text, job_skills, top_n=5):
        """
        Get the top N matching skills between user competencies and job skills
        
        Returns:
            list: List of matching skills
        """
        try:
            if not user_competencies_text or not job_skills:
                return []
            
            user_comp_lower = user_competencies_text.lower()
            matching_skills = []
            
            for skill in job_skills:
                skill_str = str(skill).lower()
                # Check for exact or partial matches
                if skill_str in user_comp_lower or any(word in user_comp_lower for word in skill_str.split()):
                    matching_skills.append(str(skill))
            
            return matching_skills[:top_n]
            
        except Exception as e:
            logger.error(f"Error getting top matching skills: {e}")
            return []


def match_jobs_for_user(user, jobs, min_threshold=10.0):
    """
    Convenience function to match jobs for a specific user
    
    Args:
        user: Django User object
        jobs: List of job dictionaries
        min_threshold: Minimum match percentage
    
    Returns:
        list: Matched jobs with match_percentage field
    """
    from .models import ApplicantPasser
    
    try:
        # Get all programs the user has passed
        passed_programs = ApplicantPasser.objects.filter(applicant=user).select_related('program')
        
        if not passed_programs.exists():
            return []  # User hasn't passed any programs
        
        # Collect all program competencies
        user_programs_competencies = []
        for passer in passed_programs:
            if passer.program and passer.program.program_competencies:
                user_programs_competencies.append(passer.program.program_competencies)
        
        if not user_programs_competencies:
            return []  # No competencies available
        
        # Use SkillMatcher to match jobs
        matcher = SkillMatcher()
        matched_jobs = matcher.match_jobs_with_competencies(
            jobs,
            user_programs_competencies,
            min_threshold
        )
        
        return matched_jobs
        
    except Exception as e:
        logger.error(f"Error matching jobs for user {user.username}: {e}")
        return []
