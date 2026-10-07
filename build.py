#!/usr/bin/env python3
"""Builds the SLG static site. Edit page content below, then run: python3 build.py
Output is written next to this file (index.html, <page>/index.html, ...)."""
import json, os, textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.theslg.co"
EMAIL = "info@theslg.co"
FORM_ACTION = f"https://formsubmit.co/{EMAIL}"

def img(pid, w=2400):
    return f"https://images.unsplash.com/photo-{pid}?w={w}&q=80&auto=format&fit=crop"

# Real photographs, Unsplash licence (free commercial use). Credits live on /credits/.
PHOTOS = {
    # Large-cabin aircraft only (ultra-long-range / long-range / super-midsize). No light jets, no airline or military liveries.
    "hero":      ("1496176744020-6fa84b9bbf15", "Gulfstream long-range jet in black and white, landing gear down", "Alec Cooks", "lFnt4pDaGrU"),
    "inflight":  ("1657409845150-f31d72aff3a0", "Gulfstream long-range jet on approach under a grey sky", "Chris Leipelt", "72RuhQunZEk"),
    "falcon":    ("1770334618960-d246fc142297", "Dassault Falcon tri-jet on an Alpine apron, snow-covered peaks behind", "David Syphers", "9vX30eYsBdc"),
    "alps":      ("1770334618966-7cd65daa8b90", "Dassault Falcon tri-jet on a snowy Alpine runway beneath the mountains", "Rafael Garcin", "Fz2Dx3k3eTY"),
    "cabin":     ("1768346564210-f382cdf18375", "Cream leather seats in a long-range jet cabin with soft cove lighting", "Andy Wang", "lU1pEjWZzXg"),
    "salon":     ("1768346564233-d71f37bd19b6", "Wide-body private cabin with lounge chairs and a credenza", "Andy Wang", "ogUyaf8JWA4"),
    # Old-money interiors
    "library":   ("1637246662831-353bde8871e8", "Panelled private library with a chandelier and carved staircase", "Daniil Smetanin", "DAE--I2sJQI"),
    "salonroom": ("1716807335144-33e138f1858a", "Gilded drawing room with a marble statue by a tall window", "Hugo Richard", "P-cJjOSRWAI"),
    # Art and sustainability: quiet classical sculpture and stone
    "seated":    ("1760029976977-253e8e11cb48", "Classical marble figure seated in raking sunlight", "Kseniia Zapiatkina", "cl1Tg6L15Gs"),
    "bust":      ("1639310940358-8f4bf57f3add", "Marble bust on a veined stone plinth", "Anna Hunko", "wUzyCxKWJBA"),
    "drapery":   ("1789379205322-056dfda0aea7", "Close study of grey drapery folds", "Niklas König", "XYHGBh2LICk"),
    "columns":   ("1519674921880-e784bc34ebd4", "White marble colonnade in soft daylight", "jacob wall", "J35x4qL0mS0"),
    "sculptroom":("1772225702317-59fad119ea2e", "Sunlit gallery of marble sculpture beside tall windows", "Tatiana Zhukova", "zp4G2VEW03w"),
}

def photo(key, cls="photo", w=2400, eager=False, extra=""):
    pid, alt, *_ = PHOTOS[key]
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<div class="{cls}"{extra}><img src="{img(pid, w)}" '
            f'srcset="{img(pid, 900)} 900w, {img(pid, 1600)} 1600w, {img(pid, 2400)} 2400w" '
            f'sizes="100vw" alt="{alt}" {loading} decoding="async"></div>')

NAV_L = [("/private-register/", "Private Register"), ("/sell/", "Sell"), ("/family-offices/", "Family Offices")]
NAV_R = [("/art/", "Art"), ("/sustainability/", "Sustainability"), ("/enquire/", "Enquire")]

def nav(items, current, cls):
    out = []
    for href, label in items:
        attrs = ' aria-current="page"' if href == current else ""
        if label == "Enquire":
            attrs += ' class="cta"'
        out.append(f'<a href="{href}"{attrs}>{label}</a>')
    return f'<nav class="nav {cls}" aria-label="Primary">{"".join(out)}</nav>'

