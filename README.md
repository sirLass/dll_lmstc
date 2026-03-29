# DLL LMSTC - Learning Management System and Training Center

[![Django Version](https://img.shields.io/badge/django-5.2.4-green.svg)](https://www.djangoproject.com/)
[![Deployment](https://img.shields.io/badge/deployed-render-blue.svg)](#)
[![Database](https://img.shields.io/badge/database-supabase-orange.svg)](#)

## 📌 Project Overview
**DLL LMSTC** is a comprehensive Learning Management System (LMS) designed specifically for training centers to streamline the entire educational lifecycle—from initial application to job placement. This platform bridges the gap between administrative management, trainer facilitation, and learner engagement.

### 🎯 Purpose
The primary purpose of DLL LMSTC is to modernize training center operations by replacing manual, paper-based processes with an automated, role-based digital ecosystem. It manages batch cycles, tracks student competencies, and ensures that graduates are matched with relevant career opportunities.

---

## 🌟 Key Features

### 👤 For Applicants (Learners)
- **Multi-Program Enrollment**: Apply for up to two tactical programs simultaneously.
- **Dynamic Dashboard**: Track application status (Pending, Approved, Declined, Incomplete) in real-time.
- **Interactive Learning**: Access class schedules, competency tracking (Basic, Common, Core), and downloadable training modules.
- **Career Growth**: Automated job recommendations based on successfully completed competencies.
- **Support System**: Create and manage support tickets for direct communication with staff.

### 👨‍🏫 For Trainers
- **Masterlist Management**: Automatically populated lists of approved students based on program assignments.
- **Session & Attendance Tracking**: Create training sessions and manage attendance for single or multi-day workshops.
- **Progress Monitoring**: Track and update student competency levels from "Not Started" to "Completed."
- **Resource Distribution**: Upload and assign manuals, guidelines, and tasks to specific batches.

### 🔑 For Administrators
- **DMS (Document Management System)**: Automated and manual review of applicant documents (IDs, signatures, profile forms).
- **Batch & Semester Cycling**: Manage the 3-batch rotating cycle and semester transitions.
- **Trainer Oversight**: Register trainers and assign expertise-specific programs.
- **Reporting**: Export detailed applicant lists, attendance records, and competency reports to Excel.
- **Walk-in Support**: Create and manage accounts for non-digital applicants.

---

## 🌍 Impact
- **Operational Efficiency**: Reduces administrative overhead by automating document verification and student filtering.
- **Data Integrity**: Centralizes all training records in a secure Supabase PostgreSQL environment, eliminating data silos.
- **Enhanced Accountability**: Provides clear audit trails for attendance, competency completion, and document reviews.
- **Improved Employment Outcomes**: Directly links student performance and skills to real-world job recommendations, boosting the success rate of graduates.

---

## 🛠️ Technology Stack
- **Framework**: Django 5.2.4
- **Database**: PostgreSQL (via Supabase)
- **Frontend**: Django Templates & Vanilla CSS
- **Deployment**: Render
- **Tools**: WhiteNoise (Static Files), dj-database-url, python-dotenv

---

## 🚀 Getting Started
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with `DATABASE_URL`, `DJANGO_SECRET_KEY`, and other necessary variables.
4. Run migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Start the server: `python manage.py runserver`

---

*Developed for the DLL Training Center to empower the next generation of skilled workforce.*
