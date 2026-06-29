#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared chrome (head, nav, footer), Hindi strings, theme + helpers.

Kabaddi-themed. Saffron/orange palette. No emojis anywhere — text + SVG icons.
"""
import re, html, json

SITE = "https://kabaddistats.com"
BRAND = "कबड्डी आँकड़े"
BRAND_EN = "KabaddiStats"
CONTACT = "info@kabaddistats.com"

# ---- Hindi label dictionary -------------------------------------------------
T = {
    "home": "होम", "players": "खिलाड़ी", "teams": "टीमें", "records": "रिकॉर्ड",
    "compare": "तुलना", "search": "खोजें", "seasons": "सीज़न", "about": "हमारे बारे में",
    "raider": "रेडर", "defender": "डिफेंडर", "allrounder": "ऑल-राउंडर",
    "season": "सीज़न", "champion": "चैंपियन", "rank": "#",
    # stat columns
    "m": "मैच", "raid_pts": "रेड अंक", "tackle_pts": "टैकल अंक",
    "total_pts": "कुल अंक", "super10": "सुपर 10", "high5": "हाई 5",
    "super_raids": "सुपर रेड", "super_tackles": "सुपर टैकल",
    "seasons_played": "सीज़न", "player": "खिलाड़ी", "team": "टीम", "role": "भूमिका",
    "played": "खेले", "won": "जीते", "lost": "हारे", "tied": "टाई", "winpct": "जीत %",
    "title": "ख़िताब", "city": "शहर", "est": "स्थापना",
    # record titles
    "most_raid_pts": "सर्वाधिक रेड अंक", "most_tackle_pts": "सर्वाधिक टैकल अंक",
    "most_total_pts": "सर्वाधिक कुल अंक", "most_super10": "सर्वाधिक सुपर 10",
    "most_high5": "सर्वाधिक हाई 5", "most_super_raids": "सर्वाधिक सुपर रेड",
    "most_super_tackles": "सर्वाधिक सुपर टैकल",
}

# role key -> (Hindi label, slug, badge classes)
ROLE = {
    "raider":     ("रेडर", "raider", "bg-orange-50 text-orange-700 border-orange-200"),
    "defender":   ("डिफेंडर", "defender", "bg-sky-50 text-sky-700 border-sky-200"),
    "allrounder": ("ऑल-राउंडर", "allrounder", "bg-violet-50 text-violet-700 border-violet-200"),
}


def esc(s):
    return html.escape(str(s), quote=True)


def slug(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", str(s).lower()).strip("-")
    return s or "x"


# ---- inline SVG icons (clean, theme-matched, currentColor) ------------------
_ICONS = {
    "trophy": ("stroke",
               '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>'
               '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>'
               '<path d="M4 22h16"/>'
               '<path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>'
               '<path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>'
               '<path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>'),
    "search": ("stroke",
               '<circle cx="11" cy="11" r="8"/>'
               '<path d="m21 21-4.3-4.3"/>'),
    # a stylised raider — outstretched figure mid-raid
    "raid": ("stroke",
             '<circle cx="12" cy="4.5" r="2"/>'
             '<path d="M12 7v6"/><path d="M4 9l8 2 8-2"/>'
             '<path d="M12 13l-4 8"/><path d="M12 13l4 8"/>'),
    # interlocked hands — a tackle
    "tackle": ("stroke",
               '<path d="M3 12h6l1.5-2 3 4 1.5-2h6"/>'
               '<circle cx="12" cy="12" r="9"/>'),
    "users": ("stroke",
              '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
              '<circle cx="9" cy="7" r="4"/>'
              '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
              '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    "calendar": ("stroke",
                 '<rect x="3" y="4" width="18" height="18" rx="2"/>'
                 '<path d="M3 10h18M8 2v4M16 2v4"/>'),
    "chart": ("stroke",
              '<path d="M3 3v18h18"/><path d="M7 15l3-4 3 2 4-6"/>'),
}


def icon(name, cls="w-5 h-5", color=None):
    kind, paths = _ICONS[name]
    if kind == "stroke":
        attrs = (f'fill="none" stroke="{color or "currentColor"}" stroke-width="2" '
                 f'stroke-linecap="round" stroke-linejoin="round"')
    else:
        attrs = f'fill="{color or "currentColor"}"'
    return (f'<svg class="{cls} shrink-0" viewBox="0 0 24 24" {attrs} '
            f'aria-hidden="true">{paths}</svg>')


def role_badge(rkey):
    label, _rslug, cls = ROLE.get(rkey, ROLE["raider"])
    return (f'<span class="inline-block text-xs font-semibold px-2 py-0.5 '
            f'rounded border {cls}">{label}</span>')


# ---- <head> -----------------------------------------------------------------
def head(title, desc, canonical, depth, jsonld=None, og_type="website"):
    """depth = number of '../' to reach site root from this page."""
    up = "../" * depth
    canon = SITE + canonical
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + \
             json.dumps(jsonld, ensure_ascii=False) + "</script>"
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Google Analytics (GA4) — measurement ID to be added -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-B3MY8Q8ST7"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', 'G-B3MY8Q8ST7');
</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{esc(canon)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND_EN}">
<meta property="og:locale" content="hi_IN">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/og-image.png">
<meta name="theme-color" content="#FF6B00">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="icon" type="image/png" sizes="32x32" href="{up}favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{up}favicon-16x16.png">
<link rel="icon" href="{up}favicon.ico" sizes="any">
<link rel="apple-touch-icon" sizes="180x180" href="{up}apple-touch-icon.png">
<link rel="manifest" href="{up}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {{ theme: {{ extend: {{
  colors: {{
    'kb-orange':'#FF6B00','kb-dark':'#9A3412','kb-accent':'#FB923C',
    'kb-bg':'#fdf7f2','kb-card':'#ffffff','kb-border':'#f0e3d8',
    'kb-text':'#6b5d52','kb-ink':'#2a1c12','kb-mat':'#1d4ed8','kb-gold':'#d97706'
  }},
  fontFamily: {{
    heading:['"Baloo 2"','"Noto Sans Devanagari"','sans-serif'],
    body:['Inter','"Noto Sans Devanagari"','sans-serif']
  }}
}} }} }}
</script>
<style>
  body{{font-family:Inter,'Noto Sans Devanagari',sans-serif;background:#fdf7f2;color:#2a1c12}}
  h1,h2,h3,h4,h5{{font-family:'Baloo 2','Noto Sans Devanagari',sans-serif}}
  .hi{{font-family:'Noto Sans Devanagari','Baloo 2',sans-serif}}
  .mat-stripe{{background:linear-gradient(90deg,#FF6B00,#FB923C)}}
  tbody tr:hover td{{background:#fdf1e7}}
  .tnum{{font-variant-numeric:tabular-nums}}
  ::selection{{background:#fed7aa}}
</style>
{ld}
</head>
<body class="min-h-screen flex flex-col">
"""


