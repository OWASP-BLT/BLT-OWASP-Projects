import os
import json
import requests

GITHUB_API_URL = "https://api.github.com"
ORG_NAME = "owasp"
OUTPUT_FILE = "www_project_repos.json"
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

def get_repos():
    all_repos = []
    page = 1
    max_pages = 100  # Safety limit: 100 pages * 100 per page = 10,000 repos max

    headers = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"}

    # Fetch all pages until API returns empty response or safety limit reached
    while page <= max_pages:
        url = f"{GITHUB_API_URL}/orgs/{ORG_NAME}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        repos = response.json()
        if not repos:  # No more repositories to fetch
            break

        all_repos.extend(repos)
        page += 1

    return all_repos

def filter_and_format_repos(repos):
    # Return all repos, no filtering by prefix
    return repos

def send_slack_alert(new_repos):
    message = "New repositories detected:\n"
    for repo in new_repos:
        # Get description or use empty string if None
        description = repo.get('description') or 'No description'
        # Use Slack markdown link format: <URL|display text>
        message += f"- <https://github.com/{repo['full_name']}|{repo['full_name']}> - {description}\n"

    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()

def main():
    print('parsing repos')
    repos = get_repos()
    all_repos = filter_and_format_repos(repos)

    try:
        with open(OUTPUT_FILE, "r") as f:
            old_repos = json.load(f)
    except FileNotFoundError:
        old_repos = []

    new_repos = [repo for repo in all_repos if repo['id'] not in [old_repo['id'] for old_repo in old_repos]]
    if new_repos:
        send_slack_alert(new_repos)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_repos, f, indent=2)

if __name__ == "__main__":
    main()
