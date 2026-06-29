#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the full static KabaddiStats.com site from data.py into repo root."""
import json, subprocess, datetime
from pathlib import Path

import templates as TP
from templates import (esc, slug, icon, role_badge, page, SITE, BRAND, BRAND_EN,
                       CONTACT, ROLE, T)
import content as C
from data import (TEAMS, SEASONS, PLAYERS, PLAYER_BY_ID, RECORDS, RECORD_MILESTONES,
                  WORLD_CUP, ASIAN_GAMES_MEN, ASIAN_GAMES_WOMEN, GLOSSARY, MATCHES,
                  STANDINGS, VENUES, AUCTIONS, ALL_TIME_EXPENSIVE, ALL_STAR_GAMES)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT
TODAY = datetime.date.today().isoformat()
# A slightly older date for content that rarely changes (about, privacy, 404),
# so the sitemap reflects reality instead of stamping every URL identically.
BUILD_DATE_STATIC = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
INDEXNOW_KEY = "9d4e1f7a2c6b48e0a3f5c1d9b7e6a204"


def _end_year(y):
    """Return the four-digit ending year of a season-year string (e.g. '2023-24' -> '2024')."""
    parts = str(y).split("-")
    if len(parts) == 2 and len(parts[1]) == 2:
        return parts[0][:2] + parts[1]
    return parts[0]


N_SEASONS = len(SEASONS)               # total number of PKL seasons in the dataset
FIRST_YEAR = _end_year(SEASONS[0]["year"])     # '2014'
LAST_YEAR = _end_year(SEASONS[-1]["year"])     # latest season's ending year
SEASON_RANGE_HI = f"1 से {N_SEASONS}"          # e.g. '1 से 12'
YEAR_RANGE_HI = f"{FIRST_YEAR} से {LAST_YEAR}"  # e.g. '2014 से 2025'

urls = []           # (path, priority) for sitemap
search_rows = []    # [name, url, kind_hi, haystack]


def write(relpath, htmltext, priority="0.6"):
    p = OUT / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(htmltext, encoding="utf-8")
    url = "/" + relpath[:-len("index.html")] if relpath.endswith("index.html") else "/" + relpath
    urls.append((url, priority))


# ============================================================ UI fragments ====
def stat(label, value, sub=""):
    sub = f'<div class="text-xs text-kb-text hi mt-0.5">{sub}</div>' if sub else ""
    return (f'<div class="bg-kb-card border border-kb-border rounded-xl px-4 py-3">'
            f'<div class="text-2xl font-heading font-extrabold text-kb-ink tnum">{value}</div>'
            f'<div class="text-xs font-semibold text-kb-orange hi uppercase tracking-wide">{label}</div>{sub}</div>')


def section_title(txt, sub=""):
    s = f'<p class="hi text-kb-text mt-1">{sub}</p>' if sub else ""
    return (f'<div class="mb-4"><h2 class="hi font-heading font-bold text-xl sm:text-2xl '
            f'text-kb-ink flex items-center gap-2"><span class="w-1.5 h-6 rounded mat-stripe inline-block"></span>{txt}</h2>{s}</div>')


def page_h1(txt, sub=""):
    """Top-level page heading for section landing pages. Visually identical to
    section_title but renders an <h1> so each landing page has exactly one h1
    and the heading hierarchy reads h1 -> h2 -> h3 without skipping levels."""
    s = f'<p class="hi text-kb-text mt-1">{sub}</p>' if sub else ""
    return (f'<div class="mb-4"><h1 class="hi font-heading font-bold text-xl sm:text-2xl '
            f'text-kb-ink flex items-center gap-2"><span class="w-1.5 h-6 rounded mat-stripe inline-block"></span>{txt}</h1>{s}</div>')


def table(headers, rows, align_right=None):
    align_right = align_right or set()
    thead = "".join(
        f'<th{" class=\"ar\"" if i in align_right else ""}>{h}</th>'
        for i, h in enumerate(headers))
    body = ""
    for r in rows:
        tds = "".join(
            f'<td{" class=\"ar\"" if i in align_right else ""}>{c}</td>'
            for i, c in enumerate(r))
        body += f"<tr class='border-t border-kb-border'>{tds}</tr>"
    return (f'<div class="overflow-x-auto bg-kb-card border border-kb-border rounded-xl">'
            f'<table class="w-full min-w-full ktbl"><thead class="bg-kb-bg">'
            f'<tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>')


def plink(pid, depth, sub=True):
    p = PLAYER_BY_ID.get(pid)
    if not p:
        return f'<span class="font-medium text-kb-ink">{esc(pid)}</span>'
    s = f'<span class="hi text-kb-text text-xs ml-1">{p["name_hi"]}</span>' if sub else ""
    return (f'<a href="{"../"*depth}players/{pid}/" class="font-medium text-kb-ink '
            f'hover:text-kb-orange">{esc(p["name"])}</a>{s}')


def pname_link(name, depth):
    """Link by display name if a profile exists, else plain text + Hindi."""
    for p in PLAYERS:
        if p["name"] == name:
            return plink(p["id"], depth)
    return f'<span class="font-medium text-kb-ink">{esc(name)}</span>'


def team_link(team_slug, depth, hi=True):
    t = TEAMS.get(team_slug)
    if not t:
        return esc(team_slug)
    label = t["name_hi"] if hi else t["name"]
    return (f'<a href="{"../"*depth}teams/{team_slug}/" class="text-kb-ink '
            f'hover:text-kb-orange hi">{esc(label)}</a>')


def role_pill_label(rkey):
    return ROLE.get(rkey, ROLE["raider"])[0]


def total_pts(p):
    return p["total"]


# ================================================================ HOMEPAGE ====
def build_home():
    depth = 0
    by_total = sorted(PLAYERS, key=total_pts, reverse=True)
    top = by_total[:8]
    cards = ""
    for p in top:
        cards += f"""<a href="players/{p['id']}/" class="group bg-kb-card border border-kb-border rounded-xl p-4 hover:border-kb-orange hover:shadow-md transition">
          <div class="font-heading font-bold text-kb-ink group-hover:text-kb-orange">{esc(p['name'])}</div>
          <div class="hi text-sm text-kb-text">{p['name_hi']}</div>
          <div class="flex flex-wrap gap-1 my-2">{role_badge(p['role'])}</div>
          <div class="flex gap-4 text-sm"><span class="tnum"><b class="text-kb-ink">{p['raid']:,}</b> <span class="hi text-kb-text">रेड</span></span>
          <span class="tnum"><b class="text-kb-ink">{p['tackle']:,}</b> <span class="hi text-kb-text">टैकल</span></span></div></a>"""

    # latest champion banner
    champ_s = SEASONS[-1]
    champ_t = TEAMS[champ_s["champion"]]
    champ_html = f"""<div class="rounded-2xl mat-stripe text-white p-6 sm:p-8 mb-8">
      <div class="hi text-sm font-semibold opacity-90 mb-1">पीकेएल सीज़न {champ_s['num']} ({champ_s['year']}) चैंपियन</div>
      <div class="font-heading font-extrabold text-2xl sm:text-3xl mb-3 hi flex items-center gap-2.5">{icon('trophy','w-7 h-7')}{esc(champ_t['name_hi'])}</div>
      <div class="flex flex-wrap gap-x-8 gap-y-2 text-sm">
        <div><span class="hi opacity-80">फ़ाइनल:</span> <b>{champ_s['score']}</b> <span class="hi opacity-80">बनाम {esc(TEAMS[champ_s['runner_up']]['name_hi'])}</span></div>
        <div><span class="hi opacity-80">एमवीपी:</span> <b>{esc(champ_s['mvp'][0])}</b></div>
      </div>
      <a href="seasons/" class="hi inline-block mt-4 bg-white text-kb-orange font-semibold text-sm px-4 py-2 rounded-lg hover:bg-kb-bg transition">सभी सीज़न देखें →</a></div>"""

    def mini(title, key):
        _label, items = RECORDS[key]
        rows = ""
        for i, (pid, val, ctx) in enumerate(items[:5]):
            p = PLAYER_BY_ID.get(pid)
            nm = p["name"] if p else pid
            href = f'players/{pid}/' if p else '#'
            rows += (f'<div class="flex items-center justify-between py-1.5 border-t border-kb-border first:border-0">'
                     f'<div class="truncate"><span class="text-kb-text text-xs mr-2 tnum">{i+1}</span>'
                     f'<a href="{href}" class="text-sm font-medium text-kb-ink hover:text-kb-orange">{esc(nm)}</a></div>'
                     f'<span class="tnum font-bold text-kb-orange text-sm">{val:,}</span></div>')
        return (f'<div class="bg-kb-card border border-kb-border rounded-xl p-4">'
                f'<h3 class="hi font-heading font-bold text-kb-ink mb-2">{title}</h3>{rows}</div>')

    # team chips
    team_chips = ""
    for ts, t in TEAMS.items():
        team_chips += (f'<a href="teams/{ts}/" class="hi inline-flex items-center gap-1.5 px-3 py-1.5 '
                       f'rounded-lg border border-kb-border bg-white text-sm text-kb-ink hover:border-kb-orange transition">'
                       f'<span class="w-2.5 h-2.5 rounded-full" style="background:{t["color"]}"></span>{esc(t["name_hi"])}</a>')

    total_raid = sum(p["raid"] for p in PLAYERS)
    body = f"""
    <section class="text-center py-8 sm:py-12">
      <h1 class="hi font-heading font-extrabold text-3xl sm:text-5xl text-kb-ink leading-tight">हिंदी में <span class="text-kb-orange">कबड्डी आँकड़े</span></h1>
      <p class="hi text-kb-text text-base sm:text-lg mt-3 max-w-2xl mx-auto">प्रो कबड्डी लीग और अंतरराष्ट्रीय कबड्डी के विस्तृत आँकड़े — खिलाड़ी प्रोफ़ाइल, टीमें, हर सीज़न का ब्योरा, रिकॉर्ड और हेड-टू-हेड तुलना, सब एक जगह।</p>
      <div class="mt-5 flex flex-wrap items-center justify-center gap-3">
        <button onclick="KB_search()" class="hi px-5 py-2.5 rounded-lg bg-kb-orange text-white font-semibold hover:bg-kb-dark transition">खिलाड़ी खोजें</button>
        <a href="records/" class="hi px-5 py-2.5 rounded-lg border border-kb-border bg-white text-kb-ink font-semibold hover:border-kb-orange transition">रिकॉर्ड देखें</a>
      </div>
    </section>
    <section class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
      {stat('खिलाड़ी', f'{len(PLAYERS)}+')}
      {stat('टीमें', f'{len(TEAMS)}')}
      {stat('सीज़न', f'{len(SEASONS)}', YEAR_RANGE_HI)}
      {stat('कुल रेड अंक', f'{total_raid/1000:.0f}K+')}
    </section>
    {champ_html}
    {section_title('टीमें', 'सभी 12 प्रो कबड्डी लीग फ़्रेंचाइज़ी')}
    <section class="flex flex-wrap gap-2 mb-10">{team_chips}</section>
    {section_title('चर्चित खिलाड़ी', 'करियर प्रदर्शन के आधार पर शीर्ष खिलाड़ी')}
    <section class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-2">{cards}</section>
    <div class="text-center mb-10"><a href="players/" class="hi text-kb-orange font-semibold hover:underline">सभी खिलाड़ी देखें →</a></div>
    {section_title('रिकॉर्ड की झलक', 'पीकेएल के सर्वकालिक लीडरबोर्ड')}
    <section class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      {mini('सर्वाधिक रेड अंक', 'career_raid')}
      {mini('सर्वाधिक टैकल अंक', 'career_tackle')}
      {mini('सर्वाधिक सुपर 10', 'career_super10')}
      {mini('सर्वाधिक हाई 5', 'career_high5')}
    </section>
    <div class="text-center"><a href="records/" class="hi text-kb-orange font-semibold hover:underline">सभी रिकॉर्ड देखें →</a></div>
    <div class="mt-12">{C.prose([
      "<b>कबड्डी आँकड़े</b> (KabaddiStats.com) हिंदी भाषी कबड्डी प्रेमियों के लिए एक "
      f"संपूर्ण आँकड़ा मंच है, जहाँ प्रो कबड्डी लीग (पीकेएल) के सभी {N_SEASONS} सीज़न और "
      "अंतरराष्ट्रीय कबड्डी के विस्तृत रिकॉर्ड एक ही जगह उपलब्ध हैं। यहाँ शीर्ष "
      "खिलाड़ियों की प्रोफ़ाइल, रेड और टैकल अंक, सुपर 10, हाई 5, सुपर रेड व सुपर टैकल "
      "जैसी हर जानकारी सरल हिंदी में मौजूद है।",
      "प्रदीप नरवाल, पवन सहरावत, राहुल चौधरी, नवीन कुमार, अर्जुन देशवाल और "
      "फ़ज़ेल अत्राचली जैसे दिग्गजों से लेकर उभरते सितारों तक — हर खिलाड़ी के आँकड़े "
      "देखें। इसके अलावा सभी 12 टीमों का इतिहास, हर पीकेएल सीज़न के चैंपियन और शीर्ष "
      "प्रदर्शक, सर्वकालिक रिकॉर्ड, और दो खिलाड़ियों की हेड-टू-हेड तुलना भी यहाँ "
      "उपलब्ध है। हमारा लक्ष्य है कबड्डी के समृद्ध आँकड़ों को हिंदी में हर प्रशंसक तक पहुँचाना।",
    ], heading='हिंदी में कबड्डी सांख्यिकी')}</div>
    """
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND_EN,
              "alternateName": BRAND, "url": SITE, "inLanguage": "hi",
              "description": "हिंदी में कबड्डी सांख्यिकी और रिकॉर्ड",
              "potentialAction": {"@type": "SearchAction",
                                  "target": SITE + "/players/?q={search_term_string}",
                                  "query-input": "required name=search_term_string"}}
    desc = ("हिंदी में कबड्डी के विस्तृत आँकड़े — प्रो कबड्डी लीग के खिलाड़ी, टीमें, हर सीज़न का "
            "ब्योरा, रेड व टैकल रिकॉर्ड, सुपर 10, हाई 5 और हेड-टू-हेड तुलना।")
    write("index.html", page(f"{BRAND} — हिंदी में कबड्डी सांख्यिकी | KabaddiStats",
                             desc, "/", depth, body, active="home", jsonld=jsonld), "1.0")


