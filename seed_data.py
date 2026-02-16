from database import save_lead, init_db
from scraper import RealEstateScraper
import os

def seed_leads():
    init_db()
    scraper = RealEstateScraper()
    city = os.getenv("TARGET_CITY", "Dallas")

    sample_raw_leads = [
        {
            "title": f"Need to sell house quickly {city} - Divorce",
            "description": f"Due to a divorce, I need to sell my house in {city} fast. It is a 4BR property. Price is negotiable for a cash buyer. Call me at 214-555-0102. Inherited this property but can no longer maintain it.",
            "url": "https://example.com/dallas-lead-1",
            "source": "Google"
        },
        {
            "title": f"Moving to {city} - Looking to buy a house",
            "description": f"My family is relocating to {city} next month. We are first time home buyers looking for a 3 bedroom home in a good school district. Budget $450,000. Email me at smith.family@gmail.com",
            "url": "https://example.com/dallas-lead-2",
            "source": "Google"
        },
        {
            "title": f"FSBO {city} - Motivated Seller",
            "description": f"For sale by owner in {city}. Motivated seller, moving soon due to job transfer. Owner financing available. Contact 214-555-9988 for a tour.",
            "url": "https://dallas.craigslist.org/reo/12345.html",
            "source": "Craigslist (reo)"
        },
        {
            "title": f"Searching for property in {city} - Cash Buyer",
            "description": f"I am a cash buyer looking to buy homes in {city} in any condition. Pre foreclosure, behind on mortgage, no problem. I can close quickly. 214-555-4433",
            "url": "https://dallas.craigslist.org/hww/67890.html",
            "source": "Craigslist (hww)"
        },
        {
            "title": f"Best real estate agent in {city}?",
            "description": f"Hi r/realestate, I'm thinking about selling my house in {city} and want to know who is the best realtor to work with for a quick sale. FSBO seems hard.",
            "url": "https://www.reddit.com/r/realestate/comments/test",
            "source": "Reddit"
        }
    ]

    print(f"[*] Seeding {len(sample_raw_leads)} high-intent {city} leads...")
    for raw in sample_raw_leads:
        processed = scraper.process_lead(raw)
        save_lead(processed)
        print(f"    - Processed: {processed['title']} (Score: {processed['intent_score']})")

    print("\n[+] Seeding complete! Visit your dashboard to see your GOLD leads.")

if __name__ == "__main__":
    seed_leads()