def header(current):
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
{nav(NAV_L, current, "left")}
<a class="wordmark" href="/" aria-label="SLG, home">SLG</a>
{nav(NAV_R, current, "right")}
</div></header>'''

FOOTER = f'''<footer class="site-footer">
<div class="wrap top">
<div class="brand"><a class="wordmark" href="/">SLG</a>
<p>Private aviation advisory for family offices and their principals. Acquisition, sale, charter, art and sustainability.</p></div>
<nav aria-label="Footer">
<a href="/private-register/">Private Register</a><a href="/art/">Art &amp; Interiors</a>
<a href="/sell/">Sell discreetly</a><a href="/sustainability/">Sustainability &amp; SAF</a>
<a href="/family-offices/">Family offices</a><a href="/charter/">Charter</a>
<a href="/journal/">Journal</a><a href="/enquire/">Enquire</a>
</nav>
<div class="reach"><a class="mail" href="mailto:{EMAIL}">{EMAIL}</a><br>
<a href="https://www.linkedin.com/company/theslgco/" rel="noopener">LinkedIn</a> · <a href="https://www.instagram.com/slg_privatejets/" rel="noopener">Instagram</a></div>
</div>
<div class="wrap legal"><span>© 2026 SLG Global LLC. SLG acts as adviser and broker and does not own or operate aircraft.</span>
<span><a href="/privacy/">Privacy</a> · <a href="/accessibility/">Accessibility</a> · <a href="/credits/">Credits</a></span></div>
</footer>'''

ORG_LD = {
    "@context": "https://schema.org", "@type": "Organization", "name": "SLG", "legalName": "SLG Global LLC",
    "url": SITE + "/", "email": EMAIL, "logo": SITE + "/assets/img/favicon.svg",
    "description": "Private aviation advisory for family offices and UHNW principals: off-market aircraft acquisition and sale, charter, art curation for cabins and sustainability advice.",
    "founder": {"@type": "Person", "name": "Tuğçe Tekin", "url": "https://www.linkedin.com/in/tugce-tekin/"},
    "sameAs": ["https://www.linkedin.com/company/theslgco/", "https://www.instagram.com/slg_privatejets/"],
}

def page(path, title, desc, body, current="", og="hero", ld=None, noindex=False):
    canonical = SITE + path
    ogimg = img(PHOTOS[og][0], 1200) + "&h=630"
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:type" content="website"><meta property="og:site_name" content="SLG">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13241B">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css">
{ld_html}
</head>
<body>
{header(current)}
<main id="main">
{textwrap.dedent(body).strip()}
</main>
{FOOTER}
</body>
</html>
'''
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    if path.endswith(".html"):
        out = os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return path

def hidden(subject):
    return f'''<input type="hidden" name="_subject" value="{subject}">
<input type="hidden" name="_next" value="{SITE}/thank-you/">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_template" value="table">
<input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">'''

def field(label, name, kind="text", full=False, required=False, auto=""):
    req = " required" if required else ""
    ac = f' autocomplete="{auto}"' if auto else ""
    cls = "field full" if full else "field"
    return f'<label class="{cls}">{label}<input type="{kind}" name="{name}"{req}{ac}></label>'

def select(label, name, options, full=False):
    cls = "field full" if full else "field"
    opts = "".join(f"<option>{o}</option>" for o in options)
    return f'<label class="{cls}">{label}<select name="{name}">{opts}</select></label>'

def consent(text):
    return f'<label class="consent full"><input type="checkbox" name="consent" value="yes" required>{text}</label>'

pages = []

