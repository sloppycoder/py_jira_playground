import os

from dotenv import load_dotenv
from jira import JIRA

load_dotenv()


def jira_connect() -> JIRA:
    server_url = os.environ["JIRA_URL"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]
    return JIRA(server=server_url, basic_auth=(jira_user, jira_token))


def main() -> None:
    jira = jira_connect()

    issue = jira.issue("VIN-5")
    print(issue.fields.project.key)
    print(issue.fields.issuetype.name)
    print(issue.fields.reporter.displayName)
    print(issue.fields.summary)


if __name__ == "__main__":
    main()
