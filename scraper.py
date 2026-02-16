import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import praw
import imaplib
import email
from email.header import decode_header
import os
import time
import urllib.parse
import logging
from extractor import extract_entities
from classifier import classify_intent
from scorer import calculate_score
from database import get_content_hash

logger = logging.getLogger(__name__)

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
            logger.warning("Reddit API keys missing. Skipping Reddit.")
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
                'realtors', 'HouseHunting', 'FirstTimeHomeBuyer'
            ]
            keywords = [
                'selling', 'buying', 'for sale', 'looking to buy',
                'owner selling', 'searching for property', 'fsbo',
                'investment property', 'motivated seller', 'urgent sale'
            ]

            for sub_name in subreddits:
                logger.info(f"Checking r/{sub_name}...")
                subreddit = reddit.subreddit(sub_name)
                for submission in subreddit.new(limit=15):
                    text = (submission.title + " " + submission.selftext).lower()
                    if any(kw in text for kw in keywords):
                        leads.append({
                            "title": submission.title,
                            "description": submission.selftext,
                            "url": f"https://www.reddit.com{submission.permalink}",
                            "source": "Reddit"
                        })
        except Exception as e:
            logger.error(f"Reddit error: {e}")
        return leads

    def _scrape_playwright_sources(self):
        """Combines Craigslist and Google Search into a single Playwright session."""
        city = os.getenv("TARGET_CITY", "dallas")
        cl_keywords = [
            "owner financing", "must sell", "motivated seller",
            "FSBO", "sell my house", "cash buyer needed",
            "relocating", "moving soon"
        ]
        google_queries = [
            f"\"sell my house fast {city}\"",
            f"\"thinking about selling my house in {city}\"",
            f"\"looking to buy a house in {city}\"",
            f"\"need to sell house quickly {city}\""
        ]

        leads = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self.headers['User-Agent'])
                page = context.new_page()

                # 1. Craigslist Scraping
                for section in ["reo", "hww"]: # reo=owner, hww=housing wanted
                    for kw in cl_keywords:
                        query = urllib.parse.quote_plus(kw)
                        url = f"https://{city}.craigslist.org/search/{section}?query={query}"
                        logger.info(f"Checking Craigslist ({section}): {kw}")
                        try:
                            page.goto(url, wait_until="networkidle")
                            # Craigslist search results are in 'li.cl-static-search-result' or similar
                            # Let's try to find 'a.result-title' or new structure
                            page.wait_for_timeout(1000)

                            # Detect if blocked
                            if "blocked" in page.title().lower():
                                logger.error(f"Craigslist blocked our request for {kw}")
                                continue

                            # New CL structure uses .cl-search-result
                            items = page.query_selector_all(".cl-search-result, .result-row")
                            for item in items[:10]:
                                link_el = item.query_selector("a.cl-app-anchor, a.result-title")
                                if link_el:
                                    title = link_el.inner_text()
                                    href = link_el.get_attribute("href")
                                    leads.append({
                                        "title": title,
                                        "description": f"Craigslist lead found in {section} section.",
                                        "url": href,
                                        "source": f"Craigslist ({section})"
                                    })
                        except Exception as e:
                            logger.error(f"Error scraping CL {kw}: {e}")
                        time.sleep(2)

                # 2. Google Search Scraping
                logger.info(f"Starting Google Search monitoring for {city}...")
                for query in google_queries:
                    try:
                        page.goto(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
                        page.wait_for_timeout(2000)
                        results = page.query_selector_all("div.g")
                        for res in results[:3]:
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
                    except Exception as e:
                        logger.error(f"Google error for {query}: {e}")
                    time.sleep(3)

                browser.close()
        except Exception as e:
            logger.error(f"Playwright main error: {e}")
        return leads

    def scrape_google_alerts(self):
        """Fetches Google Alerts from Gmail via IMAP."""
        imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        imap_user = os.getenv("IMAP_USER")
        imap_password = os.getenv("IMAP_PASSWORD")

        if not imap_user or not imap_password:
            logger.warning("IMAP credentials missing. Skipping Google Alerts.")
            return []

        leads = []
        try:
            logger.info("Checking Google Alerts via IMAP...")
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(imap_user, imap_password)
            mail.select("inbox")

            status, messages = mail.search(None, '(FROM "googlealerts-noreply@google.com")')
            if status != "OK":
                return []

            for num in messages[0].split()[-10:]:
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
                            for link in soup.find_all('a'):
                                title = link.get_text().strip()
                                url = link.get('href')
                                if url and "google.com/url?" in url and len(title) > 20:
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
            logger.error(f"Google Alerts error: {e}")
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
        all_raw.extend(self.scrape_google_alerts())
        all_raw.extend(self._scrape_playwright_sources())

        logger.info(f"Total raw leads found: {len(all_raw)}")
        processed = []
        for raw in all_raw:
            processed.append(self.process_lead(raw))
        return processed