# ---------------- HOME ----------------
pages.append(page("/", "SLG | Off-Market Private Jet Advisory for Family Offices",
 "Off-market acquisition and sale of long-range private jets for family offices and UHNW principals. Direct mandates only, with art curation and sustainability advice.",
 f'''
<section class="hero">
{photo("hero", eager=True)}
<div class="wrap">
<p class="label">Private Aviation Advisory</p>
<h1>Aircraft, acquired<br><span class="it">quietly.</span></h1>
<p class="lede">Off-market acquisition and sale of long-range jets for family offices and their principals. Direct mandates only.</p>
<div class="actions"><a class="link" href="/enquire/">Request a private conversation</a><a class="link soft" href="/sell/">Sell discreetly</a></div>
</div>
</section>

<section class="section statement wrap">
<p class="quote">We do not list. We do not broadcast.<br><span class="gold">We introduce.</span></p>
<div class="stem"></div>
<p class="tag">Absolute discretion · Structured referrals · Shared excellence</p>
</section>

<section class="rule-top"><div class="wrap columns">
<article><p class="numeral">I</p><h3>Acquisition &amp; Sale</h3><p>Long-range and ultra-long-range aircraft sourced directly from owners and their mandates. Verified serials, clean title, one point of contact.</p><a class="link" href="/private-register/">The Private Register</a></article>
<article><p class="numeral">II</p><h3>Art &amp; Interiors</h3><p>Collection-grade works curated for the cabin, with artists, interior studios and certified installers. Considered from first inspection.</p><a class="link" href="/art/">Art &amp; Interiors</a></article>
<article><p class="numeral">III</p><h3>Sustainability</h3><p>SAF access, efficiency-led fleet choices and emissions reporting a family office can stand behind.</p><a class="link" href="/sustainability/">Sustainability &amp; SAF</a></article>
</div></section>

<section class="dark"><div class="wrap section two top">
<div>
<p class="label">The Private Register</p>
<h2 class="big mb-24">Available on introduction only.</h2>
<p class="lede measure mb-48">A small number of aircraft are offered privately each season. Specifications are released under NDA to verified principals and their advisers.</p>
<a class="link" href="/private-register/">Request access</a>
</div>
<div class="register-teaser">
<div class="row"><span class="cat">Ultra-long-range</span><span class="meta">2023 · under 700 hours</span></div>
<div class="row"><span class="cat">Long-range</span><span class="meta">2021 · under 1,700 hours</span></div>
<div class="row"><span class="cat">Long-range</span><span class="meta">2016 · connectivity fitted</span></div>
<div class="row"><span class="cat">Super-midsize</span><span class="meta">2015 · Asia</span></div>
</div>
</div></section>

<section class="section wrap">
<p class="label muted">How a transaction proceeds</p>
<ol class="steps">
<li><p class="t">Introduction</p><p>A private conversation with the principal or their office. No public listing, no circulation.</p></li>
<li><p class="t">Confidentiality</p><p>Mutual NDA and a written mandate before any specification is shared.</p></li>
<li><p class="t">Verification</p><p>Serial, title, records and airworthiness confirmed. KYC and sanctions screening on both sides.</p></li>
<li><p class="t">Completion</p><p>LOI, escrow deposit, pre-purchase inspection and closing, coordinated with your counsel.</p></li>
</ol>
</section>

<section class="rule-top"><div class="wrap section two">
{photo("cabin", w=1600)}
<div>
<p class="label">For family offices</p>
<h2 class="big mb-24">One adviser, for the aircraft and everything it carries.</h2>
<p class="lede measure mb-48">For family offices, holdings, private equity and wealth managers acting for principals. We work on mandate only, never through broker chains.</p>
<a class="link" href="/family-offices/">Our approach</a>
</div>
</div></section>

<section class="band-linen"><div class="wrap section tight">
<div class="head-row"><h2 class="big">Journal</h2><a class="link" href="/journal/">All entries</a></div>
JOURNAL_GRID
</div></section>

<section class="section center wrap">
<h2 class="big mb-24">Conversations begin privately.</h2>
<p class="body mb-48">Every enquiry is answered personally, within one business day.</p>
<a class="btn" href="/enquire/">Enquire</a>
</section>
''', current="/", ld=ORG_LD))

# ---------------- JOURNAL (entries are published on LinkedIn) ----------------
ENTRIES = [
    ("inflight", "Market · September 2026", "G600 or Global 6500: reading the demand", "https://www.linkedin.com/feed/update/urn:li:activity:7506387098367832064/"),
    ("columns", "Sustainability · August 2026", "Five SAF developments in Europe this summer", "https://www.linkedin.com/feed/update/urn:li:activity:7490104204959576064/"),
    ("salon", "Interiors", "The psychology of the cabin", "https://www.linkedin.com/feed/update/urn:li:activity:7467814737389645824/"),
]
def journal_grid():
    cards = []
    for key, kicker, title, url in ENTRIES:
        cards.append(f'<a class="entry" href="{url}" rel="noopener">{photo(key, w=900)}<p class="kicker">{kicker}</p><p class="title">{title}</p></a>')
    return '<div class="journal-grid">' + "".join(cards) + "</div>"

# patch the home page grid in place
home = os.path.join(ROOT, "index.html")
with open(home, encoding="utf-8") as f:
    s = f.read().replace("JOURNAL_GRID", journal_grid())
with open(home, "w", encoding="utf-8") as f:
    f.write(s)

pages.append(page("/journal/", "Journal | SLG Private Aviation Advisory",
 "Notes on the private jet market, sustainable aviation fuel and cabin design from SLG.",
 f'''
<section class="section wrap">
<p class="label">Journal</p>
<h1 class="mb-48">Notes from the <span class="it">market.</span></h1>
<p class="lede mb-48">Observations on long-range aircraft, sustainable fuel and the cabin. New entries appear first on LinkedIn.</p>
{journal_grid()}
</section>
''', current="/journal/", og="columns"))

