"""Sangyan Kavach - hybrid scam-detection engine (stdlib only).
Layer 1: explainable rule engine (regex red flags, weighted).
Layer 2: SEBI registration check (fuzzy name match + reg-no pattern).
Layer 3 (optional): LLM explanation - plug in via explain_with_llm()."""
import json, re, os, difflib

BASE = os.path.dirname(os.path.abspath(__file__))
RULES = json.load(open(os.path.join(BASE, "data/patterns.json"), encoding="utf-8"))["rules"]
REGISTRY = json.load(open(os.path.join(BASE, "data/sebi_registered.json"), encoding="utf-8"))["entities"]

NEXT_STEPS = {
 "en": ["Do not pay or share OTP, PAN, Aadhaar or bank details.",
        "Verify the advisor on SEBI's official 'Intermediaries' search (sebi.gov.in).",
        "Report fraud: call 1930 or file at cybercrime.gov.in.",
        "Complain against a SEBI-registered entity: SEBI SCORES (scores.sebi.gov.in).",
        "Stop and tell a family member before acting on any 'tip'."],
 "hi": ["पैसे न भेजें और OTP, PAN, आधार या बैंक विवरण साझा न करें।",
        "SEBI की आधिकारिक वेबसाइट (sebi.gov.in) पर सलाहकार का रजिस्ट्रेशन जाँचें।",
        "धोखाधड़ी की रिपोर्ट करें: 1930 पर कॉल करें या cybercrime.gov.in पर शिकायत करें।",
        "SEBI-पंजीकृत संस्था की शिकायत: SEBI SCORES (scores.sebi.gov.in)।",
        "किसी भी 'टिप' पर काम करने से पहले परिवार के किसी सदस्य को बताएँ।"]}

REG_NO = re.compile(r"\bIN[ZHAMBPD]\d{9}\b", re.I)  # SEBI reg-no format e.g. INZ000031633, INH000000412

def rule_scan(text):
    hits = []
    for r in RULES:
        for pat in r["regex"]:
            m = re.search(pat, text, re.I)
            if m:
                hits.append({"id": r["id"], "weight": r["weight"], "label_en": r["label_en"],
                             "label_hi": r["label_hi"], "labels": {k[6:]: v for k, v in r.items() if k.startswith("label_")}, "evidence": m.group(0)})
                break
    return hits

def registry_check(text, claimed_name=""):
    out = {"reg_numbers": [], "matched_entity": None, "status": "not_provided"}
    nums = REG_NO.findall(text) or []
    found = [m.group(0).upper() for m in REG_NO.finditer(text)]
    out["reg_numbers"] = found
    by_no = {e["reg_no"]: e for e in REGISTRY}
    for n in found:
        if n in by_no:
            out["matched_entity"], out["status"] = by_no[n], "verified"
            return out
    if found:
        out["status"] = "number_not_found"   # claims a number that is not in registry -> suspicious
    name = (claimed_name or "").strip().lower()
    if name:
        names = {e["name"].lower(): e for e in REGISTRY}
        close = difflib.get_close_matches(name, names.keys(), n=1, cutoff=0.75)
        if close:
            out["matched_entity"], out["status"] = names[close[0]], "name_match_verify_number"
        elif out["status"] == "not_provided":
            out["status"] = "name_not_found"
    return out

def analyse(text, claimed_name="", lang="en"):
    text = text or ""
    hits = rule_scan(text)
    reg = registry_check(text, claimed_name)
    score = sum(h["weight"] for h in hits)
    if reg["status"] == "verified": score -= 25
    elif reg["status"] == "number_not_found": score += 25
    elif reg["status"] == "name_not_found": score += 15
    score = max(0, min(100, score))
    level = "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
    reasons = [h["labels"].get(lang, h["label_en"]) for h in hits]
    conf, why_unsure = confidence(len(hits), reg["status"], lang)
    return {"confidence": conf, "uncertainty": why_unsure, "score": score, "level": level, "reasons": reasons,
            "evidence": [h["evidence"] for h in hits], "registry": reg,
            "next_steps": NEXT_STEPS.get(lang, NEXT_STEPS["en"]) if level != "LOW" else NEXT_STEPS.get(lang, NEXT_STEPS["en"])[:2],
            "summary": explain(level, reasons, reg, lang),
            "disclaimer": DISCLAIMER.get(lang, DISCLAIMER["en"])}

def explain(level, reasons, reg, lang):
    """Template explanation. Replace/augment with explain_with_llm() when an API key is configured."""
    llm = explain_with_llm(level, reasons, reg, lang)
    if llm: return llm
    if lang in HEADS: return HEADS[lang][level]
    if lang == "hi":
        head = {"HIGH": "बहुत ज़्यादा जोखिम - यह संभवतः धोखाधड़ी है।",
                "MEDIUM": "मध्यम जोखिम - सावधान रहें और जाँच करें।",
                "LOW": "कम जोखिम - फिर भी पंजीकरण स्वयं जाँचें।"}[level]
    else:
        head = {"HIGH": "High risk - this looks like a likely scam.",
                "MEDIUM": "Medium risk - be careful and verify first.",
                "LOW": "Low risk - still verify registration yourself."}[level]
    return head

def explain_with_llm(level, reasons, reg, lang):
    """Optional: set ANTHROPIC_API_KEY and implement a call to generate a friendly explanation.
    Kept offline by default so the demo works without internet."""
    return None