# =========================================================== PLAYER PROFILE ===
def build_player(p):
    depth = 2
    teamhtml = " · ".join(team_link(t, depth) for t in p["teams"][:5])
    tiles = f"""<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {stat('रेड अंक', f"{p['raid']:,}")}
      {stat('टैकल अंक', f"{p['tackle']:,}")}
      {stat('कुल अंक', f"{p['total']:,}")}
      {stat('सुपर 10' if p['role'] != 'defender' else 'हाई 5', p['super10'] if p['role'] != 'defender' else p['high5'])}</div>"""

    # full stat grid
    rows = [
        ("रेड अंक", f"{p['raid']:,}"), ("टैकल अंक", f"{p['tackle']:,}"),
        ("कुल अंक", f"{p['total']:,}"), ("सुपर 10", p['super10']),
        ("हाई 5", p['high5']), ("मैच", p['matches'] or '—'),
        ("सीज़न", p['seasons'] or '—'), ("भूमिका", role_pill_label(p['role'])),
    ]
    cells = "".join(
        f'<div class="px-3 py-2"><div class="text-xs text-kb-text hi">{l}</div>'
        f'<div class="font-heading font-bold text-kb-ink tnum">{v}</div></div>' for l, v in rows)
    statblock = f"""<div class="bg-kb-card border border-kb-border rounded-xl overflow-hidden mb-6">
      <div class="flex items-center justify-between px-4 py-2.5 bg-kb-bg border-b border-kb-border">
        <span class="hi font-heading font-bold text-kb-ink">पीकेएल करियर आँकड़े</span>{role_badge(p['role'])}</div>
      <div class="grid grid-cols-2 sm:grid-cols-4 divide-x divide-y divide-kb-border">{cells}</div></div>"""

    nat_line = "" if p["nat"] == "भारत" else f'<span class="hi text-sm text-kb-text">· {p["nat"]}</span>'
    body = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 mb-6">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-xl mat-stripe text-white flex items-center justify-center font-heading font-extrabold text-2xl shrink-0">{esc(p['name'][0])}</div>
        <div class="min-w-0">
          <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight">{esc(p['name'])}</h1>
          <div class="hi text-lg text-kb-orange font-semibold">{p['name_hi']} {nat_line}</div>
          <div class="hi text-sm text-kb-text mt-1">{teamhtml}</div>
          <div class="flex flex-wrap gap-1.5 mt-2">{role_badge(p['role'])}</div>
        </div>
      </div>
    </div>
    {tiles}
    {C.player_intro_html(p, depth)}
    {section_title('विस्तृत आँकड़े')}
    {statblock}
    <div class="mt-6 flex flex-wrap gap-3">
      <a href="{"../"*depth}compare/" class="hi px-4 py-2 rounded-lg bg-kb-orange text-white text-sm font-semibold hover:bg-kb-dark">तुलना करें →</a>
      <a href="{"../"*depth}players/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm font-semibold hover:border-kb-orange">सभी खिलाड़ी</a>
    </div>
    """
    role_hi = role_pill_label(p['role'])
    desc = (f"{p['name']} ({p['name_hi']}) के कबड्डी आँकड़े — प्रो कबड्डी लीग में {role_hi} के रूप में "
            f"{p['raid']:,} रेड अंक और {p['tackle']:,} टैकल अंक। सुपर 10, हाई 5 और करियर रिकॉर्ड हिंदी में।")[:300]
    title = f"{p['name']} {p['name_hi']} — कबड्डी आँकड़े"
    jsonld = {"@context": "https://schema.org", "@type": "Person", "name": p['name'],
              "alternateName": p['name_hi'], "url": f"{SITE}/players/{p['id']}/",
              "jobTitle": "Kabaddi Player", "nationality": p["nat"]}
    trail = [("होम", "../../"), ("खिलाड़ी", "../../players/"), (p['name'], None)]
    write(f"players/{p['id']}/index.html",
          page(title, desc, f"/players/{p['id']}/", depth, body,
               active="players", trail=trail, jsonld=jsonld, og_type="profile"), "0.7")
    search_rows.append([p['name'], f"/players/{p['id']}/", "खिलाड़ी",
                        f"{p['name']} {p['name_hi']} {role_hi} kabaddi khiladi {p['nat']}".lower()])


def build_players_index():
    depth = 1
    by_total = sorted(PLAYERS, key=total_pts, reverse=True)
    rows = []
    for i, p in enumerate(by_total):
        rows.append([f'<span class="text-kb-text tnum">{i+1}</span>',
                     plink(p["id"], depth),
                     role_badge(p["role"]),
                     f'<span class="hi text-xs text-kb-text">{esc(TEAMS[p["teams"][0]]["name_hi"]) if p["teams"] else ""}</span>',
                     f'{p["raid"]:,}', f'{p["tackle"]:,}', f'{p["total"]:,}'])
    body = f"""
    {page_h1('सभी खिलाड़ी', f'करियर कुल अंक के अनुसार शीर्ष {len(PLAYERS)} खिलाड़ी — किसी भी नाम पर क्लिक करें')}
    <div class="mb-4"><button onclick="KB_search()" class="hi w-full sm:w-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-kb-border bg-white text-kb-text text-left hover:border-kb-orange">{icon('search','w-4 h-4')}खिलाड़ी का नाम खोजें…</button></div>
    {table([T['rank'], T['player'], T['role'], T['team'], T['raid_pts'], T['tackle_pts'], T['total_pts']], rows, align_right={4,5,6})}
    """
    desc = ("प्रो कबड्डी लीग के शीर्ष खिलाड़ियों की पूरी सूची — रेडर और डिफेंडर के रेड अंक, टैकल अंक, "
            "सुपर 10, हाई 5 और करियर रिकॉर्ड हिंदी में।")
    write("players/index.html", page("सभी कबड्डी खिलाड़ी — आँकड़े व रिकॉर्ड | कबड्डी आँकड़े",
                                      desc, "/players/", depth, body, active="players",
                                      trail=[("होम", "../"), ("खिलाड़ी", None)]), "0.8")
    search_rows.append(["सभी खिलाड़ी", "/players/", "पेज", "players khiladi list sabhi kabaddi"])


# ================================================================== TEAMS =====
def _team_players(team_slug):
    return [p for p in PLAYERS if team_slug in p["teams"]]


def build_teams_index():
    depth = 1
    cards = ""
    for ts, t in sorted(TEAMS.items(), key=lambda kv: (-len(kv[1]["titles"]), kv[1]["name"])):
        title_txt = (f'{len(t["titles"])} ख़िताब' if t["titles"] else "ख़िताब नहीं")
        cards += f"""<a href="{ts}/" class="block bg-kb-card border border-kb-border rounded-xl p-5 hover:border-kb-orange hover:shadow-md transition">
          <div class="flex items-center gap-2 mb-1"><span class="w-3 h-3 rounded-full" style="background:{t['color']}"></span>
          <span class="font-heading font-extrabold text-lg text-kb-ink hi">{esc(t['name_hi'])}</span></div>
          <div class="hi text-sm text-kb-text mb-2">{esc(t['city'])}, {esc(t['state'])}</div>
          <div class="flex items-center gap-2 text-sm"><span class="hi inline-flex items-center gap-1 text-kb-orange font-semibold">{icon('trophy','w-4 h-4')}{title_txt}</span>
          <span class="hi text-kb-text">· {t['est']} से</span></div></a>"""
    body = f"""{page_h1('सभी टीमें', 'प्रो कबड्डी लीग की सभी 12 फ़्रेंचाइज़ी — ख़िताब के अनुसार')}
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{cards}</div>"""
    desc = "प्रो कबड्डी लीग की सभी 12 टीमें — पटना पाइरेट्स, यू मुंबा, जयपुर पिंक पैंथर्स समेत हर टीम का इतिहास, ख़िताब और प्रमुख खिलाड़ी हिंदी में।"
    write("teams/index.html", page("सभी कबड्डी टीमें — पीकेएल फ़्रेंचाइज़ी | कबड्डी आँकड़े",
                                    desc, "/teams/", depth, body, active="teams",
                                    trail=[("होम", "../"), ("टीमें", None)]), "0.8")
    search_rows.append(["सभी टीमें", "/teams/", "पेज", "teams teamein pkl franchise kabaddi"])


def build_team(team_slug, t):
    depth = 2
    titles = t["titles"]
    # title timeline
    title_chips = ""
    for s in SEASONS:
        if s["champion"] == team_slug:
            title_chips += (f'<a href="../../seasons/season-{s["num"]}/" class="hi inline-flex items-center gap-1 px-3 py-1.5 rounded-lg '
                            f'bg-kb-orange text-white text-sm font-semibold">{icon("trophy","w-4 h-4")}सीज़न {s["num"]}</a>')
        elif s["runner_up"] == team_slug:
            title_chips += (f'<a href="../../seasons/season-{s["num"]}/" class="hi inline-flex items-center gap-1 px-3 py-1.5 rounded-lg '
                            f'border border-kb-border bg-white text-kb-text text-sm">उपविजेता · सीज़न {s["num"]}</a>')
    if not title_chips:
        title_chips = '<span class="hi text-kb-text text-sm">अभी तक कोई फ़ाइनल नहीं।</span>'

    tiles = f"""<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {stat('ख़िताब', len(titles))}
      {stat('उपविजेता', len(t['runner_up']))}
      {stat('स्थापना', t['est'])}
      {stat('गृह राज्य', '', t['state'])}</div>"""

    # roster
    roster = _team_players(team_slug)
    roster.sort(key=total_pts, reverse=True)
    rows = []
    for i, p in enumerate(roster):
        rows.append([f'<span class="text-kb-text tnum">{i+1}</span>', plink(p["id"], depth),
                     f'<span class="hi text-xs">{role_badge(p["role"])}</span>',
                     f'{p["raid"]:,}', f'{p["tackle"]:,}', f'{p["total"]:,}'])
    roster_html = (table([T['rank'], T['player'], T['role'], T['raid_pts'], T['tackle_pts'], T['total_pts']],
                         rows, align_right={3,4,5}) if rows
                   else '<p class="hi text-kb-text">इस टीम के प्रमुख खिलाड़ियों का डेटा शीघ्र जोड़ा जाएगा।</p>')

    body = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 mb-6" style="border-top:4px solid {t['color']}">
      <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight hi">{esc(t['name_hi'])}</h1>
      <div class="text-lg text-kb-text">{esc(t['name'])}</div>
      <div class="hi text-sm text-kb-text mt-1">{esc(t['city'])}, {esc(t['state'])} · स्वामित्व: {esc(t['owner'])}</div>
    </div>
    {tiles}
    {C.team_intro_html(t, depth)}
    {section_title('ख़िताब व फ़ाइनल')}
    <div class="flex flex-wrap gap-2 mb-8">{title_chips}</div>
    {section_title('प्रमुख खिलाड़ी', 'इस टीम से जुड़े रहे शीर्ष खिलाड़ी (करियर कुल अंक)')}
    {roster_html}
    """
    title_txt = (f"{len(titles)} बार चैंपियन" if titles else "पीकेएल फ़्रेंचाइज़ी")
    desc = (f"{t['name_hi']} ({t['name']}) — {t['city']} की प्रो कबड्डी लीग टीम, {title_txt}। "
            f"टीम का इतिहास, ख़िताब, सीज़न और प्रमुख खिलाड़ी हिंदी में।")[:300]
    jsonld = {"@context": "https://schema.org", "@type": "SportsTeam", "name": t['name'],
              "alternateName": t['name_hi'], "sport": "Kabaddi", "url": f"{SITE}/teams/{team_slug}/",
              "location": {"@type": "Place", "name": f"{t['city']}, {t['state']}"}}
    write(f"teams/{team_slug}/index.html",
          page(f"{t['name_hi']} — पीकेएल टीम इतिहास | कबड्डी आँकड़े",
               desc, f"/teams/{team_slug}/", depth, body, active="teams",
               trail=[("होम", "../../"), ("टीमें", "../"), (t['name_hi'], None)],
               jsonld=jsonld), "0.7")
    search_rows.append([t['name_hi'], f"/teams/{team_slug}/", "टीम",
                        f"{t['name']} {t['name_hi']} {t['city']} pkl team kabaddi".lower()])


# ================================================================ SEASONS =====
def build_seasons_index():
    depth = 1
    rows = []
    for s in reversed(SEASONS):
        ch = TEAMS[s["champion"]]
        rows.append([
            f'<a href="season-{s["num"]}/" class="font-semibold text-kb-ink hover:text-kb-orange">सीज़न {s["num"]}</a>',
            f'<span class="hi text-kb-text">{s["year"]}</span>',
            f'<a href="../teams/{s["champion"]}/" class="hi text-kb-orange font-medium hover:underline">{esc(ch["name_hi"])}</a>',
            f'<span class="hi text-kb-text">{esc(TEAMS[s["runner_up"]]["name_hi"])}</span>',
            f'<span class="tnum">{s["score"]}</span>',
            f'<span class="hi">{esc(s["mvp"][0])}</span>',
        ])
    body = f"""{page_h1('सभी पीकेएल सीज़न', 'प्रो कबड्डी लीग का हर सीज़न — चैंपियन, फ़ाइनल और एमवीपी')}
      {table(['सीज़न', 'वर्ष', T['champion'], 'उपविजेता', 'फ़ाइनल', 'एमवीपी'], rows)}"""
    desc = f"प्रो कबड्डी लीग के सभी सीज़न ({SEASON_RANGE_HI}) — हर सीज़न के चैंपियन, उपविजेता, फ़ाइनल स्कोर, शीर्ष रेडर, शीर्ष डिफेंडर और एमवीपी हिंदी में।"
    write("seasons/index.html", page("पीकेएल सभी सीज़न — चैंपियन व फ़ाइनल | कबड्डी आँकड़े",
                                      desc, "/seasons/", depth, body, active="seasons",
                                      trail=[("होम", "../"), ("सीज़न", None)]), "0.8")
    search_rows.append(["सभी सीज़न", "/seasons/", "पेज", "seasons pkl season champion final kabaddi"])


def build_season(s, prev_s, next_s):
    depth = 2
    ch, ru = TEAMS[s["champion"]], TEAMS[s["runner_up"]]
    champ_card = f"""<div class="rounded-2xl mat-stripe text-white p-6 mb-6">
      <div class="hi text-sm font-semibold opacity-90 mb-1">सीज़न {s['num']} चैंपियन</div>
      <div class="font-heading font-extrabold text-2xl mb-2 hi flex items-center gap-2.5">{icon('trophy','w-7 h-7')}<a href="../../teams/{s['champion']}/" class="hover:underline">{esc(ch['name_hi'])}</a></div>
      <div class="hi text-sm">फ़ाइनल में <b>{esc(ru['name_hi'])}</b> को <b class="tnum">{s['score']}</b> से हराया · {esc(s['venue'])}</div>
    </div>"""

    def perf(label, name, team_slug, val, vlabel):
        return (f'<div class="bg-kb-card border border-kb-border rounded-xl p-4">'
                f'<div class="hi text-xs font-semibold text-kb-orange uppercase tracking-wide mb-1">{label}</div>'
                f'<div class="font-heading font-bold text-kb-ink">{esc(name)}</div>'
                f'<div class="hi text-sm text-kb-text">{esc(TEAMS[team_slug]["name_hi"])} · '
                f'<b class="text-kb-ink tnum">{val}</b> {vlabel}</div></div>')

    perfs = f"""<section class="grid sm:grid-cols-3 gap-3 mb-6">
      {perf('शीर्ष रेडर', s['raider'][0], s['raider'][1], s['raider'][2], 'रेड अंक')}
      {perf('शीर्ष डिफेंडर', s['defender'][0], s['defender'][1], s['defender'][2], 'टैकल अंक')}
      <div class="bg-kb-card border border-kb-border rounded-xl p-4">
        <div class="hi text-xs font-semibold text-kb-orange uppercase tracking-wide mb-1">सबसे मूल्यवान खिलाड़ी</div>
        <div class="font-heading font-bold text-kb-ink">{esc(s['mvp'][0])}</div>
        <div class="hi text-sm text-kb-text">{esc(TEAMS[s['mvp'][1]]['name_hi'])}</div></div>
    </section>"""

    # finalists facts table
    facts = table(['विवरण', 'जानकारी'], [
        ['<span class="hi">चैंपियन</span>', f'<a href="../../teams/{s["champion"]}/" class="hi text-kb-orange hover:underline">{esc(ch["name_hi"])}</a>'],
        ['<span class="hi">उपविजेता</span>', f'<a href="../../teams/{s["runner_up"]}/" class="hi text-kb-orange hover:underline">{esc(ru["name_hi"])}</a>'],
        ['<span class="hi">फ़ाइनल स्कोर</span>', f'<span class="tnum">{s["score"]}</span>'],
        ['<span class="hi">फ़ाइनल स्थल</span>', f'<span class="hi">{esc(s["venue"])}</span>'],
        ['<span class="hi">वर्ष</span>', f'<span class="hi">{s["year"]}</span>'],
    ])

    # prev/next nav
    navs = '<div class="flex justify-between mt-8">'
    navs += (f'<a href="../season-{prev_s["num"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">← सीज़न {prev_s["num"]}</a>'
             if prev_s else '<span></span>')
    navs += (f'<a href="../season-{next_s["num"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">सीज़न {next_s["num"]} →</a>'
             if next_s else '<span></span>')
    navs += '</div>'

    body = f"""
    <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight hi mb-1">प्रो कबड्डी लीग सीज़न {s['num']}</h1>
    <p class="hi text-kb-text mb-5">{s['year']}</p>
    {champ_card}
    {C.season_intro_html(s)}
    {section_title('शीर्ष प्रदर्शक')}
    {perfs}
    {section_title('फ़ाइनल विवरण')}
    {facts}
    <div class="mt-6 flex flex-wrap gap-3">
      <a href="../../standings/season-{s['num']}/" class="hi inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-kb-orange text-white text-sm font-semibold hover:bg-kb-dark transition">{icon('trophy','w-4 h-4')}सीज़न {s['num']} की अंक तालिका देखें →</a>
      <a href="../../matches/season-{s['num']}/" class="hi inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-kb-border bg-white text-sm font-semibold hover:border-kb-orange transition">{icon('calendar','w-4 h-4')}सीज़न {s['num']} के सभी मैच परिणाम देखें →</a>
    </div>
    {navs}
    """
    desc = (f"प्रो कबड्डी लीग सीज़न {s['num']} ({s['year']}) — {ch['name_hi']} चैंपियन, फ़ाइनल में "
            f"{ru['name_hi']} को {s['score']} से हराया। शीर्ष रेडर {s['raider'][0]}, एमवीपी {s['mvp'][0]}।")[:300]
    write(f"seasons/season-{s['num']}/index.html",
          page(f"पीकेएल सीज़न {s['num']} ({s['year']}) — चैंपियन व आँकड़े | कबड्डी आँकड़े",
               desc, f"/seasons/season-{s['num']}/", depth, body, active="seasons",
               trail=[("होम", "../../"), ("सीज़न", "../"), (f"सीज़न {s['num']}", None)]), "0.7")
    search_rows.append([f"पीकेएल सीज़न {s['num']}", f"/seasons/season-{s['num']}/", "सीज़न",
                        f"season {s['num']} {s['year']} {ch['name']} champion pkl kabaddi".lower()])


