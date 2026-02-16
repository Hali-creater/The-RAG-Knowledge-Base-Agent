import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import praw
import imaplib
import email
from email.header import decode_header
import os
import time
from extractor import extract_entities
from classifier import classify_intent
from scorer import calculate_score
from database import get_content_hash

class RealEstateScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_reddit(self):
        """Scrapes Reddit for property leads."""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "RealEstateLeadBot/1.0")

        if not client_id or not client_secret:
            return []

        leads = []
        try:
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            subreddits = [
                'realestate', 'HomeBuying', 'property', 'investing',
                'RealEstateTechnology', 'realtors', 'HouseHunting',
                'FirstTimeHomeBuyer', 'commercialrealestate'
            ]
            keywords = [
                'selling', 'buying', 'for sale', 'looking to buy',
                'owner selling', 'searching for property', 'fsbo',
                'investment property', 'motivated seller', 'urgent sale'
            ]

            for sub_name in subreddits:
                print(f"[*] Checking r/{sub_name}...")
                subreddit = reddit.subreddit(sub_name)
                for submission in subreddit.new(limit=25):
                    text = (submission.title + " " + submission.selftext).lower()
                    if any(kw in text for kw in keywords):
                        leads.append({
                            "title": submission.title,
                            "description": submission.selftext,
                            "url": f"https://www.reddit.com{submission.permalink}",
                            "source": "Reddit"
                        })
        except Exception as e:
            print(f"Reddit error: {e}")
        return leads

    def scrape_craigslist(self):
        """Scrapes Craigslist RSS feeds."""
        # Example for multiple cities/categories
        urls = [
            "https://newyork.craigslist.org/search/reo?format=rss",
            "https://losangeles.craigslist.org/search/reo?format=rss"
        ]
        leads = []
        for url in urls:
            try:
                print(f"[*] Checking Craigslist RSS: {url}")
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                for item in items:
                    leads.append({
                        "title": item.find('title').text,
                        "description": item.find('description').text,
                        "url": item.find('link').text,
                        "source": "Craigslist"
                    })
            except Exception as e:
                print(f"Craigslist error: {e}")
        return leads

    def scrape_google_alerts(self):
        """Fetches Google Alerts from Gmail via IMAP."""
        imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        imap_user = os.getenv("IMAP_USER")
        imap_password = os.getenv("IMAP_PASSWORD")

        if not imap_user or not imap_password:
            return []

        leads = []
        try:
            print("[*] Checking Google Alerts via IMAP...")
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(imap_user, imap_password)
            mail.select("inbox")

            # Search for emails from Google Alerts
            status, messages = mail.search(None, '(FROM "googlealerts-noreply@google.com")')
            if status != "OK":
                return []

            for num in messages[0].split()[-10:]: # Get last 10 alerts
                status, data = mail.fetch(num, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/html":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        if body:
                            soup = BeautifulSoup(body, 'html.parser')
                            # Google Alerts HTML structure usually has links in <a> tags
                            # with titles in them.
                            for link in soup.find_all('a'):
                                title = link.get_text().strip()
                                url = link.get('href')
                                # Filter for actual alerts (often have 'url?' in href)
                                if url and "google.com/url?" in url and len(title) > 20:
                                    # Extract the real URL from Google's redirect
                                    import urllib.parse
                                    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('url', [url])[0]

                                    leads.append({
                                        "title": title,
                                        "description": "Lead detected via Google Alerts.",
                                        "url": parsed_url,
                                        "source": "Alert"
                                    })
            mail.logout()
        except Exception as e:
            print(f"Google Alerts error: {e}")
        return leads

    def scrape_google_search(self):
        """Basic Google Search result monitoring via Playwright."""
        queries = [
            "'must sell' house", "'urgent sale' real estate",
            "looking to buy property", "motivated seller real estate",
            "cash buyer property", "need to sell my home fast"
        ]
        leads = []
        try:
            print("[*] Starting Google Search monitoring...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                for query in queries:
                    page.goto(f"https://www.google.com/search?q={query}")
                    page.wait_for_timeout(2000)
                    results = page.query_selector_all("div.g")
                    for res in results[:5]:
                        title_el = res.query_selector("h3")
                        link_el = res.query_selector("a")
                        snippet_el = res.query_selector("div.VwiC3b")
                        if title_el and link_el:
                            leads.append({
                                "title": title_el.inner_text(),
                                "description": snippet_el.inner_text() if snippet_el else "",
                                "url": link_el.get_attribute("href"),
                                "source": "Google"
                            })
                browser.close()
        except Exception as e:
            print(f"Google error: {e}")
        return leads

    def process_lead(self, raw_lead):
        # Extract entities
        entities = extract_entities(raw_lead['description'])

        # Intent classification
        lead_type, confidence = classify_intent(raw_lead['title'] + " " + raw_lead['description'])

        # Scoring
        score, level = calculate_score({
            **raw_lead,
            **entities
        })

        return {
            **raw_lead,
            **entities,
            "lead_type": lead_type,
            "intent_score": score,
            "intent_level": level,
            "content_hash": get_content_hash(raw_lead['description']),
            "status": "New"
        }

    def run_all(self):
        all_raw = []
        all_raw.extend(self.scrape_reddit())
        all_raw.extend(self.scrape_craigslist())
        all_raw.extend(self.scrape_google_search())
        all_raw.extend(self.scrape_google_alerts())

        print(f"[+] Total raw leads found: {len(all_raw)}")
        processed = []
        for raw in all_raw:
            processed.append(self.process_lead(raw))
        return processed
