import time
from playwright.sync_api import sync_playwright

def verify_final():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})
        page.goto("http://localhost:8501")
        time.sleep(10) # Give it plenty of time

        content = page.content()
        if "IndentationError" in content:
             print("FAIL: IndentationError found.")
        elif "fix-gdrive-auth-timeout" in content:
             print("FAIL: Erroneous string found in rendered content.")
        else:
             print("SUCCESS: No IndentationError or erroneous string found.")

        page.screenshot(path="verification/final_check.png")
        browser.close()

if __name__ == "__main__":
    verify_final()
