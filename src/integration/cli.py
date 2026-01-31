"""
CLI module for the unified interface integration.

Provides command-line access to the unified interface that integrates
fp, seek, and pt tools.
"""
import argparse
import sys
import json
from .unified_interface import UnifiedInterface


def main():
    parser = argparse.ArgumentParser(description='Unified Interface for OpenClaw Integration')
    parser.add_argument('--db-path', help='Override database path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Cross-reference command
    cross_ref_parser = subparsers.add_parser('cross-ref', help='Cross-reference query across all systems')
    cross_ref_parser.add_argument('query', help='Query to cross-reference')
    
    # Recommendations command
    rec_parser = subparsers.add_parser('recommendations', help='Get system recommendations')
    rec_parser.add_argument('--context', default='', help='Context for recommendations')
    
    # Project context command
    proj_parser = subparsers.add_parser('project-context', help='Get context for a specific project')
    proj_parser.add_argument('project_name', help='Name of the project to get context for')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get status of all integrated systems')
    
    # Context command
    context_parser = subparsers.add_parser('context', help='Determine best system for a query using contextual intelligence')
    context_parser.add_argument('query', help='Query to analyze for system selection')
    
    # Add knowledge graph commands
    kg_parser = subparsers.add_parser('kg', help='Knowledge graph operations')
    kg_subparsers = kg_parser.add_subparsers(dest='kg_command')
    
    # Sub-command for building the knowledge graph
    kg_build_parser = kg_subparsers.add_parser('build', help='Build knowledge graph from existing data')
    
    # Sub-command for adding relationships
    kg_add_parser = kg_subparsers.add_parser('add', help='Add a relationship to the knowledge graph')
    kg_add_parser.add_argument('source_entity', help='Source entity')
    kg_add_parser.add_argument('source_type', help='Type of source entity')
    kg_add_parser.add_argument('target_entity', help='Target entity')
    kg_add_parser.add_argument('target_type', help='Type of target entity')
    kg_add_parser.add_argument('relationship_type', help='Type of relationship')
    kg_add_parser.add_argument('--strength', type=float, default=1.0, help='Strength of relationship (0.0 to 1.0)')
    
    # Sub-command for querying related entities
    kg_query_parser = kg_subparsers.add_parser('query', help='Query entities related to a specific entity')
    kg_query_parser.add_argument('entity', help='Entity to find relationships for')
    kg_query_parser.add_argument('--type', dest='entity_type', help='Type of the entity')
    kg_query_parser.add_argument('--rel-type', dest='relationship_type', help='Type of relationship to filter by')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    interface = UnifiedInterface(db_path=args.db_path)
    
    if args.command == 'cross-ref':
        result = interface.cross_reference_intelligence(args.query)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'recommendations':
        result = interface.get_recommendations(context=args.context)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'project-context':
        result = interface.get_project_context(args.project_name)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'status':
        # Test connectivity to all systems
        status = {
            "timestamp": "2026-01-31T01:32:45",
            "systems": {
                "project_tracker": {"status": "reachable", "details": {}},
                "family_planner": {"status": "reachable", "details": {}},
                "semantic_search": {"status": "reachable", "details": {}}
            },
            "integration": {
                "unified_interface": {"status": "active", "version": "1.0.0"}
            }
        }
        
        # Test each system individually with more detail
        try:
            pt_test = interface.pt_query(['list'])
            status["systems"]["project_tracker"]["status"] = "reachable" if pt_test["success"] else "unreachable"
            if pt_test["success"]:
                # Extract basic stats from the output
                lines = pt_test["stdout"].split('\n')
                project_count = sum(1 for line in lines if line.startswith("ID:"))
                status["systems"]["project_tracker"]["details"] = {"projects_tracked": project_count}
        except Exception as e:
            status["systems"]["project_tracker"]["status"] = "error"
            status["systems"]["project_tracker"]["error"] = str(e)
        
        try:
            fp_test = interface.fp_query(['tasks'])
            status["systems"]["family_planner"]["status"] = "reachable" if fp_test["success"] else "unreachable"
            if fp_test["success"]:
                # Extract basic stats from the output
                lines = fp_test["stdout"].split('\n')
                task_count = sum(1 for line in lines if "|" in line and "action" not in line.lower())
                status["systems"]["family_planner"]["details"] = {"tasks_open": task_count}
        except Exception as e:
            status["systems"]["family_planner"]["status"] = "error"
            status["systems"]["family_planner"]["error"] = str(e)
            
        try:
            seek_test = interface.seek_query(['status'])
            status["systems"]["semantic_search"]["status"] = "reachable" if seek_test["success"] else "unreachable"
            if seek_test["success"]:
                status["systems"]["semantic_search"]["details"] = {"status_output_length": len(seek_test["stdout"])}
        except Exception as e:
            status["systems"]["semantic_search"]["status"] = "error"
            status["systems"]["semantic_search"]["error"] = str(e)
        
        print(json.dumps(status, indent=2))
        
    # Add contextual intelligence command
    elif args.command == 'context':
        if not args.query:
            print("Usage: integrate context <query>")
            return
        query = args.query
        result = interface.determine_best_system(query)
        print(json.dumps(result, indent=2))
    
    # Knowledge graph commands
    elif args.command == 'kg':
        if args.kg_command == 'build':
            result = interface.build_knowledge_graph()
            print(json.dumps(result, indent=2))
        elif args.kg_command == 'add':
            result = interface.add_relationship(
                source_entity=args.source_entity,
                source_type=args.source_type,
                target_entity=args.target_entity,
                target_type=args.target_type,
                relationship_type=args.relationship_type,
                strength=args.strength
            )
            print(json.dumps(result, indent=2))
        elif args.kg_command == 'query':
            result = interface.get_related_entities(
                entity=args.entity,
                entity_type=args.entity_type,
                relationship_type=args.relationship_type
            )
            print(json.dumps(result, indent=2))
        else:
            print("Usage: integrate kg [build|add|query]")
            sys.exit(1)


if __name__ == "__main__":
    main()