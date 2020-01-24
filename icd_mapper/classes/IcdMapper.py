import http.client
import json
import logging
from base64 import b64encode

from icd_mapper import helpers, logger

logger.initialize()


class IcdMapper:
    """Class used to map ICD-10 codes to ICD-11 codes."""

    token: dict

    def __init__(self, client_id: str, client_secret: str):
        """Connects to WHO ICD-11 API.

        :param client_id: client id for ICD-11 API
        :type client_id: str
        :param client_secret: client secret for ICD-11 API
        :type client_secret: str
        """
        self._get_token(client_id, client_secret)

    def __del__(self):
        pass

    def _connect_http_client(self) -> http.client.HTTPSConnection:
        return http.client.HTTPSConnection("id.who.int", 443)

    def _get_token(self, client_id, client_secret):
        authorization_string: str = client_id + ":" + client_secret
        authorization_string_encoded: str = b64encode(authorization_string.encode()).decode("ascii")
        headers = {
            "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7,pl;q=0.6",
            "Authorization": "Basic {}".format(authorization_string_encoded),
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "icdaccessmanagement.who.int"
        }
        http_client = self._connect_http_client()
        http_client.request(
            "POST",
            "https://icdaccessmanagement.who.int/connect/token",
            headers=headers,
            body="grant_type=client_credentials"
        )
        res = http_client.getresponse()
        self.token = json.loads(res.read())
        http_client.close()

    def get_icd_10_name(self, icd_10_code: str) -> str:
        """Retrieves name of disease using ICD-10 code.

        :param icd_10_code: ICD-10 code
        :type icd_10_code:  str
        :return: Disease name for given ICD-10 code
        :rtype: str
        """
        icd_10_code = icd_10_code.upper()
        headers = {
            "accept": "application/json",
            "Accept-Language": "en",
            "API-Version": "v2",
            "Authorization": self.token["token_type"] + " " + self.token["access_token"],
        }
        logging.info('Searching for name of ICD-10 code: ' + icd_10_code)
        url: str = "/icd/release/10/2016/" + icd_10_code
        http_client = self._connect_http_client()
        http_client.request("GET", url, headers=headers)
        res = http_client.getresponse()
        if res.status == 404:
            return ""
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
        http_client = self._connect_http_client()
        http_client.request("GET", url_with_params, headers=headers)
        res = http_client.getresponse()
        res_json: dict = json.loads(res.read())
        if res_json["destinationEntities"]:
            return res_json["destinationEntities"][0]["theCode"].split("&")[0]
        else:
            return ""

    def icd_10_to_icd_11(self, icd_10_code: str) -> str:
        """Maps ICD-10 code to ICD-11 code via WHO ICD API.

        :param icd_10_code: ICD-10 code
        :type icd_10_code: str
        :return: ICD-11 code
        """
        disease_name: str = self.get_icd_10_name(icd_10_code)
        logging.info("Disease name for ICD-10 code '{}' is '{}'".format(icd_10_code, disease_name))
        if disease_name == "":
            return ""
        icd_11_code: str = self._get_icd_11_code(disease_name)
        logging.info("Mapped ICD-10 code '{}' to ICD-11 code '{}'".format(icd_10_code, icd_11_code))
        return icd_11_code

    def split_icd_10_code(self, icd_10_code: str) -> list:
        """Splits ICD-10 code int category, details and extension fragments.

        :param icd_10_code: ICD-10 code
        :type icd_10_code: str
        :return: split ICD-10 code
        :rtype: list
        """
        icd_10_code = icd_10_code.upper()
        result: list = icd_10_code.split('.')
        while len(result) < 3:
            result.append('')
        return result
