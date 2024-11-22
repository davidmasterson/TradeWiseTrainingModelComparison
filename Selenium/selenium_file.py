import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import date
from MachineLearningModels import manual_alg_requisition_script
import logging
from sector_finder import get_stock_company_name
import time
# Set Chrome options
options = Options()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--no-sandbox')  # Required for running in Docker or some headless environments
options.add_argument('--disable-dev-shm-usage')  # Prevent crashes due to low shared memory

# Initialize WebDriver

def get_historical_stock_specific_sentiment_scores(stock_symbol, date_of_lookup):
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # Open Google
        driver.get("https://google.com")
        
        # Wait for the search bar to be present
        search_bar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@name="q"]'))  # Search bar's XPath
        )
        print("Search bar found.")
        stock_name = get_stock_company_name(stock_symbol)
        # Input the stock name and financial news query
        search_query = f"{stock_name} {date_of_lookup.strftime('%B %Y')}"
        search_bar.send_keys(search_query)
        
        # Simulate pressing Enter
        search_bar.send_keys(Keys.RETURN)
        print(f"Searching for: {search_query}")
        
        # Wait for search results to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        print("Search results loaded.")
        
        # Optionally, capture the search results page
        driver.save_screenshot('search_results.png')
        
        # Extract links to the financial news
        headings = []
        li_container = driver.find_elements(By.XPATH, '//*[@id="rso"]')
        child_elements = li_container[0].find_elements(By.TAG_NAME, 'h3')
        for index, child in enumerate(child_elements, start=1):
            print(f"Child {index}: {child.text}")
            if len(child.text) > 10:
                headings.append(child.text)
        print("Top financial news links:")
        # Limit to top 5 results
        sa_neu, sa_pos, sa_neg = manual_alg_requisition_script.process_phrase_for_sentiment(headings)
        print(f'SENTIMENT: {sa_neu, sa_pos, sa_neg}')
        return [[sa_neu, sa_pos, sa_neg], headings]
        
    except Exception as e:
        logging.error(f"Unable to get stock detail for selected date due to: {e}")
        # Return default sentiment values in case of error
        return None, None, None
    finally:
        driver.close()
        
political_scores_cache = {}

def get_historical_political_sentiment_scores(date_of_lookup):
    # global political_scores_cache

    # # Check if the score for the given date is already cached
    # if date_of_lookup in political_scores_cache:
    #     print(f"Using cached political scores for {date_of_lookup}")
    #     return political_scores_cache[date_of_lookup]

    try:
        article_texts = []
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        month = date_of_lookup.strftime('%B').lower()
        date_string = date_of_lookup.strftime(f'{month}-%d-%Y')
        query = f'https://theweek.com {date_string}'
        url = 'https://google.com'
        driver.get(url)

        # Search for the query
        search_bar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@name="q"]'))
        )
        search_bar.send_keys(query)
        search_bar.send_keys(Keys.RETURN)
        print(f"Searching for: {query}")

        # Wait for search results to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        print("Search results loaded.")

        # Click on the first link
        this_link = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="rso"]/div[1]/div/div/div/div[1]/div/div/span/a/h3'))
        )
        this_link.click()

        # Scrape article content
        article_body = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="article-body"]'))
        )
        art = article_body.find_elements(By.TAG_NAME, 'p')
        for cld in art:
            article_texts.append(cld.text)

        print("Top financial news links:")
        
        # Process sentiment
        pol_neu, pol_pos, pol_neg = manual_alg_requisition_script.process_phrase_for_sentiment(article_texts)
        print(f'POLITICAL SCORES: {pol_neu, pol_pos, pol_neg}')

        # Cache the result
        political_scores_cache[date_of_lookup] = (pol_neu, pol_pos, pol_neg)
        return [[pol_neu, pol_pos, pol_neg], article_texts]

    except Exception as e:
        logging.error(f"Unable to get political detail for selected date due to: {e}")
        # Return default sentiment values in case of error
        return None, None, None

    finally:
        driver.quit()
    


   
    

