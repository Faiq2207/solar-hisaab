"""
Builds the guide pages for Solar Hisaab from prices.json, every day after prices update.
Also writes sitemap.xml and adds a "Solar guides" link block to index.html.
"""
import json, math, datetime, html

SITE = "https://faiq2207.github.io/solar-hisaab/"
P = json.load(open("prices.json"))
PPW, PW = float(P["panelPerWatt"]), int(P.get("panelWatt", 585))
INV = {int(k): float(v) for k, v in P["inverters"].items()}
BAT = float(P["battery"]["price"])
INSTALL_PER_KW = 20000
SUN, EFF = 5, 0.78
TODAY = P.get("updated", datetime.date.today().strftime("%-d %B %Y"))
MONTH = datetime.date.today().strftime("%B %Y")

def rs(n): return "Rs " + f"{round(n):,}"
def inv_for(kw): return min([s for s in INV if s >= kw] or [max(INV)])
def panels_for(kw): return math.ceil(kw * 1000 / PW)

CSS = """
:root{--bg:#F5F7FA;--surface:#fff;--ink:#13233A;--muted:#5A6B82;--line:#D7DFEA;--panel:#1D4E89;--soft:#E6EEF8;--sun:#F2B000;color-scheme:light;
box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root{--bg:#0D1520;--surface:#142030;--ink:#E7EDF5;--muted:#93A4BA;--line:#25364C;--panel:#6AA5EA;--soft:#1A2C44;--sun:#FFC53D;color-scheme:dark}}
*,*::before,*::after{box-sizing:inherit}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Sora",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.65}
.wrap{max-width:760px;margin:0 auto;padding:24px 20px 60px}
a{color:var(--panel)} .top{font-weight:700;text-decoration:none;color:var(--ink)}
h1{font-size:clamp(1.6rem,4vw,2.2rem);line-height:1.2;letter-spacing:-.02em;margin:20px 0 8px}
h2{font-size:1.25rem;margin:32px 0 8px}
.upd{display:inline-block;background:var(--soft);color:var(--panel);border-radius:999px;padding:3px 12px;font-size:.82rem;font-weight:600}
.lede{color:var(--muted)}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--surface);margin:12px 0}
table{border-collapse:collapse;width:100%;min-width:480px;font-size:.92rem}
th,td{text-align:left;padding:10px 14px;border-top:1px solid var(--line)} thead th{border-top:0;background:var(--soft);color:var(--muted);font-weight:500}
td.n{font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap}
.cta{display:block;background:var(--panel);color:#fff;text-decoration:none;border-radius:14px;padding:18px 20px;margin:28px 0;font-weight:600}
@media (prefers-color-scheme:dark){.cta{color:#0D1520}}
.cta span{display:block;font-weight:400;opacity:.85;font-size:.9rem}
details{border-top:1px solid var(--line);padding:12px 0} summary{cursor:pointer;font-weight:600} details p{color:var(--muted);margin:8px 0 0}
.more{display:grid;gap:8px;margin:12px 0;padding:0;list-style:none}
footer{color:var(--muted);font-size:.82rem;border-top:1px solid var(--line);margin-top:36px;padding-top:16px}
:focus-visible{outline:2px solid var(--sun);outline-offset:2px}
"""

def page(slug, title, desc, h1, body, faqs):
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    faq_html = "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in faqs)
    links = "".join(f'<li><a href="{s}.html">{html.escape(t)}</a></li>' for s, t in GUIDES if s != slug)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}{slug}.html">
<link rel="manifest" href="manifest.json"><meta name="theme-color" content="#1D4E89">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
<style>{CSS}</style></head>
<body><div class="wrap">
<a class="top" href="./">Solar Hisaab</a>
<h1>{h1}</h1>
<span class="upd">Prices updated {TODAY}</span>
{body}
<a class="cta" href="./">Calculate your own system<span>Add your AC, fridge, fans and motor to get your exact size and price.</span></a>
<h2>Common questions</h2>{faq_html}
<h2>More solar guides</h2><ul class="more">{links}</ul>
<footer>Estimates only, not a quote. Prices come from Pakistani sellers listed on the <a href="./#prices">price page</a> and change with the dollar rate. Structure, wiring and labour estimated at {rs(INSTALL_PER_KW)} per kW.</footer>
</div></body></html>"""

def system_page(kw):
    n = panels_for(kw); akw = n * PW / 1000; inv = inv_for(kw)
    cp, ci, cl = n * PW * PPW, INV[inv], akw * INSTALL_PER_KW
    base = cp + ci + cl
    units = akw * SUN * EFF
    rows = "".join(
        f"<tr><td>{lbl}</td><td class='n'>{rs(base + b * BAT)}</td></tr>"
        for lbl, b in [("Without batteries (daytime only)", 0), ("With 1 lithium battery (about 5 kWh)", 1),
                       ("With 2 lithium batteries (about 10 kWh)", 2)])
    loads = {3: "fans, lights, a fridge, TV and a small water motor during the day, or one 1 ton inverter AC for a few hours",
             5: "a 1.5 ton inverter AC for most of the day plus fans, lights, fridge and a water motor",
             10: "two 1.5 ton inverter ACs plus all normal home appliances, a good fit for a 10 marla or 1 kanal house"}[kw]
    body = f"""
