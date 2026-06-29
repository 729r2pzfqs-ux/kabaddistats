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
                  WORLD_CUP, ASIAN_GAMES_MEN, ASIAN_GAMES_WOMEN, GLOSSARY)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT
TODAY = datetime.date.today().isoformat()
INDEXNOW_KEY = "9d4e1f7a2c6b48e0a3f5c1d9b7e6a204"

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


def table(headers, rows, align_right=None):
    align_right = align_right or set()
    thead = "".join(
        f'<th class="hi px-3 py-2 text-{("right" if i in align_right else "left")} '
        f'text-xs font-bold text-kb-text uppercase tracking-wide whitespace-nowrap">{h}</th>'
        for i, h in enumerate(headers))
    body = ""
    for r in rows:
        tds = ""
        for i, c in enumerate(r):
            a = "right tnum" if i in align_right else "left"
            tds += f'<td class="px-3 py-2 text-{a} text-sm whitespace-nowrap">{c}</td>'
        body += f"<tr class='border-t border-kb-border'>{tds}</tr>"
    return (f'<div class="overflow-x-auto bg-kb-card border border-kb-border rounded-xl">'
            f'<table class="w-full min-w-full"><thead class="bg-kb-bg">'
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
      {stat('सीज़न', f'{len(SEASONS)}', '2014 से 2024')}
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
      "संपूर्ण आँकड़ा मंच है, जहाँ प्रो कबड्डी लीग (पीकेएल) के सभी 11 सीज़न और "
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
    title = f"{p['name']} {p['name_hi']} — कबड्डी आँकड़े व करियर रिकॉर्ड"
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
                     f'<span class="hi text-xs">{role_badge(p["role"])}</span>',
                     f'<span class="hi text-xs text-kb-text">{esc(TEAMS[p["teams"][0]]["name_hi"]) if p["teams"] else ""}</span>',
                     f'{p["raid"]:,}', f'{p["tackle"]:,}', f'{p["total"]:,}'])
    body = f"""
    {section_title('सभी खिलाड़ी', f'करियर कुल अंक के अनुसार शीर्ष {len(PLAYERS)} खिलाड़ी — किसी भी नाम पर क्लिक करें')}
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
    body = f"""{section_title('सभी टीमें', 'प्रो कबड्डी लीग की सभी 12 फ़्रेंचाइज़ी — ख़िताब के अनुसार')}
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
          page(f"{t['name_hi']} — पीकेएल टीम आँकड़े व इतिहास | कबड्डी आँकड़े",
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
    body = f"""{section_title('सभी पीकेएल सीज़न', 'प्रो कबड्डी लीग का हर सीज़न — चैंपियन, फ़ाइनल और एमवीपी')}
      {table(['सीज़न', 'वर्ष', T['champion'], 'उपविजेता', 'फ़ाइनल', 'एमवीपी'], rows)}"""
    desc = "प्रो कबड्डी लीग के सभी सीज़न (1 से 11) — हर सीज़न के चैंपियन, उपविजेता, फ़ाइनल स्कोर, शीर्ष रेडर, शीर्ष डिफेंडर और एमवीपी हिंदी में।"
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

    body = f"""{section_title('कबड्डी रिकॉर्ड', 'प्रो कबड्डी लीग के सर्वकालिक रिकॉर्ड और लीडरबोर्ड')}
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
]

RIVALRIES = [
    ("patna-pirates", "u-mumba", "पटना पाइरेट्स और यू मुंबा की भिड़ंत पीकेएल की सबसे पुरानी प्रतिद्वंद्विताओं में से एक है — दोनों ने शुरुआती सीज़न के कई फ़ाइनल और नॉकआउट मुक़ाबले खेले।"),
    ("u-mumba", "puneri-paltan", "महाराष्ट्र डर्बी — मुंबई बनाम पुणे। दोनों टीमों के बीच के मुक़ाबले राज्य के गौरव की लड़ाई बन जाते हैं।"),
    ("bengaluru-bulls", "telugu-titans", "दक्षिण भारत की दो उद्घाटन टीमों के बीच की टक्कर; रोहित कुमार और राहुल चौधरी के द्वंद्व ने इसे यादगार बनाया।"),
    ("jaipur-pink-panthers", "dabang-delhi", "उत्तर भारत की दो हाई-प्रोफ़ाइल टीमें — अर्जुन देशवाल बनाम नवीन कुमार की रेडिंग जंग।"),
    ("patna-pirates", "haryana-steelers", "सीज़न 11 के फ़ाइनल ने इस भिड़ंत को नई धार दी, जहाँ हरियाणा ने पटना को हराकर पहला ख़िताब जीता।"),
    ("bengal-warriors", "dabang-delhi", "सीज़न 7 के फ़ाइनल की पुनरावृत्ति — बंगाल वॉरियर्स और दबंग दिल्ली की रोमांचक प्रतिद्वंद्विता।"),
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
    for a, b, _desc in RIVALRIES:
        ta, tb = TEAMS[a], TEAMS[b]
        rcards += f"""<a href="rivalry-{a}-vs-{b}/" class="block bg-kb-card border border-kb-border rounded-xl p-4 hover:border-kb-orange hover:shadow-md transition">
          <div class="hi font-heading font-bold text-kb-ink">{esc(ta['name_hi'])} <span class="text-kb-orange">बनाम</span> {esc(tb['name_hi'])}</div></a>"""
    body = f"""{section_title('तुलना और प्रतिद्वंद्विता', 'दो खिलाड़ियों की हेड-टू-हेड तुलना और टीम प्रतिद्वंद्विताएँ')}
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
          page(f"{pa['name_hi']} बनाम {pb['name_hi']} — तुलना | कबड्डी आँकड़े",
               desc, f"/compare/{a}-vs-{b}/", depth, body, active="compare",
               trail=[("होम", "../../"), ("तुलना", "../"), (f"{pa['name_hi']} बनाम {pb['name_hi']}", None)]), "0.6")
    search_rows.append([f"{pa['name']} बनाम {pb['name']}", f"/compare/{a}-vs-{b}/", "तुलना",
                        f"{pa['name']} vs {pb['name']} compare tulna".lower()])


