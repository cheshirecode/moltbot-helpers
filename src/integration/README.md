# Unified Interface for OpenClaw Integration

The unified interface provides seamless integration between three core tools:
- `fp` (Family Planner) - for family financial data, tasks, dates
- `seek` (Semantic Search) - for local semantic search with vector embeddings
- `pt` (Project Tracker) - for project tasks, roadmap items, bugs

## Overview

This integration enables intelligent cross-referencing between family planning data, semantic search, and project tracking, allowing the OpenClaw assistant to make more informed recommendations and provide a cohesive experience across all tools.

## Components

### UnifiedInterface Class

The main class that provides methods for interacting with all three systems:

- `cross_reference_intelligence(query)` - Performs intelligent cross-referencing between all three systems
- `get_recommendations(context)` - Generates intelligent recommendations based on current state of all systems
- `get_project_context(project_name)` - Retrieves context for a specific project
- Direct access to `fp_query()`, `seek_query()`, and `pt_query()` methods

### CLI Interface

Provides command-line access to the unified interface:

- `integrate cross-ref <query>` - Cross-reference a query across all systems
- `integrate recommendations` - Get system recommendations
- `integrate project-context <project_name>` - Get context for a specific project
- `integrate status` - Get status of all integrated systems

## Usage Examples

### Cross-Referencing

Cross-reference information across all three systems:

```bash
integrate cross-ref "current projects"
```

### Getting Recommendations

Get intelligent recommendations based on current system states:

```bash
integrate recommendations
```

### Project Context

Get detailed context for a specific project:

```bash
integrate project-context openclaw
```

### System Status

Check the status of all integrated systems:

```bash
integrate status
```

## Architecture

The unified interface sits between the three core tools and provides:

1. **Centralized Access**: Single interface to query all three systems
2. **Cross-System Intelligence**: Ability to find correlations between different data sources
3. **Contextual Awareness**: Understanding of when to use each tool based on query context
4. **Recommendation Engine**: Proactive suggestions based on system states

## Implementation Details

- Direct database access for efficient project tracking operations
- Module-level imports for integration with other tools
- Flexible architecture that can accommodate additional tools in the future
- Error handling for graceful degradation when individual systems are unavailable

## Future Extensions

- Integration with additional tools beyond fp, seek, and pt
- Machine learning capabilities for improved recommendation accuracy
- API endpoints for external applications
- Advanced analytics and reporting features