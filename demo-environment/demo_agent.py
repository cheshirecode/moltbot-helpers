#!/usr/bin/env python3
"""
Demo Agent for OpenClaw

This is a simplified agent that runs in the demo environment with synthetic data
and mock services to showcase OpenClaw capabilities without accessing real systems.
"""

import json
import yaml
import time
import argparse
from pathlib import Path


class DemoAgent:
    def __init__(self, config_path):
        """Initialize the demo agent with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.data_path = Path(self.config.get('data_path', './data/'))
        self.enabled_features = self.config.get('enabled_features', [])
        
        # Load synthetic data
        data_file = self.data_path / 'synthetic_data.json'
        with open(data_file, 'r') as f:
            self.synthetic_data = json.load(f)
        
        print(f"Demo Agent initialized with {len(self.enabled_features)} features")
        print(f"Environment: {self.config['environment_name']}")
        print("="*60)
    
    def display_capabilities(self):
        """Display the capabilities of the demo agent"""
        print("\n🔍 AVAILABLE FEATURES:")
        for feature in self.enabled_features:
            print(f"  • {feature.replace('_', ' ').title()}")
        
        print(f"\n🔒 SECURITY: {self.config['environment_name']} is completely isolated")
        print("   • No access to real systems")
        print("   • Synthetic data only")
        print("   • Mock services only")
    
    def handle_command(self, command):
        """Handle a command from the user"""
        command_lower = command.lower().strip()
        
        if command_lower in ['quit', 'exit', 'bye']:
            return False
        
        elif 'hello' in command_lower or 'hi' in command_lower or 'hey' in command_lower:
            print("👋 Hello! Welcome to the OpenClaw demo environment!")
            print("I'm running in a completely isolated environment with synthetic data.")
            print("Ask me about calendar events, contacts, portfolio, or IoT devices!")
        
        elif 'calendar' in command_lower or 'schedule' in command_lower or 'appointment' in command_lower:
            print("\n📅 CALENDAR EVENTS:")
            for event in self.synthetic_data['calendar_events']:
                print(f"  • {event['title']} on {event['date']} at {event['time']}")
                print(f"    Description: {event['description']}")
                print(f"    Participants: {', '.join(event['participants'])}")
                print(f"    Status: {event['status']}\n")
        
        elif 'contact' in command_lower or 'people' in command_lower or 'friend' in command_lower:
            print("\n👥 CONTACTS:")
            for contact in self.synthetic_data['contacts']:
                print(f"  • {contact['name']} ({contact['relationship']})")
                print(f"    Email: {contact['email']}")
                print(f"    Phone: {contact['phone']}")
                print(f"    Last Contact: {contact['last_contact']}")
                print(f"    Interactions: {contact['interaction_count']}\n")
        
        elif 'finance' in command_lower or 'portfolio' in command_lower or 'stock' in command_lower:
            print("\n💼 FINANCIAL PORTFOLIO:")
            print(f"  Total Portfolio Value: ${self.synthetic_data['financial_portfolio']['total_value']:,.2f}")
            print(f"  Cash Balance: ${self.synthetic_data['financial_portfolio']['cash_balance']:,.2f}")
            print(f"  Portfolio Growth: {self.synthetic_data['financial_portfolio']['portfolio_growth']}%")
            print("\n  Holdings:")
            for holding in self.synthetic_data['financial_portfolio']['holdings']:
                gain_loss = (holding['current_price'] - holding['avg_cost']) * holding['shares']
                gain_loss_pct = ((holding['current_price'] / holding['avg_cost']) - 1) * 100
                print(f"    • {holding['symbol']}: {holding['shares']} shares at ${holding['current_price']:.2f}")
                print(f"      Avg Cost: ${holding['avg_cost']:.2f}, Value: ${holding['value']:.2f}")
                print(f"      Gain/Loss: ${gain_loss:.2f} ({gain_loss_pct:+.2f}%)\n")
        
        elif 'iot' in command_lower or 'smart home' in command_lower or 'device' in command_lower:
            print("\n🏠 SMART HOME DEVICES:")
            for device in self.synthetic_data['iot_devices']:
                print(f"  • {device['name']} ({device['type']})")
                print(f"    Status: {device['status']}")
                if device['type'] == 'light':
                    print(f"    Brightness: {device['brightness']}%, Color: {device['color_temp']}")
                elif device['type'] == 'thermostat':
                    print(f"    Current: {device['temperature']}°C, Target: {device['target']}°C, Mode: {device['mode']}")
                elif device['type'] == 'camera':
                    print(f"    Recording: {device['recording']}, Motion: {device['motion_detected']}")
                print()
        
        elif 'features' in command_lower or 'capabilities' in command_lower or 'what can you do' in command_lower:
            self.display_capabilities()
        
        elif 'help' in command_lower:
            print("\n💡 DEMO COMMANDS:")
            print("  • 'calendar' - Show calendar events")
            print("  • 'contacts' - Show contact information") 
            print("  • 'finance' - Show portfolio information")
            print("  • 'iot' - Show smart home devices")
            print("  • 'features' - Show available features")
            print("  • 'quit' - Exit the demo")
        
        else:
            print(f"\n🤖 I received your command: '{command}'")
            print("This is a demo environment. Try asking about calendar, contacts, finance, or IoT!")
            print("Type 'help' for available commands.")
        
        return True
    
    def run_interactive(self):
        """Run the agent in interactive mode"""
        print(f"\n🚀 Starting {self.config['environment_name']}...")
        print("Type 'help' for available commands or 'quit' to exit.\n")
        
        self.display_capabilities()
        
        while True:
            try:
                command = input(f"\n{self.config['environment_name']}> ").strip()
                if not command:
                    continue
                
                should_continue = self.handle_command(command)
                if not should_continue:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for trying the OpenClaw demo.")
                break
            except EOFError:
                print("\n\n👋 Goodbye! Thanks for trying the OpenClaw demo.")
                break


def main():
    parser = argparse.ArgumentParser(description='OpenClaw Demo Agent')
    parser.add_argument('--config', '-c', default='./config/demo_config.yaml',
                       help='Path to demo configuration file')
    
    args = parser.parse_args()
    
    agent = DemoAgent(args.config)
    agent.run_interactive()


if __name__ == '__main__':
    main()