import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine
def test_scam_high():
    r = engine.analyse("Join VIP Telegram group! Guaranteed 5x returns, only 10 seats, pay registration fee UPI: a@upi")
    assert r["level"] == "HIGH", r
def test_legit_low():
    r = engine.analyse("SEBI-registered RA INH000000412. Returns subject to market risk.")
    assert r["level"] == "LOW" and r["registry"]["status"] == "verified", r
def test_fake_reg_number():
    r = engine.analyse("SEBI approved advisor INH999999999. Sure-shot profit, act now")
    assert r["level"] == "HIGH" and r["registry"]["status"] == "number_not_found", r
def test_hindi():
    r = engine.analyse("पक्का मुनाफा! जल्दी करें, पेमेंट भेजें", lang="hi")
    assert r["level"] in ("MEDIUM", "HIGH") and r["reasons"], r
def test_marathi_tamil():
    a = engine.analyse("हमी परतावा! घाई करा, नोंदणी शुल्क भरा", lang="mr")
    b = engine.analyse("உத்தரவாத லாபம்! உடனே பதிவு கட்டணம் செலுத்துங்கள்", lang="ta")
    assert a["reasons"] and b["reasons"], (a, b)
    assert any("\u0b80" <= ch <= "\u0bff" for ch in b["reasons"][0])
if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"): f(); print("PASS", k)
