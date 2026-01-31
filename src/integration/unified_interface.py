"""
Unified Interface Module for OpenClaw Integration

This module provides a unified command interface that integrates:
- fp (Family Planner) - for family financial data, tasks, dates
- seek (Semantic Search) - for local semantic search with vector embeddings
- pt (Project Tracker) - for project tasks, roadmap items, bugs
"""
import json
import sqlite3
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class UnifiedInterface:
    """
    A unified interface that integrates fp, seek, and pt tools to allow
    intelligent cross-referencing between family planning data, semantic search,
    and project tracking.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize the unified interface with optional database path override."""
        self.db_path = db_path or os.path.expanduser("~/projects/_openclaw/project-tracker.db")
        
    def fp_query(self, args: List[str]) -> Dict[str, Any]:
        """Execute an fp (family planner) command by importing the module directly."""
        try:
            from fp.cli import main as fp_main
            # This is a simplified approach - in practice, we'd need to properly 
            # call the fp module functions. For now, we'll return a placeholder.
            return {
                "success": True,
                "stdout": f"fp command would be executed with args: {args}",
                "stderr": "",
                "return_code": 0
            }
        except ImportError:
            return {
                "success": False,
                "stdout": "",
                "stderr": "fp module not available",
                "return_code": 1
            }
    
    def seek_query(self, args: List[str]) -> Dict[str, Any]:
        """Execute a seek (semantic search) command by importing the module directly."""
        try:
            from seek.cli import main as seek_main
            # This is a simplified approach - in practice, we'd need to properly 
            # call the seek module functions. For now, we'll return a placeholder.
            return {
                "success": True,
                "stdout": f"seek command would be executed with args: {args}",
                "stderr": "",
                "return_code": 0
            }
        except ImportError:
            return {
                "success": False,
                "stdout": "",
                "stderr": "seek module not available",
                "return_code": 1
            }
    
    def pt_query(self, args: List[str]) -> Dict[str, Any]:
        """Execute a pt (project tracker) command by importing the module directly."""
        try:
            from pt.cli import main as pt_main
            # This is a simplified approach - in practice, we'd need to properly 
            # call the pt module functions. For now, we'll return a placeholder.
            # We'll implement direct database access for project-related queries
            if args[0] == 'list':
                return self._get_pt_list()
            elif args[0] == 'search':
                search_term = args[1] if len(args) > 1 else ''
                return self._search_pt_entries(search_term)
            else:
                return {
                    "success": True,
                    "stdout": f"pt command would be executed with args: {args}",
                    "stderr": "",
                    "return_code": 0
                }
        except ImportError:
            return {
                "success": False,
                "stdout": "",
                "stderr": "pt module not available",
                "return_code": 1
            }
    
    def _get_pt_list(self) -> Dict[str, Any]:
        """Direct implementation of pt list functionality."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, category, title, description, priority, status, tags, created_date, updated_date
                FROM entries 
                WHERE project = 'openclaw' AND status != 'completed'
                ORDER BY priority DESC
            """)
            
            entries = cursor.fetchall()
            
            result_text = f"Entries for project 'openclaw':\n"
            for entry in entries:
                result_text += "-" * 80 + "\n"
                result_text += f"ID: {entry[0]}\n"
                result_text += f"Category: {entry[1]}\n"
                result_text += f"Priority: {entry[4]}\n"
                result_text += f"Status: {entry[5]}\n"
                result_text += f"Title: {entry[2]}\n"
                desc = entry[3][:75] + "..." if len(entry[3]) > 75 else entry[3]
                result_text += f"Description: {desc}\n"
                result_text += f"Tags: {entry[6]}\n"
                result_text += f"Created: {entry[7]}, Updated: {entry[8]}\n"
            
            conn.close()
            return {
                "success": True,
                "stdout": result_text,
                "stderr": "",
                "return_code": 0
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": 1
            }
    
    def _search_pt_entries(self, search_term: str) -> Dict[str, Any]:
        """Direct implementation of pt search functionality."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search in title and description fields
            cursor.execute("""
                SELECT id, category, title, description, priority, status, tags, created_date, updated_date
                FROM entries 
                WHERE project = 'openclaw' AND status != 'completed'
                AND (title LIKE ? OR description LIKE ?)
                ORDER BY priority DESC
            """, (f'%{search_term}%', f'%{search_term}%'))
            
            entries = cursor.fetchall()
            
            result_text = f"Search results for '{search_term}' in project 'openclaw':\n"
            for entry in entries:
                result_text += "-" * 80 + "\n"
                result_text += f"ID: {entry[0]}\n"
                result_text += f"Category: {entry[1]}\n"
                result_text += f"Priority: {entry[4]}\n"
                result_text += f"Status: {entry[5]}\n"
                result_text += f"Title: {entry[2]}\n"
                desc = entry[3][:75] + "..." if len(entry[3]) > 75 else entry[3]
                result_text += f"Description: {desc}\n"
                result_text += f"Tags: {entry[6]}\n"
                result_text += f"Created: {entry[7]}, Updated: {entry[8]}\n"
            
            conn.close()
            return {
                "success": True,
                "stdout": result_text,
                "stderr": "",
                "return_code": 0
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": 1
            }
    
    def get_project_context(self, project_name: str) -> Dict[str, Any]:
        """Get context for a specific project by querying the database directly."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, category, title, description, priority, status, tags, created_date, updated_date
                FROM entries 
                WHERE project = ? AND status != 'completed'
                ORDER BY priority DESC
            """, (project_name,))
            
            entries = cursor.fetchall()
            
            result = []
            for entry in entries:
                result.append({
                    "id": entry[0],
                    "category": entry[1],
                    "title": entry[2],
                    "description": entry[3][:100] + "..." if len(entry[3]) > 100 else entry[3],  # Truncate long descriptions
                    "priority": entry[4],
                    "status": entry[5],
                    "tags": entry[6],
                    "created_date": entry[7],
                    "updated_date": entry[8]
                })
            
            conn.close()
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cross_reference_intelligence(self, query: str) -> Dict[str, Any]:
        """
        Perform intelligent cross-referencing between fp, seek, and pt data.
        
        This method attempts to find relevant information across all three systems
        based on the query provided.
        """
        results = {}
        
        # Query project tracker for relevant projects/tasks
        pt_result = self.pt_query(["search", query])
        results["project_tracker"] = pt_result
        
        # Attempt to query family planner (if relevant)
        # We'll try to detect if the query relates to family/financial matters
        if any(word in query.lower() for word in ["family", "finance", "budget", "balance", "task", "date", "event"]):
            fp_result = self.fp_query(["search", query])
            results["family_planner"] = fp_result
        else:
            results["family_planner"] = {"success": True, "stdout": "Query not relevant to family planning", "skipped": True}
        
        # Attempt semantic search for broader context
        seek_result = self.seek_query(["search", query])
        results["semantic_search"] = seek_result
        
        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
    
    def get_recommendations(self, context: str = "") -> Dict[str, Any]:
        """
        Generate intelligent recommendations based on current state of all systems.
        """
        recommendations = []
        
        # Get current open projects
        pt_result = self.pt_query(["list"])
        if pt_result["success"]:
            # Parse PT output to find actionable items
            output_lines = pt_result["stdout"].split('\n')
            current_projects = []
            current_project = {}
            
            for line in output_lines:
                if line.startswith("ID:"):
                    if current_project:
                        current_projects.append(current_project)
                    current_project = {"info": line}
                elif "Priority:" in line:
                    current_project["priority"] = line.split("Priority:")[-1].strip()
                elif "Status:" in line:
                    current_project["status"] = line.split("Status:")[-1].strip()
                elif "Title:" in line:
                    current_project["title"] = line.split("Title:")[-1].strip()
            
            if current_project:
                current_projects.append(current_project)
                
            # Filter for high priority items that might need attention
            high_priority_items = [proj for proj in current_projects 
                                 if proj.get("priority") == "high" and proj.get("status") == "new"]
            
            for item in high_priority_items:
                recommendations.append({
                    "type": "project_attention",
                    "priority": "high",
                    "title": item.get("title", "Unknown"),
                    "description": f"High priority task requires immediate attention: {item.get('title', '')}"
                })
        
        # Get family planner tasks if available
        fp_result = self.fp_query(["tasks"])
        if fp_result["success"]:
            # Simple parsing of tasks (would need more sophisticated parsing in practice)
            if "No open tasks" not in fp_result["stdout"]:
                recommendations.append({
                    "type": "family_planning_attention",
                    "priority": "medium",
                    "description": "Family planner has open tasks that may need attention"
                })
        
        # Get seek status
        seek_result = self.seek_query(["status"])
        if seek_result["success"]:
            if "indexed" in seek_result["stdout"].lower():
                recommendations.append({
                    "type": "search_ready",
                    "priority": "info",
                    "description": "Semantic search system is operational and indexed"
                })
        
        return {
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }


def main():
    """Example usage of the unified interface."""
    interface = UnifiedInterface()
    
    # Example: Cross-reference a query across all systems
    query = "current projects"
    result = interface.cross_reference_intelligence(query)
    
    print(f"Cross-reference results for query: '{query}'")
    print(json.dumps(result, indent=2))
    
    # Example: Get recommendations
    recommendations = interface.get_recommendations("General system check")
    print("\nRecommendations:")
    print(json.dumps(recommendations, indent=2))


if __name__ == "__main__":
    main()