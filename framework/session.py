import copy
import threading
import time
from functools import wraps
from io import BytesIO

import jsonpath_rw
import requests
# from jq import jq
from lxml import etree

from framework.utils import *


class TimeoutError(Exception):
    pass


class ConnectionError(Exception):
    pass


class Session(object):
    log = log.getChild('api-acceptance-tests')

    @staticmethod
    def target(*args, **kwargs):
        return HTTPAddress(*args, **kwargs)

    @staticmethod
    def request(method, address, session=None,
                params=None, headers=None, cookies=None, data=None, json=None, allow_redirects=True, timeout=30):

        Session.log.info("Request: %s %s", method, address)
        msg = "Request: params=%r, headers=%r, cookies=%r, data=%r, json=%r, allow_redirects=%r, timeout=%r"
        Session.log.debug(msg, params, headers, cookies, data, json, allow_redirects, timeout)

        if headers is None:
            headers = {}
        if "User-Agent" not in headers:
            headers["User-Agent"] = "api-acceptance-tests"

        if session is None:
            session = requests.Session()
            session.verify = False
        request = requests.Request(method, address,
                                   params=params, headers=headers, cookies=cookies, json=json, data=data)
        prepared = request.prepare()
        try:
            response = session.send(prepared, allow_redirects=allow_redirects, timeout=timeout)
        except requests.exceptions.Timeout:
            raise TimeoutError("Connection to %s timed out" % address)
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Connection to %s failed" % address)
        except BaseException:
            raise
        Session.log.info("Response: %s %s", response.status_code, response.reason)
        Session.log.debug("Response headers: %r", response.headers)
        Session.log.debug("Response cookies: %r", dict(response.cookies))
        Session.log.debug('Response content: \n%s', response.content)
        wrapped_response = HTTPResponse(response)
        return wrapped_response

    @staticmethod
    def get(address, **kwargs):
        return Session.request("GET", address, **kwargs)

    @staticmethod
    def post(address, **kwargs):
        return Session.request("POST", address, **kwargs)

    @staticmethod
    def put(address, **kwargs):
        return Session.request("PUT", address, **kwargs)

    @staticmethod
    def delete(address, **kwargs):
        return Session.request("DELETE", address, **kwargs)

    @staticmethod
    def patch(address, **kwargs):
        return Session.request("PATCH", address, **kwargs)

    @staticmethod
    def head(address, **kwargs):
        return Session.request("HEAD", address, **kwargs)

    @staticmethod
    def options(address, **kwargs):
        return Session.request("OPTIONS", address, **kwargs)

    @staticmethod
    def connect(address, **kwargs):
        return Session.request("CONNECT", address, **kwargs)

    # @staticmethod
    # def filter_json(json, selector):
    #     return jq(selector).transform(json.loads(json.text))


class HTTPAddress(object):
    def __init__(self,
                 address,
                 base_path=None,
                 use_cookies=True,
                 additional_headers=None,
                 keep_alive=True,
                 auto_assert_ok=True,
                 timeout=30,
                 allow_redirects=True):
        self.address = address
        # config flags
        self._base_path = base_path
        self._use_cookies = use_cookies
        self._keep_alive = keep_alive
        self._additional_headers = additional_headers or {}
        self._auto_assert_ok = auto_assert_ok
        self._timeout = timeout
        self._allow_redirects = allow_redirects
        self.__session = None

    def use_cookies(self, use=True):
        self._use_cookies = use
        return self

    def base_path(self, base_path):
        self._base_path = base_path
        return self

    def keep_alive(self, keep=True):
        self._keep_alive = keep
        return self

    def additional_headers(self, headers):
        self._additional_headers.update(headers)
        return self

    def auto_assert_ok(self, value=True):
        self._auto_assert_ok = value
        return self

    def timeout(self, value):
        self._timeout = value
        return self

    def allow_redirects(self, value=True):
        self._allow_redirects = value
        return self

    def _fix_address(self, path):
        addr = self.address
        if self._base_path is not None:
            addr += self._base_path
        addr += path
        return addr

    def request(self, method, path,
                params=None, headers=None, cookies=None, data=None, json=None, allow_redirects=None, timeout=None):
        headers = headers or {}
        timeout = timeout if timeout is not None else self._timeout
        allow_redirects = allow_redirects if allow_redirects is not None else self._allow_redirects

        if self._keep_alive and self.__session is None:
            self.__session = requests.Session()

        if self.__session is not None and not self._use_cookies:
            self.__session.cookies.clear()

        address = self._fix_address(path)
        req_headers = copy.deepcopy(self._additional_headers)
        req_headers.update(headers)

        response = Session.request(method, address, session=self.__session,
                                   params=params, headers=headers, cookies=cookies, data=data, json=json,
                                   allow_redirects=allow_redirects, timeout=timeout)
        if self._auto_assert_ok:
            response.assert_ok()
        return response

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def head(self, path, **kwargs):
        return self.request("HEAD", path, **kwargs)

    def options(self, path, **kwargs):
        return self.request("OPTIONS", path, **kwargs)

    def connect(self, path, **kwargs):
        return self.request("CONNECT", path, **kwargs)