# ---------------- PRIVATE REGISTER ----------------
REGISTER = [
    ("Ultra-long-range", "2023", "Under 700 hours · recent 36-month inspection", "Asia-Pacific"),
    ("Ultra-long-range", "2017", "Large cabin, extended range", "Middle East"),
    ("Long-range", "2021", "Under 1,700 hours", "Asia"),
    ("Long-range", "2016", "European maintenance history · connectivity", "Asia"),
    ("Bizliner", "2008", "Airliner-class cabin", "On request"),
    ("Super-midsize", "2015", "Single-owner history", "Asia"),
]
rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in REGISTER)
pages.append(page("/private-register/", "Off-Market Private Jets for Sale | The Private Register | SLG",
 "Off-market long-range private jets offered privately by their owners. Details released under NDA to verified principals and their advisers.",
 f'''
<section class="wrap section">
<p class="label">Off-market</p>
<h1 class="mb-48">The Private <span class="it">Register</span></h1>
<p class="lede">Aircraft offered privately by their owners, never advertised. Each is held under a direct mandate. Type, serial, records and terms are released under NDA to verified principals and their appointed advisers.</p>
</section>
<section class="wrap" style="padding-bottom:128px">
<table class="register"><thead><tr><th scope="col">Category</th><th scope="col">Year</th><th scope="col">Profile</th><th scope="col">Region</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="small mt-24">Register updated monthly. Aircraft withdrawn from sale are removed without notice.</p>
</section>
<section class="dark"><div class="wrap section two top">
<div>
<p class="label">Access</p>
<h2 class="big mb-24">Released to principals, not to the market.</h2>
<p class="lede">We share details with buyers and the advisers they appoint. We do not work through chains of intermediaries. Requests are reviewed personally; where suitable, an NDA follows within one business day.</p>
</div>
<form class="form" action="{FORM_ACTION}" method="POST" aria-label="Request access to the Private Register">
{hidden("Private Register access request")}
{field("Full name", "name", required=True, auto="name")}
{field("Organisation", "organisation", auto="organization")}
{select("You are", "role", ["The principal", "A family office", "An appointed adviser", "A corporate flight department"])}
{field("Email", "email", "email", required=True, auto="email")}
{field("Aircraft of interest (optional)", "aircraft", full=True)}
{consent("I agree that SLG may contact me about this request. Details are kept confidential and never shared without consent.")}
<button class="btn gold" type="submit">Request access</button>
</form>
</div></section>
''', current="/private-register/", og="inflight"))

# ---------------- SELL ----------------
pages.append(page("/sell/", "Sell Your Private Jet Discreetly, Off-Market | SLG",
 "Sell your aircraft without appearing on the market. Presented only to verified principals, one conversation at a time. Confidential valuation.",
 f'''
<section class="split">
<div class="text">
<p class="label">For owners</p>
<h1>Sell without <span class="it">appearing</span> on the market.</h1>
<p class="lede">Your aircraft is presented only to buyers we have verified, one conversation at a time. No listing sites, no circulated spec sheets, no public price history.</p>
<a class="link" href="#valuation" style="align-self:flex-start">Request a confidential valuation</a>
</div>
{photo("falcon", eager=True)}
</section>
<section class="rule-top"><div class="wrap section grid3">
<div><p class="numeral">I</p><h3>Your value stays private</h3><p>An aircraft that sits on public listings loses negotiating ground every week. Off-market, there is no visible days-on-market and no published reductions.</p></div>
<div><p class="numeral">II</p><h3>Only real buyers</h3><p>We introduce principals with a confirmed budget and a defined mission, not chains of intermediaries holding the same request.</p></div>
<div><p class="numeral">III</p><h3>One adviser</h3><p>Valuation, buyer vetting, LOI, inspection and closing, coordinated by one person on your behalf, with your counsel.</p></div>
</div></section>
<section class="band-linen"><div class="wrap section tight two top">
<h2 class="big">From first call to completion.</h2>
<ol class="timeline">
<li><span class="when">Week 1</span><span>Private conversation, NDA and written mandate. Records reviewed; valuation agreed.</span></li>
<li><span class="when">Weeks 2–4</span><span>Discreet introductions to vetted principals. Only you approve who sees what.</span></li>
<li><span class="when">LOI</span><span>Letter of intent and refundable deposit into escrow.</span></li>
<li><span class="when">Closing</span><span>Pre-purchase inspection, purchase agreement and delivery, typically six to ten weeks from LOI.</span></li>
</ol>
</div></section>
<section id="valuation" class="wrap section two top">
<div>
<h2 class="big mb-24">A confidential valuation.</h2>
<p class="body mb-24">Type, year and approximate hours are enough to begin. Serial and registration can follow under NDA.</p>
<p class="small">Our fee is agreed in writing before any work begins. We act for owners and their appointed representatives only.</p>
</div>
<form class="form" action="{FORM_ACTION}" method="POST" aria-label="Confidential valuation request">
{hidden("Confidential valuation request")}
{field("Aircraft type", "aircraft_type", required=True)}
{field("Year", "year")}
{field("Approximate hours", "hours")}
{field("Based in", "based_in")}
{field("Your name", "name", required=True, auto="name")}
{field("Email", "email", "email", required=True, auto="email")}
{select("You are", "role", ["The owner", "The owner's family office", "The owner's appointed representative", "The operator, on the owner's instruction"], full=True)}
{consent("I agree that SLG may contact me about this request. Nothing is shared without my consent.")}
<button class="btn" type="submit">Request valuation</button>
</form>
</section>
''', current="/sell/", og="falcon"))

