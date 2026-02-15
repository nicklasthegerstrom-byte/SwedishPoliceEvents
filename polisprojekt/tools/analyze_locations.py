from collections import Counter
import re

from data.api_fetch import fetch_events  # anpassa importväg
# eller: from data.api_fetch import fetch_events (beroende på hur du kör)

def last_part_from_name(name: str | None) -> str | None:
    if not name:
        return None
    parts = [p.strip() for p in name.split(",") if p.strip()]
    return parts[-1] if parts else None

def slug_last_from_url(url: str | None) -> str | None:
    if not url:
        return None
    # tar sista segmentet utan trailing slash
    seg = url.strip("/").split("/")[-1]
    return seg.lower()

def looks_like_place(s: str | None) -> bool:
    if not s:
        return False
    # superenkel heuristik: inga siffror, minst 2 bokstäver
    if any(ch.isdigit() for ch in s):
        return False
    return len(s) >= 2

events = fetch_events()
if events is None:
    print("Fetch failed")
    raise SystemExit(1)

counts = Counter()
examples_weird = []

for e in events:
    name = e.get("name")
    url = e.get("url")
    loc = e.get("location") or {}
    county = loc.get("name")

    last_name = last_part_from_name(name)
    slug = slug_last_from_url(url)

    counts["total"] += 1
    if county:
        counts["has_location_name"] += 1

    if name and "," in name:
        counts["name_has_comma"] += 1

    if last_name:
        counts["has_last_part"] += 1
        if looks_like_place(last_name):
            counts["last_part_looks_like_place"] += 1
        else:
            counts["last_part_not_placey"] += 1
            if len(examples_weird) < 10:
                examples_weird.append((name, county, url))

    # jämför med slug grovt (inte perfekt, men ger signal)
    if last_name and slug:
        # normalisera last_name till slug-lik form
        norm = re.sub(r"[^a-zåäö]", "", last_name.lower())
        if norm and norm in slug:
            counts["last_part_matches_slug"] += 1

print("\n--- Stats ---")
for k, v in counts.items():
    print(f"{k}: {v}")

print("\n--- Weird examples (up to 10) ---")
for name, county, url in examples_weird:
    print("\nNAME:", name)
    print("COUNTY:", county)
    print("URL:", url)