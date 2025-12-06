import csv
import requests
import urllib.parse
import time
import sys


STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/"


def find_steam_app_url(game_name: str) -> str | None:
    """
    Uses Steam's public storesearch API to find an app for the given game name.
    Returns the full store URL or None if nothing found.
    """
    params = {
        "term": game_name,
        "cc": "us",
        "l": "en",
    }
    resp = requests.get(STEAM_SEARCH_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items", [])
    if not items:
        return None

    # Try exact (case-insensitive) match on name
    lower_name = game_name.lower().strip()
    exact = None
    for item in items:
        if item.get("name", "").lower().strip() == lower_name:
            exact = item
            break

    app = exact or items[0]
    app_id = app.get("id")
    if not app_id:
        return None

    # We don't strictly need the slug in the URL, just the app id
    return f"https://store.steampowered.com/app/{app_id}/"


def main():
    input_path = "games_input.csv"
    output_path = "games_output.csv"

    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    output_rows = []
    for i, row in enumerate(rows, start=1):
        name = row["name"].strip()
        provider = row["provider"].strip()
        url = ""

        if provider.lower() == "steam":
            try:
                url = find_steam_app_url(name) or ""
                # Be a good citizen: small delay so we don't hammer Steam
                time.sleep(0.3)
            except Exception as e:
                print(f"[WARN] Failed to fetch Steam URL for '{name}': {e}")
                url = ""
        else:
            # For GOG / EPIC, you can either:
            #  - manually fill URLs later, or
            #  - extend this script with provider-specific logic
            url = ""

        output_rows.append(
            {
                "name": name,
                "provider": provider,
                "url": url,
            }
        )
        print(f"[{i}/{len(rows)}] {name} ({provider}) -> {url or 'NOT FOUND'}")

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "provider", "url"])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Done. Wrote {len(output_rows)} rows to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <file.csv>")
        sys.exit(1)
    main()