# ---------------- FAMILY OFFICES ----------------
pages.append(page("/family-offices/", "Private Aviation Advisory for Family Offices | SLG",
 "Aviation advice for family offices, holdings, private equity and wealth managers: acquisition, disposal, cabin art and SAF strategy, on mandate only.",
 f'''
<section class="hero">
{photo("library", eager=True)}
<div class="wrap">
<p class="label">Family offices · Holdings · Private capital</p>
<h1>An aviation adviser who answers to <span class="it">the family.</span></h1>
</div>
</section>
<section class="wrap section two top">
<p class="serif" style="font-size:clamp(28px,3vw,40px);line-height:1.3">An aircraft is a capital asset, a working tool and, increasingly, a place where a collection is shown. We advise on all three, with one point of contact and no conflicting loyalties.</p>
<div class="body" style="display:flex;flex-direction:column;gap:20px">
<p>We act for family offices, holding companies, private equity and the wealth managers who represent principals. Mandates are written, fees are agreed in advance, and we never work through chains of brokers.</p>
<p>Everything we share is on a need-to-know basis, under NDA, with KYC and sanctions screening completed before any introduction.</p>
</div>
</section>
<section class="rule-top" style="border-bottom:1px solid var(--rule)"><div class="wrap columns">
<article><h3>Acquisition</h3><p>Mission analysis, off-market search, verification, negotiation and closing.</p></article>
<article><h3>Disposal</h3><p>Quiet sale of an existing aircraft or a fleet renewal, timed with the replacement.</p></article>
<article><h3>Collection</h3><p>Art for the cabin, drawn from or added to the family's collection.</p></article>
<article><h3>Stewardship</h3><p>SAF strategy and emissions reporting aligned with the family's mandate.</p></article>
</div></section>
<section class="wrap section two">
{photo("salonroom", w=1600)}
<div>
<p class="label">What you can expect</p>
<ul class="ticks">
<li>A written mandate and fee before work begins</li>
<li>Direct access to owners and buyers, never a broker chain</li>
<li>Serial, title and records verified before you see a price</li>
<li>Coordination with your counsel, tax adviser and operator</li>
<li>Briefings by video at your office's convenience</li>
</ul>
</div>
</section>
<section class="dark section center">
<div class="wrap">
<h2 class="big mb-24">Arrange a private briefing.</h2>
<p class="lede" style="margin:0 auto 48px">Thirty minutes, by video, with no obligation.</p>
<a class="btn gold" href="/enquire/">Request a briefing</a>
</div>
</section>
''', current="/family-offices/", og="library"))

