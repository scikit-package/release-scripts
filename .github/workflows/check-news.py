"""Check if the PR has a news item.

Put a warning comment and return `assert False` if the PR does not
contain a news file.
"""

import os
from fnmatch import fnmatch

from github import Github, PullRequest


def get_added_files(pr: PullRequest.PullRequest):
    print(pr, pr.number)
    for file in pr.get_files():
        if file.status == "added":
            yield file.filename


def check_news_file(pr):
    return any(
        map(
            lambda file_name: fnmatch(file_name, "news/*.rst"),
            get_added_files(pr),
        )
    )


def get_pr_number():
    number = os.environ["PR_NUMBER"]
    if not number:
        raise Exception(
            f"Pull request number is not found `PR_NUMBER={number}"
        )
    return int(number)


def get_old_comment(pr: PullRequest.PullRequest):
    for comment in pr.get_issue_comments():
        if ("github-actions" in comment.user.login) and (
            "No news item is found" in comment.body
        ):
            return comment


def main():
    # using an access token
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(get_pr_number())
    has_news_added = check_news_file(pr)
    old_comment = get_old_comment(pr)

    if has_news_added:
        if old_comment:
            print("Found an existing comment from bot")
            print("Delete warning from bot, since news item is added.")
            old_comment.delete()
    else:
        print("No news item found")
        if old_comment:
            print("Old warning remains relevant, no action needed.")
        else:
            pr.create_issue_comment(
                """\
**Warning!** No news item is found for this PR. If this is a user-facing
change/feature/fix,
please add a news item by copying the format from `news/TEMPLATE.rst`.
For best practices, please visit
https://scikit-package.github.io/scikit-package/frequently-asked-questions.html#billinge-group-standards.
"""
            )
        assert False


if __name__ == "__main__":
    main()
