from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select  # Import the Select class
import urllib.parse
import os
import requests

def download_pdf_selenium_firefox(part_number, output_dir="pdfs"):
    """
    Downloads the PDF associated with a given part number from the Cyntec website using Firefox,
    including dropdown selection, form filling, and search execution.

    Args:
        part_number (str): The part number to search for.
        output_dir (str): The directory to save the PDF to.
    """

    try:
        # Set up Firefox with geckodriver-manager
        service = FirefoxService(GeckoDriverManager().install())
        options = Options()
        driver = webdriver.Firefox(service=service, options=options)

        url = "https://www.cyntec.com/partNumberSearch.aspx?id=239"
        driver.get(url)

        # Wait for the page to load and elements to be available
        wait = WebDriverWait(driver, 20)  # Increased wait time to 20 seconds

        # 1. Select "Inductor" from the "Product" dropdown
        product_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ddlProduct"))
        )
        select = Select(product_dropdown)
        select.select_by_visible_text("Inductor")  # Select by visible text

        # 2. Find and fill the "Part Number" field
        part_number_input = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtPartNumber"))
        )
        part_number_input.send_keys(part_number)

        # 3. Find and click the "Search" button
        search_button = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnSearch"))
        )
        search_button.click()

        # Wait for the search results to load and the PDF link to appear
        wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_gvSearchResult"))
        )

        # 4. Find the PDF link using a more robust XPath
        pdf_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_gvSearchResult']//a[contains(@href, '.pdf')]"))
        )

        if pdf_link:
            pdf_url = urllib.parse.urljoin(url, pdf_link.get_attribute("href"))
            pdf_filename = f"{part_number}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)

            # Download the PDF
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(pdf_path, "wb") as f:
                f.write(pdf_response.content)

            print(f"PDF for {part_number} downloaded successfully to {pdf_path}")
        else:
            print(f"No PDF found for part number: {part_number}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the browser
        if 'driver' in locals():
            driver.quit()

# Example usage
part_number = "VCHA042A-100MS6"
download_pdf_selenium_firefox(part_number)