# ---------------- ART ----------------
pages.append(page("/art/", "Art Curation for Private Jet Interiors | SLG",
 "Original works curated for private jet cabins with artists, galleries and interior studios, certified, mounted and insured for flight.",
 f'''
<section class="wrap section center" style="padding-bottom:96px">
<p class="label">Art &amp; Interiors</p>
<h1 class="mb-48">A collection, <span class="it">at altitude.</span></h1>
<p class="lede" style="margin:0 auto">We curate original works for private cabins with artists, galleries and interior studios, then see them certified, mounted and insured for flight.</p>
</section>
<section class="wrap" style="padding-bottom:128px">
<div class="gallery">
{photo("seated", cls="photo tall", w=1600)}
{photo("bust", w=1200)}
{photo("drapery", w=1200)}
</div>
</section>
<section class="band-linen"><div class="wrap section tight">
<ol class="steps">
<li><p class="label" style="margin-bottom:14px">Curation</p><p>Works chosen for the cabin's light, scale and the owner's collection, or commissioned for it.</p></li>
<li><p class="label" style="margin-bottom:14px">Design</p><p>Coordinated with the completion centre or interior studio, from first layout to final finish.</p></li>
<li><p class="label" style="margin-bottom:14px">Certification</p><p>Mounting, materials and weight approved for flight by qualified installers.</p></li>
<li><p class="label" style="margin-bottom:14px">Care</p><p>Insurance, rotation between residence and aircraft, and condition records.</p></li>
</ol>
</div></section>
<section class="wrap section" style="display:flex;flex-wrap:wrap;gap:64px;align-items:flex-end;justify-content:space-between">
<p class="serif" style="flex:2 1 560px;font-size:clamp(28px,3.4vw,46px);line-height:1.3">Considered from the first inspection, not added after delivery. Art changes which aircraft is right, and how its cabin should be finished.</p>
<a class="link" href="/enquire/">Discuss a cabin</a>
</section>
''', current="/art/", og="seated"))

# ---------------- SUSTAINABILITY ----------------
pages.append(page("/sustainability/", "Sustainable Aviation Fuel (SAF) Advisory for Private Jets | SLG",
 "Practical sustainability advice for private aviation: efficient aircraft choices, SAF access and honest emissions reporting for family offices.",
 f'''
<section class="split">
{photo("sculptroom", eager=True)}
<div class="text" style="padding-left:64px;padding-right:max(var(--gutter),calc((100% - var(--max))/2 + var(--gutter)))">
<p class="label">Sustainability &amp; SAF</p>
<h1>Responsibility, <span class="it">without ceremony.</span></h1>
<p class="lede">Practical choices that reduce a flight department's footprint and stand up to scrutiny from a family's board, auditors and next generation.</p>
</div>
</section>
<section class="wrap section grid3">
<div><p class="numeral">I</p><h3>The right aircraft</h3><p>Newer engines and right-sized cabins are the largest lever. We weigh efficiency alongside range and value at acquisition.</p></div>
<div><p class="numeral">II</p><h3>SAF access</h3><p>Where sustainable aviation fuel can be uplifted, or booked and claimed, and what EU ReFuelEU blending requirements mean for European operations.</p></div>
<div><p class="numeral">III</p><h3>Honest reporting</h3><p>Flight emissions measured and reported plainly for the family office's ESG records, with offsets kept separate from reductions.</p></div>
</section>
<section class="wrap" style="padding-bottom:144px">{photo("columns", w=2400, extra=' style="height:min(70vh,640px)"')}</section>
<section class="dark"><div class="wrap section tight" style="display:flex;flex-wrap:wrap;gap:64px;align-items:flex-end;justify-content:space-between">
<div style="flex:1 1 520px"><p class="label">Journal</p>
<p class="serif" style="font-size:clamp(28px,3.4vw,46px);line-height:1.25">Five SAF developments in Europe this summer, and what they mean for private operators.</p></div>
<a class="link" href="{ENTRIES[1][3]}" rel="noopener">Read the entry</a>
</div></section>
<section class="section center wrap">
<h2 class="big mb-24">Review a fleet, quietly.</h2>
<p class="body mb-48">A short assessment of your current aircraft and fuel options.</p>
<a class="btn" href="/enquire/">Enquire</a>
</section>
''', current="/sustainability/", og="sculptroom"))

# ---------------- CHARTER ----------------
pages.append(page("/charter/", "Private Jet Charter for Principals and Family Offices | SLG",
 "Private jet charter arranged discreetly for principals, families and executives, from the season's events to board meetings. Vetted operators only.",
 f'''
<section class="hero">
{photo("alps", eager=True)}
<div class="wrap">
<p class="label">Charter</p>
<h1>Wherever the season <span class="it">leads.</span></h1>
<p class="lede">Charter arranged personally for principals, families and executives. Operators are vetted, aircraft are matched to the mission, and every detail is confirmed before you travel.</p>
<div class="actions"><a class="link" href="/enquire/?intent=charter">Request a charter</a></div>
</div>
</section>
<section class="wrap section grid3">
<div><p class="numeral">I</p><h3>The season</h3><p>Monaco, St. Moritz, Art Basel, the Gulf winter. Flights timed to the calendar, often arranged weeks ahead.</p></div>
<div><p class="numeral">II</p><h3>The board</h3><p>Same-day returns and multi-city itineraries for executives, with one point of contact throughout.</p></div>
<div><p class="numeral">III</p><h3>The family</h3><p>Children, staff, pets and luggage planned for, with cabin preferences remembered for next time.</p></div>
</section>
<section class="rule-top"><div class="wrap section two">
{photo("salon", w=1600)}
<div>
<p class="label">Standards</p>
<ul class="ticks">
<li>Licensed operators only, with safety audits on file</li>
<li>Aircraft and crew confirmed in writing before departure</li>
<li>Transparent quotation; no hidden repositioning</li>
<li>Empty legs offered when they genuinely fit your plans</li>
</ul>
</div>
</div></section>
<section class="section center wrap">
<h2 class="big mb-24">Tell us where, and when.</h2>
<p class="body mb-48">A quotation follows the same day for most itineraries.</p>
<a class="btn" href="/enquire/?intent=charter">Request a charter</a>
</section>
''', current="/charter/", og="alps"))

