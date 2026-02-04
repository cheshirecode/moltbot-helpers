#!/usr/bin/env python3
"""
Standalone lookup utility for accessing guidelines and documentation.
Can be executed directly without installing the full package.
"""

import sys
import os
import argparse


def get_guidelines_path():
    """Get the path to the guidelines directory relative to the current workspace."""
    # Look for guidelines in common locations
    possible_paths = [
        "./guidelines",
        "../guidelines", 
        "../../guidelines",
        os.path.expanduser("~/projects/openclaw/guidelines"),
        os.path.expanduser("~/.openclaw/workspace/guidelines")
    ]
    
    for path in possible_paths:
        if os.path.isdir(path):
            return path
    
    return None


def show_group_chat_guidelines():
    """Display group chat behavior guidelines."""
    guidelines_path = get_guidelines_path()
    if guidelines_path:
        file_path = os.path.join(guidelines_path, "group-chat-behavior.md")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                print(f.read().strip())
            return
    
    # Fallback content if file not found
    print("""## Group Chat Behavior Guidelines

### When to Speak
- Directly mentioned or asked a question
- Can add genuine value (info, insight, help)
- Something witty/funny fits naturally
- Correcting important misinformation
- Summarizing when asked

### When to Stay Silent (HEARTBEAT_OK)
- Casual banter between humans
- Someone already answered the question
- Response would just be "yeah" or "nice"
- Conversation is flowing fine without intervention
- Adding a message would interrupt the flow

### Reaction Guidelines
Use emoji reactions naturally on platforms that support them (Discord, Slack):
- React when you appreciate something (👍, ❤️, 🙌)
- React when something made you laugh (😂, 💀)
- React when you find something interesting (🤔, 💡)
- React when acknowledging without needing to reply
- Use reactions instead of brief text responses to avoid clutter

Note: One reaction per message max. Humans don't respond to every message in group chats, so neither should you. Quality > quantity.""")


def show_heartbeat_guidelines():
    """Display heartbeat behavior guidelines."""
    guidelines_path = get_guidelines_path()
    if guidelines_path:
        file_path = os.path.join(guidelines_path, "heartbeat-behavior.md")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                print(f.read().strip())
            return
    
    # Fallback content if file not found
    print("""## Heartbeat Behavior Guidelines

### Purpose
Use heartbeats productively, not just to reply HEARTBEAT_OK. Batch multiple checks together to reduce API calls.

### What to Check (Rotate 2-4 times per day)
- Emails: Any urgent unread messages?
- Calendar: Upcoming events in next 24-48 hours?
- Mentions: Social media notifications?
- Weather: Relevant if your human might go out?

### When to Reach Out
- Important email arrived
- Calendar event coming up (<2h)
- Something interesting found
- Been >8h since last communication

### When to Stay Quiet (HEARTBEAT_OK)
- Late night (23:00-08:00) unless urgent
- Human is clearly busy
- Nothing new since last check
- Checked <30 minutes ago

### Proactive Work (Without Asking)
- Read and organize memory files
- Check on projects
- Update documentation
- Review and update MEMORY.md (memory maintenance)

### Heartbeat vs Cron
- Use heartbeat for batching, conversational context, flexible timing
- Use cron for exact timing, task isolation, standalone reminders""")


def show_memory_guidelines():
    """Display memory maintenance guidelines."""
    guidelines_path = get_guidelines_path()
    if guidelines_path:
        file_path = os.path.join(guidelines_path, "memory-maintenance.md")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                print(f.read().strip())
            return
    
    # Fallback content if file not found
    print("""## Memory Maintenance Guidelines

### During Heartbeats (Every Few Days)
1. Read recent `memory/YYYY-MM-DD.md` files
2. Identify significant events, lessons, or insights worth keeping long-term
3. Update `MEMORY.md` with distilled learnings
4. Remove outdated info from MEMORY.md that's no longer relevant

### Memory Files
- Daily notes: `memory/YYYY-MM-DD.md` - raw logs of what happened
- Long-term: `MEMORY.md` - curated memories for main sessions only

### Best Practices
- Capture what matters: decisions, context, things to remember
- Write important information to files - "mental notes" don't survive restarts
- Text > Brain - always externalize important information
- Only load MEMORY.md in main sessions (security reasons)""")


def show_tools_reference():
    """Display CLI tools reference."""
    print("""## CLI Tools Reference

### seek - Semantic search engine
  Commands: index, search, status, reindex, forget
  Database: ~/projects/_openclaw/seek.db

### fp - Family Planner CLI
  Commands: balances, net-worth, tasks, dates, people, docs, facts, finances, search
  Database: ~/projects/_openclaw/family-planning.db

### pt - Project Tracker CLI
  Commands: list, add, update, get, search
  Database: ~/projects/_openclaw/project-tracker.db""")


def show_all_guidelines():
    """Show all available guidelines."""
    print("## Available guidelines:")
    print("- group-chat: Group chat behavior rules")
    print("- heartbeat: Heartbeat behavior rules")
    print("- memory: Memory maintenance rules")
    print("- tools: CLI tools reference")
    print("")
    print("Usage: lookup [topic]")


def main():
    parser = argparse.ArgumentParser(description='Lookup guidelines and documentation')
    parser.add_argument('topic', nargs='?', help='Topic to lookup (group-chat, heartbeat, memory, tools, all)')
    args = parser.parse_args()

    if not args.topic:
        show_all_guidelines()
        return

    topic = args.topic.lower()
    
    if topic in ['group-chat', 'group_chat', 'chat']:
        show_group_chat_guidelines()
    elif topic in ['heartbeat', 'heartbeats']:
        show_heartbeat_guidelines()
    elif topic in ['memory', 'maintenance']:
        show_memory_guidelines()
    elif topic == 'tools':
        show_tools_reference()
    elif topic == 'all':
        show_all_guidelines()
    else:
        print(f"## Unknown topic: {args.topic}")
        print("Available topics: group-chat, heartbeat, memory, tools, all")
        print("Usage: lookup [topic]")


if __name__ == "__main__":
    main()