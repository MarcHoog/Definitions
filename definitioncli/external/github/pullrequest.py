from .request import GithubApi
from typing import Text, Optional
from definitioncli.external.puillrequest import PullRequest


class GitHubPullRequest(PullRequest):

    def __init__(
        self,
        token: Text,
        owner: Text,
        repo: Text,
        title: Text,
        head: Text,
        base: Text,
        body: Text,
        head_repo: Optional[str] = None,
        maintainer_can_modify: Optional[bool] = False,
        draft: bool = False,
        issue: Optional[int] = None,
    ):
        self._api = GithubApi(token)
        self.owner = owner
        self.repo = repo

        self.title = title
        self.head = head
        self.base = base
        self.body = body
        self.head_repo = head_repo
        self.maintainer_can_modify = maintainer_can_modify
        self.draft = draft
        self.issue = issue

    def _create_pull_request(self):
        """
        Create a pull request on GitHub.
        """

        pullrequest_endpoint = (
            self._api.__getattr__(self.owner).__getattr__(self.repo).pulls
        )

        pullrequest_endpoint.post(
            data={
                "title": self.title,
                "body": self.body,
                "head": self.head,
                "base": self.base,
                "draft": self.draft,
                "maintainer_can_modify": self.maintainer_can_modify,
            }
        )
