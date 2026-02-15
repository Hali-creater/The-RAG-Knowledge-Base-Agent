import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import praw
import os
import random
import time
try:
    from extractor import extract_entities
    from classifier import classify_intent
    from scorer import calculate_score
except ImportError:
    from .extractor import extract_entities
    from .classifier import classify_intent
    from .scorer import calculate_score

class RealEstateScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_real_estate_site(self, url):
        """Example of using Playwright to scrape a real site."""
        leads = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")

                # This is a generic example, you'd need to adapt selectors for a specific site
                # For demonstration, we'll look for common listing patterns
                listings = page.query_selector_all(".listing, .post, .ad-item")
                for listing in listings[:5]:
                    title = listing.query_selector(".title, h2, h3").inner_text() if listing.query_selector(".title, h2, h3") else "No Title"
                    desc = listing.query_selector(".description, p").inner_text() if listing.query_selector(".description, p") else "No Description"
                    leads.append({
                        "post_title": title,
                        "full_description": desc,
                        "source_platform": url.split("//")[-1].split("/")[0]
                    })
                browser.close()
        except Exception as e:
            print(f"Playwright scraping failed: {e}")
        return leads

    def scrape_reddit(self, subreddits=['realestate', 'HomeBuying', 'property', 'investing']):
        """Scrapes Reddit for property leads."""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "RealEstateLeadBot/1.0")

        if not client_id or not client_secret:
            print("Reddit credentials not set. Skipping Reddit scraping.")
            return []

        leads = []
        try:
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )

            keywords = ['selling', 'buying', 'for sale', 'looking to buy', 'owner selling', 'searching for property']

            for sub_name in subreddits:
                subreddit = reddit.subreddit(sub_name)
                # Search new posts
                for submission in subreddit.new(limit=10):
                    text = (submission.title + " " + submission.selftext).lower()
                    if any(kw in text for kw in keywords):
                        leads.append({
                            "post_title": submission.title,
                            "full_description": submission.selftext[:500] + ("..." if len(submission.selftext) > 500 else ""),
                            "source_platform": f"Reddit/r/{sub_name}"
                        })
        except Exception as e:
            print(f"Reddit scraping failed: {e}")

        return leads

    def scrape_mock_leads(self):
        """Simulates scraping leads from a mock platform."""
        mock_leads = [
            {
                "post_title": "Beautiful 3BHK Apartment for Sale",
                "full_description": "I am selling my beautiful 3BHK apartment in New York. Urgent sale! Direct owner. Contact: 212-555-0199 or email owner@example.com. Price: $450,000",
                "source_platform": "MockPlatform1"
            },
            {
                "post_title": "Looking to buy a studio in Brooklyn",
                "full_description": "Budget is $300k. Searching for a property near the subway in Brooklyn. Please call 718-555-0122.",
                "source_platform": "MockPlatform2"
            },
            {
                "post_title": "Urgent: Need to sell my villa",
                "full_description": "Relocating abroad. Must sell house in Los Angeles. $1,200,000. 310-555-9876. serious buyers only.",
                "source_platform": "MockPlatform1"
            }
        ]
        return mock_leads

    def process_raw_lead(self, raw_lead):
        entities = extract_entities(raw_lead['full_description'])
        intent_type, intent_confidence = classify_intent(raw_lead['full_description'])

        lead_data = {
            **raw_lead,
            **entities,
            "intent_type": intent_type,
            "intent_confidence": intent_confidence,
            "status": "New"
        }

        lead_data['lead_score'] = calculate_score(lead_data)
        lead_data['property_details'] = lead_data['post_title'] # Simple mapping for now

        return lead_data

    def run(self):
        print("Starting scraping...")
        # In a real scenario, you'd iterate over multiple URLs/platforms
        raw_leads = self.scrape_mock_leads()

        # Add Reddit leads if available
        reddit_leads = self.scrape_reddit()
        raw_leads.extend(reddit_leads)

        processed_leads = []
        for raw in raw_leads:
            processed = self.process_raw_lead(raw)
            processed_leads.append(processed)

        print(f"Scraped and processed {len(processed_leads)} leads.")
        return processed_leads

if __name__ == "__main__":
    # To run this as a script, we need to handle relative imports or adjust sys.path
    # For now, let's just test the logic if we were calling it from main.py
    pass
