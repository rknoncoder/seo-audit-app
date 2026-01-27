import requests

def fetch_page(url, timeout=10):
    """
    Fetch a webpage and return status code and HTML content
    """
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "SEO-Audit-App/1.0"
            },
            timeout=timeout
        )

        return {
            "url": url,
            "status_code": response.status_code,
            "html": response.text
        }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "status_code": None,
            "html": None,
            "error": str(e)
        }