# ---- nav --------------------------------------------------------------------
def nav(depth, active=""):
    up = "../" * depth
    items = [
        ("होम", up, "home"),
        ("खिलाड़ी", up + "players/", "players"),
        ("टीमें", up + "teams/", "teams"),
        ("सीज़न", up + "seasons/", "seasons"),
        ("मैच", up + "matches/", "matches"),
        ("अंक तालिका", up + "standings/", "standings"),
        ("स्टेडियम", up + "venues/", "venues"),
        ("नीलामी", up + "auctions/", "auctions"),
        ("ऑल-स्टार", up + "all-star/", "allstar"),
        ("रिकॉर्ड", up + "records/", "records"),
        ("तुलना", up + "compare/", "compare"),
        ("आज के दिन", up + "aaj-ke-din/", "thisday"),
        ("हमारे बारे में", up + "about/", "about"),
    ]
    links, mlinks = "", ""
    for label, href, act in items:
        on = "text-kb-orange font-semibold" if act == active else "text-kb-text hover:text-kb-orange"
        links += f'<a href="{href}" class="hi px-2.5 py-1.5 rounded-md transition {on}">{label}</a>'
        mlinks += f'<a href="{href}" class="hi block px-3 py-2 rounded-md {on}">{label}</a>'
    return f"""<header class="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-kb-border">
<div class="h-1 mat-stripe"></div>
<div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
  <a href="{up}" class="flex items-center gap-2 shrink-0">
    <svg width="36" height="36" viewBox="0 0 64 64" class="shrink-0" aria-hidden="true"><circle cx="32" cy="32" r="29" fill="#FF6B00"/><circle cx="32" cy="32" r="29" fill="none" stroke="#9A3412" stroke-width="2" opacity="0.25"/><circle cx="32" cy="20" r="5.5" fill="#fff"/><path d="M32 26 L32 40" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/><path d="M19 30 L32 33 L45 28" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M32 40 L24 52" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/><path d="M32 40 L42 51" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/></svg>
    <span class="font-heading font-extrabold text-lg leading-none hi">
      <span class="text-kb-orange">कबड्डी</span><span class="text-kb-ink"> आँकड़े</span>
    </span>
  </a>
  <nav class="hidden lg:flex items-center gap-0.5 text-sm">{links}
    <button onclick="KB_search()" class="hi ml-1 px-3 py-1.5 rounded-md bg-kb-orange text-white font-semibold hover:bg-kb-dark transition">{T['search']}</button>
  </nav>
  <div class="flex lg:hidden items-center gap-2">
    <button onclick="KB_search()" class="hi px-3 py-1.5 rounded-md bg-kb-orange text-white text-sm font-semibold">{T['search']}</button>
    <button onclick="document.getElementById('mnav').classList.toggle('hidden')" class="p-2 rounded-md border border-kb-border" aria-label="मेन्यू">
      <svg width="20" height="20" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
</div>
<div id="mnav" class="hidden lg:hidden border-t border-kb-border px-4 py-2 space-y-0.5 bg-white">{mlinks}</div>
</header>
<script src="{up}search.js" defer></script>
"""


