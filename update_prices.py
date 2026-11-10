"""
Daily price updater for Solar Hisaab.
Reads sources.json, collects prices politely (respects robots.txt, waits between requests),
keeps a source link + date for every price, rejects suspicious jumps, and writes prices.json
that index.html loads automatically. Also keeps price history in history.json.
"""
import json, re, time, statistics, datetime, urllib.robotparser, urllib.parse
import requests
from bs4 import BeautifulSoup

UA = "SolarHisaabBot/1.0 (price reference with source link)"
MAX_JUMP = 0.15          # hold back any price that moves more than 15% in one day
DEFAULT_PRICE = r"Rs\.?\s*([\d,]{4,})"   # e.g. "Rs. 276,000/-"
TODAY = datetime.date.today().strftime("%-d %B %Y")

def allowed(url, cache={}):
    root = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
    if root not in cache:
        rp = urllib.robotparser.RobotFileParser(root + "/robots.txt")
        try: rp.read()
        except Exception: rp = None
        cache[root] = rp
    rp = cache[root]
    return True if rp is None else rp.can_fetch(UA, url)

def page_text(url, cache={}):
    if url not in cache:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # turn table cells into "a | b | c" so patterns can read rows
        for td in soup.find_all(["td", "th"]): td.append(" | ")
        cache[url] = re.sub(r"\s+", " ", soup.get_text(" "))
        time.sleep(3)
    return cache[url]

def number(s): return float(s.replace(",", ""))

def main():
    sources = json.load(open("sources.json"))["sources"]
    try: old = {r["item"]: r for r in json.load(open("prices.json")).get("rows", [])}
    except Exception: old = {}
    try: history = json.load(open("history.json"))
    except Exception: history = {}

    rows, buckets, log = [], {}, []
    for s in sources:
        prev = old.get(s["item"])
        try:
            if not allowed(s["url"]): raise RuntimeError("blocked by robots.txt")
            m = re.search(s.get("pattern", DEFAULT_PRICE), page_text(s["url"]), re.I)
            if not m: raise RuntimeError("price not found (page layout may have changed)")
            val = number(m.group(1))
            if prev and prev.get("value"):
                if abs(val - prev["value"]) / prev["value"] > MAX_JUMP:
                    raise RuntimeError(f"jump {prev['value']} -> {val}, held for manual check")
            date = TODAY
        except Exception as e:
            log.append(f"{s['item']}: {e}")
            if not prev: continue
            val, date = prev["value"], prev["date"]
        price = f"Rs {val:.2f} per watt" if s["kind"] == "panel_ppw" else f"Rs {val:,.0f}"
        rows.append({"item": s["item"], "price": price, "value": val, "src": s["src"], "url": s["url"], "date": date, "kind": s["kind"]})
        buckets.setdefault(s["kind"], []).append(val)
        history.setdefault(s["item"], {})[datetime.date.today().isoformat()] = val

    med = lambda k, d: round(statistics.median(buckets[k]), 2) if buckets.get(k) else d
    inv6 = med("inverter_6", 230000); inv10 = med("inverter_10", 310000)
    data = {
        "updated": TODAY,
        "panelPerWatt": med("panel_ppw", 42.5),
        "panelWatt": 585,
        # 6kW and 10kW come from live prices; other sizes are scaled from them
        "inverters": {"3": round(inv6*0.65,-3), "4": round(inv6*0.76,-3), "6": inv6, "8": round((inv6+inv10)/2,-3),
                      "10": inv10, "12": round(inv10*1.3,-3), "15": round(inv10*1.6,-3)},
        "battery": {"name": "48V 100Ah lithium (about 5 kWh)", "kwh": 5.12, "price": med("battery_5kwh", 235000)},
        "exportRate": 11,
        "rows": rows,
    }
    json.dump(data, open("prices.json", "w"), indent=1)
    json.dump(history, open("history.json", "w"), indent=1)
    print(f"Updated {len(rows)} prices.")
    for line in log: print("CHECK:", line)

if __name__ == "__main__":
    main()
