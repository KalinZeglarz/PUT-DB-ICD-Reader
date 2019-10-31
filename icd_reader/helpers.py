"""Contains helper functions."""


def add_http_parameters(url: str, params: dict) -> str:
    """
    Adds HTTP parameters to url.

    :param url: url address
    :param params: http parameters
    :return: url with added http parameters
    """
    result: str = url + '?'
    params_added: int = 0
    for param in params:
        result += param + '=' + params[param].replace(' ', '%20')
        if params_added < len(params) - 1:
            result += '&'
        params_added += 1
    return result
