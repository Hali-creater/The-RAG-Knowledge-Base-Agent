# Real Estate AI Lead Intelligence System

This system automatically scrapes, classifies, and scores real estate leads from public platforms.

## Features
- **Automated Scraping**: Periodically finds new leads.
- **AI Classification**: Uses NLP and scikit-learn to identify Buyers vs. Sellers.
- **Lead Scoring**: Prioritizes leads based on urgency and relevance.
- **Dashboard**: Professional web UI to manage leads.
- **Email Alerts**: Notifications for high-priority leads.

## Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python3 -m spacy download en_core_web_sm
   playwright install chromium
   ```

2. Configure environment:
   Copy `.env.example` to `.env` and fill in your SMTP details.

3. Run the system (FastAPI):
   ```bash
   python3 main.py
   ```
   Visit `http://localhost:8000`

## Deployment to Streamlit.io

1. **GitHub Repository**: Ensure your code is in a public or private GitHub repository.
2. **Streamlit Cloud**:
   - Log in to [Streamlit Cloud](https://share.streamlit.io/).
   - Click "New app".
   - Select your repository, branch, and set the main file path to `streamlit_app.py`.
3. **Advanced Settings**:
   - In the app settings on Streamlit Cloud, go to "Secrets".
   - Add your environment variables from `.env` (SMTP credentials) in TOML format:
     ```toml
     SMTP_SERVER = "smtp.gmail.com"
     SMTP_PORT = 587
     SMTP_USER = "your_email@gmail.com"
     SMTP_PASSWORD = "your_app_password"
     EMAIL_RECEIVER = "receiver_email@gmail.com"
     ```
4. **Deploy**: Click "Deploy!".

## Project Structure
- `streamlit_app.py`: Main dashboard for Streamlit deployment.
- `main.py`: Entry point for local FastAPI deployment.
- `scraper.py`: Logic for finding leads.
- `classifier.py`: AI logic for intent detection.
- `extractor.py`: NLP logic for entity extraction (phone, email, price).
- `scorer.py`: Logic for lead scoring.
- `database.py`: SQLite database management.
- `scheduler.py`: Background job management.
- `notifier.py`: Email notification logic.
