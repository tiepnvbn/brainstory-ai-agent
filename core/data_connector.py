import os
import requests
from dotenv import load_dotenv
from connectors.github_connector import fetch_github_issues
from connectors.rally_connector import fetch_rally_data

# Load environment variables
load_dotenv()

class DataConnector:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.rally_api_key = os.getenv("RALLY_API_KEY")
        self.slack_token = os.getenv("SLACK_TOKEN")
        # GitHub Enterprise URL
        self.github_base_url = os.getenv("GITHUB_URL", "https://ghe.coxautoinc.com")
        self.github_api_url = f"{self.github_base_url}/api/v3"
    
    def get_github_data(self, repo: str, include_prs: bool = False) -> dict:
        """Lay du lieu tu GitHub repository"""
        if not self.github_token:
            return {"error": "GITHUB_TOKEN khong duoc cau hinh"}
        
        result = {
            "issues": [],
            "pull_requests": [],
            "repository_info": {},
            "files": []
        }
        
        try:
            # Lay thong tin repository
            repo_info = self._get_repo_info(repo)
            result["repository_info"] = repo_info
            
            # Lay issues
            issues = self._get_github_issues(repo)
            result["issues"] = issues
            
            # Lay pull requests neu can
            if include_prs:
                prs = self._get_github_pull_requests(repo)
                result["pull_requests"] = prs
            
            # Lay cau truc file du an
            files = self._get_repo_files(repo)
            result["files"] = files
            
        except Exception as e:
            result["error"] = f"Loi khi lay du lieu GitHub: {str(e)}"
        
        return result
    
    def get_rally_data(self, workspace: str = "", project: str = "") -> dict:
        """Lay du lieu tu Rally"""
        if not self.rally_api_key:
            return {"error": "RALLY_API_KEY khong duoc cau hinh"}
        
        result = {
            "user_stories": [],
            "features": [],
            "defects": []
        }
        
        try:
            # Lay User Stories
            stories = self._get_rally_stories(workspace, project)
            result["user_stories"] = stories
            
            # Lay Features
            features = self._get_rally_features(workspace, project)
            result["features"] = features
            
            # Lay Defects
            defects = self._get_rally_defects(workspace, project)
            result["defects"] = defects
            
        except Exception as e:
            result["error"] = f"Loi khi lay du lieu Rally: {str(e)}"
        
        return result
    
    def _get_repo_info(self, repo: str) -> dict:
        """Lay thong tin co ban ve repository"""
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        url = f"{self.github_api_url}/repos/{repo}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return {
            "name": data.get("name"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count")
        }
    
    def _get_github_issues(self, repo: str) -> list:
        """Lay danh sach issues"""
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        url = f"{self.github_api_url}/repos/{repo}/issues?state=all&per_page=50"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        issues = response.json()
        return [
            {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "labels": [label.get("name") for label in issue.get("labels", [])],
                "body": issue.get("body", "")[:500]  # Gioi han do dai
            }
            for issue in issues if "pull_request" not in issue
        ]
    
    def _get_github_pull_requests(self, repo: str) -> list:
        """Lay danh sach pull requests"""
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        url = f"{self.github_api_url}/repos/{repo}/pulls?state=all&per_page=30"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        prs = response.json()
        return [
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "body": pr.get("body", "")[:500]
            }
            for pr in prs
        ]
    
    def _get_repo_files(self, repo: str, path: str = "") -> list:
        """Lay cau truc file repository"""
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        url = f"{self.github_api_url}/repos/{repo}/contents/{path}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        files = response.json()
        result = []
        
        for file in files:
            result.append({
                "name": file.get("name"),
                "type": file.get("type"),
                "path": file.get("path"),
                "size": file.get("size")
            })
        
        return result
    
    def _get_rally_stories(self, workspace: str, project: str) -> list:
        """Lay User Stories tu Rally"""
        headers = {
            "ZSESSIONID": self.rally_api_key,
            "Content-Type": "application/json"
        }
        
        url = "https://rally1.rallydev.com/slm/webservice/v2.0/hierarchicalrequirement"
        params = {
            "pagesize": 50,
            "order": "LastUpdateDate DESC"
        }
        
        if workspace:
            params["workspace"] = f"/workspace/{workspace}"
        if project:
            params["project"] = f"/project/{project}"
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("QueryResult", {}).get("Results", [])
        
        return [
            {
                "formatted_id": story.get("FormattedID"),
                "name": story.get("Name"),
                "state": story.get("ScheduleState"),
                "description": story.get("Description", "")[:500],
                "plan_estimate": story.get("PlanEstimate"),
                "owner": story.get("Owner", {}).get("_refObjectName") if story.get("Owner") else None
            }
            for story in results
        ]
    
    def _get_rally_features(self, workspace: str, project: str) -> list:
        """Lay Features tu Rally"""
        print(f"🔍 DEBUG: Starting _get_rally_features with workspace='{workspace}', project='{project}'")
        headers = {
            "ZSESSIONID": self.rally_api_key,
            "Content-Type": "application/json"
        }
        
        url = "https://rally1.rallydev.com/slm/webservice/v2.0/project/424702908912ud"
        params = {
            "pagesize": 30,
            "order": "LastUpdateDate DESC"
        }
        
        if workspace:
            params["workspace"] = f"/{workspace}"
        if project:
            params["project"] = f"/{project}"
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"🔍 DEBUG: Response _get_rally_features with project='{data}'")
        results = data.get("QueryResult", {}).get("Results", [])
        
        return [
            {
                "formatted_id": feature.get("FormattedID"),
                "name": feature.get("Name"),
                "state": feature.get("State"),
                "description": feature.get("Description", "")[:500]
            }
            for feature in results
        ]
    
    def _get_rally_defects(self, workspace: str, project: str) -> list:
        """Lay Defects tu Rally"""
        headers = {
            "ZSESSIONID": self.rally_api_key,
            "Content-Type": "application/json"
        }
        
        url = "https://rally1.rallydev.com/slm/webservice/v2.0/defect"
        params = {
            "pagesize": 30,
            "order": "LastUpdateDate DESC"
        }
        
        if workspace:
            params["workspace"] = f"/workspace/{workspace}"
        if project:
            params["project"] = f"/project/{project}"
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("QueryResult", {}).get("Results", [])
        
        return [
            {
                "formatted_id": defect.get("FormattedID"),
                "name": defect.get("Name"),
                "state": defect.get("State"),
                "severity": defect.get("Severity"),
                "description": defect.get("Description", "")[:300]
            }
            for defect in results
        ]

# Khoi tao connector
data_connector = DataConnector()