def build_rivalry(a, b, narr):
    depth = 2
    ta, tb = TEAMS[a], TEAMS[b]

    def tbox(t, ts):
        return (f'<div class="bg-kb-card border border-kb-border rounded-xl p-4 text-center" style="border-top:3px solid {t["color"]}">'
                f'<a href="../../teams/{ts}/" class="font-heading font-bold text-kb-ink hover:text-kb-orange hi">{esc(t["name_hi"])}</a>'
                f'<div class="hi text-xs text-kb-text mt-1">{esc(t["city"])}</div>'
                f'<div class="hi text-sm mt-2 text-kb-orange font-semibold">{len(t["titles"])} ख़िताब</div></div>')

    body = f"""
    <h1 class="font-heading font-extrabold text-xl sm:text-2xl text-kb-ink text-center hi mb-6">{esc(ta['name_hi'])} <span class="text-kb-orange">बनाम</span> {esc(tb['name_hi'])}</h1>
    <div class="grid grid-cols-2 gap-4 mb-6">{tbox(ta, a)}{tbox(tb, b)}</div>
    {C.prose([narr])}
    <div class="text-center"><a href="../" class="hi text-kb-orange font-semibold hover:underline">← सभी तुलनाएँ</a></div>
    """
    desc = (f"{ta['name_hi']} बनाम {tb['name_hi']} — पीकेएल की प्रतिद्वंद्विता, ख़िताब और प्रमुख मुक़ाबले हिंदी में।")[:300]
    write(f"compare/rivalry-{a}-vs-{b}/index.html",
          page(f"{ta['name_hi']} बनाम {tb['name_hi']} — पीकेएल प्रतिद्वंद्विता | कबड्डी आँकड़े",
               desc, f"/compare/rivalry-{a}-vs-{b}/", depth, body, active="compare",
               trail=[("होम", "../../"), ("तुलना", "../"), (f"{ta['name_hi']} बनाम {tb['name_hi']}", None)]), "0.6")


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

    body = f"""{section_title('अंतरराष्ट्रीय कबड्डी', 'विश्व कप और एशियाई खेलों में भारत का दबदबा')}
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
    body = f"""{section_title('आज के दिन कबड्डी में', 'कबड्डी इतिहास की यादगार तारीख़ें')}
      <section class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">{rows}</section>"""
    desc = "आज के दिन कबड्डी में — पीकेएल फ़ाइनल, रिकॉर्ड और कबड्डी इतिहास की यादगार घटनाएँ तारीख़ के अनुसार हिंदी में।"
    write("aaj-ke-din/index.html", page("आज के दिन कबड्डी में — ऐतिहासिक घटनाएँ | कबड्डी आँकड़े",
                                         desc, "/aaj-ke-din/", depth, body, active="thisday",
                                         trail=[("होम", "../"), ("आज के दिन", None)]), "0.6")
    search_rows.append(["आज के दिन कबड्डी में", "/aaj-ke-din/", "पेज", "this day aaj ke din history kabaddi"])

    for (mo, da), evs in days.items():
        ds = _dayslug(mo, da)
        cards = ""
        for yr, title, desc2 in sorted(evs):
            cards += (f'<div class="bg-kb-card border border-kb-border rounded-xl p-5 mb-4">'
                      f'<div class="hi text-sm font-bold text-kb-orange mb-1">{yr}</div>'
                      f'<h3 class="hi font-heading font-bold text-lg text-kb-ink mb-1">{esc(title)}</h3>'
                      f'<p class="hi text-[15px] text-kb-text leading-relaxed">{esc(desc2)}</p></div>')
        body = f"""<h1 class="font-heading font-extrabold text-2xl sm:text-3xl text-kb-ink hi mb-1">{da} {HI_MONTHS[mo]} — कबड्डी इतिहास</h1>
          <p class="hi text-kb-text mb-5">इस दिन कबड्डी जगत में क्या हुआ</p>{cards}
          <div class="text-center mt-6"><a href="../" class="hi text-kb-orange font-semibold hover:underline">← सभी तारीख़ें</a></div>"""
        d2 = f"{da} {HI_MONTHS[mo]} को कबड्डी इतिहास में हुई घटनाएँ — {evs[0][1]}।"
        write(f"aaj-ke-din/{ds}/index.html",
              page(f"{da} {HI_MONTHS[mo]} — आज के दिन कबड्डी में | कबड्डी आँकड़े",
                   d2, f"/aaj-ke-din/{ds}/", 2, body, active="thisday",
                   trail=[("होम", "../../"), ("आज के दिन", "../"), (f"{da} {HI_MONTHS[mo]}", None)]), "0.5")


