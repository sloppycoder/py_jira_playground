import logging
import os
import pprint
import sys

from dotenv import load_dotenv
from jira import JIRA

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

custom_fields = {}

query1 = 'created >= -30w AND project = EIPP AND issuetype in ("BE DEV Task", "FE AND DEV Task", "FE IOS DEV Task", "FE WEB DEV Task") AND status in (BE-AD-FOR-REVIEW, BE-AD-IN-PROGRESS, BE-AD-TO-DO, BE-DEV-FOR-REVIEW, BE-DEV-IN-PROGRESS, BE-DEV-TO-DO, Blocked, FE-AD-FOR-REVIEW, FE-AD-IN-PROGRESS, FE-AD-TO-DO, FE-DEV-FOR-REVIEW, FE-DEV-IN-PROGRESS, FE-DEV-TO-DO) AND Sprint = 2138 '
query2 = 'created >= -30w AND project = EIPP AND key in ("EIPP-245")'


def jira_connect() -> JIRA:
    server_url = os.environ["JIRA_URL"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]
    return JIRA(server=server_url, basic_auth=(jira_user, jira_token))


def issue_to_map(jira: JIRA, issue):
    global custom_fields
    if custom_fields == {}:
        custom_fields = {field["name"]: field["id"] for field in jira.fields()}

    return {
        "key": issue.fields.project.key,
        "type": issue.fields.issuetype.name,
        "status": issue.fields.status.name,
        "summary": issue.fields.summary,
        "labels": issue.fields.labels,
        "feature": getattr(issue.fields, custom_fields["BN Feature Grouping"]),
    }


def search_issue(jira: JIRA, jql: str, max_results=1000, page_size=100):
    for offset in range(0, max_results, page_size):
        logging.debug(f"calling search_issues with maxResults={page_size}, startAt={offset}")
        issues = jira.search_issues(jql, maxResults=page_size, startAt=offset)
        for issue in issues:
            yield issue
        if len(issues) < page_size:
            logging.debug("issues exhausted, break")
            break


def main():
    jira = jira_connect()
    count = 0
    for issue in search_issue(jira, query1):
        count += 1
        pprint.pprint(issue)
    print(f"\ntotal issues: {count}")


if __name__ == "__main__":
    load_dotenv()
    main()
