from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import requests
from urllib.parse import urljoin
import time

def imagedown(url, folder):
    # Configure Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('path/to/chrome/driver')  # Update with the correct path
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Open the URL
        driver.get(url)
        
        # Scroll to the bottom of the page to trigger lazy-loading
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(20)  # Wait for lazy-loading
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Extract all image elements
        images = driver.find_elements(By.TAG_NAME, 'img')
        
        # Create folder if not exists
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        for image in images:
            try:
                # Check for 'src', 'data-src', or 'srcset'
                src = image.get_attribute('src') or image.get_attribute('data-src')
                srcset = image.get_attribute('srcset')
                
                # If srcset is available, choose the highest-resolution URL
                if srcset:
                    src = srcset.split(',')[-1].strip().split(' ')[0]
                
                if src and not src.startswith('data:'):
                    # Resolve relative URLs to absolute URLs
                    src = urljoin(url, src)
                    
                    alt = image.get_attribute('alt') or "image"
                    filename = alt.replace(' ', '-').replace('/', '') + '.jpg'
                    filepath = os.path.join(folder, filename)
                    
                    # Download the image
                    response = requests.get(src, stream=True)
                    if response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Error downloading image: {e}")
    finally:
        driver.quit()

# Run the function
imagedown('https://japan-clothing.com/collections/kimonos-for-women', 'clothing')
