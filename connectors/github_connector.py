import requests

def fetch_github_issues(repo: str, token: str, state: str = "open", github_url: str = "https://ghe.coxautoinc.com") -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    # Sử dụng GitHub Enterprise URL
    url = f"{github_url}/api/v3/repos/{repo}/issues?state={state}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        issues = response.json()
        if not issues:
            return "📭 Không có issue nào trên GitHub Enterprise."
        lines = [f"- #{issue['number']} {issue['title']}" for issue in issues if 'pull_request' not in issue]
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Lỗi khi truy cập GitHub Enterprise: {str(e)}"