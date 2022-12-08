import os
import platform
from fnmatch import fnmatch

import requests
from dotenv import load_dotenv
from gitlab import Gitlab, GitlabAuthenticationError, GitlabGetError

requests.packages.urllib3.disable_warnings()


# from unittest.mock import MagicMock
# platform.system = MagicMock(return_value="Windows")


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


def mkdir_cmd():
    return "mkdir -Force " if platform.system() == "Windows" else "mkdir -p"


def clone_script(parent_path, repo, clone_url):
    base_path = os.environ.get("LOCAL_BASE_PATH")
    output_path = f"{base_path}/{parent_path}"
    print(f"# {clone_url}")

    if os.path.isdir(f"{output_path}/{repo}/.git"):
        print(f"cd {output_path}/{repo}")
        print("git remote prune origin")
        print("git fetch")
        print("git pull")
        print("\n")
    else:
        print(f"{mkdir_cmd()} {output_path}")
        print(f"cd {output_path}")
        print(f"git clone {clone_url}")
        print("\n")


def print_all_repos():
    url, group, xfilter = "https://gitlab.com", "mobilityaccelerator", "*"
    for repo in enumerate_gitlab_projects(url, group, xfilter)[:2]:
        parent_path = "/".join(repo.path_with_namespace.split("/")[:-1])
        clone_script(parent_path, repo.name, repo.ssh_url_to_repo)


if __name__ == "__main__":
    load_dotenv()
    print_all_repos()
