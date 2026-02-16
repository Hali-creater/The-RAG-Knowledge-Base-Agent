from database import save_lead, init_db
from scraper import RealEstateScraper
import random

def seed_leads():
    init_db()
    scraper = RealEstateScraper()

    sample_raw_leads = [
        {
            "title": "URGENT: Must sell 3BR house in Austin - Relocating",
            "description": "I need to sell my house immediately due to a job transfer. 3 bedrooms, 2 baths, large backyard. Asking $350k or best offer. Contact me at 512-555-0199 or email fastsale@gmail.com. Below market value for quick sale!",
            "url": "https://example.com/listing/1",
            "source": "Reddit"
        },
        {
            "title": "Looking to buy a condo in Miami downtown",
            "description": "Hi, I am searching for a property to purchase in Miami. My budget is around $500,000. Prefer 2 bedrooms with a view. Please send details to buyer_agent@yahoo.com",
            "url": "https://example.com/listing/2",
            "source": "Craigslist"
        },
        {
            "title": "Off-market investment opportunity - Multi-family",
            "description": "Cash buyers only. Distressed multi-family property in Atlanta. High ROI potential. Foreclosure process started. Call for details: 404-555-9876",
            "url": "https://example.com/listing/3",
            "source": "Google"
        },
        {
            "title": "Moving soon, selling my apartment furniture and lease",
            "description": "Selling some items, also looking for someone to take over my lease. Not a house sale but a rental assignment.",
            "url": "https://example.com/listing/4",
            "source": "Reddit"
        },
        {
            "title": "Searching for luxury villa in Beverly Hills",
            "description": "Client looking for luxury properties in 90210. Budget $5M+. Contact via DM.",
            "url": "https://example.com/listing/5",
            "source": "Alert"
        }
    ]

    print(f"[*] Seeding {len(sample_raw_leads)} sample leads...")
    for raw in sample_raw_leads:
        processed = scraper.process_lead(raw)
        save_lead(processed)
        print(f"    - Processed: {processed['title']} (Score: {processed['intent_score']})")

    print("\n[+] Seeding complete! Visit your dashboard to see the results.")

if __name__ == "__main__":
    seed_leads()
