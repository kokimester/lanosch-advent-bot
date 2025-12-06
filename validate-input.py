import json
import re
import datetime
import sys
from dateutil.parser import parse as parse_date


# --------------------------
# Utility: find line/column
# --------------------------
def get_line_col(text, index):
    line = text.count("\n", 0, index) + 1
    col = index - text.rfind("\n", 0, index)
    return line, col


# --------------------------
# Emoji validation regex
# <:name:id>
# --------------------------
EMOJI_RE = re.compile(r"^<:[a-zA-Z0-9_]+:[0-9]+>$")


# --------------------------
# URL validation
# --------------------------
def is_valid_url(url: str) -> bool:
    return url.startswith("https://")


# --------------------------
# Main validator
# --------------------------
def validate_json_file(json_path):
    errors = []

    with open(json_path, "r", encoding="utf-8") as f:
        raw = f.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error at line {e.lineno}, column {e.colno}: {e.msg}")
        return

    if not isinstance(data, list):
        print("❌ Root element must be a list []")
        return

    # Loop through each day entry
    for idx, day in enumerate(data):
        # ------------- Validate date -------------
        if "date" not in day:
            errors.append(("Missing 'date' field", raw.find("{", 0)))
        else:
            date_str = day["date"]
            try:
                parse_date(date_str)
            except Exception:
                pos = raw.find(date_str)
                errors.append((f"Invalid date format: {date_str}", pos))

        # ------------- Validate intro -------------
        intro = day.get("intro", "")
        if not isinstance(intro, str) or intro.strip() == "":
            pos = raw.find(str(day.get("intro", "")))
            errors.append(("Invalid or empty 'intro' field", pos))

        # ------------- Validate is_posted -------------
        if not isinstance(day.get("is_posted"), bool):
            pos = raw.find(str(day.get("is_posted")))
            errors.append(("'is_posted' must be boolean", pos))

        # ------------- Validate keys -------------
        keys = day.get("keys", [])
        if not isinstance(keys, list):
            pos = raw.find(str(keys))
            errors.append(("'keys' must be a list", pos))
            continue  # cannot process keys

        for gidx, game in enumerate(keys):
            # Emoji
            emoji = game.get("emoji", "")
            if not isinstance(emoji, str) or not EMOJI_RE.match(emoji):
                pos = raw.find(emoji)
                errors.append((f"Invalid emoji format: {emoji}", pos))

            # Name
            name = game.get("name", "")
            if not isinstance(name, str) or name.strip() == "":
                pos = raw.find(str(name))
                errors.append(("Invalid or empty 'name' field", pos))

            # Vendor
            vendor = game.get("vendor", "")
            if not isinstance(vendor, str) or vendor.strip() == "":
                pos = raw.find(str(vendor))
                errors.append(("Invalid or empty 'vendor' field", pos))

            # Link
            link = game.get("link", "")
            if link != "" and not is_valid_url(link):
                pos = raw.find(str(link))
                errors.append((f"Invalid link (must be https:// or empty): {link}", pos))

            # Key / Person rules:
            key = game.get("key", "")
            person = game.get("person", "")

            if key == "" and person == "":
                # Both empty => NOT allowed
                pos = raw.find(str(game))
                errors.append(("Both 'key' and 'person' are empty. One must be provided.", pos))

            if key != "" and not isinstance(key, str):
                pos = raw.find(str(key))
                errors.append(("'key' must be text", pos))

            if person != "" and not isinstance(person, str):
                pos = raw.find(str(person))
                errors.append(("'person' must be text", pos))

            if key == "" and person != "":
                # OK: person gives the contact
                pass

            if key != "" and person != "":
                # OK: both filled (not forbidden)
                pass

    # -------------------------
    # Print error report
    # -------------------------
    if not errors:
        print("✅ JSON file is valid!")
        return

    print("\n❌ ERRORS FOUND:\n")
    for message, index in errors:
        line, col = get_line_col(raw, index)
        print(f"- {message}  (line {line}, col {col})")

    print(f"\nTotal errors: {len(errors)}")


# --------------------------
# Entry point
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <file.json>")
        sys.exit(1)

    validate_json_file(sys.argv[1])