# ---------- Scam Drill (resilience training) ----------
DRILLS = [
 {"id": 1, "msg": "🔥 VIP Telegram group! Join now, 5x returns in 7 days GUARANTEED. Only 10 seats left, pay ₹2,000 registration fee on UPI: tipster@upi",
  "is_scam": True, "why": "Guaranteed returns + urgency + advance fee + group funnel."},
 {"id": 2, "msg": "Your Zerodha account KYC is due. Please complete it only through the official Kite app or zerodha.com. Never share OTP with anyone.",
  "is_scam": False, "why": "No money demand, no pressure, directs to the official app and warns about OTP."},
 {"id": 3, "msg": "Insider operator call: buy XYZ penny stock tomorrow, upper circuit sure-shot. Download our institutional trading app (.apk).",
  "is_scam": True, "why": "Insider claim + sure-shot + APK install."},
 {"id": 4, "msg": "Reminder: SEBI-registered RA INH000000412 shares educational research. Returns are subject to market risk. Read the risk disclosure.",
  "is_scam": False, "why": "Gives a verifiable SEBI number and states market risk."},
]


def search_registry(q):
    """Case-insensitive lookup by name or registration number."""
    q = (q or "").strip().lower()
    if len(q) < 2:
        return []
    return [e for e in REGISTRY if q in e["name"].lower() or q in e["reg_no"].lower()]


def confidence(n_flags, reg_status, lang):
    """How sure are we? More independent signals or a verified number means more confidence.
    We never present the score as a fact; it is a heuristic estimate."""
    if reg_status == "verified" or n_flags >= 3:
        level = "Higher"
    elif n_flags == 0 and reg_status == "not_provided":
        level = "Low"
    else:
        level = "Medium"
    msg = {
        "en": "This is a heuristic estimate from known warning patterns, not proof. New scams may use wording we do not know. Always verify on sebi.gov.in.",
        "mr": "हा ज्ञात धोक्याच्या खुणांवर आधारित अंदाज आहे, पुरावा नाही. नवीन फसवणुकीचे शब्द वेगळे असू शकतात. नेहमी sebi.gov.in वर तपासा.", "ta": "இது அறியப்பட்ட எச்சரிக்கை வடிவங்களின் அடிப்படையிலான மதிப்பீடு, ஆதாரம் அல்ல. புதிய மோசடிகள் வேறு சொற்களைப் பயன்படுத்தலாம். எப்போதும் sebi.gov.in-இல் சரிபார்க்கவும்.", "hi": "यह जाने-पहचाने चेतावनी पैटर्न पर आधारित अनुमान है, सबूत नहीं। नए स्कैम की भाषा अलग हो सकती है। हमेशा sebi.gov.in पर जाँचें।"}[lang]
    return level, msg


# ---- extra languages: Marathi (mr) and Tamil (ta)
NEXT_STEPS["mr"] = ["पैसे पाठवू नका आणि OTP, PAN, आधार किंवा बँक तपशील देऊ नका.",
    "SEBI च्या अधिकृत वेबसाइटवर (sebi.gov.in) सल्लागाराची नोंदणी तपासा.",
    "फसवणुकीची तक्रार करा: 1930 वर कॉल करा किंवा cybercrime.gov.in वर तक्रार नोंदवा.",
    "SEBI-नोंदणीकृत संस्थेची तक्रार: SEBI SCORES (scores.sebi.gov.in).",
    "कोणत्याही 'टिप'वर कृती करण्यापूर्वी कुटुंबातील कोणाला तरी सांगा."]
NEXT_STEPS["ta"] = ["பணம் அனுப்ப வேண்டாம்; OTP, PAN, ஆதார் அல்லது வங்கி விவரங்களை பகிர வேண்டாம்.",
    "SEBI அதிகாரப்பூர்வ இணையதளத்தில் (sebi.gov.in) ஆலோசகரின் பதிவை சரிபார்க்கவும்.",
    "மோசடியை புகாரளிக்க: 1930-ஐ அழைக்கவும் அல்லது cybercrime.gov.in-இல் புகார் செய்யவும்.",
    "SEBI-பதிவு பெற்ற நிறுவனம் மீது புகார்: SEBI SCORES (scores.sebi.gov.in).",
    "எந்த 'டிப்'-பின் மீதும் செயல்படும் முன் குடும்பத்தினரிடம் சொல்லுங்கள்."]
DISCLAIMER = {"en": "Decision-support only, not legal/financial advice.",
    "hi": "यह केवल सहायक जानकारी है, कानूनी/वित्तीय सलाह नहीं।",
    "mr": "ही केवळ निर्णय-सहाय्यक माहिती आहे, आर्थिक/कायदेशीर सल्ला नाही.",
    "ta": "இது முடிவெடுக்க உதவும் தகவல் மட்டுமே; நிதி/சட்ட ஆலோசனை அல்ல."}
HEADS = {
 "hi": {"HIGH": "बहुत ज़्यादा जोखिम - यह संभवतः धोखाधड़ी है।", "MEDIUM": "मध्यम जोखिम - सावधान रहें और जाँच करें।", "LOW": "कम जोखिम - फिर भी पंजीकरण स्वयं जाँचें।"},
 "mr": {"HIGH": "खूप जास्त धोका - ही बहुधा फसवणूक आहे.", "MEDIUM": "मध्यम धोका - सावध रहा आणि आधी तपासा.", "LOW": "कमी धोका - तरीही नोंदणी स्वतः तपासा."},
 "ta": {"HIGH": "மிக அதிக ஆபத்து - இது மோசடியாக இருக்கலாம்.", "MEDIUM": "நடுத்தர ஆபத்து - கவனமாக இருந்து முதலில் சரிபார்க்கவும்.", "LOW": "குறைந்த ஆபத்து - இருப்பினும் பதிவை நீங்களே சரிபார்க்கவும்."}}
