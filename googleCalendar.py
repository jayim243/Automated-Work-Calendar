from scheduleScraper import scrapeSchedule
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Set the path to your credentials JSON file 
credentials_path = 'your google calendar API credentials'

# Set the path to the token JSON file (will be created if it doesn't exist)
token_path = 'token.json'

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    credentials = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        credentials = Credentials.from_authorized_user_file(token_path)
    
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(credentials.to_json())

    return credentials

def parse_datetime(date_str, time_str):
    # Parse date and time
    datetime_str = f'{date_str} {time_str}'
    parsed_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %I:%M%p')
    return parsed_datetime.strftime('%Y-%m-%dT%H:%M:%S')

def add_event_to_calendar(date, start_time, end_time, event_summary, credentials):
    service = build('calendar', 'v3', credentials=credentials)

    # Parse start and end datetime strings
    start_datetime = parse_datetime(date, start_time)
    end_datetime = parse_datetime(date, end_time)

    event = {
        'summary': event_summary,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'America/Los_Angeles',
        },
    }

    # Specify the calendar ID where you want to add the event
    calendar_id = 'primary'

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f'Event created: {event_summary} on {date} starting from {start_time} ending at {end_time} {event.get("htmlLink")}')

if __name__ == '__main__':
    # call scrapeSchedule() to scrape dates and times from work schedule which returns a dictionary: {'2023-12-17': [9:00AM, 2:30PM]}
    schedule = scrapeSchedule()
    for date, times in schedule.items(): 
        date = date
        role = schedule[date][0]
        start_time = schedule[date][1]
        end_time = schedule[date][2]
        event_summary = f'Work {role}'

        credentials = authenticate_google_calendar()
        add_event_to_calendar(date, start_time, end_time, event_summary, credentials) #calls method to add event for each date and times
