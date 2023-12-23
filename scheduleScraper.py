from selenium import webdriver
from bs4 import BeautifulSoup
import bs4
from datetime import datetime
import time

def scrapeSchedule():
    url = 'https://mytime.target.com/schedule'

    
    # Set up the Chrome webdriver
    driver = webdriver.Chrome()
    driver.get(url)


    # Wait for the dynamic content to load (you might need to adjust the sleep duration)
    time.sleep(40)

    # Get the page source after dynamic content has loaded
    page_source = driver.page_source

    # Close the webdriver
    driver.quit()

    # Parse the HTML content
    soup = BeautifulSoup(page_source, 'html.parser')

    # finding all paragraph tags that starts with weekdays or ends with AM or PM
    filtered_paragraphs = soup.find_all('p', string=lambda x: x and (x.startswith('Sunday') or
                                                                    x.startswith('Monday') or
                                                                    x.startswith('Tuesday') or 
                                                                    x.startswith('Wednesday') or 
                                                                    x.startswith('Thursday') or 
                                                                    x.startswith('Friday') or
                                                                    x.startswith('Saturday') or 
                                                                    x.endswith("AM") or 
                                                                    x.endswith("PM") or
                                                                    x.startswith("Service Advocate") or
                                                                    x.startswith("Checkout Advocate")))


    current_year = datetime.now().year #does not take into account if work is scheduled on next year
    start_time = end_time = formatted_date = role = ''
    
    wasDate = False # used to know when we should check for start_time
    wasStart = False # used to know when we should check for end_time
    wasEnd = False # used to know when we should check for role
    datesToSchedule = {} # {'2023-12-17': [9:00AM, 2:30PM]}
    for tag in filtered_paragraphs:
        if isinstance(tag, bs4.element.Tag):
            # date handling
            paragraph = tag.text
            parts = paragraph.split(', ')
            if len(parts) > 1:
                dateStringWithYear = f'{parts[1]}, {current_year}'
                date_object = datetime.strptime(dateStringWithYear, "%B %d, %Y")
                formatted_date = date_object.strftime("%Y-%m-%d")
                wasDate = True
                continue
        
        
        # start_time and end_time handling
        if wasDate:
            start_time = paragraph
            wasStart = True
            wasDate = False
        elif wasStart:
            end_time = paragraph
            wasEnd = True
            wasStart = False
        elif wasEnd:
            role = paragraph
            wasEnd = False

        
        # when we scrape the date, start_time, and end_time then we have a schedule to add to the dictionary
        if formatted_date and start_time and end_time and role:
            datesToSchedule[formatted_date] = [role, start_time, end_time]
            formatted_date = start_time = end_time = role = '' # reset those values for the next schedule to be added

    return datesToSchedule