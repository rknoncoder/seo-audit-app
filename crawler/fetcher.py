import requests


HEADERS = {"User-Agent": "SEO-Audit-App/1.0"}


def fetch_page(url, timeout=10):
    """
    Fetch a webpage and return the response metadata and HTML content.
    """
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )

        return {
            "url": url,
            "final_url": response.url,
            "status_code": response.status_code,
            "html": response.text,
            "headers": dict(response.headers),
            "redirected": response.url != url,
            "redirect_count": len(response.history),
        }

    except requests.exceptions.RequestException as error:
        return {
            "url": url,
            "final_url": url,
            "status_code": None,
            "html": None,
            "headers": {},
            "redirected": False,
            "redirect_count": 0,
            "error": str(error),
        }
