"""Contains implementation of IcdMapper class."""

import http.client
import json
import logging
from base64 import b64encode

from icd_reader import helpers, logger

logger.initialize()


class IcdMapper:
    """Contains methods used to map ICD 10 codes to ICD 11 codes."""

    http_client: http.client.HTTPSConnection
    token: dict

    def __init__(self, client_id, client_secret):
        self.http_client = http.client.HTTPSConnection("id.who.int", 443)
        self._get_token(client_id, client_secret)

    def __del__(self):
        self.http_client.close()

    def _get_token(self, client_id, client_secret):
        authorization_string: str = client_id + ":" + client_secret
        authorization_string_encoded: str = b64encode(authorization_string.encode()).decode("ascii")
        headers = {
            "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,pl;q=0.6",
            "Authorization": "Basic {0}".format(authorization_string_encoded),
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "icdaccessmanagement.who.int"
        }
        self.http_client.request(
            "POST",
            "https://icdaccessmanagement.who.int/connect/token",
            headers=headers,
            body="grant_type=client_credentials"
        )
        res = self.http_client.getresponse()
        self.token = json.loads(res.read())

    def _get_icd_10_name(self, icd_10_code: str) -> str:
        headers = {
            "accept": "application/json",
            "Accept-Language": "en",
            "API-Version": "v2",
            "Authorization": self.token["token_type"] + " " + self.token["access_token"],
        }
        url: str = "/icd/release/10/2016/" + icd_10_code
        self.http_client.request("GET", url, headers=headers)
        res = self.http_client.getresponse()
        res_json: dict = json.loads(res.read())
        return res_json["title"]["@value"]

    def _get_icd_11_code(self, disease_name) -> str:
        headers = {
            "accept": "application/json",
            "Accept-Language": "en",
            "API-Version": "v2",
            "Authorization": self.token["token_type"] + " " + self.token["access_token"],
        }
        url_params: dict = {
            "q": disease_name,
            "includeKeywordResult": "false",
            "useFlexisearch": "false",
            "flatResults": "true"
        }
        url: str = "/icd/release/11/2019-04/mms/search"
        url_with_params: str = helpers.add_http_parameters(url, url_params)
        self.http_client.request("GET", url_with_params, headers=headers)
        res = self.http_client.getresponse()
        res_json: dict = json.loads(res.read())
        return res_json["destinationEntities"][0]["theCode"].split("&")[0]

    def icd_10_to_icd_11(self, icd_10_code: str) -> str:
        """
        Maps ICD 10 code to ICD 11 code via WHO ICD API.

        :param icd_10_code:
        :return: ICD 11 code
        """
        disease_name: str = self._get_icd_10_name(icd_10_code)
        logging.info("Disease name for ICD 10 code '{0}' is '{1}'".format(icd_10_code, disease_name))
        icd_11_code: str = self._get_icd_11_code(disease_name)
        logging.info("Mapped ICD 10 code '{0}' to ICD 11 code '{1}'".format(icd_10_code, icd_11_code))
        return icd_11_code
