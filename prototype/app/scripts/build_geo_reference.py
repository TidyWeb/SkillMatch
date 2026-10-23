"""Build the offline geography fallbacks from postcodes.io (run once; outputs are committed).

- data/town_coords.csv: the towns SkillMatch covers, plus county and region names adverts use,
  with coordinates, region and county, from postcodes.io /places.
- data/outcode_coords.csv: centroids for every outward code in the West Midlands postcode
  areas, from postcodes.io /outcodes, so a user's home can be placed without the network.

Data: ONS Postcode Directory and OS Open Names via postcodes.io (Open Government Licence;
contains OS data © Crown copyright and database right; contains Royal Mail data © Royal Mail
copyright and database right; source: Office for National Statistics).

Usage: uv run python scripts/build_geo_reference.py
"""

import csv

from skillmatch import config
from skillmatch.sources.http import PoliteClient

API = "https://api.postcodes.io"
TOWNS = [
    "Birmingham",
    "Solihull",
    "Coventry",
    "Wolverhampton",
    "Dudley",
    "Walsall",
    "West Bromwich",
    "Sutton Coldfield",
    "Worcester",
    "Redditch",
    "Bromsgrove",
    "Kidderminster",
    "Droitwich Spa",
    "Telford",
    "Shrewsbury",
    "Stafford",
    "Lichfield",
    "Tamworth",
    "Cannock",
    "Warwick",
    "Royal Leamington Spa",
    "Nuneaton",
    "Rugby",
    "Stratford-upon-Avon",
    "Hereford",
    "Stoke-on-Trent",
    "Oldbury",
    "Smethwick",
    "Halesowen",
    "Brierley Hill",
    "Stourbridge",
    "Kingswinford",
    "Aldridge",
    "Kenilworth",
    "Atherstone",
    "Malvern",
    "Evesham",
    "Leominster",
    "Ludlow",
    "Oswestry",
    "Newcastle-under-Lyme",
    "Burton upon Trent",
    "Stone",
    "Bedworth",
    "Wellington",
    "Bridgnorth",
    "Ellesmere",
    "Coleshill",
    "Chelmsley Wood",
    "Gaydon",
    "Cheltenham",
    "Gloucester",
    "Leicester",
    "Lutterworth",
    "Derby",
    "Crewe",
    "Macclesfield",
]
# Names adverts use for the town, mapped to the /places name above.
ALIASES = {
    "Droitwich": "Droitwich Spa",
    "Leamington Spa": "Royal Leamington Spa",
    "Leamington": "Royal Leamington Spa",
    "Burton-on-Trent": "Burton upon Trent",
    "Royal Sutton Coldfield": "Sutton Coldfield",
}
# Area-level names: placed at the named place below and flagged approximate.
AREAS = {
    "West Midlands": ("Birmingham", "West Midlands"),
    "West Midlands (Region)": ("Birmingham", "West Midlands"),
    "Warwickshire": ("Warwick", "West Midlands"),
    "Staffordshire": ("Stafford", "West Midlands"),
    "Worcestershire": ("Worcester", "West Midlands"),
    "Shropshire": ("Shrewsbury", "West Midlands"),
    "Herefordshire": ("Hereford", "West Midlands"),
    "Gloucestershire": ("Gloucester", "South West"),
    "Derbyshire": ("Derby", "East Midlands"),
    "Cheshire": ("Crewe", "North West"),
}
OUTCODE_AREAS = {
    "B": 99,
    "CV": 47,
    "WV": 16,
    "WS": 15,
    "DY": 14,
    "WR": 15,
    "ST": 21,
    "TF": 13,
    "SY": 25,
    "HR": 9,
}


def main() -> None:
    client = PoliteClient(min_interval=0.4, max_requests=800, cache_ttl_hours=24 * 30)
    rows = {}
    for town in TOWNS:
        body = client.get(f"{API}/places", params={"q": town, "limit": 10})
        hits = [
            p
            for p in (body.get("result") or [])
            if p["local_type"] in ("City", "Town", "Village", "Suburban Area", "Other Settlement")
        ]
        exact = [p for p in hits if p["name_1"].lower() == town.lower()] or hits
        if not exact:
            print("no place for", town)
            continue
        # Several places share a name (Dudley is also in North Tyneside): prefer ours.
        in_region = [p for p in exact if p.get("region") == "West Midlands"]
        p = (in_region or exact)[0]
        rows[town] = {
            "name": town,
            "lat": round(p["latitude"], 5),
            "lon": round(p["longitude"], 5),
            "region": p.get("region") or "",
            "county": p.get("county_unitary") or p.get("district_borough") or "",
            "approximate": "false",
        }
    for alias, target in ALIASES.items():
        if target in rows:
            rows[alias] = {**rows[target], "name": alias}
    for area, (anchor, region) in AREAS.items():
        if anchor in rows:
            rows[area] = {**rows[anchor], "name": area, "region": region, "approximate": "true"}
    path = config.DATA_DIR / "town_coords.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, ["name", "lat", "lon", "region", "county", "approximate"])
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: r["name"]))
    print(f"wrote {len(rows)} places to {path}")

    out = []
    for area, top in OUTCODE_AREAS.items():
        for n in range(1, top + 1):
            code = f"{area}{n}"
            try:
                body = client.get(f"{API}/outcodes/{code}")
            except Exception:
                continue  # 404: this outward code doesn't exist
            r = body.get("result") or {}
            if r.get("latitude"):
                out.append(
                    {
                        "outcode": code,
                        "lat": round(r["latitude"], 5),
                        "lon": round(r["longitude"], 5),
                        "district": "; ".join(r.get("admin_district") or []),
                    }
                )
    path = config.DATA_DIR / "outcode_coords.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, ["outcode", "lat", "lon", "district"])
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} outward codes to {path} ({client.requests_made} requests)")


if __name__ == "__main__":
    main()
