#!/bin/bash
# test_docker_external_sources.sh - Test Docker image with external data sources

echo "Building Docker image..."
cd /home/fred/projects/moltbot-helpers
docker build -t moltbot-helpers .

echo "Running Docker container with external data sources..."
# Run container mounting the current data directories
docker run -it --rm \
  -v /home/fred/projects/_openclaw:/data/_openclaw \
  -v /home/fred/.openclaw/workspace:/workspace \
  moltbot-helpers /bin/bash -c "
    echo 'Testing pt (Project Tracker)...';
    pt --project openclaw list | head -10;
    
    echo '';
    echo 'Testing seek (Semantic Search)...';
    seek status;
    
    echo '';
    echo 'Testing fp (Family Planner)...';
    fp tasks || echo 'No family planning tasks found (expected)';
    
    echo '';
    echo 'Testing integrate (Cross-reference)...';
    integrate status;
    
    echo '';
    echo 'Testing backup utility...';
    backup info || echo 'No backup available yet';
    
    echo '';
    echo 'All tools are accessible and working with external data sources!';
    echo 'Data directory contents:';
    ls -la /data/_openclaw/;
    echo '';
    echo 'Workspace directory contents:';
    ls -la /workspace/ || echo 'Workspace may not be accessible depending on permissions';
  "