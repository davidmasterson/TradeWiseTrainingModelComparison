import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random
import urllib



def search(required_keywords = None, encoded_query = None,current_page=None, ):
    if required_keywords:
        query = build_query(required_keywords)
        encoded_query = urllib.parse.quote(query)
    filtered_links = []
    # Correct pagination parameter
    target_url = f"https://www.bing.com/search?q={encoded_query}&rdr=1&first={current_page * 10}&setmkt=en-US&setlang=en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    response = requests.get(target_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch Bing results. Status code: {response.status_code}")
        return
    response_text = response.text
    soup = BeautifulSoup(response_text, 'html.parser')
    completeData = soup.find_all("li",{"class":"b_algo"})
    for i in range(0, len(completeData)):
        curlink =completeData[i].find("a")['href']
        filtered_links.append(curlink)
    time.sleep(2)  # Add delay between requests
    current_page += 1
    return [filtered_links, encoded_query, current_page]



def scrape_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to access {url}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = " ".join([p.get_text() for p in paragraphs])
        return article_text
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def get_sentiment_scores(text):
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        return scores['neg'], scores['neu'], scores['pos']

def get_filtered_links(soup, required_keywords):
    
    
    filtlinks = []  # To store filtered external links
    with open('results.txt','w') as writer:
        writer.write(soup.text)
        writer.close()
    # Bing result links are in <a> tags
    
        print(curlink)
        if (not 'thread' in curlink and not 'wikipedia' in curlink and not 'store' in curlink and not 'discussion' in curlink and not 'support' in curlink):
            print(f"Adding filtered link: {curlink}")
            filtlinks.append(curlink)
    return filtlinks



def build_query(required_keywords):
    return " ".join(required_keywords)








def filter_results_by_date(links, target_date):
    """
    Filters results by checking the presence of a specific date in the page content.

    Args:
        links (list): List of URLs to check.
        target_date (str): Specific date to look for (e.g., "February 20, 2023").

    Returns:
        list: Links containing the target date.
    """
    matching_links = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for link in links:
        try:
            response = requests.get(link, headers=headers)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if target_date in soup.text:
                print(f"Found date in: {link}")
                matching_links.append(link)
        except Exception as e:
            print(f"Error processing {link}: {e}")
    
    return matching_links, links