def breadcrumb(depth, trail):
    """trail = list of (label, href_or_None). Last item is current page."""
    up = "../" * depth
    parts, items = [], []
    for i, (lbl, href) in enumerate(trail):
        if href:
            parts.append(f'<a href="{href}" class="hover:text-kb-orange">{lbl}</a>')
        else:
            parts.append(f'<span class="text-kb-ink font-medium">{lbl}</span>')
        items.append({"@type": "ListItem", "position": i + 1, "name": str(lbl),
                      **({"item": SITE + "/" + href.replace(up, "")} if href else {})})
    sep = '<span class="mx-2 text-kb-border">/</span>'
    ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                     "itemListElement": items}, ensure_ascii=False)
    return (f'<nav aria-label="breadcrumb" class="hi max-w-7xl mx-auto px-4 sm:px-6 '
            f'pt-4 text-sm text-kb-text">{sep.join(parts)}</nav>'
            f'<script type="application/ld+json">{ld}</script>')


def footer(depth):
    up = "../" * depth
    col = lambda title, links: (
        f'<div><h4 class="hi font-heading font-bold text-kb-ink mb-3">{title}</h4>'
        f'<div class="space-y-1.5 text-sm">' +
        "".join(f'<a href="{h}" class="hi block text-kb-text hover:text-kb-orange">{l}</a>'
                for l, h in links) + "</div></div>")
    return f"""<footer class="mt-auto border-t border-kb-border bg-white">
<div class="max-w-7xl mx-auto px-4 sm:px-6 py-10">
  <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
    <div class="col-span-2 md:col-span-1">
      <div class="font-heading font-extrabold text-lg hi mb-2"><span class="text-kb-orange">कबड्डी</span><span class="text-kb-ink"> आँकड़े</span></div>
      <p class="hi text-sm text-kb-text leading-relaxed">हिंदी में कबड्डी सांख्यिकी — प्रो कबड्डी लीग और अंतरराष्ट्रीय कबड्डी के विस्तृत आँकड़े, रिकॉर्ड और खिलाड़ी प्रोफ़ाइल।</p>
    </div>
    {col("ब्राउज़ करें", [("खिलाड़ी", up+"players/"), ("टीमें", up+"teams/"), ("सीज़न", up+"seasons/"), ("मैच", up+"matches/"), ("अंक तालिका", up+"standings/"), ("स्टेडियम", up+"venues/"), ("नीलामी", up+"auctions/"), ("ऑल-स्टार", up+"all-star/"), ("रिकॉर्ड", up+"records/")])}
    {col("अधिक", [("तुलना", up+"compare/"), ("आज के दिन", up+"aaj-ke-din/"), ("हमारे बारे में", up+"about/"), ("गोपनीयता नीति", up+"privacy/")])}
    {col("संपर्क", [(CONTACT, "mailto:"+CONTACT)])}
  </div>
  <div class="border-t border-kb-border pt-6 text-center text-sm text-kb-text">
    <p class="hi mb-1">प्रो कबड्डी लीग (सीज़न 1–12) और अंतरराष्ट्रीय कबड्डी के सार्वजनिक रूप से उपलब्ध आँकड़ों पर आधारित।</p>
    <p class="hi">© 2026 कबड्डी आँकड़े · KabaddiStats.com — किसी भी कबड्डी बोर्ड या लीग से आधिकारिक रूप से संबद्ध नहीं।</p>
  </div>
</div>
</footer>
</body></html>"""


def page(title, desc, canonical, depth, body, active="", trail=None, jsonld=None, og_type="website"):
    out = head(title, desc, canonical, depth, jsonld, og_type)
    out += nav(depth, active)
    if trail:
        out += breadcrumb(depth, trail)
    out += f'<main class="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 py-6">{body}</main>'
    out += footer(depth)
    return out
