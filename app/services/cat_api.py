import requests

CAT_API_URL = "https://api.thecatapi.com/v1/images/search"

def fetch_gallery_images(breed_id: str, limit: int = 12) -> list[str]:
    try:
        r = requests.get(
            CAT_API_URL,
            params={"breed_ids": breed_id, "limit": limit},
            timeout=5
        )
        r.raise_for_status()
        return [img["url"] for img in r.json() if "url" in img]
    except requests.RequestException:
        return []