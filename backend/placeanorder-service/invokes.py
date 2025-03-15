import requests

def invoke_http(url, method='GET', json=None):
    """
    Makes an HTTP request to a given URL using the specified method.
    
    :param url: The target URL.
    :param method: The HTTP method (GET, POST, PUT, DELETE).
    :param json: (Optional) JSON payload for POST/PUT requests.
    
    :return: A dictionary containing the response code and data.
    """
    try:
        headers = {'Content-Type': 'application/json'}

        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=json, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=json, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return {"code": 400, "message": f"Unsupported HTTP method: {method}"}

        return {
            "code": response.status_code,
            "data": response.json() if response.content else {}
        }

    except requests.exceptions.RequestException as e:
        return {
            "code": 500,
            "message": f"Error invoking {url}: {str(e)}"
        }