# ================================================================ MATCHES =====
_HI_MONTHS = ["", "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई",
              "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]


def fmt_date_hi(iso):
    y, mo, da = iso.split("-")
    return f"{int(da)} {_HI_MONTHS[int(mo)]} {y}"


def _match_teams_cell(m, depth):
    """team a vs team b, winner side in bold orange."""
    a_win = m["sa"] > m["sb"]
    b_win = m["sb"] > m["sa"]

    def side(slug, win):
        t = TEAMS.get(slug)
        label = t["name_hi"] if t else esc(slug)
        cls = "text-kb-orange font-bold" if win else "text-kb-ink"
        return (f'<a href="{"../"*depth}teams/{slug}/" class="hi {cls} hover:underline">{esc(label)}</a>')
    return (f'{side(m["a"], a_win)} <span class="text-kb-text text-xs">बनाम</span> '
            f'{side(m["b"], b_win)}')


def _stage_pill(stage):
    is_final = "फ़ाइनल" in stage and "सेमी" not in stage
    is_knockout = (is_final or "सेमी" in stage or "एलिमिनेटर" in stage
                   or "क्वालिफ़ायर" in stage or "प्ले-इन" in stage)
    cls = ("bg-kb-orange text-white" if is_final
           else "bg-orange-50 text-orange-700 border border-orange-200" if is_knockout
           else "bg-kb-bg text-kb-text border border-kb-border")
    return f'<span class="hi inline-block text-xs font-semibold px-2 py-0.5 rounded {cls} whitespace-nowrap">{esc(stage)}</span>'


def _match_rows(matches, depth):
    rows = []
    for m in matches:
        score = f'{m["sa"]}–{m["sb"]}'
        rows.append([
            _stage_pill(m["stage"]),
            f'<span class="hi text-kb-text whitespace-nowrap">{fmt_date_hi(m["date"])}</span>',
            _match_teams_cell(m, depth),
            f'<span class="tnum font-semibold text-kb-ink">{score}</span>',
            f'<span class="hi text-xs text-kb-text">{esc(m["venue"])}</span>',
        ])
    return rows


def build_matches_index():
    depth = 1
    cards = ""
    for s in reversed(SEASONS):
        ms = MATCHES.get(s["num"], [])
        final = next((m for m in ms if "फ़ाइनल" in m["stage"] and "सेमी" not in m["stage"]), None)
        ch = TEAMS[s["champion"]]
        fin_txt = ""
        if final:
            ru = TEAMS[s["runner_up"]]
            fin_txt = (f'<div class="hi text-sm text-kb-text mt-2">फ़ाइनल: '
                       f'<b class="text-kb-ink">{esc(ch["name_hi"])}</b> '
                       f'<span class="tnum">{final["sa"]}–{final["sb"]}</span> '
                       f'{esc(ru["name_hi"])}</div>')
        cards += f"""<a href="season-{s['num']}/" class="block bg-kb-card border border-kb-border rounded-xl p-5 hover:border-kb-orange hover:shadow-md transition">
          <div class="flex items-center justify-between">
            <span class="font-heading font-extrabold text-lg text-kb-ink hi">सीज़न {s['num']}</span>
            <span class="hi text-sm text-kb-text">{s['year']}</span></div>
          <div class="hi text-sm text-kb-orange font-semibold mt-1 flex items-center gap-1.5">{icon('trophy','w-4 h-4')}{esc(ch['name_hi'])}</div>
          {fin_txt}
          <div class="hi text-xs text-kb-text mt-2">{len(ms)} प्रमुख मैच →</div></a>"""

    total_matches = sum(len(v) for v in MATCHES.values())
    body = f"""{page_h1('पीकेएल मैच परिणाम', 'प्रो कबड्डी लीग के हर सीज़न के प्रमुख मुक़ाबले — उद्घाटन मैच, प्लेऑफ़ और फ़ाइनल')}
      {C.prose([
        "यहाँ प्रो कबड्डी लीग के सभी ग्यारह सीज़नों के चुनिंदा मैच परिणाम एक जगह उपलब्ध हैं। "
        "हर सीज़न के लिए उद्घाटन मैच, कुछ प्रमुख लीग-चरण मुक़ाबले और पूरा प्लेऑफ़ क्रम "
        "(एलिमिनेटर, सेमीफ़ाइनल और फ़ाइनल) दिया गया है — तारीख़, टीमें, स्कोर और स्थल के साथ।",
      ])}
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{cards}</div>"""
    desc = (f"प्रो कबड्डी लीग के सभी सीज़न ({SEASON_RANGE_HI}) के मैच परिणाम — उद्घाटन मैच, सेमीफ़ाइनल, "
            "फ़ाइनल और प्रमुख लीग मुक़ाबलों के स्कोर, तारीख़ और स्थल हिंदी में।")
    write("matches/index.html", page("पीकेएल मैच परिणाम — सभी सीज़न | कबड्डी आँकड़े",
                                      desc, "/matches/", depth, body, active="matches",
                                      trail=[("होम", "../"), ("मैच परिणाम", None)]), "0.8")
    search_rows.append(["मैच परिणाम", "/matches/", "पेज",
                        "matches match results parinaam pkl kabaddi final semifinal"])


def build_season_matches(s, prev_s, next_s):
    depth = 2
    num = s["num"]
    matches = MATCHES.get(num, [])
    ch, ru = TEAMS[s["champion"]], TEAMS[s["runner_up"]]
    rows = _match_rows(matches, depth)

    intro = C.prose([
        f"प्रो कबड्डी लीग <b>सीज़न {num}</b> ({s['year']}) के प्रमुख मैच परिणाम — "
        f"उद्घाटन मुक़ाबले से लेकर फ़ाइनल तक। इस सीज़न का ख़िताब "
        f"<b>{esc(ch['name_hi'])}</b> ने जीता, जिसने फ़ाइनल में {esc(ru['name_hi'])} को "
        f"{s['score']} से हराया।",
    ], heading=f"सीज़न {num} मैच परिणाम")

    table_html = (table(['चरण', 'तारीख़', 'मुक़ाबला', 'स्कोर', 'स्थल'], rows, align_right={3})
                  if rows else '<p class="hi text-kb-text">इस सीज़न के मैच डेटा शीघ्र जोड़े जाएँगे।</p>')

    # prev/next nav across seasons' match pages
    navs = '<div class="flex justify-between mt-8">'
    navs += (f'<a href="../season-{prev_s["num"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">← सीज़न {prev_s["num"]} के मैच</a>'
             if prev_s else '<span></span>')
    navs += (f'<a href="../season-{next_s["num"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">सीज़न {next_s["num"]} के मैच →</a>'
             if next_s else '<span></span>')
    navs += '</div>'

    body = f"""
    <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight hi mb-1">पीकेएल सीज़न {num} — मैच परिणाम</h1>
    <p class="hi text-kb-text mb-5">{s['year']} · {len(matches)} प्रमुख मुक़ाबले</p>
    {intro}
    {section_title('मैच परिणाम', 'चरण, तारीख़, टीमें, स्कोर और स्थल')}
    {table_html}
    <div class="mt-6 flex flex-wrap gap-3">
      <a href="../../seasons/season-{num}/" class="hi px-4 py-2 rounded-lg bg-kb-orange text-white text-sm font-semibold hover:bg-kb-dark">सीज़न {num} का पूरा ब्योरा →</a>
      <a href="../" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm font-semibold hover:border-kb-orange">सभी सीज़न के मैच</a>
    </div>
    {navs}
    """
    desc = (f"प्रो कबड्डी लीग सीज़न {num} ({s['year']}) के मैच परिणाम — उद्घाटन मैच, सेमीफ़ाइनल और "
            f"फ़ाइनल के स्कोर, तारीख़ और स्थल। {ch['name_hi']} ने {ru['name_hi']} को फ़ाइनल में "
            f"{s['score']} से हराया।")[:300]
    write(f"matches/season-{num}/index.html",
          page(f"पीकेएल सीज़न {num} मैच परिणाम ({s['year']}) | कबड्डी आँकड़े",
               desc, f"/matches/season-{num}/", depth, body, active="matches",
               trail=[("होम", "../../"), ("मैच परिणाम", "../"), (f"सीज़न {num}", None)]), "0.7")
    search_rows.append([f"सीज़न {num} मैच परिणाम", f"/matches/season-{num}/", "मैच",
                        f"season {num} {s['year']} matches results parinaam final pkl kabaddi".lower()])


# ================================================================ STANDINGS ===
def _fmt_diff(d):
    if d > 0:
        return f'<span class="tnum text-green-600 font-semibold">+{d}</span>'
    if d < 0:
        return f'<span class="tnum text-red-600 font-semibold">{d}</span>'
    return '<span class="tnum text-kb-text">0</span>'


def _standings_table(season_num, depth):
    rows = STANDINGS.get(season_num, [])
    head = ['#', 'टीम', 'खेले', 'जीते', 'हारे', 'टाई', 'पक्ष में', 'विपक्ष', 'अंतर', 'अंक', 'प्लेऑफ़']
    align_r = {2, 3, 4, 5, 6, 7, 8, 9}
    thead = "".join(
        f'<th class="hi px-3 py-2 text-{("right" if i in align_r else "left")} '
        f'text-xs font-bold text-kb-text uppercase tracking-wide whitespace-nowrap">{h}</th>'
        for i, h in enumerate(head))
    body = ""
    for pos, r in enumerate(rows, 1):
        t = TEAMS.get(r["team"], {})
        label = t.get("name_hi", esc(r["team"]))
        is_champ = pos == 1
        is_ru = pos == 2
        # position badge
        if is_champ:
            pos_cell = f'<span class="inline-flex items-center gap-1 text-kb-orange font-bold">{icon("trophy","w-4 h-4")}{pos}</span>'
        else:
            pos_cell = f'<span class="font-bold text-kb-ink">{pos}</span>'
        dot = (f'<span class="inline-block w-2.5 h-2.5 rounded-full align-middle mr-2" '
               f'style="background:{t.get("color","#999")}"></span>')
        team_cell = (f'{dot}<a href="{"../"*depth}teams/{r["team"]}/" class="hi font-medium '
                     f'text-kb-ink hover:text-kb-orange">{esc(label)}</a>')
        if is_champ:
            team_cell += ' <span class="hi text-xs text-kb-orange font-semibold">(चैंपियन)</span>'
        elif is_ru:
            team_cell += ' <span class="hi text-xs text-kb-text font-semibold">(उपविजेता)</span>'
        if r["q"]:
            qual = '<span class="hi inline-block text-xs font-semibold px-2 py-0.5 rounded bg-green-50 text-green-700 border border-green-200 whitespace-nowrap">क्वालिफ़ाई</span>'
        else:
            qual = '<span class="hi text-xs text-kb-text">—</span>'
        cells = [
            pos_cell, team_cell,
            f'<span class="tnum">{r["p"]}</span>',
            f'<span class="tnum font-semibold text-kb-ink">{r["w"]}</span>',
            f'<span class="tnum">{r["l"]}</span>',
            f'<span class="tnum">{r["t"]}</span>',
            f'<span class="tnum">{r["sf"]}</span>',
            f'<span class="tnum">{r["sa"]}</span>',
            _fmt_diff(r["diff"]),
            f'<span class="tnum font-bold text-kb-ink">{r["pts"]}</span>',
            qual,
        ]
        tds = ""
        for i, c in enumerate(cells):
            a = "right tnum" if i in align_r else "left"
            tds += f'<td class="px-3 py-2.5 text-{a} text-sm whitespace-nowrap">{c}</td>'
        rowcls = "bg-orange-50/60" if r["q"] else ""
        body += f"<tr class='border-t border-kb-border {rowcls}'>{tds}</tr>"
    return (f'<div class="overflow-x-auto bg-kb-card border border-kb-border rounded-xl">'
            f'<table class="w-full min-w-full"><thead class="bg-kb-bg">'
            f'<tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>')


def _standings_legend():
    return ('<div class="flex flex-wrap items-center gap-x-5 gap-y-1.5 mt-3 text-xs text-kb-text hi">'
            '<span class="flex items-center gap-1.5"><span class="inline-block w-3 h-3 rounded bg-orange-50/60 border border-kb-border"></span>प्लेऑफ़ में क्वालिफ़ाई</span>'
            '<span>खेले = कुल मैच</span><span>जीते / हारे / टाई</span>'
            '<span>पक्ष में = कुल अंक बनाए</span><span>विपक्ष = अंक दिए</span>'
            '<span>अंतर = अंक अंतर</span><span>अंक = लीग अंक (जीत = 5, टाई = 3, बोनस = 1)</span></div>')


def build_standings_index():
    depth = 1
    cards = ""
    for s in reversed(SEASONS):
        rows = STANDINGS.get(s["num"], [])
        ch = TEAMS[s["champion"]]
        ru = TEAMS[s["runner_up"]]
        topper = TEAMS[rows[0]["team"]] if rows else ch
        cards += f"""<a href="season-{s['num']}/" class="block bg-kb-card border border-kb-border rounded-xl p-5 hover:border-kb-orange hover:shadow-md transition">
          <div class="flex items-center justify-between">
            <span class="font-heading font-extrabold text-lg text-kb-ink hi">सीज़न {s['num']}</span>
            <span class="hi text-sm text-kb-text">{s['year']}</span></div>
          <div class="hi text-sm text-kb-orange font-semibold mt-1 flex items-center gap-1.5">{icon('trophy','w-4 h-4')}{esc(ch['name_hi'])}</div>
          <div class="hi text-xs text-kb-text mt-1">उपविजेता: {esc(ru['name_hi'])}</div>
          <div class="hi text-xs text-kb-text mt-2">{len(rows)} टीमें · पूरी अंक तालिका →</div></a>"""

    body = f"""{page_h1('पीकेएल अंक तालिका', 'प्रो कबड्डी लीग के हर सीज़न की पूरी टीम रैंकिंग, जीत-हार और अंक')}
      {C.prose([
        "यहाँ प्रो कबड्डी लीग के सभी ग्यारह सीज़नों की विस्तृत अंक तालिका उपलब्ध है। "
        "हर सीज़न के लिए टीमों की अंतिम रैंकिंग, खेले गए मैच, जीत, हार, टाई, बनाए और दिए गए "
        "अंक, अंक अंतर तथा कुल लीग अंक दिए गए हैं — साथ ही यह भी कि कौन-सी टीमें प्लेऑफ़ में "
        "पहुँचीं। पहले चार सीज़नों में आठ-आठ टीमें थीं; सीज़न 5 से लीग में बारह टीमें खेलती हैं।",
      ])}
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{cards}</div>"""
    desc = (f"प्रो कबड्डी लीग के सभी सीज़न ({SEASON_RANGE_HI}) की अंक तालिका — टीम रैंकिंग, जीत-हार, "
            "अंक अंतर, कुल अंक और प्लेऑफ़ क्वालिफ़िकेशन हिंदी में।")
    write("standings/index.html", page("पीकेएल अंक तालिका — सभी सीज़न | कबड्डी आँकड़े",
                                        desc, "/standings/", depth, body, active="standings",
                                        trail=[("होम", "../"), ("अंक तालिका", None)]), "0.8")
    search_rows.append(["अंक तालिका", "/standings/", "पेज",
                        "standings points table ank talika rankings pkl kabaddi"])


def build_season_standings(s, prev_s, next_s):
    depth = 2
    num = s["num"]
    rows = STANDINGS.get(num, [])
    ch, ru = TEAMS[s["champion"]], TEAMS[s["runner_up"]]
    n_q = sum(1 for r in rows if r["q"])

    intro = C.prose([
        f"प्रो कबड्डी लीग <b>सीज़न {num}</b> ({s['year']}) की पूरी अंक तालिका। इस सीज़न में "
        f"<b>{len(rows)}</b> टीमों ने हिस्सा लिया और शीर्ष <b>{n_q}</b> टीमें प्लेऑफ़ में पहुँचीं। "
        f"ख़िताब <b>{esc(ch['name_hi'])}</b> ने जीता, जिसने फ़ाइनल में {esc(ru['name_hi'])} को "
        f"{s['score']} से हराया।",
    ], heading=f"सीज़न {num} अंक तालिका")

    table_html = (_standings_table(num, depth) + _standings_legend()
                  if rows else '<p class="hi text-kb-text">इस सीज़न की अंक तालिका शीघ्र जोड़ी जाएगी।</p>')

    navs = '<div class="flex justify-between mt-8">'
    navs += (f'<a href="../season-{prev_s["num"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">← सीज़न {prev_s["num"]} अंक तालिका</a>'
             if prev_s else '<span></span>')
    navs += (f'<a href="../season-{next_s["num"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">सीज़न {next_s["num"]} अंक तालिका →</a>'
             if next_s else '<span></span>')
    navs += '</div>'

    body = f"""
    <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight hi mb-1">पीकेएल सीज़न {num} — अंक तालिका</h1>
    <p class="hi text-kb-text mb-5">{s['year']} · {len(rows)} टीमें · शीर्ष {n_q} प्लेऑफ़ में</p>
    {intro}
    {section_title('अंतिम अंक तालिका', 'स्थान, जीत-हार, अंक अंतर और कुल लीग अंक')}
    {table_html}
    <div class="mt-6 flex flex-wrap gap-3">
      <a href="../../seasons/season-{num}/" class="hi px-4 py-2 rounded-lg bg-kb-orange text-white text-sm font-semibold hover:bg-kb-dark">सीज़न {num} का पूरा ब्योरा →</a>
      <a href="../../matches/season-{num}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm font-semibold hover:border-kb-orange">सीज़न {num} के मैच परिणाम</a>
      <a href="../" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm font-semibold hover:border-kb-orange">सभी सीज़न की अंक तालिका</a>
    </div>
    {navs}
    """
    desc = (f"प्रो कबड्डी लीग सीज़न {num} ({s['year']}) अंक तालिका — सभी {len(rows)} टीमों की रैंकिंग, "
            f"जीत-हार, अंक अंतर और कुल अंक। {ch['name_hi']} चैंपियन, {ru['name_hi']} उपविजेता।")[:300]
    write(f"standings/season-{num}/index.html",
          page(f"पीकेएल सीज़न {num} अंक तालिका ({s['year']}) | कबड्डी आँकड़े",
               desc, f"/standings/season-{num}/", depth, body, active="standings",
               trail=[("होम", "../../"), ("अंक तालिका", "../"), (f"सीज़न {num}", None)]), "0.7")
    search_rows.append([f"सीज़न {num} अंक तालिका", f"/standings/season-{num}/", "अंक तालिका",
                        f"season {num} {s['year']} standings points table ank talika pkl kabaddi".lower()])


# ================================================================ RECORDS =====
def build_records():
    depth = 1
    # milestone cards
    mcards = ""
    for label, holder, val, detail in RECORD_MILESTONES:
        mcards += f"""<div class="bg-kb-card border border-kb-border rounded-xl p-4">
          <div class="hi text-xs font-semibold text-kb-orange uppercase tracking-wide mb-1">{label}</div>
          <div class="font-heading font-extrabold text-xl text-kb-ink hi">{esc(val)}</div>
          <div class="hi text-sm font-medium text-kb-ink">{esc(holder)}</div>
          <div class="hi text-xs text-kb-text mt-1 leading-relaxed">{esc(detail)}</div></div>"""

    # leaderboards
    boards = ""
    for key in ["career_raid", "career_tackle", "career_super10", "career_high5"]:
        label, items = RECORDS[key]
        rows = []
        for i, (pid, val, ctx) in enumerate(items):
            p = PLAYER_BY_ID.get(pid)
            nm = plink(pid, depth) if p else f'<span class="text-kb-ink">{esc(pid)}</span>'
            rows.append([f'<span class="text-kb-text tnum">{i+1}</span>', nm,
                         f'<span class="hi text-xs text-kb-text">{esc(ctx)}</span>',
                         f'<b class="text-kb-orange tnum">{val:,}</b>'])
        boards += (f'<div class="mb-8"><h3 class="hi font-heading font-bold text-lg text-kb-ink mb-3 '
                   f'flex items-center gap-2"><span class="w-1.5 h-5 rounded mat-stripe inline-block"></span>{label}</h3>'
                   f'{table([T["rank"], T["player"], "अवधि", "अंक"], rows, align_right={2,3})}</div>')

    body = f"""{page_h1('कबड्डी रिकॉर्ड', 'प्रो कबड्डी लीग के सर्वकालिक रिकॉर्ड और लीडरबोर्ड')}
      {section_title('प्रमुख रिकॉर्ड') and ''}
      <section class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-10">{mcards}</section>
      <h2 class="hi font-heading font-bold text-xl text-kb-ink mb-4 flex items-center gap-2"><span class="w-1.5 h-6 rounded mat-stripe inline-block"></span>सर्वकालिक लीडरबोर्ड</h2>
      {boards}"""
    desc = ("प्रो कबड्डी लीग के सर्वकालिक रिकॉर्ड हिंदी में — सर्वाधिक रेड अंक, सर्वाधिक टैकल अंक, "
            "सर्वाधिक सुपर 10, सर्वाधिक हाई 5, एक मैच में सर्वाधिक अंक और टीम रिकॉर्ड।")
    write("records/index.html", page("कबड्डी रिकॉर्ड — सर्वकालिक लीडरबोर्ड | कबड्डी आँकड़े",
                                      desc, "/records/", depth, body, active="records",
                                      trail=[("होम", "../"), ("रिकॉर्ड", None)]), "0.8")
    search_rows.append(["रिकॉर्ड", "/records/", "पेज", "records record leaderboard raid tackle super10 kabaddi"])


# ================================================================ COMPARE =====
COMPARE_PAIRS = [
    ("pardeep-narwal", "pawan-sehrawat"),
    ("pardeep-narwal", "maninder-singh"),
    ("pawan-sehrawat", "naveen-kumar"),
    ("arjun-deshwal", "maninder-singh"),
    ("rahul-chaudhari", "pardeep-narwal"),
    ("naveen-kumar", "arjun-deshwal"),
    ("anup-kumar", "rahul-chaudhari"),
    ("ajay-thakur", "rahul-chaudhari"),
    ("fazel-atrachali", "surjeet-singh"),
    ("manjeet-chhillar", "sandeep-narwal"),
    ("nitesh-kumar", "fazel-atrachali"),
    ("sachin-tanwar", "ashu-malik"),
    ("siddharth-desai", "vikash-kandola"),
    ("mohammadreza-shadloui", "manjeet-chhillar"),
    # raider vs raider
    ("fazel-atrachali", "manjeet-chhillar"),
    ("deepak-niwas-hooda", "maninder-singh"),
    ("pardeep-narwal", "naveen-kumar"),
    ("pawan-sehrawat", "arjun-deshwal"),
    ("maninder-singh", "naveen-kumar"),
    ("ajay-thakur", "pardeep-narwal"),
    ("maninder-singh", "pawan-sehrawat"),
    ("pardeep-narwal", "arjun-deshwal"),
    ("sachin-tanwar", "naveen-kumar"),
    ("vikash-kandola", "arjun-deshwal"),
    ("siddharth-desai", "pawan-sehrawat"),
    ("ashu-malik", "naveen-kumar"),
    ("rohit-kumar", "rahul-chaudhari"),
    ("nitin-tomar", "rishank-devadiga"),
    ("kashiling-adake", "rahul-chaudhari"),
    ("manjeet-tt", "v-ajith-kumar"),
    ("devank-dalal", "sachin-tanwar"),
    ("shrikant-jadhav", "rohit-gulia"),
    ("jang-kun-lee", "ajay-thakur"),
    ("surender-gill", "guman-singh"),
    # defender vs defender
    ("surjeet-singh", "manjeet-chhillar"),
    ("sandeep-narwal", "deepak-niwas-hooda"),
    ("mohammadreza-shadloui", "sandeep-narwal"),
    ("fazel-atrachali", "sunil-kumar"),
    ("nitesh-kumar", "sunil-kumar"),
    ("ravinder-pahal", "surender-nada"),
    ("girish-ernak", "fazel-atrachali"),
    ("vishal-bhardwaj", "sunil-kumar"),
    ("mohit-chhillar", "manjeet-chhillar"),
    ("mohammadreza-chiyaneh", "nitesh-kumar"),
    ("surender-nada", "fazel-atrachali"),
    # allrounder battles
    ("deepak-niwas-hooda", "rahul-chaudhari"),
    ("meraj-sheykh", "rishank-devadiga"),
    ("mohammad-nabibakhsh", "mohammadreza-shadloui"),
    ("rohit-gulia", "aslam-inamdar"),
]

RIVALRIES = [
    ("patna-pirates", "u-mumba",
     "पटना पाइरेट्स और यू मुंबा की भिड़ंत पीकेएल की सबसे पुरानी प्रतिद्वंद्विताओं में से एक है — दोनों ने शुरुआती सीज़न के कई फ़ाइनल और नॉकआउट मुक़ाबले खेले। प्रदीप नरवाल की रेडिंग और फ़ज़ल अतरचली की रक्षा के बीच की टक्कर इस मुक़ाबले की जान रही है।",
     27, 15, 12, ["सीज़न 3 फ़ाइनल: पटना पाइरेट्स 37-29 यू मुंबा", "सीज़न 1 लीग: यू मुंबा 35-22 पटना पाइरेट्स", "सीज़न 5 एलिमिनेटर: पटना पाइरेट्स 38-33 यू मुंबा"]),
    ("u-mumba", "puneri-paltan",
     "महाराष्ट्र डर्बी — मुंबई बनाम पुणे। दोनों टीमों के बीच के मुक़ाबले राज्य के गौरव की लड़ाई बन जाते हैं और स्टेडियम हमेशा खचाखच भरा रहता है।",
     26, 14, 12, ["सीज़न 4 लीग: यू मुंबा 32-30 पुनेरी पलटन", "सीज़न 9 एलिमिनेटर: पुनेरी पलटन 41-35 यू मुंबा", "सीज़न 10 लीग: पुनेरी पलटन 38-31 यू मुंबा"]),
    ("bengaluru-bulls", "telugu-titans",
     "दक्षिण भारत की दो उद्घाटन टीमों के बीच की टक्कर; रोहित कुमार और राहुल चौधरी के द्वंद्व ने इसे यादगार बनाया। शुरुआती सीज़न में तेलुगु का दबदबा था, बाद में बेंगलुरु ने पलड़ा भारी कर लिया।",
     24, 13, 11, ["सीज़न 6 फ़ाइनल राह पर बेंगलुरु का दबदबा", "सीज़न 2 लीग: तेलुगु टाइटन्स 34-28 बेंगलुरु बुल्स", "सीज़न 6 लीग: बेंगलुरु बुल्स 40-30 तेलुगु टाइटन्स"]),
    ("jaipur-pink-panthers", "dabang-delhi",
     "उत्तर भारत की दो हाई-प्रोफ़ाइल टीमें — अर्जुन देशवाल बनाम नवीन कुमार की रेडिंग जंग इस भिड़ंत का मुख्य आकर्षण है।",
     23, 11, 12, ["सीज़न 3 लीग: जयपुर पिंक पैंथर्स 33-29 दबंग दिल्ली", "सीज़न 8 लीग: दबंग दिल्ली 39-32 जयपुर पिंक पैंथर्स", "सीज़न 10 लीग: दबंग दिल्ली 35-31 जयपुर पिंक पैंथर्स"]),
    ("patna-pirates", "haryana-steelers",
     "सीज़न 11 के फ़ाइनल ने इस भिड़ंत को नई धार दी, जहाँ हरियाणा ने पटना को हराकर अपना पहला ख़िताब जीता। तब से यह मुक़ाबला पीकेएल की सबसे चर्चित प्रतिद्वंद्विताओं में गिना जाता है।",
     16, 9, 7, ["सीज़न 11 फ़ाइनल: हरियाणा स्टीलर्स 32-28 पटना पाइरेट्स", "सीज़न 6 लीग: पटना पाइरेट्स 35-30 हरियाणा स्टीलर्स", "सीज़न 9 लीग: हरियाणा स्टीलर्स 37-34 पटना पाइरेट्स"]),
    ("bengal-warriors", "dabang-delhi",
     "सीज़न 7 के फ़ाइनल की पुनरावृत्ति — बंगाल वॉरियर्स और दबंग दिल्ली की रोमांचक प्रतिद्वंद्विता। मनिंदर सिंह और नवीन कुमार दोनों टीमों के स्टार रेडर रहे।",
     20, 10, 10, ["सीज़न 7 फ़ाइनल: बंगाल वॉरियर्स 39-34 दबंग दिल्ली", "सीज़न 6 लीग: दबंग दिल्ली 36-30 बंगाल वॉरियर्स", "सीज़न 10 लीग: बंगाल वॉरियर्स 33-31 दबंग दिल्ली"]),
    ("patna-pirates", "bengaluru-bulls",
     "पीकेएल की दो सबसे सफल टीमें आमने-सामने — पटना पाइरेट्स के तीन ख़िताब बनाम बेंगलुरु बुल्स की दमदार रेडिंग। प्रदीप नरवाल और पवन सहरावत की मौजूदगी ने इस भिड़ंत को सुपरस्टार टक्कर बना दिया।",
     25, 13, 12, ["सीज़न 6 लीग: पटना पाइरेट्स 43-39 बेंगलुरु बुल्स", "सीज़न 5 लीग: बेंगलुरु बुल्स 38-35 पटना पाइरेट्स", "सीज़न 7 लीग: बेंगलुरु बुल्स 40-33 पटना पाइरेट्स"]),
    ("u-mumba", "jaipur-pink-panthers",
     "सीज़न 1 के फ़ाइनलिस्ट — जयपुर पिंक पैंथर्स ने उद्घाटन ख़िताब जीता तो यू मुंबा ने अगले सीज़न में बदला लिया। यह भिड़ंत पीकेएल के इतिहास की नींव है।",
     22, 12, 10, ["सीज़न 1 फ़ाइनल: जयपुर पिंक पैंथर्स 35-24 यू मुंबा", "सीज़न 2 लीग: यू मुंबा 36-29 जयपुर पिंक पैंथर्स", "सीज़न 7 लीग: यू मुंबा 34-28 जयपुर पिंक पैंथर्स"]),
    ("telugu-titans", "tamil-thalaivas",
     "दक्षिण भारतीय डर्बी — तेलुगु टाइटन्स बनाम तमिल थलाइवाज़। राहुल चौधरी और अजय ठाकुर जैसे दिग्गजों ने दोनों खेमों का प्रतिनिधित्व किया।",
     16, 8, 8, ["सीज़न 6 लीग: तमिल थलाइवाज़ 38-30 तेलुगु टाइटन्स", "सीज़न 5 लीग: तेलुगु टाइटन्स 34-31 तमिल थलाइवाज़", "सीज़न 9 लीग: तमिल थलाइवाज़ 35-33 तेलुगु टाइटन्स"]),
    ("haryana-steelers", "up-yoddhas",
     "उत्तर भारत की दो युवा फ़्रैंचाइज़ी — हरियाणा स्टीलर्स बनाम यूपी योद्धा। दोनों सीज़न 5 में पीकेएल से जुड़ीं और तब से कांटे के मुक़ाबले खेलती आई हैं।",
     18, 9, 9, ["सीज़न 6 एलिमिनेटर: यूपी योद्धा 38-35 हरियाणा स्टीलर्स", "सीज़न 8 लीग: हरियाणा स्टीलर्स 36-32 यूपी योद्धा", "सीज़न 10 लीग: हरियाणा स्टीलर्स 34-30 यूपी योद्धा"]),
    ("gujarat-giants", "puneri-paltan",
     "गुजरात जायंट्स बनाम पुनेरी पलटन — दो पश्चिमी भारतीय टीमों की भिड़ंत। गुजरात ने सीज़न 5 और 6 में लगातार फ़ाइनल खेले, पुणे ने सीज़न 9 का ख़िताब जीता।",
     17, 8, 9, ["सीज़न 6 लीग: गुजरात जायंट्स 32-28 पुनेरी पलटन", "सीज़न 9 लीग: पुनेरी पलटन 37-31 गुजरात जायंट्स", "सीज़न 10 लीग: पुनेरी पलटन 35-30 गुजरात जायंट्स"]),
    ("dabang-delhi", "u-mumba",
     "दबंग दिल्ली बनाम यू मुंबा — दो बड़े महानगरों की टीमें। नवीन कुमार की लगातार सुपर-10 पारियों ने इस मुक़ाबले में दिल्ली को धार दी।",
     21, 11, 10, ["सीज़न 7 लीग: दबंग दिल्ली 35-30 यू मुंबा", "सीज़न 8 लीग: यू मुंबा 33-29 दबंग दिल्ली", "सीज़न 5 लीग: यू मुंबा 36-31 दबंग दिल्ली"]),
    ("patna-pirates", "dabang-delhi",
     "पटना पाइरेट्स बनाम दबंग दिल्ली — प्रदीप नरवाल का दोनों टीमों से जुड़ाव रहा, जिसने इस भिड़ंत में भावनात्मक रंग भर दिया।",
     22, 12, 10, ["सीज़न 6 लीग: पटना पाइरेट्स 39-33 दबंग दिल्ली", "सीज़न 8 लीग: दबंग दिल्ली 37-32 पटना पाइरेट्स (प्रदीप नरवाल नई टीम में)", "सीज़न 4 लीग: पटना पाइरेट्स 41-29 दबंग दिल्ली"]),
    ("bengaluru-bulls", "u-mumba",
     "बेंगलुरु बुल्स बनाम यू मुंबा — रोहित कुमार और पवन सहरावत की रेडिंग बनाम फ़ज़ल अतरचली की दीवार जैसी रक्षा।",
     23, 11, 12, ["सीज़न 6 लीग: बेंगलुरु बुल्स 40-34 यू मुंबा", "सीज़न 2 लीग: यू मुंबा 32-26 बेंगलुरु बुल्स", "सीज़न 7 लीग: बेंगलुरु बुल्स 38-35 यू मुंबा"]),
    ("jaipur-pink-panthers", "bengaluru-bulls",
     "जयपुर पिंक पैंथर्स बनाम बेंगलुरु बुल्स — दो चैंपियन टीमों की भिड़ंत। अर्जुन देशवाल और पवन सहरावत की रेडिंग जंग देखने लायक होती है।",
     20, 10, 10, ["सीज़न 8 लीग: जयपुर पिंक पैंथर्स 36-31 बेंगलुरु बुल्स", "सीज़न 6 लीग: बेंगलुरु बुल्स 39-34 जयपुर पिंक पैंथर्स", "सीज़न 9 लीग: जयपुर पिंक पैंथर्स 35-32 बेंगलुरु बुल्स"]),
    ("bengal-warriors", "gujarat-giants",
     "बंगाल वॉरियर्स बनाम गुजरात जायंट्स — सीज़न 7 के बाद से लगातार रोमांचक मुक़ाबले। मनिंदर सिंह की रेडिंग बनाम गुजरात की मज़बूत रक्षापंक्ति।",
     16, 8, 8, ["सीज़न 7 लीग: बंगाल वॉरियर्स 34-30 गुजरात जायंट्स", "सीज़न 8 लीग: गुजरात जायंट्स 33-28 बंगाल वॉरियर्स", "सीज़न 10 लीग: बंगाल वॉरियर्स 36-33 गुजरात जायंट्स"]),
    ("tamil-thalaivas", "bengaluru-bulls",
     "तमिल थलाइवाज़ बनाम बेंगलुरु बुल्स — दक्षिण भारत की दो लोकप्रिय टीमें। नरेंद्र और पवन सहरावत की रेडिंग टक्कर इस मुक़ाबले की खासियत है।",
     15, 7, 8, ["सीज़न 8 लीग: तमिल थलाइवाज़ 37-33 बेंगलुरु बुल्स", "सीज़न 9 लीग: बेंगलुरु बुल्स 35-31 तमिल थलाइवाज़", "सीज़न 10 लीग: तमिल थलाइवाज़ 34-32 बेंगलुरु बुल्स"]),
    ("up-yoddhas", "bengal-warriors",
     "यूपी योद्धा बनाम बंगाल वॉरियर्स — सुरेंद्र गिल और मनिंदर सिंह की रेडिंग जंग। दोनों टीमें प्ले-ऑफ़ की दौड़ में अक्सर आमने-सामने रही हैं।",
     15, 7, 8, ["सीज़न 6 लीग: यूपी योद्धा 36-32 बंगाल वॉरियर्स", "सीज़न 8 लीग: बंगाल वॉरियर्स 34-30 यूपी योद्धा", "सीज़न 9 लीग: बंगाल वॉरियर्स 35-33 यूपी योद्धा"]),
    ("puneri-paltan", "tamil-thalaivas",
     "पुनेरी पलटन बनाम तमिल थलाइवाज़ — अस्लम इनामदार और नरेंद्र की युवा रेडिंग प्रतिभाओं की भिड़ंत। पुणे की सीज़न 9 ख़िताबी टीम ने यहाँ दबदबा बनाया।",
     16, 9, 7, ["सीज़न 9 लीग: पुनेरी पलटन 38-31 तमिल थलाइवाज़", "सीज़न 8 लीग: तमिल थलाइवाज़ 33-30 पुनेरी पलटन", "सीज़न 10 लीग: पुनेरी पलटन 36-32 तमिल थलाइवाज़"]),
    ("haryana-steelers", "gujarat-giants",
     "हरियाणा स्टीलर्स बनाम गुजरात जायंट्स — दो रक्षा-प्रधान टीमों की टक्कर। जयदीप और सुनील कुमार की मज़बूत डिफ़ेंस लाइनें यहाँ टकराती हैं।",
     14, 7, 7, ["सीज़न 7 लीग: हरियाणा स्टीलर्स 33-29 गुजरात जायंट्स", "सीज़न 8 लीग: गुजरात जायंट्स 32-30 हरियाणा स्टीलर्स", "सीज़न 10 लीग: हरियाणा स्टीलर्स 35-31 गुजरात जायंट्स"]),
    ("telugu-titans", "jaipur-pink-panthers",
     "तेलुगु टाइटन्स बनाम जयपुर पिंक पैंथर्स — राहुल चौधरी और अर्जुन देशवाल की रेडिंग कलाकारी। शुरुआती सीज़न में दोनों चोटी की टीमें थीं।",
     17, 8, 9, ["सीज़न 2 लीग: जयपुर पिंक पैंथर्स 34-30 तेलुगु टाइटन्स", "सीज़न 3 लीग: तेलुगु टाइटन्स 33-31 जयपुर पिंक पैंथर्स", "सीज़न 8 लीग: जयपुर पिंक पैंथर्स 37-32 तेलुगु टाइटन्स"]),
    ("up-yoddhas", "gujarat-giants",
     "यूपी योद्धा बनाम गुजरात जायंट्स — दोनों टीमें अब तक ख़िताब की तलाश में हैं। हर मुक़ाबला प्ले-ऑफ़ की उम्मीदों से भरा होता है।",
     14, 7, 7, ["सीज़न 6 लीग: यूपी योद्धा 35-31 गुजरात जायंट्स", "सीज़न 7 लीग: गुजरात जायंट्स 33-30 यूपी योद्धा", "सीज़न 9 लीग: यूपी योद्धा 34-32 गुजरात जायंट्स"]),
    ("patna-pirates", "telugu-titans",
     "पटना पाइरेट्स बनाम तेलुगु टाइटन्स — प्रदीप नरवाल बनाम राहुल चौधरी, पीकेएल के दो सबसे बड़े रेडरों की सीधी टक्कर रही है।",
     20, 12, 8, ["सीज़न 3 लीग: पटना पाइरेट्स 38-34 तेलुगु टाइटन्स", "सीज़न 5 लीग: पटना पाइरेट्स 41-36 तेलुगु टाइटन्स", "सीज़न 2 लीग: तेलुगु टाइटन्स 35-30 पटना पाइरेट्स"]),
    ("haryana-steelers", "dabang-delhi",
     "हरियाणा स्टीलर्स बनाम दबंग दिल्ली — हरियाणवी पहलवानों से भरी दोनों टीमों की भिड़ंत में जोश और जुनून चरम पर होता है।",
     16, 8, 8, ["सीज़न 11 लीग: हरियाणा स्टीलर्स 34-31 दबंग दिल्ली", "सीज़न 7 लीग: दबंग दिल्ली 36-32 हरियाणा स्टीलर्स", "सीज़न 9 लीग: हरियाणा स्टीलर्स 35-33 दबंग दिल्ली"]),
    ("puneri-paltan", "bengal-warriors",
     "पुनेरी पलटन बनाम बंगाल वॉरियर्स — सीज़न 9 के सेमीफ़ाइनल और फ़ाइनल राह की कई बड़ी जंगें इस भिड़ंत का हिस्सा हैं।",
     17, 9, 8, ["सीज़न 9 लीग: पुनेरी पलटन 37-33 बंगाल वॉरियर्स", "सीज़न 7 लीग: बंगाल वॉरियर्स 34-30 पुनेरी पलटन", "सीज़न 10 लीग: पुनेरी पलटन 36-34 बंगाल वॉरियर्स"]),
    ("tamil-thalaivas", "up-yoddhas",
     "तमिल थलाइवाज़ बनाम यूपी योद्धा — नरेंद्र और सुरेंद्र गिल की युवा रेडिंग प्रतिभाएँ आमने-सामने। दोनों टीमों का प्रशंसक आधार बेहद जोशीला है।",
     13, 6, 7, ["सीज़न 8 लीग: यूपी योद्धा 35-31 तमिल थलाइवाज़", "सीज़न 9 लीग: तमिल थलाइवाज़ 34-32 यूपी योद्धा", "सीज़न 10 लीग: यूपी योद्धा 36-33 तमिल थलाइवाज़"]),
    ("telugu-titans", "u-mumba",
     "तेलुगु टाइटन्स बनाम यू मुंबा — राहुल चौधरी की धुआँधार रेडिंग बनाम यू मुंबा की मज़बूत रक्षा। शुरुआती सीज़न के कई यादगार मुक़ाबले इसमें शामिल हैं।",
     19, 9, 10, ["सीज़न 2 लीग: यू मुंबा 36-31 तेलुगु टाइटन्स", "सीज़न 4 लीग: तेलुगु टाइटन्स 34-32 यू मुंबा", "सीज़न 1 लीग: यू मुंबा 33-28 तेलुगु टाइटन्स"]),
    ("jaipur-pink-panthers", "haryana-steelers",
     "जयपुर पिंक पैंथर्स बनाम हरियाणा स्टीलर्स — अर्जुन देशवाल की रेडिंग बनाम हरियाणा की दमदार डिफ़ेंस। दोनों उत्तर भारतीय टीमों के बीच कांटे की टक्कर।",
     15, 8, 7, ["सीज़न 8 लीग: जयपुर पिंक पैंथर्स 35-30 हरियाणा स्टीलर्स", "सीज़न 9 लीग: हरियाणा स्टीलर्स 34-32 जयपुर पिंक पैंथर्स", "सीज़न 10 लीग: जयपुर पिंक पैंथर्स 36-33 हरियाणा स्टीलर्स"]),
]


def build_compare_index():
    depth = 1
    pcards = ""
    for a, b in COMPARE_PAIRS:
        pa, pb = PLAYER_BY_ID[a], PLAYER_BY_ID[b]
        pcards += f"""<a href="{a}-vs-{b}/" class="block bg-kb-card border border-kb-border rounded-xl p-4 hover:border-kb-orange hover:shadow-md transition">
          <div class="hi font-heading font-bold text-kb-ink">{esc(pa['name_hi'])} <span class="text-kb-orange">बनाम</span> {esc(pb['name_hi'])}</div>
          <div class="text-sm text-kb-text mt-1">{esc(pa['name'])} vs {esc(pb['name'])}</div></a>"""
    rcards = ""
    for r in RIVALRIES:
        a, b = r[0], r[1]
        wa, wb = (r[4], r[5]) if len(r) > 5 else (0, 0)
        ta, tb = TEAMS[a], TEAMS[b]
        rcards += f"""<a href="rivalry-{a}-vs-{b}/" class="block bg-kb-card border border-kb-border rounded-xl p-4 hover:border-kb-orange hover:shadow-md transition">
          <div class="hi font-heading font-bold text-kb-ink">{esc(ta['name_hi'])} <span class="text-kb-orange">बनाम</span> {esc(tb['name_hi'])}</div>
          <div class="hi text-xs text-kb-text mt-1">आमने-सामने: {wa}–{wb}</div></a>"""
    body = f"""{page_h1('तुलना और प्रतिद्वंद्विता', 'दो खिलाड़ियों की हेड-टू-हेड तुलना और टीम प्रतिद्वंद्विताएँ')}
      <h2 class="hi font-heading font-bold text-lg text-kb-ink mb-3 flex items-center gap-2"><span class="w-1.5 h-5 rounded mat-stripe inline-block"></span>खिलाड़ी तुलना</h2>
      <section class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-10">{pcards}</section>
      <h2 class="hi font-heading font-bold text-lg text-kb-ink mb-3 flex items-center gap-2"><span class="w-1.5 h-5 rounded mat-stripe inline-block"></span>टीम प्रतिद्वंद्विताएँ</h2>
      <section class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{rcards}</section>"""
    desc = "कबड्डी खिलाड़ियों की हेड-टू-हेड तुलना और पीकेएल टीम प्रतिद्वंद्विताएँ — प्रदीप नरवाल बनाम पवन सहरावत समेत कई दिलचस्प मुक़ाबले हिंदी में।"
    write("compare/index.html", page("कबड्डी तुलना — खिलाड़ी व टीम हेड-टू-हेड | कबड्डी आँकड़े",
                                      desc, "/compare/", depth, body, active="compare",
                                      trail=[("होम", "../"), ("तुलना", None)]), "0.7")
    search_rows.append(["तुलना", "/compare/", "पेज", "compare tulna head to head kabaddi"])


def build_compare_pair(a, b):
    depth = 2
    pa, pb = PLAYER_BY_ID[a], PLAYER_BY_ID[b]

    def hdr(p):
        return (f'<div class="text-center"><div class="w-16 h-16 mx-auto rounded-xl mat-stripe text-white flex items-center justify-center font-heading font-extrabold text-2xl">{esc(p["name"][0])}</div>'
                f'<a href="../../players/{p["id"]}/" class="block font-heading font-bold text-kb-ink hover:text-kb-orange mt-2">{esc(p["name"])}</a>'
                f'<div class="hi text-sm text-kb-orange">{p["name_hi"]}</div>'
                f'<div class="mt-1">{role_badge(p["role"])}</div></div>')

    metrics = [("रेड अंक", "raid"), ("टैकल अंक", "tackle"), ("कुल अंक", "total"),
               ("सुपर 10", "super10"), ("हाई 5", "high5"), ("मैच", "matches")]
    rows = ""
    for label, key in metrics:
        va, vb = pa[key], pb[key]
        wa = "text-kb-orange font-bold" if va > vb else "text-kb-ink"
        wb = "text-kb-orange font-bold" if vb > va else "text-kb-ink"
        rows += (f'<tr class="border-t border-kb-border">'
                 f'<td class="px-3 py-2.5 text-center tnum {wa}">{va:,}</td>'
                 f'<td class="px-3 py-2.5 text-center hi text-xs font-semibold text-kb-text uppercase">{label}</td>'
                 f'<td class="px-3 py-2.5 text-center tnum {wb}">{vb:,}</td></tr>')

    body = f"""
    <h1 class="font-heading font-extrabold text-xl sm:text-2xl text-kb-ink text-center hi mb-6">{esc(pa['name_hi'])} <span class="text-kb-orange">बनाम</span> {esc(pb['name_hi'])}</h1>
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 mb-6">
      <div class="grid grid-cols-2 gap-4 mb-4">{hdr(pa)}{hdr(pb)}</div>
      <table class="w-full"><tbody>{rows}</tbody></table>
    </div>
    <p class="hi text-sm text-kb-text text-center">नारंगी रंग में दिखाया गया मान उस मीट्रिक में आगे रहने वाले खिलाड़ी का है। आँकड़े पीकेएल करियर के अनुमानित कुल हैं।</p>
    """
    desc = (f"{pa['name_hi']} बनाम {pb['name_hi']} — कबड्डी आँकड़ों की हेड-टू-हेड तुलना: रेड अंक, टैकल अंक, "
            f"सुपर 10, हाई 5 और करियर रिकॉर्ड हिंदी में।")[:300]
    write(f"compare/{a}-vs-{b}/index.html",
          page(f"{pa['name_hi']} बनाम {pb['name_hi']} — तुलना",
               desc, f"/compare/{a}-vs-{b}/", depth, body, active="compare",
               trail=[("होम", "../../"), ("तुलना", "../"), (f"{pa['name_hi']} बनाम {pb['name_hi']}", None)]), "0.6")
    search_rows.append([f"{pa['name']} बनाम {pb['name']}", f"/compare/{a}-vs-{b}/", "तुलना",
                        f"{pa['name']} vs {pb['name']} compare tulna".lower()])


def build_rivalry(a, b, narr, total=0, wins_a=0, wins_b=0, notable=None):
    depth = 2
    ta, tb = TEAMS[a], TEAMS[b]
    notable = notable or []

    def tbox(t, ts):
        return (f'<div class="bg-kb-card border border-kb-border rounded-xl p-4 text-center" style="border-top:3px solid {t["color"]}">'
                f'<a href="../../teams/{ts}/" class="font-heading font-bold text-kb-ink hover:text-kb-orange hi">{esc(t["name_hi"])}</a>'
                f'<div class="hi text-xs text-kb-text mt-1">{esc(t["city"])}</div>'
                f'<div class="hi text-sm mt-2 text-kb-orange font-semibold">{len(t["titles"])} ख़िताब</div></div>')

    # head-to-head record bar
    pa = round(wins_a / total * 100) if total else 50
    pb = 100 - pa
    h2h = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 mb-6">
      <h2 class="hi font-heading font-bold text-kb-ink mb-3">आमने-सामने का रिकॉर्ड</h2>
      <div class="grid grid-cols-3 text-center mb-3">
        <div><div class="tnum text-2xl font-extrabold text-kb-orange">{wins_a}</div><div class="hi text-xs text-kb-text mt-1">{esc(ta['name_hi'])} जीते</div></div>
        <div><div class="tnum text-2xl font-extrabold text-kb-ink">{total}</div><div class="hi text-xs text-kb-text mt-1">कुल मुक़ाबले</div></div>
        <div><div class="tnum text-2xl font-extrabold text-kb-orange">{wins_b}</div><div class="hi text-xs text-kb-text mt-1">{esc(tb['name_hi'])} जीते</div></div>
      </div>
      <div class="flex h-3 rounded-full overflow-hidden border border-kb-border">
        <div style="width:{pa}%;background:{ta['color']}"></div>
        <div style="width:{pb}%;background:{tb['color']}"></div>
      </div>
    </div>"""

    # key stats comparison table
    def srow(label, va, vb):
        wa = "text-kb-orange font-bold" if va > vb else "text-kb-ink"
        wb = "text-kb-orange font-bold" if vb > va else "text-kb-ink"
        return (f'<tr class="border-t border-kb-border">'
                f'<td class="px-3 py-2.5 text-center tnum {wa}">{va}</td>'
                f'<td class="px-3 py-2.5 text-center hi text-xs font-semibold text-kb-text uppercase">{label}</td>'
                f'<td class="px-3 py-2.5 text-center tnum {wb}">{vb}</td></tr>')
    stats = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 mb-6">
      <h2 class="hi font-heading font-bold text-kb-ink mb-3">मुख्य आँकड़े</h2>
      <table class="w-full"><tbody>
        {srow('ख़िताब', len(ta['titles']), len(tb['titles']))}
        {srow('इस भिड़ंत में जीत', wins_a, wins_b)}
      </tbody></table>
    </div>"""

    nm = ""
    if notable:
        items = "".join(f'<li class="hi text-sm text-kb-text py-2 border-t border-kb-border flex gap-2"><span class="text-kb-orange">›</span>{esc(m)}</li>' for m in notable)
        nm = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 mb-6">
      <h2 class="hi font-heading font-bold text-kb-ink mb-1">यादगार मुक़ाबले</h2>
      <ul>{items}</ul>
    </div>"""

    body = f"""
    <h1 class="font-heading font-extrabold text-xl sm:text-2xl text-kb-ink text-center hi mb-6">{esc(ta['name_hi'])} <span class="text-kb-orange">बनाम</span> {esc(tb['name_hi'])}</h1>
    <div class="grid grid-cols-2 gap-4 mb-6">{tbox(ta, a)}{tbox(tb, b)}</div>
    {h2h}
    {C.prose([narr])}
    {stats}
    {nm}
    <p class="hi text-xs text-kb-text text-center mb-6">आँकड़े पीकेएल सीज़न 1–{N_SEASONS} के अनुमानित कुल हैं और संदर्भ के लिए दिए गए हैं।</p>
    <div class="text-center"><a href="../" class="hi text-kb-orange font-semibold hover:underline">← सभी तुलनाएँ</a></div>
    """
    desc = (f"{ta['name_hi']} बनाम {tb['name_hi']} — पीकेएल की प्रतिद्वंद्विता: आमने-सामने का रिकॉर्ड ({wins_a}-{wins_b}), ख़िताब और यादगार मुक़ाबले हिंदी में।")[:300]
    write(f"compare/rivalry-{a}-vs-{b}/index.html",
          page(f"{ta['name_hi']} बनाम {tb['name_hi']} — प्रतिद्वंद्विता",
               desc, f"/compare/rivalry-{a}-vs-{b}/", depth, body, active="compare",
               trail=[("होम", "../../"), ("तुलना", "../"), (f"{ta['name_hi']} बनाम {tb['name_hi']}", None)]), "0.6")
    search_rows.append([f"{ta['name']} बनाम {tb['name']}", f"/compare/rivalry-{a}-vs-{b}/", "प्रतिद्वंद्विता",
                        f"{ta['name']} vs {tb['name']} rivalry h2h".lower()])


# =========================================================== INTERNATIONAL ====
# folded into "seasons" hub? Make a dedicated page under /international/.
def build_international():
    depth = 1
    wc_rows = [[y, f'<span class="hi font-medium">{w}</span>', f'<span class="hi text-kb-text">{ru}</span>',
                f'<span class="tnum">{sc}</span>', f'<span class="hi text-kb-text">{loc}</span>']
               for (y, loc, w, ru, sc) in WORLD_CUP]
    ag_men = [[y, f'<span class="hi font-medium">{w}</span>'] for (y, w) in ASIAN_GAMES_MEN]
    ag_women = [[y, f'<span class="hi font-medium">{w}</span>', f'<span class="hi text-kb-text">{ru}</span>',
                 f'<span class="tnum">{sc}</span>'] for (y, w, ru, sc) in ASIAN_GAMES_WOMEN]

    body = f"""{page_h1('अंतरराष्ट्रीय कबड्डी', 'विश्व कप और एशियाई खेलों में भारत का दबदबा')}
      {C.prose([
        "कबड्डी में भारत का अंतरराष्ट्रीय रिकॉर्ड बेजोड़ रहा है। अंतरराष्ट्रीय कबड्डी "
        "महासंघ (IKF) के मानक-शैली विश्व कप के तीनों संस्करण भारत ने जीते हैं, और हर "
        "बार फ़ाइनल में ईरान को हराया। एशियाई खेलों में भी भारत ने अधिकांश स्वर्ण पदक "
        "अपने नाम किए हैं, हालाँकि 2018 जकार्ता में ईरान ने पुरुष और महिला दोनों वर्गों "
        "में स्वर्ण जीतकर बड़ा उलटफेर किया।"])}
      <h2 class="hi font-heading font-bold text-lg text-kb-ink mb-3 flex items-center gap-2"><span class="w-1.5 h-5 rounded mat-stripe inline-block"></span>कबड्डी विश्व कप (मानक शैली)</h2>
      <div class="mb-8">{table(['वर्ष', 'विजेता', 'उपविजेता', 'स्कोर', 'मेज़बान'], wc_rows)}</div>
      <h2 class="hi font-heading font-bold text-lg text-kb-ink mb-3 flex items-center gap-2"><span class="w-1.5 h-5 rounded mat-stripe inline-block"></span>एशियाई खेल — पुरुष स्वर्ण</h2>
      <div class="mb-8">{table(['वर्ष', 'स्वर्ण पदक विजेता'], ag_men)}</div>
      <h2 class="hi font-heading font-bold text-lg text-kb-ink mb-3 flex items-center gap-2"><span class="w-1.5 h-5 rounded mat-stripe inline-block"></span>एशियाई खेल — महिला स्वर्ण</h2>
      {table(['वर्ष', 'स्वर्ण', 'रजत', 'फ़ाइनल स्कोर'], ag_women)}"""
    desc = "अंतरराष्ट्रीय कबड्डी — कबड्डी विश्व कप के विजेता, एशियाई खेलों में भारत के स्वर्ण पदक और भारत बनाम ईरान की प्रतिद्वंद्विता हिंदी में।"
    write("international/index.html", page("अंतरराष्ट्रीय कबड्डी — विश्व कप व एशियाई खेल | कबड्डी आँकड़े",
                                           desc, "/international/", depth, body, active="seasons",
                                           trail=[("होम", "../"), ("अंतरराष्ट्रीय कबड्डी", None)]), "0.6")
    search_rows.append(["अंतरराष्ट्रीय कबड्डी", "/international/", "पेज",
                        "international world cup asian games india iran kabaddi antarrashtriya"])


# ================================================================ VENUES ======
def build_venues_index():
    depth = 1
    cards = ""
    for v in sorted(VENUES, key=lambda x: -x["capacity"]):
        homes = " · ".join(TEAMS[h]["name_hi"] for h in v["home"] if h in TEAMS)
        home_txt = (f'<div class="hi text-sm text-kb-orange font-semibold mt-1 flex items-center gap-1.5">'
                    f'{icon("trophy","w-4 h-4")}गृह मैदान: {esc(homes)}</div>' if homes else "")
        cards += f"""<a href="{v['slug']}/" class="block bg-kb-card border border-kb-border rounded-xl p-5 hover:border-kb-orange hover:shadow-md transition">
          <div class="font-heading font-extrabold text-lg text-kb-ink hi leading-tight">{esc(v['name_hi'])}</div>
          <div class="hi text-sm text-kb-text mt-1">{esc(v['city_hi'])}, {esc(v['state'])}</div>
          {home_txt}
          <div class="hi text-xs text-kb-text mt-2">क्षमता: <b class="text-kb-ink tnum">{v['capacity']:,}</b> दर्शक · {len(v['seasons'])} सीज़न में मेज़बानी</div></a>"""
    body = f"""{page_h1('पीकेएल स्टेडियम', 'प्रो कबड्डी लीग के प्रमुख मैदान और एरिना — शहर, क्षमता और मेज़बान टीमें')}
      {C.prose([
        "प्रो कबड्डी लीग के मुक़ाबले देश भर के अलग-अलग शहरों के इनडोर स्टेडियमों में खेले जाते हैं। "
        "हर टीम का अपना गृह मैदान होता है जहाँ घरेलू दर्शकों का जोश खेल को और रोमांचक बना देता है। "
        "यहाँ पीकेएल के प्रमुख स्टेडियमों की सूची है — उनकी क्षमता, स्थान, मेज़बान टीमें और किन सीज़नों "
        "के यादगार मुक़ाबले व फ़ाइनल वहाँ खेले गए।",
      ])}
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{cards}</div>"""
    desc = ("प्रो कबड्डी लीग के सभी प्रमुख स्टेडियम और एरिना — पुणे, दिल्ली, मुंबई, हैदराबाद, चेन्नई, "
            "कोलकाता समेत हर मैदान की क्षमता, स्थान और मेज़बान टीमें हिंदी में।")
    write("venues/index.html", page("पीकेएल स्टेडियम — सभी मैदान व एरिना | कबड्डी आँकड़े",
                                     desc, "/venues/", depth, body, active="venues",
                                     trail=[("होम", "../"), ("स्टेडियम", None)]), "0.8")
    search_rows.append(["स्टेडियम", "/venues/", "पेज",
                        "venues stadium arena maidan pkl kabaddi ground"])


def build_venue(v):
    depth = 2
    homes = [TEAMS[h] for h in v["home"] if h in TEAMS]
    home_chips = ""
    for h in v["home"]:
        t = TEAMS.get(h)
        if not t:
            continue
        home_chips += (f'<a href="../../teams/{h}/" class="hi inline-flex items-center gap-1.5 px-3 py-1.5 '
                       f'rounded-lg border border-kb-border bg-white text-sm text-kb-ink hover:border-kb-orange transition">'
                       f'<span class="w-2.5 h-2.5 rounded-full" style="background:{t["color"]}"></span>{esc(t["name_hi"])}</a>')
    if not home_chips:
        home_chips = '<span class="hi text-kb-text text-sm">कोई निश्चित गृह टीम नहीं।</span>'

    # season chips (seasons hosted), link to season pages
    season_chips = ""
    for n in v["seasons"]:
        season_chips += (f'<a href="../../seasons/season-{n}/" class="hi inline-flex items-center gap-1 px-3 py-1.5 '
                         f'rounded-lg bg-kb-orange text-white text-sm font-semibold hover:bg-kb-dark transition">सीज़न {n}</a>')
    if not season_chips:
        season_chips = '<span class="hi text-kb-text text-sm">डेटा शीघ्र जोड़ा जाएगा।</span>'

    tiles = f"""<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {stat('क्षमता', f"{v['capacity']:,}")}
      {stat('सीज़न मेज़बानी', len(v['seasons']))}
      {stat('शहर', '', v['city_hi'])}
      {stat('निर्माण' if v['opened'] else 'राज्य', v['opened'] if v['opened'] else '', '' if v['opened'] else v['state'])}</div>"""

    facts = table(['विवरण', 'जानकारी'], [
        ['<span class="hi">स्टेडियम</span>', f'<span class="hi">{esc(v["name_hi"])}</span>'],
        ['<span class="hi">अंग्रेज़ी नाम</span>', f'<span>{esc(v["name"])}</span>'],
        ['<span class="hi">शहर</span>', f'<span class="hi">{esc(v["city_hi"])} ({esc(v["city"])})</span>'],
        ['<span class="hi">राज्य</span>', f'<span class="hi">{esc(v["state"])}</span>'],
        ['<span class="hi">दर्शक क्षमता</span>', f'<span class="tnum">{v["capacity"]:,}</span>'],
        ['<span class="hi">निर्माण वर्ष</span>', f'<span class="tnum">{esc(v["opened"]) if v["opened"] else "—"}</span>'],
    ])

    body = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 mb-6" style="border-top:4px solid #FF6B00">
      <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight hi">{esc(v['name_hi'])}</h1>
      <div class="text-lg text-kb-text">{esc(v['name'])}</div>
      <div class="hi text-sm text-kb-text mt-1">{esc(v['city_hi'])}, {esc(v['state'])}</div>
    </div>
    {tiles}
    {C.prose([v['note']])}
    {section_title('गृह टीमें', 'इस मैदान को अपना घरेलू मैदान मानने वाली टीमें')}
    <div class="flex flex-wrap gap-2 mb-8">{home_chips}</div>
    {section_title('मेज़बानी किए सीज़न', 'इस स्टेडियम में खेले गए पीकेएल सीज़न')}
    <div class="flex flex-wrap gap-2 mb-8">{season_chips}</div>
    {section_title('स्टेडियम विवरण')}
    {facts}
    <div class="mt-6"><a href="../" class="hi text-kb-orange font-semibold hover:underline">← सभी स्टेडियम</a></div>
    """
    home_txt = (f"{homes[0]['name_hi']} का गृह मैदान" if homes else "पीकेएल मैदान")
    desc = (f"{v['name_hi']} ({v['city_hi']}, {v['state']}) — {home_txt}। दर्शक क्षमता {v['capacity']:,}, "
            f"पीकेएल के {len(v['seasons'])} सीज़न की मेज़बानी। स्टेडियम का इतिहास और विवरण हिंदी में।")[:300]
    jsonld = {"@context": "https://schema.org", "@type": "StadiumOrArena", "name": v['name'],
              "alternateName": v['name_hi'], "url": f"{SITE}/venues/{v['slug']}/",
              "maximumAttendeeCapacity": v['capacity'],
              "address": {"@type": "PostalAddress", "addressLocality": v['city'],
                          "addressRegion": v['state'], "addressCountry": "IN"}}
    write(f"venues/{v['slug']}/index.html",
          page(f"{v['name_hi']} — पीकेएल स्टेडियम",
               desc, f"/venues/{v['slug']}/", depth, body, active="venues",
               trail=[("होम", "../../"), ("स्टेडियम", "../"), (v['name_hi'], None)],
               jsonld=jsonld), "0.7")
    search_rows.append([v['name_hi'], f"/venues/{v['slug']}/", "स्टेडियम",
                        f"{v['name']} {v['name_hi']} {v['city']} {v['city_hi']} stadium venue arena kabaddi".lower()])


# ================================================================ AUCTIONS ====
def fmt_price(lakh):
    """Hindi price string from a value in lakh. 100 लाख = 1 करोड़।"""
    if lakh >= 100:
        s = f"{lakh / 100:.3f}".rstrip("0").rstrip(".")
        return f"₹{s} करोड़"
    s = f"{lakh:.2f}".rstrip("0").rstrip(".")
    return f"₹{s} लाख"


def _buy_name_cell(b, depth):
    """Player name cell — links to profile if it exists, else plain Hindi name."""
    if b.get("slug") and b["slug"] in PLAYER_BY_ID:
        return plink(b["slug"], depth)
    return (f'<span class="font-medium text-kb-ink">{esc(b["name"])}</span>'
            f'<span class="hi text-kb-text text-xs ml-1">{b["name_hi"]}</span>')


def build_auctions_index():
    depth = 1
    # all-time most expensive table
    rows = []
    for i, b in enumerate(ALL_TIME_EXPENSIVE, 1):
        rank = (f'<span class="inline-flex items-center justify-center w-6 h-6 rounded-full '
                f'bg-kb-orange text-white text-xs font-bold tnum">{i}</span>' if i <= 3
                else f'<span class="tnum text-kb-text">{i}</span>')
        rows.append([
            rank,
            _buy_name_cell(b, depth),
            team_link(b["team"], depth),
            f'<b class="text-kb-ink">{fmt_price(b["lakh"])}</b>',
            f'<a href="../seasons/season-{b["season"]}/" class="hi text-kb-orange hover:underline">सीज़न {b["season"]}</a> '
            f'<span class="hi text-kb-text text-xs">({b["year"]})</span>',
        ])
    expensive_tbl = table(["#", "खिलाड़ी", "टीम", "क़ीमत", "नीलामी"], rows, align_right={3})

    # season links grid
    cards = ""
    for n in sorted(AUCTIONS.keys()):
        a = AUCTIONS[n]
        top = a["buys"][0]
        cards += f"""<a href="season-{n}/" class="block bg-kb-card border border-kb-border rounded-xl p-5 hover:border-kb-orange hover:shadow-md transition">
          <div class="font-heading font-extrabold text-lg text-kb-ink hi leading-tight">सीज़न {n} नीलामी</div>
          <div class="hi text-sm text-kb-text mt-0.5">वर्ष {a['year']}</div>
          <div class="hi text-sm text-kb-text mt-2">सबसे महँगा: <b class="text-kb-ink">{esc(top['name_hi'])}</b> — <span class="text-kb-orange font-semibold">{fmt_price(top['lakh'])}</span></div></a>"""

    body = f"""{page_h1('पीकेएल नीलामी इतिहास', 'प्रो कबड्डी लीग की खिलाड़ी नीलामी — सबसे महँगे खिलाड़ी, सीज़न-दर-सीज़न टॉप बोलियाँ')}
      {C.prose([
        "प्रो कबड्डी लीग की खिलाड़ी नीलामी हर सीज़न से पहले होने वाला सबसे रोमांचक आयोजन है, "
        "जहाँ फ़्रेंचाइज़ी अपने पर्स (वेतन सीमा) के भीतर रहकर देश-विदेश के सर्वश्रेष्ठ रेडर और "
        "डिफ़ेंडर ख़रीदती हैं। सीज़न 1 (2014) में जहाँ कीमतें कुछ लाख रुपये में थीं, वहीं अब "
        "शीर्ष खिलाड़ी करोड़ों में बिकते हैं।",
        "सीज़न 6 (2018) में मोनू गोयत ₹1.51 करोड़ में बिककर पहले 'करोड़पति' बने, सीज़न 8 में "
        "प्रदीप नरवाल ₹1.65 करोड़ तक पहुँचे, और सीज़न 9 में पवन सहरावत ₹2.605 करोड़ में बिककर "
        "पीकेएल इतिहास के सर्वकालिक सबसे महँगे खिलाड़ी बन गए। यहाँ दी गई कीमतें प्रसिद्ध हेडलाइन "
        "आँकड़ों पर आधारित हैं।",
      ])}
      {section_title('सर्वकालिक सबसे महँगे खिलाड़ी', 'पीकेएल नीलामी इतिहास की सबसे बड़ी बोलियाँ')}
      {expensive_tbl}
      <div class="mt-8">{section_title('सीज़न-दर-सीज़न नीलामी', 'किसी भी सीज़न की टॉप बोलियाँ देखने के लिए चुनें')}</div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{cards}</div>"""
    desc = ("पीकेएल खिलाड़ी नीलामी का इतिहास — पवन सहरावत, प्रदीप नरवाल समेत सर्वकालिक सबसे महँगे "
            "खिलाड़ी और हर सीज़न की टॉप बोलियाँ हिंदी में।")
    write("auctions/index.html", page("पीकेएल नीलामी इतिहास — सबसे महँगे खिलाड़ी | कबड्डी आँकड़े",
                                       desc, "/auctions/", depth, body, active="auctions",
                                       trail=[("होम", "../"), ("नीलामी", None)]), "0.8")
    search_rows.append(["पीकेएल नीलामी", "/auctions/", "पेज",
                        "auction neelami nilami pkl player price crore lakh kabaddi bid"])


def build_auction_season(n):
    depth = 2
    a = AUCTIONS[n]
    s = next((x for x in SEASONS if x["num"] == n), None)
    rows = []
    for i, b in enumerate(a["buys"], 1):
        rows.append([
            f'<span class="tnum text-kb-text">{i}</span>',
            _buy_name_cell(b, depth),
            team_link(b["team"], depth),
            f'<b class="text-kb-ink">{fmt_price(b["lakh"])}</b>',
        ])
    buys_tbl = table(["#", "खिलाड़ी", "टीम", "क़ीमत"], rows, align_right={3})
    top = a["buys"][0]

    tiles = f"""<div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
      {stat('नीलामी वर्ष', a['year'])}
      {stat('सबसे महँगा', fmt_price(top['lakh']), top['name_hi'])}
      {stat('दर्ज बोलियाँ', len(a['buys']))}</div>"""

    # prev/next nav across auction seasons
    keys = sorted(AUCTIONS.keys())
    idx = keys.index(n)
    prev_n = keys[idx - 1] if idx > 0 else None
    next_n = keys[idx + 1] if idx < len(keys) - 1 else None
    navs = '<div class="flex justify-between mt-8">'
    navs += (f'<a href="../season-{prev_n}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">← सीज़न {prev_n} नीलामी</a>'
             if prev_n else '<span></span>')
    navs += (f'<a href="../season-{next_n}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">सीज़न {next_n} नीलामी →</a>'
             if next_n else '<span></span>')
    navs += '</div>'

    champ_line = ""
    if s:
        champ_line = (f' इस सीज़न का ख़िताब {TEAMS[s["champion"]]["name_hi"]} ने जीता।')

    body = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 mb-6" style="border-top:4px solid #FF6B00">
      <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight hi">पीकेएल सीज़न {n} नीलामी</h1>
      <div class="hi text-sm text-kb-text mt-1">वर्ष {a['year']} · {esc(a['purse_hi'])}</div>
    </div>
    {tiles}
    {C.prose([a['note'] + champ_line])}
    {section_title('टॉप बोलियाँ', f'सीज़न {n} नीलामी की सबसे बड़ी ख़रीद')}
    {buys_tbl}
    <div class="mt-6"><a href="../" class="hi text-kb-orange font-semibold hover:underline">← सभी नीलामी</a></div>
    {navs}
    """
    desc = (f"पीकेएल सीज़न {n} ({a['year']}) खिलाड़ी नीलामी — सबसे महँगा {top['name_hi']} "
            f"({fmt_price(top['lakh'])})। टॉप बोलियाँ, टीम और क़ीमत हिंदी में।")[:300]
    write(f"auctions/season-{n}/index.html",
          page(f"पीकेएल सीज़न {n} नीलामी ({a['year']}) — टॉप बोलियाँ | कबड्डी आँकड़े",
               desc, f"/auctions/season-{n}/", depth, body, active="auctions",
               trail=[("होम", "../../"), ("नीलामी", "../"), (f"सीज़न {n}", None)]), "0.6")
    search_rows.append([f"सीज़न {n} नीलामी", f"/auctions/season-{n}/", "नीलामी",
                        f"auction season {n} neelami pkl {a['year']} top buys price kabaddi".lower()])


# ============================================================ ALL-STAR =======
def _as_name_cell(o, depth):
    """Player name cell — links to profile if it exists, else plain Hindi name."""
    if o.get("slug") and o["slug"] in PLAYER_BY_ID:
        return plink(o["slug"], depth)
    return (f'<span class="font-medium text-kb-ink">{esc(o["name"])}</span>'
            f'<span class="hi text-kb-text text-xs ml-1">{o["name_hi"]}</span>')


def _as_roster_table(roster, depth):
    rows = []
    for pl in roster:
        rows.append([
            _as_name_cell(pl, depth),
            team_link(pl["team"], depth),
            f'<span class="hi inline-flex px-2 py-0.5 rounded-md bg-kb-bg border border-kb-border text-xs text-kb-text">{role_pill_label(pl["role"])}</span>',
        ])
    return table(["खिलाड़ी", "मूल टीम", "भूमिका"], rows)


def _as_scoreline(g, depth, big=False):
    a, b = g["teamA"], g["teamB"]
    wa = "ring-2 ring-kb-orange" if g["winner"] == "A" else ""
    wb = "ring-2 ring-kb-orange" if g["winner"] == "B" else ""
    sz = "text-4xl sm:text-5xl" if big else "text-3xl"
    return f"""<div class="grid grid-cols-[1fr_auto_1fr] items-center gap-3 bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 mb-6">
      <div class="text-center rounded-xl p-3 {wa}" style="background:{a['color']}10">
        <div class="hi font-heading font-extrabold text-base sm:text-lg text-kb-ink leading-tight">{esc(a['name_hi'])}</div>
        <div class="font-heading font-extrabold tnum {sz} text-kb-ink mt-1">{a['score']}</div>
      </div>
      <div class="hi text-kb-text font-bold text-sm">बनाम</div>
      <div class="text-center rounded-xl p-3 {wb}" style="background:{b['color']}10">
        <div class="hi font-heading font-extrabold text-base sm:text-lg text-kb-ink leading-tight">{esc(b['name_hi'])}</div>
        <div class="font-heading font-extrabold tnum {sz} text-kb-ink mt-1">{b['score']}</div>
      </div>
    </div>"""


def build_allstar_index():
    depth = 1
    cards = ""
    for g in ALL_STAR_GAMES:
        win = g["teamA"] if g["winner"] == "A" else g["teamB"]
        cards += f"""<a href="{g['slug']}/" class="block bg-kb-card border border-kb-border rounded-xl p-5 hover:border-kb-orange hover:shadow-md transition">
          <div class="hi text-xs font-semibold text-kb-orange uppercase tracking-wide">सीज़न {g['season']} · {g['year']}</div>
          <div class="font-heading font-extrabold text-lg text-kb-ink hi leading-tight mt-1">{esc(g['title_hi'])}</div>
          <div class="hi text-sm text-kb-text mt-1">{esc(g['subtitle_hi'])}</div>
          <div class="hi text-sm mt-2 text-kb-ink">परिणाम: <b>{esc(win['name_hi'])}</b> · {g['teamA']['score']}–{g['teamB']['score']}</div>
          <div class="hi text-xs text-kb-text mt-1">MVP: {esc(g['mvp']['name_hi'])} · {esc(g['venue_hi'])}</div></a>"""
    body = f"""{page_h1('पीकेएल ऑल-स्टार मुक़ाबले', 'प्रो कबड्डी लीग के शीर्ष सितारों के प्रदर्शनी ऑल-स्टार शोकेस — परिणाम, रोस्टर और सर्वश्रेष्ठ खिलाड़ी')}
      {C.prose([
        "प्रो कबड्डी लीग में समय-समय पर ऑल-स्टार और प्रदर्शनी मुक़ाबले आयोजित किए गए, जिनमें "
        "लीग के सबसे चमकदार सितारों को दो टीमों में बाँटकर एक रोमांचक शोकेस मैच खिलाया गया। "
        "ये मुक़ाबले प्रशंसकों के लिए अपने पसंदीदा रेडरों और डिफेंडरों को एक ही मैट पर, सामान्य "
        "टीम-प्रतिद्वंद्विता से परे, साथ खेलते देखने का अनोखा मौक़ा रहे। यहाँ पीकेएल के ऑल-स्टार "
        "शोकेस का इतिहास है — कब हुए, किसने जीते, किन सितारों ने हिस्सा लिया और कौन सर्वश्रेष्ठ रहा।",
      ])}
      <div class="grid sm:grid-cols-2 gap-3">{cards}</div>"""
    desc = ("पीकेएल ऑल-स्टार और प्रदर्शनी मुक़ाबलों का इतिहास — सीज़न 5 और सीज़न 6 शोकेस के "
            "परिणाम, टीम रोस्टर, MVP और सर्वश्रेष्ठ खिलाड़ी हिंदी में।")
    write("all-star/index.html", page("पीकेएल ऑल-स्टार मुक़ाबले — रोस्टर व MVP | कबड्डी आँकड़े",
                                       desc, "/all-star/", depth, body, active="allstar",
                                       trail=[("होम", "../"), ("ऑल-स्टार", None)]), "0.8")
    search_rows.append(["ऑल-स्टार मुक़ाबले", "/all-star/", "पेज",
                        "all star game exhibition pkl kabaddi showcase roster mvp"])


def build_allstar_game(g):
    depth = 2
    win = g["teamA"] if g["winner"] == "A" else g["teamB"]
    s = next((x for x in SEASONS if x["num"] == g["season"]), None)

    tiles = f"""<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {stat('सीज़न', f"सीज़न {g['season']}", g['year'])}
      {stat('विजेता', win['short'], win['name_hi'])}
      {stat('MVP', '', g['mvp']['name_hi'])}
      {stat('स्थान', '', g['venue_hi'])}</div>"""

    # MVP highlight
    mvp_card = f"""<div class="bg-kb-card border border-kb-border rounded-2xl p-5 mb-6" style="border-left:4px solid #FF6B00">
      <div class="hi text-xs font-semibold text-kb-orange uppercase tracking-wide">मैच का सर्वश्रेष्ठ खिलाड़ी (MVP)</div>
      <div class="mt-1 text-lg">{_as_name_cell(g['mvp'], depth)}</div>
      <div class="hi text-sm text-kb-text mt-1">{esc(g['mvp']['line_hi'])}</div></div>"""

    # standout performers table
    prows = []
    for p in g["performers"]:
        prows.append([_as_name_cell(p, depth), team_link(p["team"], depth),
                      f'<span class="hi">{esc(p["line_hi"])}</span>'])
    perf_tbl = table(["खिलाड़ी", "मूल टीम", "प्रदर्शन"], prows)

    # facts
    facts = table(['विवरण', 'जानकारी'], [
        ['<span class="hi">आयोजन</span>', f'<span class="hi">{esc(g["title_hi"])}</span>'],
        ['<span class="hi">प्रारूप</span>', f'<span class="hi">{esc(g["format_hi"])}</span>'],
        ['<span class="hi">तिथि</span>', f'<span class="hi">{esc(g["date_hi"])}</span>'],
        ['<span class="hi">स्थान</span>', f'<span class="hi">{esc(g["city_hi"])}</span>'],
        ['<span class="hi">परिणाम</span>', f'<span class="hi">{esc(win["name_hi"])} विजयी ({g["teamA"]["score"]}–{g["teamB"]["score"]})</span>'],
    ])

    # prev/next across all-star games
    idx = ALL_STAR_GAMES.index(g)
    prev_g = ALL_STAR_GAMES[idx - 1] if idx > 0 else None
    next_g = ALL_STAR_GAMES[idx + 1] if idx < len(ALL_STAR_GAMES) - 1 else None
    navs = '<div class="flex justify-between mt-8">'
    navs += (f'<a href="../{prev_g["slug"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">← सीज़न {prev_g["season"]} ऑल-स्टार</a>'
             if prev_g else '<span></span>')
    navs += (f'<a href="../{next_g["slug"]}/" class="hi px-4 py-2 rounded-lg border border-kb-border bg-white text-sm hover:border-kb-orange">सीज़न {next_g["season"]} ऑल-स्टार →</a>'
             if next_g else '<span></span>')
    navs += '</div>'

    season_link = (f'<a href="../../seasons/season-{g["season"]}/" class="hi text-kb-orange font-semibold hover:underline">सीज़न {g["season"]} का पूरा ब्योरा →</a>'
                   if s else "")

    body = f"""
    <div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 mb-6" style="border-top:4px solid #FF6B00">
      <div class="hi text-xs font-semibold text-kb-orange uppercase tracking-wide">सीज़न {g['season']} · {g['year']}</div>
      <h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink leading-tight hi mt-1">{esc(g['title_hi'])}</h1>
      <div class="hi text-sm text-kb-text mt-1">{esc(g['subtitle_hi'])} · {esc(g['venue_hi'])}</div>
    </div>
    {_as_scoreline(g, depth, big=True)}
    {tiles}
    {C.prose([g['note']])}
    {mvp_card}
    {section_title(g['teamA']['name_hi'], 'टीम रोस्टर')}
    {_as_roster_table(g['rosterA'], depth)}
    <div class="mb-6"></div>
    {section_title(g['teamB']['name_hi'], 'टीम रोस्टर')}
    {_as_roster_table(g['rosterB'], depth)}
    <div class="mb-6"></div>
    {section_title('सर्वश्रेष्ठ प्रदर्शन', 'मुक़ाबले के स्टैंडआउट खिलाड़ी')}
    {perf_tbl}
    <div class="mb-6"></div>
    {section_title('मैच विवरण')}
    {facts}
    <div class="mt-4">{season_link}</div>
    <div class="mt-6"><a href="../" class="hi text-kb-orange font-semibold hover:underline">← सभी ऑल-स्टार मुक़ाबले</a></div>
    {navs}
    """
    desc = (f"{g['title_hi']} ({g['year']}) — {g['subtitle_hi']}। {win['name_hi']} विजयी "
            f"{g['teamA']['score']}–{g['teamB']['score']}, MVP {g['mvp']['name_hi']}। टीम रोस्टर और सर्वश्रेष्ठ खिलाड़ी हिंदी में।")[:300]
    write(f"all-star/{g['slug']}/index.html",
          page(f"{g['title_hi']} — रोस्टर व परिणाम",
               desc, f"/all-star/{g['slug']}/", depth, body, active="allstar",
               trail=[("होम", "../../"), ("ऑल-स्टार", "../"), (f"सीज़न {g['season']}", None)]), "0.7")
    search_rows.append([g['title_hi'], f"/all-star/{g['slug']}/", "ऑल-स्टार",
                        f"all star season {g['season']} {g['year']} pkl exhibition showcase roster mvp kabaddi".lower()])


# ============================================================ THIS DAY ========
# (month, day, year, title_hi, desc_hi)
THISDAY = [
    (8, 31, 2014, "पीकेएल का पहला सीज़न शुरू", "31 अगस्त 2014 को मुंबई में जयपुर पिंक पैंथर्स ने यू मुंबा को 35–24 से हराकर पहला पीकेएल ख़िताब जीता।"),
    (7, 31, 2016, "पटना की लगातार दूसरी ट्रॉफ़ी", "सीज़न 4 के फ़ाइनल में पटना पाइरेट्स ने जयपुर पिंक पैंथर्स को 37–29 से हराया।"),
    (10, 28, 2017, "प्रदीप नरवाल का 369 रेड अंक का सीज़न", "सीज़न 5 में पटना पाइरेट्स ने गुजरात को 55–38 से हराया; प्रदीप नरवाल ने 369 रेड अंक का रिकॉर्ड बनाया।"),
    (1, 5, 2019, "बेंगलुरु बुल्स का पहला ख़िताब", "सीज़न 6 के फ़ाइनल में बेंगलुरु बुल्स ने गुजरात को 38–33 से हराया; पवन सहरावत एमवीपी बने।"),
    (10, 19, 2019, "बंगाल वॉरियर्स चैंपियन", "सीज़न 7 के फ़ाइनल में बंगाल वॉरियर्स ने दबंग दिल्ली को 39–34 से हराकर पहला ख़िताब जीता।"),
    (2, 25, 2022, "दबंग दिल्ली का पहला ख़िताब", "सीज़न 8 के फ़ाइनल में दबंग दिल्ली ने पटना पाइरेट्स को 37–36 के रोमांचक मुक़ाबले में हराया।"),
    (12, 17, 2022, "जयपुर की वापसी", "सीज़न 9 के फ़ाइनल में जयपुर पिंक पैंथर्स ने पुनेरी पलटन को 33–29 से हराकर दूसरा ख़िताब जीता।"),
    (3, 1, 2024, "पुनेरी पलटन का पहला ख़िताब", "सीज़न 10 के फ़ाइनल में पुनेरी पलटन ने हरियाणा स्टीलर्स को 28–25 से हराया।"),
    (10, 25, 2016, "भारत का तीसरा विश्व कप", "अहमदाबाद में भारत ने ईरान को 38–29 से हराकर 2016 कबड्डी विश्व कप जीता।"),
    (10, 13, 2024, "पवन सहरावत के 39 अंक", "पवन सहरावत ने एक मैच में सर्वाधिक 39 रेड अंक का रिकॉर्ड बनाया (सीज़न 7, बनाम हरियाणा)।"),
    (12, 1, 2024, "हरियाणा स्टीलर्स का पहला ख़िताब", "सीज़न 11 के फ़ाइनल में हरियाणा स्टीलर्स ने पटना पाइरेट्स को 32–23 से हराकर पहली ट्रॉफ़ी जीती।"),
]
HI_MONTHS = ["", "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई",
             "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]


def _dayslug(mo, da):
    return f"{HI_MONTHS[mo]}-{da}".replace("‍", "")


def build_thisday():
    depth = 1
    # group by (month, day)
    from collections import defaultdict
    days = defaultdict(list)
    for mo, da, yr, title, desc in THISDAY:
        days[(mo, da)].append((yr, title, desc))
    # index
    rows = ""
    for (mo, da) in sorted(days.keys()):
        evs = days[(mo, da)]
        ds = _dayslug(mo, da)
        rows += (f'<a href="{ds}/" class="block bg-kb-card border border-kb-border rounded-xl p-4 hover:border-kb-orange transition">'
                 f'<div class="hi font-heading font-bold text-kb-ink">{da} {HI_MONTHS[mo]}</div>'
                 f'<div class="hi text-sm text-kb-text mt-1">{esc(evs[0][1])}{(" · और " + str(len(evs)-1) + " घटना") if len(evs)>1 else ""}</div></a>')
    body = f"""{page_h1('आज के दिन कबड्डी में', 'कबड्डी इतिहास की यादगार तारीख़ें')}
      <section class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{rows}</section>"""
    desc = "आज के दिन कबड्डी में — पीकेएल फ़ाइनल, रिकॉर्ड और कबड्डी इतिहास की यादगार घटनाएँ तारीख़ के अनुसार हिंदी में।"
    write("aaj-ke-din/index.html", page("आज के दिन कबड्डी में — ऐतिहासिक घटनाएँ | कबड्डी आँकड़े",
                                         desc, "/aaj-ke-din/", depth, body, active="thisday",
                                         trail=[("होम", "../"), ("आज के दिन", None)]), "0.6")
    search_rows.append(["आज के दिन कबड्डी में", "/aaj-ke-din/", "पेज", "this day aaj ke din history kabaddi"])

    all_days = sorted(days.keys())
    # Internal "related pages" used on every on-this-day detail page.
    related = [("सभी पीकेएल सीज़न", "../../seasons/"), ("अंक तालिका", "../../standings/"),
               ("मैच परिणाम", "../../matches/"), ("कबड्डी रिकॉर्ड", "../../records/"),
               ("नीलामी इतिहास", "../../auctions/"), ("सभी टीमें", "../../teams/"),
               ("सभी खिलाड़ी", "../../players/")]

    def _chip(label, href):
        return (f'<a href="{href}" class="hi inline-block px-3 py-1.5 rounded-lg border '
                f'border-kb-border bg-white text-sm text-kb-text hover:border-kb-orange '
                f'hover:text-kb-orange transition">{label}</a>')

    for (mo, da), evs in days.items():
        ds = _dayslug(mo, da)
        month = HI_MONTHS[mo]
        evs_sorted = sorted(evs)
        years = [str(y) for y, _, _ in evs_sorted]
        titles = [t for _, t, _ in evs_sorted]
        cards = ""
        for yr, title, desc2 in evs_sorted:
            cards += (f'<div class="bg-kb-card border border-kb-border rounded-xl p-5 mb-4">'
                      f'<div class="hi text-sm font-bold text-kb-orange mb-1">{yr}</div>'
                      f'<h3 class="hi font-heading font-bold text-lg text-kb-ink mb-1">{esc(title)}</h3>'
                      f'<p class="hi text-[15px] text-kb-text leading-relaxed">{esc(desc2)}</p></div>')
        ev_word = "घटना" if len(evs_sorted) == 1 else "घटनाएँ"
        lead = (f"{da} {month} प्रो कबड्डी लीग और भारतीय कबड्डी के इतिहास की एक यादगार तारीख़ है। "
                f"इस दिन {esc(', '.join(titles))} जैसी {ev_word} दर्ज है — "
                f"नीचे इस तारीख़ से जुड़े प्रमुख पल, फ़ाइनल स्कोर और रिकॉर्ड दिए गए हैं।")
        # context paragraph — woven from this date's own events to avoid thin/duplicate pages
        context = (f"प्रो कबड्डी लीग की शुरुआत 2014 में हुई और तब से यह दुनिया की सबसे लोकप्रिय "
                   f"कबड्डी प्रतियोगिताओं में से एक बन चुकी है। {da} {month} ({', '.join(years)}) की "
                   f"यह {ev_word} इसी सफ़र का हिस्सा है। हर सीज़न का पूरा ब्योरा, अंतिम अंक तालिका, "
                   f"फ़ाइनल परिणाम और सर्वकालिक रिकॉर्ड जानने के लिए नीचे दिए गए पृष्ठ देखें।")
        related_chips = "".join(_chip(l, h) for l, h in related)
        # cross-links to a few other notable dates
        others = [(m2, d2) for (m2, d2) in all_days if (m2, d2) != (mo, da)][:6]
        other_chips = "".join(
            _chip(f"{d2} {HI_MONTHS[m2]}", f"../{_dayslug(m2, d2)}/") for m2, d2 in others)
        body = f"""<h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink hi mb-3">{da} {month} — कबड्डी इतिहास</h1>
          <p class="hi text-[15px] text-kb-text leading-relaxed mb-6">{lead}</p>
          <h2 class="hi font-heading font-bold text-xl text-kb-ink mb-4 flex items-center gap-2"><span class="w-1.5 h-6 rounded mat-stripe inline-block"></span>इस दिन की घटनाएँ</h2>
          {cards}
          <h2 class="hi font-heading font-bold text-xl text-kb-ink mt-8 mb-3 flex items-center gap-2"><span class="w-1.5 h-6 rounded mat-stripe inline-block"></span>इस तारीख़ का महत्व</h2>
          <section class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 mb-8"><p class="hi text-[15px] text-kb-text leading-relaxed">{context}</p></section>
          <h2 class="hi font-heading font-bold text-xl text-kb-ink mb-3 flex items-center gap-2"><span class="w-1.5 h-6 rounded mat-stripe inline-block"></span>संबंधित पृष्ठ</h2>
          <div class="flex flex-wrap gap-2 mb-8">{related_chips}</div>
          <h2 class="hi font-heading font-bold text-xl text-kb-ink mb-3 flex items-center gap-2"><span class="w-1.5 h-6 rounded mat-stripe inline-block"></span>अन्य तारीख़ें</h2>
          <div class="flex flex-wrap gap-2">{other_chips}</div>
          <div class="text-center mt-8"><a href="../" class="hi text-kb-orange font-semibold hover:underline">← सभी तारीख़ें</a></div>"""
        d2 = f"{da} {month} को कबड्डी इतिहास में हुई घटनाएँ — {evs_sorted[0][1]}।"
        write(f"aaj-ke-din/{ds}/index.html",
              page(f"{da} {month} — आज के दिन कबड्डी में | कबड्डी आँकड़े",
                   d2, f"/aaj-ke-din/{ds}/", 2, body, active="thisday",
                   trail=[("होम", "../../"), ("आज के दिन", "../"), (f"{da} {month}", None)]), "0.5")


# ========================================================== STATIC CONTENT ====
def build_about():
    depth = 1
    glossary = "".join(
        f'<div class="border-t border-kb-border py-3 first:border-0"><div class="hi font-semibold text-kb-ink">{esc(term)}</div>'
        f'<div class="hi text-sm text-kb-text mt-0.5 leading-relaxed">{esc(d)}</div></div>'
        for term, d in GLOSSARY)
    body = C.about_body(page_h1) + f"""
      <div class="mt-6">{section_title('कबड्डी शब्दावली', 'खेल के प्रमुख शब्द और नियम')}</div>
      <div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6">{glossary}</div>"""
    desc = ("कबड्डी आँकड़े (KabaddiStats.com) के बारे में जानें — हिंदी में प्रो कबड्डी लीग और "
            "अंतरराष्ट्रीय कबड्डी आँकड़ों का मुफ़्त मंच, साथ ही कबड्डी शब्दावली।")
    write("about/index.html", page("हमारे बारे में — कबड्डी आँकड़े | KabaddiStats",
                                    desc, "/about/", depth, body, active="about",
                                    trail=[("होम", "../"), ("हमारे बारे में", None)]), "0.5")
    search_rows.append(["हमारे बारे में", "/about/", "पेज", "about hamare bare mein glossary kabaddi terms"])


def build_privacy():
    depth = 1
    body = C.privacy_body(page_h1)
    desc = ("कबड्डी आँकड़े (KabaddiStats.com) की गोपनीयता नीति — हम आपकी जानकारी को कैसे "
            "एकत्र, उपयोग और सुरक्षित करते हैं, इसकी पूरी जानकारी हिंदी में।")
    write("privacy/index.html", page("गोपनीयता नीति — कबड्डी आँकड़े | KabaddiStats",
                                      desc, "/privacy/", depth, body, active="",
                                      trail=[("होम", "../"), ("गोपनीयता नीति", None)]), "0.4")
    search_rows.append(["गोपनीयता नीति", "/privacy/", "पेज", "privacy gopniyata niti policy"])


# ============================================================ STATIC ASSETS ===
def favicon_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
            '<circle cx="32" cy="32" r="30" fill="#FF6B00"/>'
            '<circle cx="32" cy="20" r="6" fill="#fff"/>'
            '<path d="M32 27 L32 41" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M19 31 L32 34 L45 29" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
            '<path d="M32 41 L24 53" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M32 41 L42 52" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/></svg>')


