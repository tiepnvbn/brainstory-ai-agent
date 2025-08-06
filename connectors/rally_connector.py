import requests

def fetch_rally_data(query: str, api_key: str, workspace: str, project: str) -> str:
    headers = {
        "ZSESSIONID": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "query": query,
        "workspace": f"/workspace/{workspace}",
        "project": f"/project/{project}"
    }

    url = "https://rally1.rallydev.com/slm/webservice/v2.0/hierarchicalrequirement"
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        results = response.json().get("QueryResult", {}).get("Results", [])
        if not results:
            return "🔍 Không tìm thấy dữ liệu phù hợp từ Rally."
        stories = [f"- {item.get('Name')} (ID: {item.get('FormattedID')})" for item in results]
        return "\n".join(stories)
    except Exception as e:
        return f"❌ Lỗi khi truy cập Rally: {str(e)}"