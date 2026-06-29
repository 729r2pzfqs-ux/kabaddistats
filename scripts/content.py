#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hindi prose: auto-generated intros + static About / Privacy bodies."""

from data import TEAMS, SEASONS, PLAYER_BY_ID
from templates import ROLE, CONTACT

ROLE_HI = {"raider": "रेडर", "defender": "डिफेंडर", "allrounder": "ऑल-राउंडर"}


def prose(paras, heading=None):
    if isinstance(paras, str):
        paras = [paras]
    h = (f'<h2 class="hi font-heading font-bold text-lg text-kb-ink mb-3 '
         f'flex items-center gap-2"><span class="w-1.5 h-5 rounded mat-stripe '
         f'inline-block"></span>{heading}</h2>') if heading else ""
    body = "".join(f'<p class="mb-3 last:mb-0">{p}</p>' for p in paras)
    return (f'<section class="bg-kb-card border border-kb-border rounded-2xl '
            f'p-5 sm:p-6 mb-6">{h}<div class="hi text-[15px] leading-relaxed '
            f'text-kb-text">{body}</div></section>')


def _team_names(slugs, link=False, depth=0):
    out = []
    for s in slugs:
        t = TEAMS.get(s)
        if not t:
            continue
        out.append(t["name_hi"])
    return out


def player_intro_html(p, depth):
    """Rich Hindi intro card for a player profile."""
    role_hi = ROLE_HI.get(p["role"], "खिलाड़ी")
    teams = " · ".join(_team_names(p["teams"]))
    lead = (f"<b>{p['name_hi']}</b> ({p['name']}) प्रो कबड्डी लीग के एक प्रमुख {role_hi} हैं"
            f"{'' if p['nat'] == 'भारत' else f' और {p['nat']} का प्रतिनिधित्व करते हैं'}। "
            f"उन्होंने {teams} जैसी टीमों के लिए खेला है।")
    stats_bits = []
    if p["raid"]:
        stats_bits.append(f"लगभग {p['raid']:,} रेड अंक")
    if p["tackle"]:
        stats_bits.append(f"{p['tackle']:,} टैकल अंक")
    statline = ""
    if stats_bits:
        statline = (f"पीकेएल करियर में उन्होंने कुल {' और '.join(stats_bits)} "
                    f"({p['total']:,} कुल अंक) बनाए हैं।")
    paras = [lead + " " + statline, p["note"]]
    return prose([x for x in paras if x.strip()],
                 heading=f"{p['name_hi']} के बारे में")


def team_intro_html(t, depth):
    titles = t["titles"]
    if titles:
        tline = (f"{t['name_hi']} ने पीकेएल में {len(titles)} ख़िताब जीते हैं "
                 f"(सीज़न {', '.join(str(s) for s in titles)})।")
    else:
        tline = f"{t['name_hi']} अब तक पीकेएल ख़िताब जीतने में सफल नहीं रही है।"
        if t["runner_up"]:
            tline += f" हालाँकि टीम सीज़न {', '.join(str(s) for s in t['runner_up'])} में उपविजेता रही।"
    paras = [
        f"<b>{t['name_hi']}</b> ({t['name']}) {t['city']}, {t['state']} की प्रतिनिधि "
        f"प्रो कबड्डी लीग फ़्रेंचाइज़ी है, जिसकी शुरुआत {t['est']} में हुई। {t['tag']}",
        tline + f" टीम का स्वामित्व {t['owner']} के पास है।",
    ]
    return prose(paras, heading=f"{t['name_hi']} के बारे में")


def season_intro_html(s):
    champ = TEAMS[s["champion"]]["name_hi"]
    ru = TEAMS[s["runner_up"]]["name_hi"]
    paras = [
        f"प्रो कबड्डी लीग का <b>सीज़न {s['num']}</b> ({s['year']}) {champ} ने जीता, "
        f"जिसने फ़ाइनल में {ru} को {s['score']} से हराया। यह मुक़ाबला "
        f"{s['venue']} में खेला गया।",
        f"इस सीज़न में {s['raider'][0]} सर्वाधिक रेड अंक ({s['raider'][2]}) के साथ शीर्ष रेडर रहे, "
        f"जबकि {s['defender'][0]} ने सर्वाधिक टैकल अंक ({s['defender'][2]}) बटोरे। "
        f"सीज़न के सबसे मूल्यवान खिलाड़ी (एमवीपी) {s['mvp'][0]} रहे।",
    ]
    return prose(paras, heading=f"सीज़न {s['num']} — एक नज़र")


