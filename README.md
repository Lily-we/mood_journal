# Mood-Based Recommendation App

## Inspiration
We wanted to create a tool that helps people improve their mood using personalized song and mini-story recommendations. Mental health is important, and small interventions can make a big difference.

## What it does
- Users submit their mood via a slider (from depressed to happy).
- The app records the mood and note.
- It immediately provides mood-based recommendations:
  - Songs to match or improve the mood
  - Mini-stories to calm, motivate, or entertain
- Helps users reflect on their feelings and feel better.

## Tech Stack
- **Backend:** Python, Django
- **Frontend:** HTML, CSS
- **Database:** SQLite (local)
- **Optional AI/ML component:** Mood-based recommendation logic

## How to Run
1. Clone the repo
2. Install requirements: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start server: `python manage.py runserver`
5. Open browser at `http://127.0.0.1:8000/submit-mood/`

## Features to Highlight
- Mood slider with custom labels (Depressed → Happy)
- AI-style recommendation system for songs & mini-stories
- Responsive design for cozy UX

