from typing import Optional
from definitioncli.external.request import ApiRequest, BearerAuth


class GithubApi(ApiRequest):

    def __init__(self, token):
        """
        Initialize GithubApi with provided keyword arguments.

        Parameters:
            **kwargs: Arbitrary keyword arguments containing request details.
        """
        super().__init__(
            url=self.normalize_url("https://api.github.com"),
            authenticate=BearerAuth(token),
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