def about_body(section_title):
    paras = [
        "<b>कबड्डी आँकड़े</b> (KabaddiStats.com) हिंदी भाषी कबड्डी प्रेमियों के लिए "
        "बनाया गया एक मुफ़्त मंच है, जहाँ प्रो कबड्डी लीग (पीकेएल) और अंतरराष्ट्रीय "
        "कबड्डी के विस्तृत आँकड़े सरल हिंदी में उपलब्ध हैं। हमारा उद्देश्य कबड्डी के "
        "समृद्ध आँकड़ों को उन करोड़ों प्रशंसकों तक पहुँचाना है जो हिंदी में पढ़ना पसंद करते हैं।",
        "इस वेबसाइट पर आपको शीर्ष खिलाड़ियों की प्रोफ़ाइल, रेड और टैकल अंक, सुपर 10 व "
        "हाई 5, सभी 12 टीमों का इतिहास, पीकेएल के हर सीज़न (सीज़न 1 से 11) का ब्योरा, "
        "सर्वकालिक रिकॉर्ड और खिलाड़ियों की हेड-टू-हेड तुलना मिलेगी — सब कुछ एक ही जगह।",
        "हमारे आँकड़े प्रो कबड्डी लीग, ओलंपिक्स डॉट कॉम और अन्य सार्वजनिक रूप से उपलब्ध "
        "स्रोतों पर आधारित हैं। करियर के कुल आँकड़े अनुमानित हैं, क्योंकि आधिकारिक प्रोफ़ाइलें "
        "अक्सर केवल चालू सीज़न के आँकड़े दिखाती हैं। हम सटीकता के लिए प्रतिबद्ध हैं, फिर भी "
        "किसी त्रुटि की संभावना से इनकार नहीं किया जा सकता।",
        "<b>कबड्डी आँकड़े</b> किसी भी कबड्डी बोर्ड, लीग या आधिकारिक संस्था से संबद्ध नहीं "
        "है। यह कबड्डी प्रेमियों द्वारा, कबड्डी प्रेमियों के लिए बनाया गया एक स्वतंत्र, "
        "ग़ैर-व्यावसायिक सूचना संसाधन है। किसी भी सुझाव या प्रतिक्रिया के लिए आप हमसे "
        f"<a href='mailto:{CONTACT}' class='text-kb-orange hover:underline'>{CONTACT}</a> "
        "पर संपर्क कर सकते हैं।",
    ]
    return (section_title("हमारे बारे में", "हिंदी में कबड्डी आँकड़ों का घर") +
            f'<div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6 '
            f'hi text-[15px] leading-relaxed text-kb-text">' +
            "".join(f'<p class="mb-3 last:mb-0">{p}</p>' for p in paras) + "</div>")


def privacy_body(section_title):
    blocks = [
        ("परिचय",
         "यह गोपनीयता नीति बताती है कि <b>कबड्डी आँकड़े</b> (KabaddiStats.com) आपकी "
         "जानकारी को कैसे एकत्र, उपयोग और सुरक्षित करता है। हमारी वेबसाइट का उपयोग "
         "करके आप इस नीति में वर्णित प्रथाओं से सहमति प्रदान करते हैं।"),
        ("कौन-सी जानकारी एकत्र की जाती है",
         "हमारी वेबसाइट मुख्य रूप से एक स्थिर (स्टैटिक) सूचना वेबसाइट है। हम आपसे नाम, "
         "ईमेल या फ़ोन नंबर जैसी व्यक्तिगत जानकारी सीधे नहीं माँगते। आपके ब्राउज़र द्वारा "
         "स्वचालित रूप से भेजी जाने वाली सामान्य जानकारी केवल वेबसाइट के बेहतर संचालन "
         "के लिए उपयोग हो सकती है।"),
        ("कुकीज़ और एनालिटिक्स",
         "वेबसाइट के उपयोग को समझने और उसे बेहतर बनाने के लिए हम तृतीय-पक्ष एनालिटिक्स "
         "सेवाओं (जैसे Google Analytics) का उपयोग कर सकते हैं। ये सेवाएँ कुकीज़ का उपयोग "
         "कर सकती हैं। आप अपने ब्राउज़र की सेटिंग्स से कुकीज़ को कभी भी अक्षम कर सकते हैं।"),
        ("विज्ञापन",
         "भविष्य में वेबसाइट पर तृतीय-पक्ष विज्ञापन (जैसे Google AdSense) दिखाए जा सकते "
         "हैं। ये सेवाएँ प्रासंगिक विज्ञापन दिखाने के लिए कुकीज़ का उपयोग कर सकती हैं। इनकी "
         "अपनी गोपनीयता नीतियाँ होती हैं, जिन पर हमारा नियंत्रण नहीं है।"),
        ("बाहरी लिंक",
         "हमारी वेबसाइट पर अन्य वेबसाइटों के लिंक हो सकते हैं। उन बाहरी वेबसाइटों की "
         "गोपनीयता प्रथाओं के लिए हम ज़िम्मेदार नहीं हैं और आपको उनकी नीतियाँ अलग से "
         "पढ़ने की सलाह दी जाती है।"),
        ("बच्चों की गोपनीयता",
         "हमारी वेबसाइट सभी आयु वर्ग के कबड्डी प्रेमियों के लिए है और हम जानबूझकर बच्चों "
         "से कोई व्यक्तिगत जानकारी एकत्र नहीं करते।"),
        ("नीति में बदलाव",
         "हम समय-समय पर इस गोपनीयता नीति को अद्यतन कर सकते हैं। कोई भी बदलाव इसी पेज "
         "पर प्रकाशित किया जाएगा, इसलिए कृपया समय-समय पर इसे देखते रहें।"),
        ("संपर्क करें",
         "इस गोपनीयता नीति के बारे में किसी भी प्रश्न के लिए आप हमसे "
         f"<a href='mailto:{CONTACT}' class='text-kb-orange hover:underline'>{CONTACT}</a> "
         "पर संपर्क कर सकते हैं।"),
    ]
    inner = ""
    for h, txt in blocks:
        inner += (f'<h2 class="hi font-heading font-bold text-lg text-kb-ink mb-2 mt-5 '
                  f'first:mt-0 flex items-center gap-2"><span class="w-1.5 h-5 rounded '
                  f'mat-stripe inline-block"></span>{h}</h2>'
                  f'<p class="hi text-[15px] leading-relaxed text-kb-text mb-2">{txt}</p>')
    return (section_title("गोपनीयता नीति", "आपकी निजता के प्रति हमारी प्रतिबद्धता") +
            f'<div class="bg-kb-card border border-kb-border rounded-2xl p-5 sm:p-6">'
            f'{inner}</div>')
