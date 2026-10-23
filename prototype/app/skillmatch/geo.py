"""Geography: postcode handling, geocoding with postcodes.io, offline fallbacks, distance.

- Jobs are geocoded from the advert's postcode (postcodes.io /postcodes, which returns a region)
  or its place name (data/town_coords.csv first, then postcodes.io /places, which also returns
  a region). Area names like "Warwickshire" or "West Midlands (Region)" are placed at a
  representative town and flagged approximate.
- A user's home is placed from the OUTWARD CODE ONLY ("B91"), never the full postcode:
  data/outcode_coords.csv first, then postcodes.io /outcodes.
- Distance is straight-line (haversine), in miles.
"""

from __future__ import annotations

import csv
import logging
import math
import re
from dataclasses import dataclass
from functools import lru_cache

from skillmatch import config

log = logging.getLogger(__name__)

API = "https://api.postcodes.io"
WEST_MIDLANDS = "West Midlands"
EARTH_RADIUS_MILES = 3958.8

# UK postcode: outward code (area + district) and optional inward code.
OUTWARD = r"[A-Z]{1,2}\d[A-Z\d]?"
INWARD = r"\d[A-Z]{2}"
FULL_RE = re.compile(rf"^({OUTWARD})\s*({INWARD})$")
OUTWARD_RE = re.compile(rf"^({OUTWARD})$")
POSTCODE_IN_TEXT = re.compile(rf"\b({OUTWARD})\s?({INWARD})\b")

