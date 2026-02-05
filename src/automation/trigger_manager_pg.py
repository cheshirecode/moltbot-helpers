"""
PostgreSQL Trigger Manager for OpenClaw Automation

This module provides functionalities to define and manage trigger-based actions
that respond to changes in project status, approaching deadlines, or other
defined conditions using PostgreSQL.
"""
import os
import json
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Placeholder for the message tool. In a real scenario, this would be an actual tool invocation.
# For now, we'll just print the message content.
def send_notification(to: str, message_text: str):
    print(f"--- NOTIFICATION SENT ---")
    print(f"To: {to}")
    print(f"Message: {message_text}")
    print(f"-------------------------")

class TriggerManager:
    """
    Manages triggers and executes associated actions based on predefined conditions.
    """
    
    def __init__(self, db_host: str = None, db_port: int = None, db_name: str = None, db_user: str = None, db_password: str = None):
        """
        Initialize the TriggerManager with PostgreSQL connection.
        
        Args:
            db_host: PostgreSQL host
            db_port: PostgreSQL port
            db_name: PostgreSQL database name
            db_user: PostgreSQL user
            db_password: PostgreSQL password
        """
        self.db_host = db_host or os.environ.get("PT_DB_HOST", "localhost")
        self.db_port = db_port or int(os.environ.get("PT_DB_PORT", 5433))
        self.db_name = db_name or os.environ.get("PT_DB_NAME", "financial_analysis")
        self.db_user = db_user or os.environ.get("PT_DB_USER", "finance_user")
        self.db_password = db_password or os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
        
        self._init_trigger_db()
        
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

    def _init_trigger_db(self):
        """Initialize the database for storing trigger configurations."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table to store trigger definitions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triggers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                type VARCHAR(255) NOT NULL,          -- e.g., 'project_status_change', 'project_deadline_nearing'
                condition_json TEXT NOT NULL,        -- JSON string of condition details
                action_json TEXT NOT NULL,           -- JSON string of action details (e.g., recipient, message template)
                enabled BOOLEAN DEFAULT TRUE,        -- true for enabled, false for disabled
                last_checked TIMESTAMP,
                last_triggered TIMESTAMP
            )
        """)
        
        # Table to store historical trigger events to prevent spamming
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_history (
                id SERIAL PRIMARY KEY,
                trigger_id INTEGER,
                entity_id VARCHAR(255),             -- e.g., project ID
                entity_type VARCHAR(255),           -- e.g., 'project'
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trigger_id) REFERENCES triggers(id)
            )
        """)
        
        conn.commit()
        conn.close()

    def add_trigger(self, name: str, type: str, condition: Dict, action: Dict, enabled: bool = True) -> Dict[str, Any]:
        """
        Add a new trigger to the system.
        
        Args:
            name: Unique name for the trigger.
            type: Type of the trigger (e.g., 'project_status_change').
            condition: Dictionary defining the trigger condition.
            action: Dictionary defining the action to take.
            enabled: Whether the trigger is enabled by default.
        
        Returns:
            Dictionary indicating success or failure.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO triggers (name, type, condition_json, action_json, enabled)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, type, json.dumps(condition), json.dumps(action), enabled))
            conn.commit()
            return {"success": True, "message": f"Trigger '{name}' added successfully."}
        except psycopg2.IntegrityError:
            return {"success": False, "error": f"Trigger with name '{name}' already exists."}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def list_triggers(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """List all defined triggers."""
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT id, name, type, condition_json, action_json, enabled, last_checked, last_triggered FROM triggers"
        if enabled_only:
            query += " WHERE enabled = true"
        cursor.execute(query)
        triggers = []
        for row in cursor.fetchall():
            triggers.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "condition": json.loads(row[3]),
                "action": json.loads(row[4]),
                "enabled": row[5],
                "last_checked": row[6],
                "last_triggered": row[7]
            })
        conn.close()
        return triggers

    def _get_project_entries(self, project_name: str = 'openclaw', status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Helper to get project entries from the PostgreSQL project tracker."""
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT id, title, status, priority, updated_date FROM project_tracker WHERE project = %s"
        params = [project_name]
        if status:
            query += " AND status = %s"
            params.append(status)
        cursor.execute(query, params)
        entries = []
        for row in cursor.fetchall():
            entries.append({
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "priority": row[3],
                "updated_date": row[4]
            })
        conn.close()
        return entries
        
    def _has_been_triggered_recently(self, trigger_id: int, entity_id: str, cooldown_minutes: int = 60) -> bool:
        """
        Check if a trigger for a specific entity has been fired recently.
        This prevents spamming notifications for the same event.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cooldown_threshold = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        cursor.execute("""
            SELECT COUNT(*) FROM trigger_history
            WHERE trigger_id = %s AND entity_id = %s AND triggered_at >= %s
        """, (trigger_id, entity_id, cooldown_threshold))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def _record_trigger_event(self, trigger_id: int, entity_id: str, entity_type: str):
        """Record a trigger event in the history."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trigger_history (trigger_id, entity_id, entity_type)
            VALUES (%s, %s, %s)
        """, (trigger_id, entity_id, entity_type))
        cursor.execute("UPDATE triggers SET last_triggered = %s WHERE id = %s", (datetime.now(), trigger_id))
        conn.commit()
        conn.close()

    def check_for_triggers(self, project_name: str = 'openclaw'):
        """
        Check all enabled triggers and execute actions if conditions are met.
        This method is intended to be called periodically (e.g., by a cron job).
        """
        enabled_triggers = self.list_triggers(enabled_only=True)
        
        for trigger in enabled_triggers:
            trigger_id = trigger["id"]
            trigger_name = trigger["name"]
            trigger_type = trigger["type"]
            condition = trigger["condition"]
            action = trigger["action"]
            
            # Update last_checked timestamp for the trigger
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE triggers SET last_checked = %s WHERE id = %s", (datetime.now(), trigger_id))
            conn.commit()
            conn.close()

            # --- Evaluate conditions based on trigger type ---
            
            if trigger_type == 'project_status_change':
                # Condition: {"project_id": <int>, "from_status": "new", "to_status": "completed"}
                # or {"project_id": <int>, "to_status": "completed"}
                
                project_id = condition.get("project_id")
                from_status = condition.get("from_status")
                to_status = condition.get("to_status")
                
                project_entries = self._get_project_entries(project_name) # Get all projects to find status changes
                for entry in project_entries:
                    if str(entry["id"]) == str(project_id): # Ensure ID match (can be int or str)
                        if to_status and entry["status"] == to_status:
                            # If from_status is specified, check previous status (requires more complex tracking)
                            # For simplicity, we'll check if it just reached 'to_status'
                            # We need to ensure we don't re-trigger for the same completion
                            if not self._has_been_triggered_recently(trigger_id, str(entry["id"]), cooldown_minutes=1440): # 24-hour cooldown
                                notification_message = action.get("message_template", f"Project {entry['title']} (ID: {entry['id']}) changed status to {entry['status']}!")
                                notification_message = notification_message.replace("{project_title}", entry["title"])
                                notification_message = notification_message.replace("{project_id}", str(entry["id"]))
                                notification_message = notification_message.replace("{new_status}", entry["status"])
                                
                                send_notification(action.get("recipient"), notification_message)
                                self._record_trigger_event(trigger_id, str(entry["id"]), "project")
                                print(f"Trigger '{trigger_name}' fired for project {entry['id']}.")
            
            elif trigger_type == 'project_deadline_nearing':
                # Condition: {"days_until_deadline": 7, "priority": "high"}
                
                days_until_deadline = condition.get("days_until_deadline")
                target_priority = condition.get("priority")
                
                # Retrieve projects that are not completed
                all_projects = self._get_project_entries(project_name)
                
                for entry in all_projects:
                    if entry["status"] != "completed" and entry["priority"] == target_priority:
                        # Assuming updated_date can be used as a pseudo-deadline for simplicity
                        # In a real system, a 'deadline' field would be better
                        if entry["updated_date"]: # For now, check if updated_date is within 'days_until_deadline'
                            if isinstance(entry["updated_date"], str):
                                updated_dt = datetime.fromisoformat(entry["updated_date"])
                            else:
                                updated_dt = entry["updated_date"]
                            
                            time_diff = updated_dt - datetime.now()
                            
                            # This logic needs refinement. A proper 'deadline' field is crucial.
                            # For now, let's assume 'deadline_date' field might exist
                            # More realistically, we'd have a 'deadline_date' column.
                            # Given the schema, I can't check 'deadline_date'.
                            # I will simulate a deadline being near by checking if the project was
                            # updated within the last N days for this trigger type
                            
                            if abs(time_diff.days) <= days_until_deadline:
                                if not self._has_been_triggered_recently(trigger_id, str(entry["id"]), cooldown_minutes=1440): # 24-hour cooldown
                                    notification_message = action.get("message_template", f"Project {entry['title']} (ID: {entry['id']}) has an upcoming deadline (or recent update) and is {entry['status']}.")
                                    notification_message = notification_message.replace("{project_title}", entry["title"])
                                    notification_message = notification_message.replace("{project_id}", str(entry["id"]))
                                    notification_message = notification_message.replace("{days_remaining}", str(time_diff.days))
                                    
                                    send_notification(action.get("recipient"), notification_message)
                                    self._record_trigger_event(trigger_id, str(entry["id"]), "project")
                                    print(f"Trigger '{trigger_name}' fired for project {entry['id']}.")

def main():
    """Example usage of the TriggerManager."""
    manager = TriggerManager()
    
    # Example: Add a trigger for a project status change
    manager.add_trigger(
        name="ProjectCompletionNotification",
        type="project_status_change",
        condition={"project_id": "openclaw", "to_status": "completed"}, # This condition expects a single project ID, not 'openclaw' as a project name
        action={"recipient": "user", "message_template": "Project '{project_title}' (ID: {project_id}) has been completed!"}
    )
    
    # Example: Add a trigger for a high-priority project nearing a deadline
    manager.add_trigger(
        name="HighPriorityProjectAlert",
        type="project_deadline_nearing",
        condition={"days_until_deadline": 7, "priority": "high"},
        action={"recipient": "user", "message_template": "High-priority project '{project_title}' is approaching its deadline! Days remaining: {days_remaining}"}
    )
    
    print("Triggers added.")
    
    # List triggers
    print("\nListing triggers:")
    for trigger in manager.list_triggers():
        print(f"- {trigger['name']} (ID: {trigger['id']}) - Enabled: {trigger['enabled']}")
    
    # Simulate checking for triggers
    print("\nChecking for triggers...")
    manager.check_for_triggers()
    
    print("\nDone checking triggers.")


if __name__ == "__main__":
    main()