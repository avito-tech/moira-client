from retry.api import retry_call
from requests import HTTPError
from requests.auth import HTTPBasicAuth
import requests


def raise_for_status_with_body(r):
    try:
        r.raise_for_status()
    except HTTPError as e:
        try:
            body = r.json()
        except ValueError:
            body = r.text
        e.args = e.args + (body,)
        raise e


class ResponseStructureError(Exception):
    def __init__(self, msg, content):
        """

        :param msg: str error message
        :param content: dict response content
        """
        self.msg = msg
        self.content = content


class InvalidJSONError(Exception):
    def __init__(self, content):
        """

        :param content: bytes response content
        """
        self.content = content


class RetryPolicy:
    def __init__(self, max_tries=1, delay=0, backoff=1):
        """A helper object describing client retry policy.

        :param max_tries: maximum number of attempts
        :param delay: delay between attempts in seconds
        :param backoff: multiplier applied to delay between attempts
        """
        self.max_tries = max_tries
        self.delay = delay
        self.backoff = backoff

    def _as_kwargs(self):
        return {
            "tries": self.max_tries,
            "delay": self.delay,
            "backoff": self.backoff,
        }


class Client:
    def __init__(self, api_url, auth_custom=None, auth_user=None, auth_pass=None, login=None, retry_policy=None):
        """

        :param api_url: str Moira API URL
        :param auth_custom: dict auth custom headers
        :param auth_user: str auth user
        :param auth_pass: str auth password
        :param login: str auth login
        :param retry_policy: RetryPolicy
        """
        if not api_url.endswith('/'):
            self.api_url = api_url + '/'
        else:
            self.api_url = api_url

        self.retry_policy = retry_policy or RetryPolicy()

        self.auth = None
        self.headers = {
            'X-Webauth-User': login,
            'Content-Type': 'application/json',
            'User-Agent': 'Python Moira Client'
            }

        if auth_user and auth_pass:
            self.auth = HTTPBasicAuth(auth_user, auth_pass)

        if auth_custom:
            self.headers.update(auth_custom)

    def get(self, path='', **kwargs):
        """

        :param path: str api path
        :param kwargs: additional parameters for request
        :return: dict response

        :raises: HTTPError
        :raises: InvalidJSONError
        """
        return retry_call(
            self._get, (path, ), kwargs,
            **self.retry_policy._as_kwargs(),
        )

    def _get(self, path='', **kwargs):
        r = requests.get(self._path_join(path), timeout=10, headers=self.headers, auth=self.auth, **kwargs)
        raise_for_status_with_body(r)
        try:
            return r.json()
        except ValueError:
            raise InvalidJSONError(r.content)

    def delete(self, path='', **kwargs):
        """

        :param path: str api path
        :param kwargs: additional parameters for request
        :return: dict response

        :raises: HTTPError
        :raises: InvalidJSONError
        """
        return retry_call(
            self._delete, (path, ), kwargs,
            **self.retry_policy._as_kwargs(),
        )

    def _delete(self, path='', **kwargs):
        r = requests.delete(self._path_join(path), timeout=10, headers=self.headers, auth=self.auth, **kwargs)
        raise_for_status_with_body(r)
        # AD-13298: DELETE requests (sometimes?) return a 0-byte response
        # and this is not an error
        if len(r.content) == 0:
            return None
        else:
            try:
                return r.json()
            except ValueError:
                raise InvalidJSONError(r.content)

    def put(self, path='', **kwargs):
        """

        :param path: str api path
        :param kwargs: additional parameters for request
        :return: dict response

        :raises: HTTPError
        :raises: InvalidJSONError
        """
        return retry_call(
            self._put, (path, ), kwargs,
            **self.retry_policy._as_kwargs(),
        )

    def _put(self, path='', **kwargs):
        r = requests.put(self._path_join(path), timeout=10, headers=self.headers, auth=self.auth, **kwargs)
        raise_for_status_with_body(r)
        try:
            return r.json()
        except ValueError:
            raise InvalidJSONError(r.content)

    def _path_join(self, *args):
        path = self.api_url
        for part in args:
            if part.startswith('/'):
                path += part[1:]
            else:
                path += part
        return path