REMOTE_LOCATIONS = re.compile(
    r"^(uk[- ]?remote|remote(\s*\(uk\))?|united kingdom|uk|home[- ]based|nationwide|"
    r"anywhere in the uk|work from home|england)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Place:
    lat: float
    lon: float
    region: str | None
    county: str | None
    method: str  # postcode | town_table | places_api | outcode_table | outcodes_api
    approximate: bool = False


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle (straight-line) distance in miles."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def normalise_postcode(text: str | None) -> str | None:
    """'b913qs' -> 'B91 3QS'; anything that isn't a full postcode -> None."""
    if not isinstance(text, str):
        return None
    m = FULL_RE.match(re.sub(r"\s+", "", text.upper()))
    return f"{m.group(1)} {m.group(2)}" if m else None


def outward_code(text: str | None) -> str | None:
    """The outward code from a full postcode or an outward code alone; None if invalid.

    This is the only part of a user's postcode that is ever sent anywhere.
    """
    raw = text.strip().upper() if isinstance(text, str) else ""
    full = normalise_postcode(raw)
    if full:
        return full.split()[0]
    m = OUTWARD_RE.match(raw.replace(" ", ""))
    return m.group(1) if m else None


def is_remote_location(text: str | None) -> bool:
    return isinstance(text, str) and bool(REMOTE_LOCATIONS.match(text.strip()))


SUFFIXES = re.compile(r",?\s*\b(West Midlands|England|United Kingdom|UK|GB)\s*$", re.I)


def _clean_place_name(text: str) -> str:
    """'Solihull, England, United Kingdom' -> 'Solihull'; 'Birmingham (Hybrid)' -> 'Birmingham'."""
    t = re.sub(r"\s+", " ", text).strip()
    t = re.sub(r"\s*\((hybrid|remote|on-?site|office based)\)\s*$", "", t, flags=re.I)
    while True:
        shorter = SUFFIXES.sub("", t).strip(" ,")
        if shorter == t or not shorter:
            break
        t = shorter
    return t or text.strip()


@lru_cache(maxsize=1)
def town_table() -> dict[str, Place]:
    path = config.DATA_DIR / "town_coords.csv"
    out: dict[str, Place] = {}
    if path.exists():
        with path.open() as f:
            for r in csv.DictReader(f):
                out[r["name"].lower()] = Place(
                    float(r["lat"]),
                    float(r["lon"]),
                    r["region"] or None,
                    r["county"] or None,
                    "town_table",
                    r["approximate"] == "true",
                )
    return out


@lru_cache(maxsize=1)
def outcode_table() -> dict[str, Place]:
    path = config.DATA_DIR / "outcode_coords.csv"
    out: dict[str, Place] = {}
    if path.exists():
        with path.open() as f:
            for r in csv.DictReader(f):
                out[r["outcode"].upper()] = Place(
                    float(r["lat"]), float(r["lon"]), None, r["district"] or None, "outcode_table"
                )
    return out


class Geocoder:
    """Geocode advert locations and user outward codes, caching every answer.

    `client` is a PoliteClient (or None to stay offline). `cache` maps a lookup key to a Place
    or None and becomes the ETL's `places` table.
    """

    def __init__(self, client=None, offline: bool = False):
        self.client = None if offline else client
        self.cache: dict[str, Place | None] = {}
        self.failures: list[str] = []

    # ----- jobs -----

    def locate_job(self, location_text: str | None, postcode: str | None = None) -> Place | None:
        location_text = location_text if isinstance(location_text, str) else None
        pc = normalise_postcode(postcode) or self._postcode_in(location_text)
        if pc:
            place = self._postcode(pc)
            if place:
                return place
        if location_text:
            place = self._place_name(location_text)
            if place:
                return place
        self.failures.append(location_text or postcode or "")
        return None

    def _postcode_in(self, text: str | None) -> str | None:
        m = POSTCODE_IN_TEXT.search((text or "").upper())
        return f"{m.group(1)} {m.group(2)}" if m else None

    def _postcode(self, pc: str) -> Place | None:
        key = f"postcode:{pc}"
        if key in self.cache:
            return self.cache[key]
        place = None
        if self.client:
            try:
                r = self.client.get(f"{API}/postcodes/{pc.replace(' ', '')}").get("result") or {}
                if r.get("latitude") is not None:
                    place = Place(
                        r["latitude"],
                        r["longitude"],
                        r.get("region"),
                        r.get("admin_county") or r.get("admin_district"),
                        "postcode",
                    )
            except Exception as exc:  # network failure or 404: fall back below
                log.info("postcode lookup failed for %s: %s", pc, type(exc).__name__)
        if place is None:
            fallback = outcode_table().get(pc.split()[0])
            if fallback:
                place = Place(
                    fallback.lat,
                    fallback.lon,
                    region_for_district(fallback.county),
                    fallback.county,
                    "outcode_table",
                    approximate=True,
                )
        self.cache[key] = place
        return place

    def _place_name(self, text: str) -> Place | None:
        name = _clean_place_name(text)
        key = f"place:{name.lower()}"
        if key in self.cache:
            return self.cache[key]
        place = town_table().get(name.lower())
        if place is None and "," in name:
            # "Brierley Hill, Dudley" -> try each part against the offline table.
            for part in (p.strip() for p in name.split(",")):
                place = town_table().get(part.lower())
                if place:
                    break
        if place is None and self.client:
            place = self._places_api(name)
        self.cache[key] = place
        return place

    def _places_api(self, name: str) -> Place | None:
        try:
            body = self.client.get(f"{API}/places", params={"q": name, "limit": 10})
        except Exception as exc:
            log.info("place lookup failed for %r: %s", name, type(exc).__name__)
            return None
        hits = body.get("result") or []
        exact = [p for p in hits if p.get("name_1", "").lower() == name.lower()]
        settlements = [
            p
            for p in (exact or hits)
            if p.get("local_type")
            in ("City", "Town", "Village", "Suburban Area", "Other Settlement")
        ]
        if not settlements:
            return None
        # Several places share a name (Dudley is also in North Tyneside): prefer ours.
        in_region = [p for p in settlements if p.get("region") == WEST_MIDLANDS]
        p = (in_region or settlements)[0]
        region = p.get("region")
        if not region:
            region = self._reverse_region(p["longitude"], p["latitude"])
        return Place(
            p["latitude"],
            p["longitude"],
            region,
            p.get("county_unitary") or p.get("district_borough"),
            "places_api",
        )

    def _reverse_region(self, lon: float, lat: float) -> str | None:
        try:
            body = self.client.get(f"{API}/postcodes", params={"lon": lon, "lat": lat, "limit": 1})
            hits = body.get("result") or []
            return hits[0].get("region") if hits else None
        except Exception:
            return None

    # ----- users -----

    def locate_outcode(self, code: str) -> Place | None:
        """Place a user's home from the outward code only."""
        oc = outward_code(code)
        if not oc:
            return None
        key = f"outcode:{oc}"
        if key in self.cache:
            return self.cache[key]
        place = outcode_table().get(oc)
        if place is None and self.client:
            try:
                r = self.client.get(f"{API}/outcodes/{oc}").get("result") or {}
                if r.get("latitude") is not None:
                    place = Place(r["latitude"], r["longitude"], None, None, "outcodes_api")
            except Exception as exc:
                log.info("outcode lookup failed for %s: %s", oc, type(exc).__name__)
        self.cache[key] = place
        return place


# Local authorities in the West Midlands region (ONS), for the offline postcode fallback.
WM_DISTRICTS = {
    "birmingham", "coventry", "dudley", "sandwell", "solihull", "walsall", "wolverhampton",
    "herefordshire, county of", "herefordshire", "shropshire", "telford and wrekin",
    "stoke-on-trent", "cannock chase", "east staffordshire", "lichfield",
    "newcastle-under-lyme", "south staffordshire", "stafford", "staffordshire moorlands",
    "tamworth", "north warwickshire", "nuneaton and bedworth", "rugby", "stratford-on-avon",
    "warwick", "bromsgrove", "malvern hills", "redditch", "worcester", "wychavon", "wyre forest",
}  # fmt: skip


def region_for_district(districts: str | None) -> str | None:
    """'Solihull' -> 'West Midlands'; None when unknown or outside the region."""
    if not districts:
        return None
    names = [d.strip().lower() for d in districts.split(";")]
    return WEST_MIDLANDS if any(n in WM_DISTRICTS for n in names) else None


# Postcode areas wholly outside the West Midlands region (used only to skip work early; areas
# that straddle the boundary, like DE (Burton upon Trent) and SY (Shropshire and Powys), are not
# listed and get a full lookup instead).
NON_WM_AREAS = {
    "GL", "LE", "NN", "OX", "CW", "SK", "NG", "BS", "CH", "LL", "NP", "SA", "MK", "HP", "LU",
    "PE", "S", "M", "L", "WA", "BB", "BL", "OL", "SN", "BA", "RG", "CB", "IP", "NR", "LN",
}  # fmt: skip


def postcode_outside_region(postcode: str | None) -> bool:
    pc = normalise_postcode(postcode)
    if not pc:
        return False
    area = re.match(r"[A-Z]+", pc).group(0)
    return area in NON_WM_AREAS
