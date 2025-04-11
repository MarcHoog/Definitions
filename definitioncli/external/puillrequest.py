from typing import Text

from abc import ABC, abstractmethod


class PullRequest(ABC):
    def __init__(
        self,
        title: Text,
        head: Text,
        base: Text,
        body: Text,
    ):
        self.head = head
        self.base = base
        self.title = title
        self.body = body

    def create_pull_request(self):
        """
        Create a pull request.
        """
        self._validate_branch(self.head)
        self._validate_branch(self.base)
        self._create_pull_request()

    @abstractmethod
    def _create_pull_request(self):
        """
        Create a pull request.
        """
        pass

    @abstractmethod
    def _validate_branch(self, branch: Text):
        pass

    def __repr__(self):
        return f"PullRequest(title={self.title}, head={self.head}, base={self.base}, body={self.body})"

    def __str__(self):
        return self.__repr__()
