"""Regenerates the files in output/ from the real code.   Run:  python tools/generate_outputs.py"""
import sys, os, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine

OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

CASES = [
    ("Scam: guaranteed returns + VIP group + fee", "en",
     "Join our VIP Telegram group. SEBI approved insider tips, guaranteed 5x returns in 7 days. Only 10 seats left, pay Rs 2000 registration fee on UPI: tips@upi",
     "Rahul Capital Advisors"),
    ("Scam: fake registration number", "en",
     "SEBI approved advisor INH999999999. Sure-shot profit, act now", ""),
    ("Genuine: valid registration number", "en",
     "SEBI-registered RA INH000000412. Research is educational. Returns are subject to market risk.",
     "Motilal Oswal Financial Services"),
    ("Neutral message, nothing to flag", "en", "Hello, are we meeting for lunch tomorrow?", ""),
    ("Scam in Hindi", "hi", "पक्का मुनाफा! जल्दी करें, पेमेंट भेजें", ""),
    ("Scam in Marathi", "mr", "हमी परतावा! घाई करा, नोंदणी शुल्क भरा", ""),
    ("Scam in Tamil", "ta", "உத்தரவாத லாபம்! உடனே பதிவு கட்டணம் செலுத்துங்கள்", ""),
]

results, lines = [], []
for title, lang, text, name in CASES:
    r = engine.analyse(text, name, lang)
    results.append({"case": title, "language": lang, "input": {"text": text, "advisor_name": name}, "output": r})
    lines += ["=" * 70, title + "  [" + lang + "]", "INPUT : " + text,
              "RESULT: %s  score %d/100  confidence %s" % (r["level"], r["score"], r["confidence"]),
              "SUMMARY: " + r["summary"]]
    lines += ["  - " + x for x in r["reasons"]] or ["  (no warning signs found)"]
    lines.append("REGISTRY: " + r["registry"]["status"] + (" -> " + r["registry"]["matched_entity"]["name"] if r["registry"]["matched_entity"] else ""))
    lines.append("")

json.dump(results, open(os.path.join(OUT, "sample_api_outputs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(os.path.join(OUT, "sample_run.txt"), "w", encoding="utf-8").write("\n".join(lines))
json.dump({"query": "zerodha", "results": engine.search_registry("zerodha")},
          open(os.path.join(OUT, "sample_registry_search.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
t = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "test_engine.py")], capture_output=True, text=True)
open(os.path.join(OUT, "test_results.txt"), "w").write("$ python tests/test_engine.py\n" + t.stdout + t.stderr + "\nexit code: %d\n" % t.returncode)
print("Outputs written to", OUT)
