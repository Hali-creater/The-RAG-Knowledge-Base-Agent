import time
from playwright.sync_api import sync_playwright, expect

def verify_cloud_integrations():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})

        # Navigate to the app
        page.goto("http://localhost:8501")

        # Wait for the app to load
        page.wait_for_selector("[data-testid='stSidebar']")

        # Switch to Admin role
        page.get_by_text("👤 User & Model Settings").click()
        time.sleep(1)
        page.get_by_label("Select Your Role").click()
        page.get_by_text("Admin", exact=True).click()
        time.sleep(2)

        # Open Knowledge Ingestion expander
        page.get_by_text("📁 Knowledge Ingestion").click()
        time.sleep(1)

        # Open Cloud Integrations expander
        page.get_by_text("☁️ Cloud Integrations").click()
        time.sleep(1)

        # Check GDrive
        page.get_by_text("GDrive", exact=True).click()
        time.sleep(1)
        sidebar = page.locator("[data-testid='stSidebar']")
        sidebar.screenshot(path="verification/sidebar_gdrive.png")

        # Check SharePoint
        page.get_by_text("SharePoint", exact=True).click()
        time.sleep(1)
        sidebar.screenshot(path="verification/sidebar_sharepoint.png")

        browser.close()

if __name__ == "__main__":
    verify_cloud_integrations()
