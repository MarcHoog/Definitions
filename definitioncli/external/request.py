import json
from requests import Response, request
from requests.auth import AuthBase


class BearerAuth(AuthBase):
    """
    Custom authentication class for Bearer token authentication.
    """

    def __init__(self, token: str):
        """
        Initialize BearerAuth with a token.

        Parameters:
            token (str): The Bearer token for authentication.
        """
        self.token = token

    def __call__(self, request):
        """
        Attach the Bearer token to the request headers.

        Parameters:
            request (requests.PreparedRequest): The request object.

        Returns:
            requests.PreparedRequest: The modified request object.
        """
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


class ApiRequest(object):
    """
    Handles HTTPs request easily and dynamically.
    """

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initialize request with provided keyword arguments.

        Parameters:
            **kwargs: Arbitrary keyword arguments containing request details.
        """
        self._store = kwargs

    @staticmethod
    def normalize_url(url):
        """
        Normalize the given URL by removing a trailing slash if present.

        Parameters:
            url (str): The URL to normalize.

        Returns:
            str: The normalized URL.
        """
        if url[-1] == "/":
            return url[:-1]
        return url

    def combine_url(self, url, path):
        """
        Combine base URL with a specific API path.

        Parameters:
            url (str): Base URL.
            path (str): API resource path.

        Returns:
            str: The full API URL.
        """
        return f"{url}/{path}"

    def __getattr__(self, resource: str) -> "ApiRequest":
        """
        Dynamically handle resource paths as attributes.

        Parameters:
            resource (str): The API resource name.

        Returns:
            ManagedEngineCeRequest: A new instance with updated URL.
        """
        store = self._store.copy()
        store["url"] = self.combine_url(store["url"], resource)
        return ApiRequest(**store)

    def _handle_error_response(self, response: Response):
        """
        Handle API error responses.

        Parameters:
            response (requests.Response): The response object.

        Raises:
            RequestError: If the response status code indicates an error.
        """

        code = response.status_code
        if code < 500:
            response.raise_for_status()
        elif code > 500:
            response.raise_for_status()

    def _send_request(self, method, params: dict = {}, data: dict = {}):
        """
        Send an HTTP request to the API.

        Parameters:
            method (str): HTTP method (GET, POST, etc.).
            params (dict): Query parameters.
            data (dict): Request body data.

        Returns:
            dict: Parsed JSON response.

        Raises:
            RequestError: If the request fails.
        """
        headers = self._store.get("headers", {"Content-Type": "application/json"})

        resp: Response = request(
            method,
            self._store["url"],
            params=params,
            data=data,
            verify=self._store["verify_ssl"],
            auth=self._store.get("authenticate", None),
            headers=headers,
        )

        if resp.status_code >= 400:
            self._handle_error_response(resp)

        elif 200 <= resp.status_code <= 299:
            return json.loads(resp.text)

    def __call__(self, method: str, params: dict = {}, data: dict = {}):
        return self._send_request(method, params=params, data=data)

    def get(self, **kwargs):
        """
        Perform a GET request.

        Parameters:
            params (dict): Query parameters.

        Returns:
            dict: API response.
        """
        return self._send_request("GET", params=kwargs)

    def post(self, data: dict = {}):
        """
        Perform a POST request.

        Parameters:
            data (dict): Request body data.

        Returns:
            dict: API response.
        """
        return self._send_request("POST", data=data)

    def __str__(self) -> str:
        return f"{self._store['url']}"

    def __repr__(self):
        return f"Api Request: {self._store['url']}"
