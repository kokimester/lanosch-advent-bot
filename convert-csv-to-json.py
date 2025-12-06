import csv
from collections import defaultdict
from datetime import datetime
import json
import sys


def load_giveaways_from_csv(path: str):
    grouped = defaultdict(lambda: {"intro": "", "is_posted": False, "keys": []})

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row["date"].strip()
            if not date_str:
                continue  # skip empty lines

            # Initialize per-date metadata once; later rows can override if needed
            if not grouped[date_str]["intro"]:
                grouped[date_str]["intro"] = row.get("intro", "")
            # Parse is_posted as bool from string
            is_posted_str = (row.get("is_posted") or "").strip()
            grouped[date_str]["is_posted"] = is_posted_str.lower() == "true"

            key_entry = {
                "emoji": row.get("emoji", ""),
                "name": row.get("name", ""),
                "vendor": row.get("vendor", ""),
                "link": row.get("link", ""),
                "key": row.get("key", ""),
                "person": row.get("person", ""),
            }
            grouped[date_str]["keys"].append(key_entry)

    # Build final list, sorted by datetime
    result = []
    for date_str, info in grouped.items():
        # dt = datetime.fromisoformat(date_str)
        result.append(
            {
                "date": date_str,
                "intro": info["intro"],
                "is_posted": info["is_posted"],
                "keys": info["keys"],
            }
        )

    # sort by actual datetime
    result.sort(key=lambda x: x["date"])
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <file.json>")
        sys.exit(1)
    data = load_giveaways_from_csv(sys.argv[1])

    # This prints a Python literal like in your example:
    output_file_name = "bot_input_converted.json"
    print(f"Saving output to: {output_file_name}")
    with open(output_file_name, "w", encoding="utf-8") as out:
        json.dump(
            data,
            out,
            ensure_ascii=False,
            indent=2
        )
