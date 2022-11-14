import os
import pprint

from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

names_map = {}


def jira_connect() -> JIRA:
    server_url = os.environ["JIRA_URL"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]
    return JIRA(server=server_url, basic_auth=(jira_user, jira_token))


def issue_to_map(jira: JIRA, issue):
    global names_map
    if names_map == {}:
        names_map = {field["name"]: field["id"] for field in jira.fields()}

    return {
        "Key": issue.fields.project.key,
        "Type": issue.fields.issuetype.name,
        "Status": issue.fields.status.name,
        "Summary": issue.fields.summary,
        "Labels": issue.fields.labels,
        "Feature": getattr(issue.fields, names_map["BN Feature Grouping"]),
    }


def get_issue_list(jira: JIRA):
    jql = 'created >= -30w AND project = EIPP AND issuetype in ("BE DEV Task", "FE AND DEV Task", "FE IOS DEV Task", "FE WEB DEV Task") AND status in (BE-AD-FOR-REVIEW, BE-AD-IN-PROGRESS, BE-AD-TO-DO, BE-DEV-FOR-REVIEW, BE-DEV-IN-PROGRESS, BE-DEV-TO-DO, Blocked, FE-AD-FOR-REVIEW, FE-AD-IN-PROGRESS, FE-AD-TO-DO, FE-DEV-FOR-REVIEW, FE-DEV-IN-PROGRESS, FE-DEV-TO-DO) AND Sprint = 2138 '
    # jql = 'created >= -30w AND project = EIPP AND key in ("EIPP-245")'
    result = jira.search_issues(jql, maxResults=200)
    print(f"total issues: {len(result)}")
    for item in result:
        pprint.pprint(issue_to_map(jira, item))


if __name__ == "__main__":
    jira = jira_connect()
    get_issue_list(jira)
