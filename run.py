from crawler.fetcher import fetch_page
from crawler.parser import parse_basic_seo

if __name__ == "__main__":
    url = "https://togrowmarketing.com"

    page = fetch_page(url)

    if page.get("html"):
        seo_data = parse_basic_seo(page["html"])

        print("URL:", page["url"])
        print("Status Code:", page["status_code"])
        print("Title:", seo_data["title"])
        print("Meta Description:", seo_data["meta_description"])
        print("H1:", seo_data["h1"])
    else:
        print("Error:", page.get("error"))
