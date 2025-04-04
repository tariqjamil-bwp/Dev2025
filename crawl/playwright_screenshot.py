from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    page.goto("https://dps.psx.com.pk/company/GGGL")
    page.screenshot(path="example.png")
    browser.close()

    