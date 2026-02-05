#!/usr/bin/env python3
"""
PostgreSQL Google Calendar CLI (gc)

Performs CRUD operations against Google Calendar.
Syncs events to PostgreSQL database for tracking.
"""

import argparse
import os
import sys
import psycopg2
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

# Scopes for Calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    """Client for interacting with Google Calendar API."""
    
    def __init__(self, db_host=None, db_port=None, db_name=None, db_user=None, db_password=None, sync_to_local=False):
        self.service = None
        self.sync_to_local = sync_to_local
        
        # PostgreSQL connection parameters
        self.db_host = db_host or os.environ.get("PT_DB_HOST", "localhost")
        self.db_port = db_port or int(os.environ.get("PT_DB_PORT", 5433))
        self.db_name = db_name or os.environ.get("PT_DB_NAME", "financial_analysis")
        self.db_user = db_user or os.environ.get("PT_DB_USER", "finance_user")
        self.db_password = db_password or os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
        
        self._authenticate()
        if sync_to_local:
            self._init_local_db()
    
    def get_connection(self):
        """Get a PostgreSQL database connection."""
        conn = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
        return conn
    
    def _init_local_db(self):
        """Initialize PostgreSQL database for calendar event syncing."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create table for calendar events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id VARCHAR(255) PRIMARY KEY,
                calendar_id VARCHAR(255),
                summary TEXT,
                description TEXT,
                start_time TEXT,
                end_time TEXT,
                created_time TEXT,
                updated_time TEXT,
                status TEXT,
                attendees TEXT,
                external_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None
        
        # Try to load existing credentials
        token_path = os.path.expanduser('~/.config/google/calendar_token.json')
        
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                print(f"Could not load existing credentials: {e}")
        
        # If there are no valid credentials, initiate authentication flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("Credentials refreshed successfully")
                except RefreshError:
                    print("Could not refresh credentials, need to re-authenticate")
                    creds = None
            else:
                creds = None
        
        if not creds:
            print("No valid credentials found. Please run authentication setup first.")
            print("You can authenticate by running a Python script with the proper OAuth flow.")
            print("For now, trying to use existing credentials from other sources...")
            
            # Try to use the credentials we know exist
            cred_sources = [
                os.path.expanduser('~/.config/google/oauth-credentials.json'),
                os.path.expanduser('~/.gemini/oauth_creds.json')
            ]
            
            for cred_path in cred_sources:
                if os.path.exists(cred_path):
                    print(f"Found credentials at {cred_path}, but may need proper formatting for Calendar API")
                    break
            else:
                print("No credential sources found. Please set up Google Calendar authentication.")
                return
        
        if creds:
            try:
                self.service = build('calendar', 'v3', credentials=creds)
            except Exception as e:
                print(f"Failed to build Calendar service: {e}")
        else:
            print("Unable to authenticate with Google Calendar API")
    
    def list_calendars(self):
        """List all available calendars."""
        if not self.service:
            print("Calendar service not available. Authentication failed.")
            return
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            if not calendars:
                print("No calendars found.")
                return
            
            print("\nAvailable Calendars:")
            print("-" * 50)
            for i, calendar in enumerate(calendars, 1):
                print(f"{i}. {calendar['summary']}")
                print(f"   ID: {calendar['id']}")
                print(f"   Primary: {calendar.get('primary', False)}")
                print()
        except Exception as e:
            print(f"Error listing calendars: {e}")
    
    def list_events(self, calendar_id='primary', max_results=10, time_min=None, time_max=None):
        """List events from a calendar."""
        if not self.service:
            print("Calendar service not available. Authentication failed.")
            return
        
        try:
            # Set default time range to next 7 days if not specified
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            if not time_max:
                next_week = datetime.utcnow() + timedelta(days=7)
                time_max = next_week.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                print(f"No events found in calendar '{calendar_id}' for the specified time range.")
                return
            
            print(f"\nEvents in calendar '{calendar_id}':")
            print("-" * 80)
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                print(f"{i}. {event.get('summary', 'No title')}")
                print(f"   Start: {start}")
                print(f"   End: {end}")
                print(f"   ID: {event['id']}")
                if 'description' in event:
                    desc_preview = event['description'][:100] + '...' if len(event['description']) > 100 else event['description']
                    print(f"   Description: {desc_preview}")
                if 'attendees' in event:
                    attendee_emails = [att.get('email', 'Unknown') for att in event['attendees']]
                    print(f"   Attendees: {', '.join(attendee_emails)}")
                print()
        except Exception as e:
            print(f"Error listing events: {e}")
    
    def create_event(self, calendar_id='primary', summary='', description='', start_time=None, end_time=None, attendees=None):
        """Create a new event."""
        if not self.service:
            print("Calendar service not available. Authentication failed.")
            return
        
        if not summary:
            print("Summary is required to create an event.")
            return
        
        if not start_time or not end_time:
            print("Both start and end times are required to create an event.")
            return
        
        try:
            event = {
                'summary': summary,
                'description': description or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'America/Edmonton',  # Use local timezone
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'America/Edmonton',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId=calendar_id, 
                body=event
            ).execute()
            
            print(f"Event created successfully!")
            print(f"Event ID: {created_event.get('id')}")
            print(f"Summary: {created_event.get('summary')}")
            print(f"Link: {created_event.get('htmlLink')}")
            
            # Optionally sync to PostgreSQL database
            if self.sync_to_local:
                self._sync_event_to_local(created_event, calendar_id, 'created')
                
        except Exception as e:
            print(f"Error creating event: {e}")
    
    def update_event(self, event_id, calendar_id='primary', summary=None, description=None, start_time=None, end_time=None):
        """Update an existing event."""
        if not self.service:
            print("Calendar service not available. Authentication failed.")
            return
        
        try:
            # First, get the existing event
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            
            # Update the fields that were provided
            if summary is not None:
                event['summary'] = summary
            if description is not None:
                event['description'] = description
            if start_time is not None:
                event['start'] = {
                    'dateTime': start_time,
                    'timeZone': 'America/Edmonton',
                }
            if end_time is not None:
                event['end'] = {
                    'dateTime': end_time,
                    'timeZone': 'America/Edmonton',
                }
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            print(f"Event updated successfully!")
            print(f"Event ID: {updated_event.get('id')}")
            print(f"Summary: {updated_event.get('summary')}")
            
            # Optionally sync to PostgreSQL database
            if self.sync_to_local:
                self._sync_event_to_local(updated_event, calendar_id, 'updated')
                
        except Exception as e:
            print(f"Error updating event: {e}")
    
    def delete_event(self, event_id, calendar_id='primary'):
        """Delete an event."""
        if not self.service:
            print("Calendar service not available. Authentication failed.")
            return
        
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"Event {event_id} deleted successfully from calendar {calendar_id}")
            
            # Optionally remove from PostgreSQL database
            if self.sync_to_local:
                self._remove_event_from_local(event_id)
                
        except Exception as e:
            print(f"Error deleting event: {e}")
    
    def _sync_event_to_local(self, event, calendar_id, operation):
        """Sync an event to the PostgreSQL database."""
        if not self.sync_to_local:
            return
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            event_id = event.get('id')
            summary = event.get('summary', '')
            description = event.get('description', '')
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            end_time = event['end'].get('dateTime', event['end'].get('date'))
            created_time = event.get('created', datetime.now().isoformat())
            updated_time = event.get('updated', datetime.now().isoformat())
            status = event.get('status', 'confirmed')
            attendees = ', '.join([att.get('email', '') for att in event.get('attendees', [])])
            external_link = event.get('htmlLink', '')
            
            # Insert or update the event
            cursor.execute("""
                INSERT INTO calendar_events 
                (id, calendar_id, summary, description, start_time, end_time, 
                 created_time, updated_time, status, attendees, external_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    summary = EXCLUDED.summary,
                    description = EXCLUDED.description,
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    updated_time = EXCLUDED.updated_time,
                    status = EXCLUDED.status,
                    attendees = EXCLUDED.attendees,
                    external_link = EXCLUDED.external_link,
                    updated_at = CURRENT_TIMESTAMP
            """, (event_id, calendar_id, summary, description, start_time, end_time,
                  created_time, updated_time, status, attendees, external_link))
            
            conn.commit()
            conn.close()
            
            print(f"Event {event_id} {operation} and synced to PostgreSQL database.")
        except Exception as e:
            print(f"Error syncing event to PostgreSQL database: {e}")
    
    def _remove_event_from_local(self, event_id):
        """Remove an event from the PostgreSQL database."""
        if not self.sync_to_local:
            return
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM calendar_events WHERE id = %s", (event_id,))
            conn.commit()
            conn.close()
            
            print(f"Event {event_id} removed from PostgreSQL database.")
        except Exception as e:
            print(f"Error removing event from PostgreSQL database: {e}")
    
    def sync_local_events(self, calendar_id='primary'):
        """Sync PostgreSQL database events with Google Calendar."""
        if not self.service:
            print("Calendar service not available. Authentication failed.")
            return
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM calendar_events WHERE calendar_id = %s", (calendar_id,))
            local_events = cursor.fetchall()
            
            conn.close()
            
            print(f"Found {len(local_events)} events in PostgreSQL database for calendar '{calendar_id}'.")
            
            for event in local_events:
                print(f"- {event[2]} (ID: {event[0]}, Start: {event[4]})")
                
        except Exception as e:
            print(f"Error syncing local events: {e}")


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL Google Calendar CLI (gc) - Performs CRUD operations against Google Calendar")
    
    # Add global option for local sync
    parser.add_argument("--sync-local", action="store_true", help="Sync events to PostgreSQL database")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List calendars command
    parser_list_calendars = subparsers.add_parser('list-calendars', help='List all available calendars')
    
    # List events command
    parser_list_events = subparsers.add_parser('list-events', help='List events from a calendar')
    parser_list_events.add_argument("--calendar", "-c", default='primary', help="Calendar ID (default: primary)")
    parser_list_events.add_argument("--max-results", "-m", type=int, default=10, help="Maximum number of events to return (default: 10)")
    parser_list_events.add_argument("--time-min", help="Lower bound for an event's start time")
    parser_list_events.add_argument("--time-max", help="Upper bound for an event's end time")

    # Create event command
    parser_create = subparsers.add_parser('create', help='Create a new event')
    parser_create.add_argument("--calendar", "-c", default='primary', help="Calendar ID (default: primary)")
    parser_create.add_argument("--summary", "-s", required=True, help="Event summary/title")
    parser_create.add_argument("--description", "-d", help="Event description")
    parser_create.add_argument("--start", required=True, help="Event start time (ISO format: YYYY-MM-DDTHH:MM:SS)")
    parser_create.add_argument("--end", required=True, help="Event end time (ISO format: YYYY-MM-DDTHH:MM:SS)")
    parser_create.add_argument("--attendees", nargs='+', help="Attendee email addresses")

    # Update event command
    parser_update = subparsers.add_parser('update', help='Update an existing event')
    parser_update.add_argument("event_id", help="ID of the event to update")
    parser_update.add_argument("--calendar", "-c", default='primary', help="Calendar ID (default: primary)")
    parser_update.add_argument("--summary", "-s", help="New event summary/title")
    parser_update.add_argument("--description", "-d", help="New event description")
    parser_update.add_argument("--start", help="New event start time (ISO format)")
    parser_update.add_argument("--end", help="New event end time (ISO format)")

    # Delete event command
    parser_delete = subparsers.add_parser('delete', help='Delete an event')
    parser_delete.add_argument("event_id", help="ID of the event to delete")
    parser_delete.add_argument("--calendar", "-c", default='primary', help="Calendar ID (default: primary)")

    # Sync local events command
    parser_sync = subparsers.add_parser('sync-local', help='Sync PostgreSQL database events with Google Calendar')
    parser_sync.add_argument("--calendar", "-c", default='primary', help="Calendar ID (default: primary)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize the calendar client with sync option
    client = GoogleCalendarClient(sync_to_local=args.sync_local)

    if args.command == 'list-calendars':
        client.list_calendars()
    elif args.command == 'list-events':
        client.list_events(
            calendar_id=args.calendar,
            max_results=args.max_results,
            time_min=args.time_min,
            time_max=args.time_max
        )
    elif args.command == 'create':
        client.create_event(
            calendar_id=args.calendar,
            summary=args.summary,
            description=args.description,
            start_time=args.start,
            end_time=args.end,
            attendees=args.attendees
        )
    elif args.command == 'update':
        client.update_event(
            event_id=args.event_id,
            calendar_id=args.calendar,
            summary=args.summary,
            description=args.description,
            start_time=args.start,
            end_time=args.end
        )
    elif args.command == 'delete':
        client.delete_event(
            event_id=args.event_id,
            calendar_id=args.calendar
        )
    elif args.command == 'sync-local':
        client.sync_local_events(calendar_id=args.calendar)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()