# ---------------- ENQUIRE ----------------
pages.append(page("/enquire/", "Enquire | SLG Private Aviation Advisory",
 "Begin a private conversation with SLG about acquiring or selling an aircraft, charter, or art for your cabin. Answered personally within one business day.",
 f'''
<section class="wrap section" style="display:flex;flex-wrap:wrap;gap:112px">
<div style="flex:1 1 380px;display:flex;flex-direction:column;gap:40px">
<div>
<p class="label">Enquire</p>
<h1 class="mb-24">Conversations begin <span class="it">privately.</span></h1>
<p class="lede measure">Every enquiry is read and answered personally, within one business day. Nothing you share leaves this conversation without your consent.</p>
</div>
<div class="contact-lines rule-top" style="padding-top:32px">
<p><span>Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p><span>Founder</span><a href="https://www.linkedin.com/in/tugce-tekin/" rel="noopener">Tuğçe Tekin</a></p>
</div>
</div>
<form class="form" style="flex:1 1 560px" action="{FORM_ACTION}" method="POST" aria-label="Private enquiry">
{hidden("Private enquiry from theslg.co")}
<fieldset class="choices full"><legend>I wish to</legend>
<label><input type="radio" name="intent" value="Acquire" checked>Acquire an aircraft</label>
<label><input type="radio" name="intent" value="Sell">Sell an aircraft</label>
<label><input type="radio" name="intent" value="Charter">Charter</label>
<label><input type="radio" name="intent" value="Art">Art &amp; interiors</label>
<label><input type="radio" name="intent" value="Briefing">A family office briefing</label>
</fieldset>
{field("Full name", "name", required=True, auto="name")}
{field("Organisation (optional)", "organisation", auto="organization")}
{field("Email", "email", "email", required=True, auto="email")}
{select("Preferred contact", "contact_by", ["Email", "Video call", "WhatsApp"])}
<label class="field full">A few words (optional)<textarea name="message" rows="4"></textarea></label>
{consent('I agree that SLG may contact me about this enquiry, as described in the <a href="/privacy/">privacy notice</a>.')}
<button class="btn" type="submit">Send privately</button>
</form>
</section>
<script>
(function(){{var p=new URLSearchParams(location.search).get('intent');if(!p)return;var m={{charter:'Charter',sell:'Sell',art:'Art',briefing:'Briefing',acquire:'Acquire'}};var v=m[p.toLowerCase()];if(!v)return;var r=document.querySelector('input[name=intent][value="'+v+'"]');if(r)r.checked=true;}})();
</script>
''', current="/enquire/", og="cabin"))

# ---------------- THANK YOU ----------------
pages.append(page("/thank-you/", "Thank you | SLG", "Your enquiry has been received.",
 '''
<section class="wrap section center" style="min-height:60vh">
<p class="label">Received</p>
<h1 class="mb-24">Thank you.</h1>
<p class="lede" style="margin:0 auto 48px">Your note has reached us privately. You will hear from us personally within one business day.</p>
<a class="link" href="/">Return home</a>
</section>
''', noindex=True))