# ========================================================== STATIC CONTENT ====
def build_about():
    depth = 1
    glossary = "".join(
        f'<div class="border-t border-kb-border py-3 first:border-0"><div class="hi font-semibold text-kb-ink">{esc(term)}</div>'
        f'<div class="hi text-sm text-kb-text mt-0.5 leading-relaxed">{esc(d)}</div></div>'
        for term, d in GLOSSARY)
    body = C.about_body(section_title) + f"""
      <div class="mt-6">{section_title('कबड्डी शब्दावली', 'खेल के प्रमुख शब्द और नियम')}</div>
      <div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6">{glossary}</div>"""
    desc = ("कबड्डी आँकड़े (KabaddiStats.com) के बारे में जानें — हिंदी भाषी कबड्डी प्रेमियों के लिए "
            "प्रो कबड्डी लीग और अंतरराष्ट्रीय कबड्डी आँकड़ों का मुफ़्त मंच, साथ ही कबड्डी शब्दावली।")
    write("about/index.html", page("हमारे बारे में — कबड्डी आँकड़े | KabaddiStats",
                                    desc, "/about/", depth, body, active="about",
                                    trail=[("होम", "../"), ("हमारे बारे में", None)]), "0.5")
    search_rows.append(["हमारे बारे में", "/about/", "पेज", "about hamare bare mein glossary kabaddi terms"])


def build_privacy():
    depth = 1
    body = C.privacy_body(section_title)
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
    body404 = ('<div class="text-center py-20"><div class="hi font-heading font-extrabold text-6xl text-kb-orange">404</div>'
               '<p class="hi text-xl text-kb-ink mt-4">यह पेज नहीं मिला</p>'
               '<a href="/" class="hi inline-block mt-6 px-5 py-2.5 rounded-lg bg-kb-orange text-white font-semibold">होम पर लौटें</a></div>')
    (OUT / "404.html").write_text(page("पेज नहीं मिला (404) | कबड्डी आँकड़े",
        "यह पेज उपलब्ध नहीं है।", "/404.html", 0, body404, active=""), encoding="utf-8")


def write_sitemap():
    seen, items = set(), []
    for url, prio in urls:
        if url in seen:
            continue
        seen.add(url)
        items.append(f"  <url><loc>{SITE}{url}</loc><lastmod>{TODAY}</lastmod>"
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
    build_records()
    build_compare_index()
    for a, b in COMPARE_PAIRS:
        build_compare_pair(a, b)
    for a, b, narr in RIVALRIES:
        build_rivalry(a, b, narr)
    build_international()
    build_thisday()
    build_about()
    build_privacy()
    write_static()
    n = write_sitemap()
    print(f"  pages written: {len(urls)}  ·  sitemap urls: {n}")
    print(f"  players: {len(PLAYERS)}  teams: {len(TEAMS)}  seasons: {len(SEASONS)}")
    print("Done.")


if __name__ == "__main__":
    main()