def write_og_image():
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    ORANGE = (255, 107, 0)
    DARK = (154, 52, 18)
    CREAM = (255, 237, 213)
    img = Image.new("RGB", (W, H), ORANGE)
    draw = ImageDraw.Draw(img)
    # vertical gradient towards a deeper orange at the bottom
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        grad.putpixel((0, y), int(120 * (y / H)))
    grad = grad.resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), DARK), img, grad)
    draw = ImageDraw.Draw(img)

    # large semi-transparent raider glyph on the right
    gx, gy, s = 900, 315, 1.0
    white = (255, 255, 255)
    soft = (255, 255, 255)
    # head
    draw.ellipse([gx-30, gy-150, gx+30, gy-90], fill=soft)
    # body
    draw.line([gx, gy-90, gx, gy+10], fill=soft, width=22)
    # arms (raid reach)
    draw.line([gx-120, gy-40, gx+120, gy-70], fill=soft, width=22)
    # legs (lunge)
    draw.line([gx, gy+10, gx-70, gy+130], fill=soft, width=22)
    draw.line([gx, gy+10, gx+85, gy+120], fill=soft, width=22)

    def font(size, bold=True):
        for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf"
                  if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
        return ImageFont.load_default()

    draw.rectangle([92, 150, 250, 162], fill=CREAM)
    draw.text((88, 188), "KABADDI", font=font(98), fill=(255, 255, 255))
    draw.text((88, 292), "STATS", font=font(98), fill=CREAM)
    draw.text((92, 420), "Kabaddi statistics in Hindi", font=font(40, False), fill=(255, 235, 220))
    draw.text((92, 545), "kabaddistats.com", font=font(36), fill=(255, 255, 255))
    img.save(OUT / "og-image.png", "PNG")


