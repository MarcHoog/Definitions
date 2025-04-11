from abc import ABC, abstractmethod


class PullRequest(ABC):
    @abstractmethod
    def create_pull_request(self):
        """
        Create a pull request.
        """
        pass
