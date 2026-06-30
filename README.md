# AI Resume Analyzer

An AI-powered Resume Analyzer web application built with Python, Flask, Google Gemini AI, and PyPDF2. The application analyzes resumes, extracts skills and experience, evaluates ATS compatibility, and provides intelligent recommendations.

## Features

- User Authentication (Login/Register)
- PDF Resume Upload
- Resume Text Extraction using PyPDF2
- AI-powered Resume Analysis using Google Gemini
- Skill Extraction
- Education & Experience Detection
- Certification Analysis
- Project Identification
- ATS Score Calculation
- Resume Improvement Suggestions
- Recommended Job Roles
- Dashboard Interface

## Tech Stack

- Python
- Flask
- Google Gemini API
- PyPDF2
- SQLite
- HTML/CSS
- JavaScript
- Scikit-learn

## Project Structure

```
ai_resume_analyzer/
├── app.py
├── routes.py
├── ai_analyzer.py
├── resume_parser.py
├── models.py
├── database.py
├── templates/
├── uploads/
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/vorak916-code/ai-resume-analyzer.git
cd ai-resume-analyzer

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

## Future Improvements

- OCR support for image-based resumes
- Resume-to-job matching
- Resume scoring analytics
- Export reports to PDF
- Admin dashboard