class HTTPResponse(object):
    def __init__(self, py_response):
        """
        Construct HTTPResponse from requests.Response object

        :type py_response: requests.Response
        """
        self.url = py_response.url
        self.method = py_response.request.method
        self.status_code = int(py_response.status_code)
        self.reason = py_response.reason

        self.headers = dict(py_response.headers)
        self.cookies = dict(py_response.cookies)

        self.text = py_response.text
        self.content = py_response.content

        self.elapsed = py_response.elapsed

        self._response = py_response
        self._request = py_response.request

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.status_code == other.status_code \
               and self.method == other.method \
               and self.url == other.url \
               and self.reason == other.reason \
               and self.headers == other.headers \
               and self.cookies == other.cookies \
               and self.text == other.text \
               and self.content == other.content

    def json(self):
        return self._response.json()

    def assert_ok(self, msg=None):
        if self.status_code >= 400:
            msg = msg or "Request to %s didn't succeed (%s)" % (self.url, self.status_code)
            raise AssertionError(msg)
        return self

    def assert_jsonpath(self, jsonpath_query, expected_value=None, msg=None):
        jsonpath_expr = jsonpath_rw.parse(jsonpath_query)
        body = self.json()
        matches = jsonpath_expr.find(body)
        if not matches:
            msg = msg or "JSONPath query %r didn't match response: %s" % (jsonpath_query, body)
            raise AssertionError(msg)
        actual_value = matches[0].value
        Session.log.info(matches)
        if expected_value is not None and actual_value != expected_value:
            tmp = "Actual value at JSONPath query (%r) isn't as expected: (%r)"
            msg = msg or tmp % (actual_value, expected_value)
            raise AssertionError(msg)
        return self

    def assert_not_jsonpath(self, jsonpath_query, msg=None):
        jsonpath_expr = jsonpath_rw.parse(jsonpath_query)
        body = self.json()
        matches = jsonpath_expr.find(body)
        if matches:
            msg = msg or "JSONPath query %r did match response content: %s" % (jsonpath_query, body)
            raise AssertionError(msg)
        return self

    def extract_regex(self, regex, default=None):
        extracted_value = default
        for item in re.finditer(regex, self.text):
            extracted_value = item
            break
        return extracted_value

    def extract_jsonpath(self, jsonpath_query, default=None):
        jsonpath_expr = jsonpath_rw.parse(jsonpath_query)
        body = self.json()
        matches = jsonpath_expr.find(body)
        if not matches:
            return default
        return matches[0].value

    def extract_xpath(self, xpath_query, default=None, parser_type='html', validate=False):
        parser = etree.HTMLParser() if parser_type == 'html' else etree.XMLParser(dtd_validation=validate)
        tree = etree.parse(BytesIO(self.content), parser)
        matches = tree.xpath(xpath_query)
        if not matches:
            return default
        match = matches[0]
        return match.text