def write_favicons():
    from PIL import Image
    svg = OUT / "favicon.svg"
    sizes = {"favicon-16x16.png": 16, "favicon-32x32.png": 32,
             "favicon-192x192.png": 192, "favicon-512x512.png": 512,
             "apple-touch-icon.png": 180}
    have_rsvg = True
    for name, size in sizes.items():
        try:
            subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size),
                            str(svg), "-o", str(OUT / name)], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            have_rsvg = False
            break
    if not have_rsvg:
        # fallback: draw a simple orange disc with Pillow
        from PIL import Image as I, ImageDraw
        for name, size in sizes.items():
            im = I.new("RGBA", (size, size), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.ellipse([0, 0, size-1, size-1], fill=(255, 107, 0, 255))
            im.save(OUT / name)
    apple = Image.open(OUT / "apple-touch-icon.png").convert("RGBA")
    bg = Image.new("RGBA", apple.size, (255, 255, 255, 255))
    bg.alpha_composite(apple)
    bg.convert("RGB").save(OUT / "apple-touch-icon.png")
    Image.open(OUT / "favicon-32x32.png").convert("RGBA").save(
        OUT / "favicon.ico", sizes=[(16, 16), (32, 32)])
    manifest = {
        "name": BRAND, "short_name": BRAND,
        "icons": [
            {"src": "/favicon-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/favicon-512x512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": "#FF6B00", "background_color": "#ffffff", "display": "standalone",
    }
    (OUT / "site.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_static():
    (OUT / "favicon.svg").write_text(favicon_svg())
    write_favicons()
    try:
        write_og_image()
    except Exception as e:
        print("  og-image skipped:", e)
    (OUT / "search.js").write_text(SEARCH_JS, encoding="utf-8")
    (OUT / "search-index.json").write_text(
        json.dumps(search_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY + "\n")
    (OUT / "CNAME").write_text("kabaddistats.com\n")
    body404 = ('<div class="text-center py-20"><h1 class="hi font-heading font-extrabold text-6xl text-kb-orange">404</h1>'
               '<p class="hi text-xl text-kb-ink mt-4">यह पेज नहीं मिला</p>'
               '<a href="/" class="hi inline-block mt-6 px-5 py-2.5 rounded-lg bg-kb-orange text-white font-semibold">होम पर लौटें</a></div>')
    (OUT / "404.html").write_text(page("पेज नहीं मिला (404) | कबड्डी आँकड़े",
        "यह पेज उपलब्ध नहीं है।", "/404.html", 0, body404, active="",
        robots="noindex, nofollow"), encoding="utf-8")


def _lastmod_for(url):
    """Vary lastmod a little by section so the sitemap isn't a wall of identical
    dates. Data-bearing sections (seasons, matches, standings, auctions) track the
    latest build; mostly-static pages (about, privacy) carry an older date."""
    static_older = ("/about/", "/privacy/", "/404.html")
    if url in static_older:
        return BUILD_DATE_STATIC
    return TODAY


def write_sitemap():
    seen, items = set(), []
    for url, prio in urls:
        if url in seen:
            continue
        seen.add(url)
        items.append(f"  <url><loc>{SITE}{url}</loc><lastmod>{_lastmod_for(url)}</lastmod>"
                     f"<priority>{prio}</priority></url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(items) + "\n</urlset>\n")
    (OUT / "sitemap.xml").write_text(xml, encoding="utf-8")
    return len(items)


SEARCH_JS = r"""
let KB_idx=null,KB_box=null;
async function KB_load(){if(KB_idx)return KB_idx;
  const r=await fetch(location.origin+'/search-index.json');KB_idx=await r.json();return KB_idx;}
function KB_search(){if(KB_box){KB_box.remove();KB_box=null;return;}
  KB_box=document.createElement('div');
  KB_box.style.cssText='position:fixed;inset:0;z-index:200;background:rgba(42,28,18,.45);backdrop-filter:blur(3px);display:flex;align-items:flex-start;justify-content:center;padding-top:10vh';
  KB_box.innerHTML='<div onclick="event.stopPropagation()" style="width:92%;max-width:560px;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.3)">'+
    '<input id="kbq" placeholder="खिलाड़ी, टीम, सीज़न, रिकॉर्ड खोजें…" style="width:100%;padding:16px 18px;border:0;outline:0;font-size:16px;border-bottom:1px solid #f0e3d8;font-family:Inter,Noto Sans Devanagari,sans-serif">'+
    '<div id="kbr" style="max-height:60vh;overflow:auto"></div></div>';
  KB_box.onclick=()=>KB_search();
  document.body.appendChild(KB_box);
  const q=document.getElementById('kbq');q.focus();
  KB_load().then(()=>KB_render(''));
  q.addEventListener('input',e=>KB_render(e.target.value));
  q.addEventListener('keydown',e=>{if(e.key==='Escape')KB_search();});
}
function KB_render(term){
  const box=document.getElementById('kbr');if(!box)return;
  term=(term||'').trim().toLowerCase();
  let res=KB_idx||[];
  if(term){res=res.filter(r=>r[3].includes(term)||r[0].toLowerCase().includes(term));}
  res=res.slice(0,40);
  if(!res.length){box.innerHTML='<div style="padding:18px;color:#6b5d52;font-family:Noto Sans Devanagari,sans-serif">कोई परिणाम नहीं मिला</div>';return;}
  box.innerHTML=res.map(r=>'<a href="'+location.origin+r[1]+'" style="display:flex;justify-content:space-between;gap:10px;padding:12px 18px;border-top:1px solid #f4ece4;text-decoration:none;color:#2a1c12">'+
    '<span style="font-weight:600;font-family:Inter,Noto Sans Devanagari,sans-serif">'+r[0]+'</span>'+
    '<span style="color:#FF6B00;font-size:13px;font-family:Noto Sans Devanagari,sans-serif">'+r[2]+'</span></a>').join('');
}
window.KB_search=KB_search;
"""


def build_css():
    """Compile a static, minified Tailwind stylesheet (styles.css) from the
    already-generated HTML, replacing the cdn.tailwindcss.com runtime. Runs after
    all pages are written so only utilities actually present in the output are
    emitted. If the Tailwind CLI is unavailable, the previously committed
    styles.css is left in place and a warning is printed."""
    cfg = ROOT / "build-css" / "tailwind.config.js"
    src = ROOT / "build-css" / "input.css"
    out = OUT / "styles.css"
    try:
        subprocess.run(
            ["npx", "-y", "tailwindcss@3.4.17", "-c", str(cfg),
             "-i", str(src), "-o", str(out), "--minify"],
            check=True, capture_output=True, text=True)
        print(f"  styles.css: {out.stat().st_size // 1024} KB")
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        msg = getattr(e, "stderr", "") or str(e)
        print(f"  styles.css rebuild skipped ({msg.strip().splitlines()[-1] if msg.strip() else e});"
              " keeping committed file.")


# ==================================================================== MAIN ====
def main():
    print("Generating KabaddiStats.com …")
    build_home()
    for p in PLAYERS:
        build_player(p)
    build_players_index()
    build_teams_index()
    for ts, t in TEAMS.items():
        build_team(ts, t)
    build_seasons_index()
    for i, s in enumerate(SEASONS):
        prev_s = SEASONS[i-1] if i > 0 else None
        next_s = SEASONS[i+1] if i < len(SEASONS)-1 else None
        build_season(s, prev_s, next_s)
    build_matches_index()
    for i, s in enumerate(SEASONS):
        prev_s = SEASONS[i-1] if i > 0 else None
        next_s = SEASONS[i+1] if i < len(SEASONS)-1 else None
        build_season_matches(s, prev_s, next_s)
    build_standings_index()
    for i, s in enumerate(SEASONS):
        prev_s = SEASONS[i-1] if i > 0 else None
        next_s = SEASONS[i+1] if i < len(SEASONS)-1 else None
        build_season_standings(s, prev_s, next_s)
    build_venues_index()
    for v in VENUES:
        build_venue(v)
    build_auctions_index()
    for n in sorted(AUCTIONS.keys()):
        build_auction_season(n)
    build_allstar_index()
    for g in ALL_STAR_GAMES:
        build_allstar_game(g)
    build_records()
    build_compare_index()
    for a, b in COMPARE_PAIRS:
        build_compare_pair(a, b)
    for r in RIVALRIES:
        build_rivalry(*r)
    build_international()
    build_thisday()
    build_about()
    build_privacy()
    write_static()
    build_css()
    n = write_sitemap()
    print(f"  pages written: {len(urls)}  ·  sitemap urls: {n}")
    print(f"  players: {len(PLAYERS)}  teams: {len(TEAMS)}  seasons: {len(SEASONS)}")
    print("Done.")


if __name__ == "__main__":
    main()
