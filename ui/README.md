# OpenClaw Task Management Dashboard

A web-based dashboard for visualizing and managing tasks stored in the PostgreSQL database.

## Features

- **Project Overview**: Visualize tasks grouped by project
- **Status Tracking**: See task distribution by status (completed, in-progress, todo)
- **Priority Visualization**: View tasks by priority levels
- **Category Breakdown**: Analyze tasks by category
- **Real-time Data**: Connects directly to PostgreSQL database

## Architecture

- **Frontend**: HTML/CSS/JavaScript with Chart.js for visualizations
- **Backend**: Flask API connecting to PostgreSQL
- **Database**: PostgreSQL with project_tracker table

## Setup

1. Ensure PostgreSQL database is running with the project_tracker table
2. Install dependencies: `pip install -e .` (includes Flask)
3. Set environment variables (optional):
   - `PT_DB_HOST`: Database host (default: localhost)
   - `PT_DB_PORT`: Database port (default: 5433)
   - `PT_DB_NAME`: Database name (default: financial_analysis)
   - `PT_DB_USER`: Database user (default: finance_user)
   - `PT_DB_PASSWORD`: Database password (default: secure_finance_password)

## Running the Dashboard

```bash
# Navigate to the UI directory
cd ui/

# Start the API server
./start_server.sh

# Or run directly:
python3 api.py
```

Then open your browser to `http://localhost:5000`

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/projects` - List all projects with task counts
- `GET /api/project/{project_name}` - Detailed data for a specific project
- `GET /api/stats` - Global statistics across all projects

## Screenshots

The dashboard includes:
- Interactive charts for task visualization
- Project overview cards
- Status, priority, and category breakdowns
- Recent tasks listing
- Progress tracking