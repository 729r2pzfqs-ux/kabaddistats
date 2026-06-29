# कबड्डी आँकड़े — KabaddiStats.com

A comprehensive **Hindi-language kabaddi statistics** website. Static HTML on
GitHub Pages + Cloudflare. Saffron/orange themed, data-rich, **no emojis**
(text + inline SVG icons only). All UI in Devanagari (`lang="hi"`).

Covers **Pro Kabaddi League (PKL) Seasons 1–11** and **international kabaddi** —
player profiles (raid/tackle points, super 10s, high 5s), all 12 franchises,
every PKL season with champions and top performers, all-time records, player
head-to-head comparisons, team rivalries, "This Day in Kabaddi", plus World Cup
and Asian Games history.

## Data

Hand-compiled from public sources — official prokabaddi.com, Olympics.com,
Wikipedia and major kabaddi aggregators. Season finals, winners, venues, records
and award winners are cross-verified. Career aggregate totals are approximate
(official profiles publish only current-season figures).

## Architecture

```
scripts/
  templates.py   shared chrome (head/nav/footer), Hindi strings, saffron theme
  data.py        teams, seasons, players, records, international, glossary
  content.py     Hindi prose (auto intros + About / Privacy / glossary)
  generate.py    data -> static HTML at repo root + assets/sitemap/search
```

## Rebuild

```bash
python3 scripts/generate.py        # writes all HTML + assets to repo root
python3 -m http.server 8799        # preview locally
```

`generate.py` also produces the favicon pack, `og-image.png` (Pillow),
`sitemap.xml`, `robots.txt`, a client-side search index (`search-index.json` +
`search.js`), an IndexNow key file, `404.html` and `CNAME`.

## SEO

Every page ships a self-referential canonical, full OG + Twitter cards, Hindi
meta descriptions, JSON-LD (`WebSite` / `Person` / `SportsTeam` /
`BreadcrumbList`), plus sitemap, robots and the search index. A GA4 placeholder
(`G-XXXXXXXXXX`) is wired in `templates.py` — replace with the real measurement
ID when available.

## Deploy

GitHub Pages serves from repo root. `CNAME` → `kabaddistats.com`.

---

*KabaddiStats.com is an independent, non-commercial fan resource. Not affiliated
with the Pro Kabaddi League or any kabaddi board. Contact: info@kabaddistats.com*