<p class="lede">A {kw}kW solar system in Pakistan costs about <strong>{rs(base)}</strong> without batteries at today’s prices. Here’s the full breakdown.</p>
<h2>{kw}kW system cost breakdown</h2>
<div class="tw"><table><thead><tr><th>Part</th><th>Price</th></tr></thead><tbody>
<tr><td>{n} solar panels of {PW}W (Rs {PPW:g} per watt)</td><td class="n">{rs(cp)}</td></tr>
<tr><td>{inv}kW hybrid inverter</td><td class="n">{rs(ci)}</td></tr>
<tr><td>Structure, wiring and labour</td><td class="n">{rs(cl)}</td></tr>
<tr><td><strong>Total without batteries</strong></td><td class="n">{rs(base)}</td></tr>
</tbody></table></div>
<h2>{kw}kW price with batteries</h2>
<div class="tw"><table><thead><tr><th>Option</th><th>Total price</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>How much electricity does it make?</h2>
<p>With about 5 hours of strong sun a day in Lahore, {n} panels ({akw:.1f}kW) make roughly <strong>{units:.0f} units a day</strong>, or about {units*30:.0f} units a month. That’s enough to run {loads}.</p>
"""
    faqs = [
        (f"What is the price of a {kw}kW solar system in Pakistan?",
         f"As of {TODAY}, a {kw}kW solar system costs about {rs(base)} without batteries, including {n} panels, a {inv}kW hybrid inverter and installation. Adding one lithium battery brings it to about {rs(base+BAT)}."),
        (f"How many panels are in a {kw}kW solar system?",
         f"You need {n} panels of {PW} watts for a {kw}kW system."),
        (f"How many units does a {kw}kW solar system make?",
         f"About {units:.0f} units a day in Lahore, or {units*30:.0f} units a month, depending on season, dust and panel angle."),
    ]
    return page(f"{kw}kw-solar-system-price-pakistan", f"{kw}kW Solar System Price in Pakistan ({MONTH}) with Batteries",
                f"{kw}kW solar system price in Pakistan today: about {rs(base)} without batteries. See panels, inverter, battery options and units per day.",
                f"{kw}kW solar system price in Pakistan", body, faqs)

def ac_page():
    acs = [("1 ton inverter AC", 750, 8), ("1.5 ton inverter AC", 1000, 8), ("1.5 ton non-inverter AC", 1700, 8), ("2 ton inverter AC", 1350, 8)]
    rows = ""
    for name, w, h in acs:
        u = w * h / 1000; kw = u / (SUN * EFF); n = panels_for(kw)
        rows += f"<tr><td>{name}</td><td class='n'>{u:.0f} units</td><td class='n'>{n} panels</td><td class='n'>{rs(n*PW*PPW)}</td></tr>"
    u15 = 8; n15 = panels_for(u15 / (SUN * EFF))
    body = f"""
<p class="lede">A 1.5 ton inverter AC running 8 hours a day needs about <strong>{n15} solar panels of {PW}W</strong> on its own. Here’s the number for every common AC.</p>
<h2>Panels needed for each AC (8 hours a day)</h2>
<div class="tw"><table><thead><tr><th>AC type</th><th>Units per day</th><th>Panels needed</th><th>Panel cost</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>This counts the AC only. Your fans, lights, fridge and motor need extra panels, so add them in the calculator for your real total.</p>
<h2>Running an AC at night</h2>
<p>Panels only make power in daylight. To run a 1.5 ton inverter AC for 4 hours at night you need about 4 units of battery storage, which is roughly one 48V 100Ah lithium battery ({rs(BAT)}) plus a hybrid inverter.</p>
<h2>Inverter AC or non-inverter on solar?</h2>
<p>An inverter AC uses about 40% less power once the room is cool, so it needs fewer panels and a smaller inverter. If you’re buying a new AC for a solar home, an inverter AC almost always pays for itself.</p>
"""
    faqs = [
        ("How many solar panels do I need for a 1.5 ton inverter AC?",
         f"About {n15} panels of {PW}W to run a 1.5 ton inverter AC for 8 hours a day, not counting your other appliances."),
        ("Can I run an AC on solar without batteries?",
         "Yes, during the day. With a hybrid or on-grid inverter, the AC runs on solar while the sun is up and switches to the grid or batteries after sunset."),
        ("What size inverter do I need for a 1.5 ton AC?",
         "A 6kW hybrid inverter is the common choice for a home with one 1.5 ton AC plus normal appliances."),
    ]
    return page("solar-panels-for-1-5-ton-ac", f"How Many Solar Panels for a 1.5 Ton AC in Pakistan? ({MONTH})",
                "How many solar panels you need for a 1 ton, 1.5 ton or 2 ton inverter AC in Pakistan, with units per day and today’s panel cost.",
                "How many solar panels do you need for a 1.5 ton AC?", body, faqs)

def net_billing_page():
    exp = P.get("exportRate", 11)
    sold = 150; rate = 35
    body = f"""
