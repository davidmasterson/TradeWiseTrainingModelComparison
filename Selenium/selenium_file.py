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
import requests
from bs4 import BeautifulSoup
import time




# Initialize WebDriver

def get_historical_stock_specific_sentiment_scores(stock_symbol, date_of_lookup):
    try:
        
        import os
        logging.debug(os.environ['PATH'])
    
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Runs Chrome in headless mode
        options.add_argument('--no-sandbox')  # Prevents sandboxing for Chrome
        options.add_argument('--disable-dev-shm-usage')  # Reduces shared memory usage
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument('--window-size=1920x1080')  # Set a default window size
        options.add_argument('--log-level=3')  # Set log level
        options.add_argument('--verbose')  # Enable verbose logging

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
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

def get_historical_political_sentiment_scores(date_of_lookup, driver=None):
    
    try:
        # Check if the date is already cached
        if date_of_lookup in political_scores_cache:
            return political_scores_cache[date_of_lookup]
        
        # Format date for Wikipedia query
        month = date_of_lookup.strftime('%B').lower()
        day = date_of_lookup.strftime('%d')
        finished_day = day.lstrip('0')  # Remove leading zero
        caps_month = month.capitalize()
        wikipedia_month_search = f"{date_of_lookup.year}_{caps_month}_{finished_day}"
        date_string = f"{date_of_lookup.year} {caps_month} {finished_day}"
        
        # Wikipedia portal URL for current events
        wiki_url = f"https://en.wikipedia.org/wiki/Portal:Current_events/{wikipedia_month_search}"
        # Send GET request to Wikipedia
        response = requests.get(wiki_url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch page: {wiki_url} (Status Code: {response.status_code})")
            return None, None, None
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main content section for the day
        content_section = soup.find('div', id=wikipedia_month_search)
        if not content_section:
            logging.warning(f"Content not found for {date_of_lookup} on {wiki_url}")
            return None, None, None
        # Extract relevant excerpts
        article_excerpts = []
        for ul in content_section.find_all('ul'):
            article_excerpts.append(ul.get_text(strip=True))
        # Deduplicate excerpts
        articles_set = set(article_excerpts)
        
        # Process sentiment
        pol_neu, pol_pos, pol_neg = manual_alg_requisition_script.process_phrase_for_sentiment(articles_set)
        # Cache the result
        political_scores_cache[date_of_lookup] = (pol_neu, pol_pos, pol_neg)
        return [[pol_neu, pol_pos, pol_neg], articles_set]
    except Exception as e:
        logging.error(f"Error fetching political sentiment for {date_of_lookup}: {e}")
        return None, None, None

    


   
def get_correctly_formatted_day(day):
    formatted_day = day
    if day[0] == '0':
        formatted_day = day[1]
    return formatted_day
            

def normalize_and_percentage(pol_neu, pol_pos, pol_neg):
    # Step 1: Calculate the total sum
    total = pol_neu + pol_pos + pol_neg
    if total == 0:
        # Handle edge case where all variables are zero
        return 0, 0, 0

    # Step 2: Calculate percentages for each variable
    pol_neu = int((pol_neu / total) * 100)
    pol_pos = int((pol_pos / total) * 100)
    pol_neg = int((pol_neg / total) * 100)

    # Store values in a list for easier adjustment
    ratings_list = [pol_neu, pol_pos, pol_neg]

    # Step 3: Adjust the sum if it's less than 100
    while sum(ratings_list) < 100:
        for i in range(len(ratings_list)):
            if ratings_list[i] == 0:  # Increase only non-zero values
                ratings_list[i] = 1
            else:
                ratings_list[0] += 1
                break  # Break to distribute evenly

    # Step 4: Return the updated values
    return ratings_list[0], ratings_list[1], ratings_list[2]

