#!/usr/bin/env python3
"""
Gmail and Google Calendar Checker CLI (gm)

Checks both Gmail and Google Calendar using existing credentials.
"""

import argparse
import os
import pickle
import base64
import sys
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError


# Scopes for Gmail and Calendar access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]


def get_google_credentials():
    """Load existing credentials from JSON files."""
    creds = None
    
    # Try to load from the available credential files
    credential_paths = [
        os.path.expanduser('~/.config/google/oauth-credentials.json'),
        os.path.expanduser('~/.gemini/oauth_creds.json')
    ]
    
    for cred_path in credential_paths:
        if os.path.exists(cred_path):
            print(f"Loading credentials from {cred_path}")
            try:
                # Load credentials from JSON file
                creds = Credentials.from_authorized_user_file(cred_path, SCOPES)
                break
            except Exception as e:
                print(f"Could not load credentials from {cred_path}: {e}")
    
    if not creds:
        print("No valid credentials found")
        return None
    
    # Refresh credentials if needed
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print("Credentials refreshed successfully")
        except RefreshError as e:
            print(f"Could not refresh credentials: {e}")
            return None
    
    return creds


def read_latest_email(service):
    """Read the latest email from Gmail."""
    try:
        # Get the latest email
        results = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No emails found.")
            return None
        
        # Get the latest message
        latest_message = messages[0]
        msg = service.users().messages().get(userId='me', id=latest_message['id']).execute()
        
        # Extract email details
        email_data = {}
        
        # Get headers
        headers = msg['payload'].get('headers', [])
        for header in headers:
            name = header['name']
            value = header['value']
            if name.lower() == 'subject':
                email_data['subject'] = value
            elif name.lower() == 'from':
                email_data['from'] = value
            elif name.lower() == 'date':
                email_data['date'] = value
        
        # Get body
        parts = msg['payload'].get('parts', [])
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    decoded_data = base64.urlsafe_b64decode(data.encode('ASCII'))
                    email_data['body'] = decoded_data.decode('UTF-8')
                    break
        else:
            # For simple messages without parts
            if 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                data = msg['payload']['body']['data']
                decoded_data = base64.urlsafe_b64decode(data.encode('ASCII'))
                email_data['body'] = decoded_data.decode('UTF-8')
        
        return email_data
    except Exception as e:
        print(f"Error reading email: {e}")
        return None


def get_next_week_events(service):
    """Get calendar events for the next week."""
    try:
        # Calculate the next week's time range
        now = datetime.utcnow()
        next_week = now + timedelta(days=7)
        
        # Format dates for the API
        time_min = now.isoformat() + 'Z'
        time_max = next_week.isoformat() + 'Z'
        
        # Get events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print("No upcoming events found for the next week.")
            return []
        
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_list.append({
                'summary': event.get('summary', 'No title'),
                'start': start,
                'end': end
            })
        
        return event_list
    except Exception as e:
        print(f"Error getting calendar events: {e}")
        return []


def check_both_services():
    """Check both Gmail and Google Calendar."""
    print("Checking access to Gmail and Google Calendar...")
    
    # Get credentials
    creds = get_google_credentials()
    
    if not creds:
        print("Could not authenticate with Google services.")
        return
    
    print("Successfully authenticated with Google services!")
    
    # Build services
    try:
        gmail_service = build('gmail', 'v1', credentials=creds)
        calendar_service = build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Error building Google services: {e}")
        return
    
    print("\n" + "="*50)
    print("READING LATEST EMAIL")
    print("="*50)
    
    latest_email = read_latest_email(gmail_service)
    if latest_email:
        print(f"Subject: {latest_email.get('subject', 'No subject')}")
        print(f"From: {latest_email.get('from', 'Unknown sender')}")
        print(f"Date: {latest_email.get('date', 'Unknown date')}")
        print(f"Body preview: {latest_email.get('body', 'No body')[:200]}...")
    else:
        print("Could not retrieve latest email.")
    
    print("\n" + "="*50)
    print("CALENDAR EVENTS FOR NEXT WEEK")
    print("="*50)
    
    next_week_events = get_next_week_events(calendar_service)
    if next_week_events:
        for i, event in enumerate(next_week_events, 1):
            print(f"{i}. {event['summary']}")
            print(f"   Start: {event['start']}")
            print(f"   End: {event['end']}")
            print()
    else:
        print("No events found for the next week.")


def read_latest_email_only():
    """Only read latest email."""
    creds = get_google_credentials()
    
    if not creds:
        print("Could not authenticate with Gmail.")
        return
    
    try:
        gmail_service = build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return
    
    latest_email = read_latest_email(gmail_service)
    if latest_email:
        print(f"Latest Email:")
        print(f"Subject: {latest_email.get('subject', 'No subject')}")
        print(f"From: {latest_email.get('from', 'Unknown sender')}")
        print(f"Date: {latest_email.get('date', 'Unknown date')}")
        print(f"Body: {latest_email.get('body', 'No body')[:500]}...")
    else:
        print("Could not retrieve latest email.")


def get_calendar_events_only():
    """Only get calendar events."""
    creds = get_google_credentials()
    
    if not creds:
        print("Could not authenticate with Google Calendar.")
        return
    
    try:
        calendar_service = build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Error building Calendar service: {e}")
        return
    
    next_week_events = get_next_week_events(calendar_service)
    if next_week_events:
        print("Calendar Events for Next Week:")
        for i, event in enumerate(next_week_events, 1):
            print(f"{i}. {event['summary']}")
            print(f"   Start: {event['start']}")
            print(f"   End: {event['end']}")
            print()
    else:
        print("No events found for the next week.")


def main():
    parser = argparse.ArgumentParser(description="Gmail and Google Calendar Checker CLI (gm)")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check both command
    parser_both = subparsers.add_parser('both', help='Check both Gmail and Google Calendar')
    
    # Check email only command
    parser_email = subparsers.add_parser('email', help='Check only Gmail')
    
    # Check calendar only command
    parser_calendar = subparsers.add_parser('calendar', help='Check only Google Calendar')
    
    args = parser.parse_args()
    
    if args.command == 'both':
        check_both_services()
    elif args.command == 'email':
        read_latest_email_only()
    elif args.command == 'calendar':
        get_calendar_events_only()
    else:
        # Default behavior if no command specified
        check_both_services()


if __name__ == "__main__":
    main()