<p class="lede">In February 2026, NEPRA replaced net metering with <strong>net billing</strong> for new solar connections. Here’s what changed and what it means for your savings.</p>
<h2>What changed</h2>
<p>Under the old net metering system, every unit you sent to the grid cancelled out a unit you bought, at the same price. Under the new NEPRA (Prosumer) Regulations 2026, buying and selling have different prices. You still pay the full tariff for units you take from the grid, but extra units you send back are bought at around the national average energy purchase price, about <strong>Rs {exp:g} per unit</strong>. Before, exported units were credited at roughly Rs 22–27.</p>
<h2>Who is affected</h2>
<p>New solar users are on net billing. Net metering applications submitted up to 8 February 2026 are processed under the old rules, and existing net metering contracts stay protected until they expire.</p>
<h2>What it means for your money</h2>
<p>Say your system sends {sold} extra units to the grid in a month. Under net billing that earns about {rs(sold*exp)}. If you used those same units at home instead of buying them at around Rs {rate} each, you’d save about {rs(sold*rate)}. So the new rule rewards using your own solar power: run heavy appliances during the day, size your system to your real use, and consider batteries for the evening.</p>
<h2>Is solar still worth it?</h2>
<p>For most homes, yes, if the system is sized to what you actually use. Units you use yourself save the full bill rate, which is often Rs 30–45 with taxes. The calculator on the home page uses the new export rate in its savings estimate.</p>
<h2>Sources</h2>
<ul class="more">
<li><a href="https://www.thenews.pk/print/1398311-govt-ends-net-metering-shifts-rooftop-solar-to-net-billing" rel="nofollow noopener" target="_blank">The News, 10 Feb 2026: Govt ends net metering, shifts rooftop solar to net billing</a></li>
<li><a href="https://www.thenews.pk/print/1407896-nepra-restores-old-net-metering-for-pre-feb-9-applications" rel="nofollow noopener" target="_blank">The News: NEPRA restores old net metering for pre-Feb 9 applications</a></li>
<li><a href="https://www.arabnews.com/node/2655920/pakistan" rel="nofollow noopener" target="_blank">Arab News: Existing net-metering agreements protected until expiry</a></li>
</ul>
"""
    faqs = [
        ("What is net billing in Pakistan?",
         f"Net billing is the system NEPRA introduced in February 2026. You pay the normal tariff for grid units and get about Rs {exp:g} per unit for extra solar power you export."),
        ("Is net metering finished in Pakistan?",
         "For new users, yes. Applications submitted up to 8 February 2026 follow the old net metering rules, and existing contracts are protected until they expire."),
        ("Is solar still worth it after net billing?",
         "Yes for most homes, as long as you use most of the power yourself, because every unit you don’t buy saves your full bill rate."),
    ]
    return page("net-billing-pakistan-2026", "Net Billing Pakistan 2026: New Solar Rules Explained Simply",
                f"NEPRA’s 2026 net billing rules explained: export rate about Rs {exp:g} per unit, who is affected, and how to still save with solar.",
                "Net billing in Pakistan 2026, explained simply", body, faqs)

GUIDES = [
    ("3kw-solar-system-price-pakistan", "3kW solar system price in Pakistan"),
    ("5kw-solar-system-price-pakistan", "5kW solar system price in Pakistan"),
    ("10kw-solar-system-price-pakistan", "10kW solar system price in Pakistan"),
    ("solar-panels-for-1-5-ton-ac", "How many solar panels for a 1.5 ton AC"),
    ("net-billing-pakistan-2026", "Net billing in Pakistan 2026, explained"),
]

def main():
    out = {"3kw-solar-system-price-pakistan": system_page(3),
           "5kw-solar-system-price-pakistan": system_page(5),
           "10kw-solar-system-price-pakistan": system_page(10),
           "solar-panels-for-1-5-ton-ac": ac_page(),
           "net-billing-pakistan-2026": net_billing_page()}
    for slug, doc in out.items():
        open(f"{slug}.html", "w").write(doc)

    iso = datetime.date.today().isoformat()
    urls = [SITE] + [f"{SITE}{s}.html" for s in out]
    open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"<url><loc>{u}</loc><lastmod>{iso}</lastmod><changefreq>daily</changefreq></url>\n" for u in urls) + "</urlset>\n")

    idx = open("index.html").read()
    block = ('<!--guides--><nav class="faq" aria-label="Solar guides"><h2 style="font-size:1.5rem">Solar guides</h2><ul style="display:grid;gap:8px;padding-left:18px">' +
             "".join(f'<li><a href="{s}.html">{html.escape(t)}</a></li>' for s, t in GUIDES) + "</ul></nav><!--/guides-->")
    if "<!--guides-->" in idx:
        a, b = idx.index("<!--guides-->"), idx.index("<!--/guides-->") + len("<!--/guides-->")
        idx = idx[:a] + block + idx[b:]
    else:
        idx = idx.replace("<footer>", block + "\n  <footer>", 1)
    open("index.html", "w").write(idx)
    print(f"Built {len(out)} guide pages and sitemap.")

if __name__ == "__main__":
    main()
