# Mock Google API Service for Demo

import json
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request


class MockGoogleAPI:
    """Mock Google API service for demo environment"""
    
    def __init__(self, data_file="./data/synthetic_data.json"):
        with open(data_file, 'r') as f:
            self.data = json.load(f)
    
    def get_calendar_events(self, time_min=None, time_max=None):
        """Mock calendar events endpoint"""
        # Simulate API delay
        time.sleep(0.1)
        
        events = self.data['calendar_events']
        
        # Filter by time if provided
        if time_min:
            min_time = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
            events = [e for e in events if datetime.fromisoformat(f"{e['date']}T{e['time']}:00+00:00") >= min_time]
        
        if time_max:
            max_time = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
            events = [e for e in events if datetime.fromisoformat(f"{e['date']}T{e['time']}:00+00:00") <= max_time]
            
        return {"events": events}
    
    def search_contacts(self, query=""):
        """Mock contacts search endpoint"""
        time.sleep(0.05)
        
        contacts = self.data['contacts']
        
        if query:
            contacts = [c for c in contacts if query.lower() in c['name'].lower()]
            
        return {"contacts": contacts}
    
    def get_user_info(self):
        """Mock user info endpoint"""
        time.sleep(0.05)
        
        return {
            "user": {
                "name": "Demo User",
                "email": "demo@example.com",
                "photo_url": "https://via.placeholder.com/150"
            }
        }


def create_mock_google_app():
    app = Flask(__name__)
    mock_api = MockGoogleAPI()
    
    @app.route('/calendar/events', methods=['GET'])
    def calendar_events():
        time_min = request.args.get('time_min')
        time_max = request.args.get('time_max')
        events = mock_api.get_calendar_events(time_min, time_max)
        return jsonify(events)
    
    @app.route('/contacts/search', methods=['GET'])
    def search_contacts():
        query = request.args.get('q', '')
        contacts = mock_api.search_contacts(query)
        return jsonify(contacts)
    
    @app.route('/user/info', methods=['GET'])
    def user_info():
        user_info = mock_api.get_user_info()
        return jsonify(user_info)
    
    return app


if __name__ == '__main__':
    app = create_mock_google_app()
    app.run(host='0.0.0.0', port=5003, debug=False)