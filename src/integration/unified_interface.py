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
        if any(word in query.lower() for word in ["family", "finance", "budget", "balance", "task", "date", "event", "people", "person", "birth", "anniversary", "appointment", "reminder"]):
            fp_result = self.fp_query(["search", query])
            results["family_planner"] = fp_result
        else:
            # Still attempt to find connections by searching for tasks or dates that might relate to projects
            fp_result = self._enhanced_fp_query(query)
            results["family_planner"] = fp_result
        
        # Attempt semantic search for broader context
        seek_result = self.seek_query(["search", query])
        results["semantic_search"] = seek_result
        
        # Perform enhanced cross-referencing analysis
        enhanced_analysis = self._perform_enhanced_cross_reference(pt_result, fp_result, query)
        results["cross_reference_analysis"] = enhanced_analysis
        
        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
    
    def _enhanced_fp_query(self, query: str) -> Dict[str, Any]:
        """Enhanced family planner query that attempts to find connections even when initial detection doesn't match."""
        try:
            from fp.cli import main as fp_main
            # Look for potential matches by checking if the query relates to known projects or tasks
            db_path = os.path.expanduser("~/projects/_openclaw/family-planning.db")
            if not os.path.exists(db_path):
                return {"success": False, "stdout": "", "stderr": "Family planning database not found", "return_code": 1}
            
            # Attempt to find connections between projects and family data
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if query might match any family planning categories or topics
            possible_matches = []
            query_lower = query.lower()
            
            # Search in various family planning tables for potential matches
            try:
                # Search in tasks
                cursor.execute("SELECT id, action, category, due_date FROM tasks WHERE status != 'DONE' AND (action LIKE ? OR category LIKE ?)", (f'%{query}%', f'%{query}%'))
                task_results = cursor.fetchall()
                if task_results:
                    possible_matches.append(f"Family tasks related to '{query}': {len(task_results)} found")
                
                # Search in key dates
                cursor.execute("SELECT label, date, category FROM key_dates WHERE label LIKE ? OR category LIKE ?", (f'%{query}%', f'%{query}%'))
                date_results = cursor.fetchall()
                if date_results:
                    possible_matches.append(f"Family dates related to '{query}': {len(date_results)} found")
                    
                # Search in facts
                cursor.execute("SELECT topic, key, value FROM facts WHERE topic LIKE ? OR key LIKE ? OR value LIKE ?", (f'%{query}%', f'%{query}%', f'%{query}%'))
                fact_results = cursor.fetchall()
                if fact_results:
                    possible_matches.append(f"Family facts related to '{query}': {len(fact_results)} found")
                
                conn.close()
                
                if possible_matches:
                    return {
                        "success": True,
                        "stdout": "\n".join(possible_matches),
                        "stderr": "",
                        "return_code": 0
                    }
                else:
                    return {
                        "success": True,
                        "stdout": "Query not directly relevant to family planning data",
                        "stderr": "",
                        "return_code": 0
                    }
            except Exception as e:
                conn.close()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": 1
                }
                
        except ImportError:
            return {
                "success": False,
                "stdout": "",
                "stderr": "fp module not available",
                "return_code": 1
            }
    
    def _perform_enhanced_cross_reference(self, pt_result: Dict[str, Any], fp_result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Perform enhanced analysis to find connections between project tracker and family planner data."""
        analysis = {
            "connections_found": [],
            "recommendations": [],
            "conflicts_identified": [],
            "opportunities": []
        }
        
        # Analyze project tracker results
        if pt_result.get("success") and pt_result.get("stdout"):
            pt_text = pt_result["stdout"]
            # Look for potential conflicts or overlaps with family data
            
            # Check for dates that might conflict with family events
            import re
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{2}-\d{2}-\d{4}'   # MM-DD-YYYY
            ]
            
            for pattern in date_patterns:
                dates = re.findall(pattern, pt_text)
                if dates:
                    analysis["opportunities"].append(f"Potential project deadlines identified: {', '.join(dates[:5])} - check against family calendar")
        
        # Analyze family planner results
        if fp_result.get("success") and fp_result.get("stdout"):
            fp_text = fp_result["stdout"]
            
            # Look for high-priority family tasks that might impact project work
            if "high" in fp_text.lower() or "urgent" in fp_text.lower():
                analysis["recommendations"].append("High-priority family tasks detected that may require scheduling adjustments for project work")
            
            # Check for upcoming family events that might impact project timeline
            if "event" in fp_text.lower() or "appointment" in fp_text.lower() or "birthday" in fp_text.lower() or "anniversary" in fp_text.lower():
                analysis["conflicts_identified"].append("Upcoming family events identified - consider rescheduling intensive project work around these dates")
        
        # Look for general connections between the datasets
        if pt_result.get("success") and fp_result.get("success"):
            pt_content = pt_result.get("stdout", "").lower()
            fp_content = fp_result.get("stdout", "").lower()
            
            # Check if the same topics appear in both systems
            if any(topic in pt_content for topic in ["family", "personal", "home"]) and \
               any(topic in fp_content for topic in ["project", "work", "development", "task"]):
                analysis["connections_found"].append("Cross-domain connection identified: personal/family topics in project work and work topics in family planning")
        
        return analysis
    
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