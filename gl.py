import os
from fnmatch import fnmatch

import requests
from dotenv import load_dotenv
from gitlab import Gitlab, GitlabAuthenticationError, GitlabGetError

requests.packages.urllib3.disable_warnings()


def enumerate_gitlab_projects(url, group, xfilter, ssl_verify=False):
    token = os.environ.get("GITLAB_TOKEN")

    try:
        gl = Gitlab(url, private_token=token, ssl_verify=ssl_verify)
        projects = gl.groups.get(group).projects.list(include_subgroups=True, as_list=False)
        return [proj for proj in projects if fnmatch(proj.path_with_namespace, xfilter)]
    except GitlabAuthenticationError:
        print(f"authentication error {url}, {token}, {ssl_verify}")
    except GitlabGetError as e:
        print(f"gitlab search {group} error {type(e)} => {e}")
    return []


def print_all_repos():
    url, group, xfilter = "https://gitlab.com", "mobilityaccelerator", "*"
    for repo in enumerate_gitlab_projects(url, group, xfilter):
        print(repo.ssh_url_to_repo)


if __name__ == "__main__":
    load_dotenv()
    print_all_repos()
