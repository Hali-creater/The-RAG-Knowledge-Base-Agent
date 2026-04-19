import asyncio
from playwright.sync_api import sync_playwright
import os
import time

def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Start streamlit in background
        os.system("streamlit run streamlit_app.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &")
        time.sleep(10) # Wait for it to start

        try:
            page.goto("http://localhost:8501")
            page.wait_for_selector("text=System Control", timeout=30000)

            # Click User & Model Settings
            page.click("text=User & Model Settings")
            time.sleep(1)

            # Change role to Admin
            page.click('div[data-testid="stSelectbox"] >> text=Employee')
            time.sleep(1)
            page.click('li[role="option"] >> text=Admin')
            time.sleep(2)

            # Now "Knowledge Ingestion" should appear
            page.click("text=Knowledge Ingestion")
            time.sleep(1)

            # Open Cloud Integrations expander
            page.click("text=Cloud Integrations")
            time.sleep(2)

            # Check for GDrive Connect button
            page.screenshot(path="verification/gdrive_auth_btn_final.png")
            print("GDrive screenshot saved.")

            # Switch to SharePoint
            page.click("text=SharePoint")
            time.sleep(1)
            page.screenshot(path="verification/sp_auth_btn_final.png")
            print("SharePoint screenshot saved.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
            os.system("pkill -f streamlit")

if __name__ == "__main__":
    if not os.path.exists("verification"):
        os.makedirs("verification")
    verify_ui()
