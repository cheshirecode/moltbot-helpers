# Mock GitHub API Service for Demo

import json
import time
from flask import Flask, jsonify, request


class MockGitHubAPI:
    """Mock GitHub API service for demo environment"""
    
    def __init__(self, data_file="./data/synthetic_data.json"):
        # Using synthetic data or creating specific GitHub mock data
        self.mock_data = {
            "repos": [
                {
                    "id": 1,
                    "name": "openclaw-demo-project",
                    "full_name": "demo-user/openclaw-demo-project",
                    "private": False,
                    "html_url": "https://github.com/demo-user/openclaw-demo-project",
                    "description": "Demo repository showcasing OpenClaw capabilities",
                    "fork": False,
                    "created_at": "2026-01-15T10:00:00Z",
                    "updated_at": "2026-02-05T09:00:00Z",
                    "pushed_at": "2026-02-05T08:30:00Z",
                    "size": 154,
                    "stargazers_count": 42,
                    "watchers_count": 42,
                    "language": "Python",
                    "has_issues": True,
                    "has_projects": True,
                    "has_downloads": True,
                    "has_wiki": True,
                    "has_pages": False,
                    "forks_count": 8,
                    "open_issues_count": 3,
                    "license": {
                        "key": "mit",
                        "name": "MIT License",
                        "spdx_id": "MIT"
                    }
                },
                {
                    "id": 2,
                    "name": "moltbot-helpers-demo",
                    "full_name": "demo-user/moltbot-helpers-demo",
                    "private": False,
                    "html_url": "https://github.com/demo-user/moltbot-helpers-demo",
                    "description": "Helper tools demo for Moltbot ecosystem",
                    "fork": False,
                    "created_at": "2026-01-20T14:30:00Z",
                    "updated_at": "2026-02-04T16:45:00Z",
                    "pushed_at": "2026-02-04T16:30:00Z",
                    "size": 89,
                    "stargazers_count": 28,
                    "watchers_count": 28,
                    "language": "JavaScript",
                    "has_issues": True,
                    "has_projects": False,
                    "has_downloads": True,
                    "has_wiki": True,
                    "has_pages": True,
                    "forks_count": 5,
                    "open_issues_count": 1,
                    "license": {
                        "key": "apache-2.0",
                        "name": "Apache License 2.0",
                        "spdx_id": "Apache-2.0"
                    }
                }
            ],
            "issues": [
                {
                    "id": 101,
                    "number": 1,
                    "title": "Implement demo feature",
                    "body": "Create a comprehensive demo of the system capabilities",
                    "state": "open",
                    "created_at": "2026-02-01T10:00:00Z",
                    "updated_at": "2026-02-05T09:15:00Z",
                    "user": {
                        "login": "demo-contributor",
                        "id": 1001,
                        "type": "User"
                    },
                    "labels": [
                        {
                            "name": "enhancement",
                            "color": "a2eeef"
                        }
                    ]
                },
                {
                    "id": 102,
                    "number": 2,
                    "title": "Fix minor UI bug",
                    "body": "Small visual issue in the dashboard component",
                    "state": "closed",
                    "created_at": "2026-01-28T15:30:00Z",
                    "updated_at": "2026-01-29T09:15:00Z",
                    "closed_at": "2026-01-29T09:15:00Z",
                    "user": {
                        "login": "demo-contributor",
                        "id": 1001,
                        "type": "User"
                    },
                    "labels": [
                        {
                            "name": "bug",
                            "color": "e11d21"
                        }
                    ]
                }
            ],
            "pull_requests": [
                {
                    "id": 201,
                    "number": 5,
                    "title": "Add comprehensive demo functionality",
                    "state": "open",
                    "created_at": "2026-02-04T14:20:00Z",
                    "updated_at": "2026-02-05T08:45:00Z",
                    "user": {
                        "login": "demo-contributor",
                        "id": 1001,
                        "type": "User"
                    },
                    "draft": False
                }
            ]
        }
    
    def get_user_repos(self, username="demo-user", sort="updated", direction="desc", per_page=30, page=1):
        """Mock repositories endpoint"""
        time.sleep(0.1)
        repos = self.mock_data['repos']
        
        # Apply sorting
        if sort == "updated":
            repos.sort(key=lambda x: x['updated_at'], reverse=(direction == "desc"))
        elif sort == "created":
            repos.sort(key=lambda x: x['created_at'], reverse=(direction == "desc"))
        elif sort == "name":
            repos.sort(key=lambda x: x['name'], reverse=(direction == "desc"))
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_repos = repos[start_idx:end_idx]
        
        return {
            "repositories": paginated_repos,
            "total_count": len(repos),
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_pages": (len(repos) + per_page - 1) // per_page
            }
        }
    
    def get_repo_issues(self, owner="demo-user", repo="openclaw-demo-project", state="open", labels=None):
        """Mock issues endpoint"""
        time.sleep(0.08)
        issues = self.mock_data['issues']
        
        # Filter by state
        if state != "all":
            issues = [i for i in issues if i['state'] == state]
        
        # Filter by labels if provided
        if labels:
            label_names = labels.split(',')
            issues = [i for i in issues if any(label['name'] in label_names for label in i['labels'])]
        
        return {"issues": issues}
    
    def get_pull_requests(self, owner="demo-user", repo="openclaw-demo-project", state="open"):
        """Mock pull requests endpoint"""
        time.sleep(0.08)
        prs = self.mock_data['pull_requests']
        
        if state != "all":
            prs = [pr for pr in prs if pr['state'] == state]
        
        return {"pull_requests": prs}


def create_mock_github_app():
    app = Flask(__name__)
    mock_api = MockGitHubAPI()
    
    @app.route('/user/repos', methods=['GET'])
    def user_repos():
        username = request.args.get('username', 'demo-user')
        sort = request.args.get('sort', 'updated')
        direction = request.args.get('direction', 'desc')
        per_page = int(request.args.get('per_page', 30))
        page = int(request.args.get('page', 1))
        
        repos = mock_api.get_user_repos(username, sort, direction, per_page, page)
        return jsonify(repos)
    
    @app.route('/repos/<owner>/<repo>/issues', methods=['GET'])
    def repo_issues(owner, repo):
        state = request.args.get('state', 'open')
        labels = request.args.get('labels')
        
        issues = mock_api.get_repo_issues(owner, repo, state, labels)
        return jsonify(issues)
    
    @app.route('/repos/<owner>/<repo>/pulls', methods=['GET'])
    def repo_pulls(owner, repo):
        state = request.args.get('state', 'open')
        
        prs = mock_api.get_pull_requests(owner, repo, state)
        return jsonify(prs)
    
    return app


if __name__ == '__main__':
    app = create_mock_github_app()
    app.run(host='0.0.0.0', port=5004, debug=False)