# ---------------- PRIVACY ----------------
pages.append(page("/privacy/", "Privacy Notice | SLG", "How SLG Global LLC handles personal information shared through this website.",
 f'''
<section class="wrap section"><div class="prose">
<p class="label">Privacy</p>
<h1 class="mb-48">Privacy notice</h1>
<p>This notice explains how SLG Global LLC ("SLG", "we") handles personal information you share through theslg.co. Last updated 7 October 2026.</p>
<h2>What we collect</h2>
<p>Only what you choose to send through our forms or by email: your name, email address, organisation, role, the aircraft or service you are interested in, and any message you write.</p>
<h2>Why we use it</h2>
<p>To reply to your enquiry and, where you ask us to, to act on it, for example to arrange an NDA, a valuation or a charter quotation. We do not use it for marketing lists and we never sell it.</p>
<h2>Who processes it</h2>
<p>Form submissions are relayed to our inbox by FormSubmit (formsubmit.co). Our email is hosted by Microsoft 365. This website is hosted by GitHub Pages and uses Google Fonts and Unsplash-hosted images, which may record your IP address when your browser loads them.</p>
<h2>How long we keep it</h2>
<p>For as long as needed to deal with your enquiry and any resulting transaction, and as required for legal, KYC and anti-money-laundering obligations.</p>
<h2>Your rights</h2>
<p>You may ask to see, correct or delete the information we hold about you, or object to its use, by writing to <a href="mailto:{EMAIL}">{EMAIL}</a>. If you are in the UK or EU you may also complain to your data protection authority.</p>
<h2>Cookies</h2>
<p>This website sets no cookies of its own and uses no analytics or advertising trackers.</p>
</div></section>
''', noindex=False))

# ---------------- ACCESSIBILITY ----------------
pages.append(page("/accessibility/", "Accessibility | SLG", "SLG's commitment to an accessible website.",
 f'''
<section class="wrap section"><div class="prose">
<p class="label">Accessibility</p>
<h1 class="mb-48">Accessibility</h1>
<p>We aim for this website to meet WCAG 2.2 level AA. Pages use real headings, labelled form fields, keyboard-reachable controls, sufficient colour contrast and descriptive alternative text for photographs, and they respect reduced-motion settings.</p>
<p>If anything is difficult to use, please tell us at <a href="mailto:{EMAIL}">{EMAIL}</a> and we will help directly and correct it.</p>
</div></section>
'''))

# ---------------- CREDITS ----------------
credit_rows = "".join(
    f'<li>{alt} — <a href="https://unsplash.com/photos/{slug}" rel="noopener">{who}</a></li>'
    for (_pid, alt, who, slug) in PHOTOS.values())
pages.append(page("/credits/", "Credits | SLG", "Photography credits.",
 f'''
<section class="wrap section"><div class="prose">
<p class="label">Credits</p>
<h1 class="mb-48">Photography</h1>
<p>Photographs are used under the Unsplash licence. With thanks to:</p>
<ul>{credit_rows}</ul>
</div></section>
'''))

# ---------------- 404 ----------------
page("/404.html", "Page not found | SLG", "This page could not be found.",
 '''
<section class="wrap section center" style="min-height:60vh">
<p class="label">Not found</p>
<h1 class="mb-24">This page has moved, <span class="it">quietly.</span></h1>
<p class="lede" style="margin:0 auto 48px">The address may have changed with our new website.</p>
<a class="link" href="/">Return home</a>
</section>
''', noindex=True)

# ---------------- OLD WIX ADDRESSES -> NEW ----------------
REDIRECTS = {
    "sales-acquisition": "/private-register/",
    "private-jet-charter": "/charter/",
    "art-curation": "/art/",
    "insights": "/journal/",
    "contact": "/enquire/",
    "privacy-policy": "/privacy/",
    "accessibility-statement": "/accessibility/",
    "blog": "/journal/",
}
for old, new in REDIRECTS.items():
    os.makedirs(os.path.join(ROOT, old), exist_ok=True)
    with open(os.path.join(ROOT, old, "index.html"), "w", encoding="utf-8") as f:
        f.write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved | SLG</title>
<link rel="canonical" href="{SITE}{new}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={new}">
<script>location.replace("{new}" + location.search + location.hash);</script></head>
<body><p>This page has moved to <a href="{new}">{SITE}{new}</a>.</p></body></html>
''')

# ---------------- SITEMAP / ROBOTS / CNAME ----------------
indexable = [p for p in pages if p not in ("/thank-you/",)]
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for p in indexable:
        f.write(f"  <url><loc>{SITE}{p}</loc><lastmod>2026-10-07</lastmod></url>\n")
    f.write("</urlset>\n")
with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(f"User-agent: *\nAllow: /\nDisallow: /thank-you/\n\nSitemap: {SITE}/sitemap.xml\n")
if os.environ.get("SLG_CUSTOM_DOMAIN"):
  with open(os.path.join(ROOT, "CNAME"), "w") as f:
    f.write("www.theslg.co\n")
open(os.path.join(ROOT, ".nojekyll"), "w").close()

print("Built", len(pages), "pages +", len(REDIRECTS), "redirects")
