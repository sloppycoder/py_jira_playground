import os
import platform
import sys
from fnmatch import fnmatch

import requests
from dotenv import dotenv_values
from gitlab import Gitlab, GitlabAuthenticationError, GitlabGetError

requests.packages.urllib3.disable_warnings()


# from unittest.mock import MagicMock
# platform.system = MagicMock(return_value="Windows")


def enumerate_gitlab_projects(url, group, token, ssl_verify=False):
    try:
        gl = Gitlab(url, private_token=token, ssl_verify=ssl_verify)
        return gl.groups.get(group).projects.list(include_subgroups=True, as_list=False)
    except GitlabAuthenticationError:
        print(f"authentication error {url}, {token}, {ssl_verify}")
    except GitlabGetError as e:
        print(f"gitlab search {group} error {type(e)} => {e}")
    return []


def mkdir_cmd():
    return "mkdir -Force " if platform.system() == "Windows" else "mkdir -p"


def clone_script(base_path, parent_path, repo, clone_url):
    output_path = f"{base_path}/{parent_path}"
    print(f"# {clone_url}")

    if os.path.isdir(f"{output_path}/{repo}/.git"):
        print(f'echo "existing: {output_path}/{repo}"')
        print(f"cd {output_path}/{repo}")
        print("git remote prune origin")
        print("git fetch")
        print("git pull")
        print("\n")
    else:
        print(f'echo "new: {output_path}/{repo}"')
        print(f"{mkdir_cmd()} {output_path}")
        print(f"cd {output_path}")
        print(f"git clone {clone_url}")
        print("\n")


def print_clone_all_script(url, group, token, local_base_path, xfilter="*", strip_prefix=""):
    strip_prefix = group + "/" + strip_prefix

    for repo in enumerate_gitlab_projects(url, group, token):
        if not fnmatch(repo.path_with_namespace, xfilter):
            continue

        repo_path = repo.path_with_namespace
        if repo_path.find(strip_prefix) == 0:
            repo_path = repo_path[len(strip_prefix) + 1 :]
        parent_path = "/".join(repo_path.split("/")[:-1])

        clone_script(local_base_path, parent_path, repo.name, repo.ssh_url_to_repo)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        conf = dotenv_values("gl.env")
    else:
        conf = dotenv_values(sys.argv[1])

    print_clone_all_script(
        conf["GITLAB_URL"],
        conf["GITLAB_GROUP"],
        conf["GITLAB_TOKEN"],
        conf["LOCAL_BASE_PATH"],
        conf["GITLAB_PROJECT_FILTER"],
        conf["STRIP_PREFIX"],
    )
