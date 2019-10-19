def add_http_parameters(url: str, params: dict) -> str:
    result: str = url + '?'
    params_added: int = 0
    for param in params:
        result += param + '=' + params[param]
        if params_added < len(params) - 1:
            result += '&'
        params_added += 1
    return result
