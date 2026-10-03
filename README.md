# Sangyan Kavach

A scam check for first-time investors in India. Paste a tip or message you received, and the tool tells you
how risky it looks, why, whether the advisor is in the SEBI registry, and where to report it. Works in English, Hindi, Marathi and Tamil.

Built for the SANGYAN hackathon (SNTC IIT BHU, with SEBI and NSDL). Track A: Digital Fraud & Scam Resilience.
Reporting steps and the regional-language interface support the grievance and Bharat-reach goals.

## Screenshots

| Risky message | Hindi view | Genuine message |
|---|---|---|
| ![](output/screenshots/01_check_high.png) | ![](output/screenshots/02_check_hindi.png) | ![](output/screenshots/03_check_low.png) |

| Registry search | Scam drill |
|---|---|
| ![](output/screenshots/04_registry.png) | ![](output/screenshots/05_drill_question.png) |

| Marathi | Tamil |
|---|---|
| ![](output/screenshots/02b_check_marathi.png) | ![](output/screenshots/02c_check_tamil.png) |

## Output folder

Everything the code produces is saved in `output/`:

- `output/screenshots/` - screenshots of the running app (English, Hindi, Marathi, Tamil, registry, drill)
- `output/demo_video.mp4` - screen recording of the full demo
- `output/test_results.txt` - result of the automated tests
- `output/sample_run.txt` - readable results for 7 example messages
- `output/sample_api_outputs.json` - the same results as raw JSON from the engine
- `output/sample_registry_search.json` - example registry search
Regenerate with `python tools/generate_outputs.py`.

## Features

- Message check with 0-100 risk score, highlighted phrases, reasons and a confidence note
- SEBI registry lookup by name or registration number (sample data)
- Four languages: English, Hindi, Marathi, Tamil (interface, reasons, next steps)
- Voice input and read-aloud (browser speech APIs, Chrome or Edge)
- Screenshot upload: text is read in the browser with Tesseract.js (needs internet; the image is not sent to our server)
- Scam drill with explained answers
- Guardrails: no stock tips, no monetisation, nothing stored, no SMS/OTP access

## Run it

Needs Python 3.8 or newer. No packages to install.

    python server.py        (Windows: double-click run.bat, or try: py server.py)
    # a browser opens at http://localhost:8000

Important: do not double-click `static/index.html`. The page needs the server running to work.
If port 8000 is busy, the server picks the next free port and prints the address.

Run the tests:

    python tests/test_engine.py

## Example output (`POST /api/analyse`)

    {
  "score": 100,
  "level": "HIGH",
  "reasons": [
    "Promises guaranteed / assured returns",
    "Unrealistic return numbers (double/triple money, daily %)",
    "Creates false urgency / pressure",
    "Claims insider / operator tips",
    "Asks for money / advance fee / UPI to a personal account",
    "Claims to be 'SEBI approved' without proof"
  ],
  "evidence": [
    "guaranteed",
    "5x return",
    "Only 10 seats",
    "insider",
    "registration fee",
    "SEBI approved"
  ],
  "summary": "High risk - this looks like a likely scam."
}

## How it works

1. `engine.py` scans the text against weighted red-flag patterns from `data/patterns.json`
   (guaranteed returns, fake urgency, advance fee, insider claims, unofficial apps, group funnels).
2. It looks for SEBI registration numbers (format `INZ/INH/INA` plus 9 digits) and compares them, and the
   advisor name, with `data/sebi_registered.json`. A number that is not in the registry raises the score.
3. The score (0-100) maps to Low / Medium / High. Reasons come straight from the rules that fired,
   so every verdict can be explained.
4. `server.py` exposes `/api/analyse`, `/api/registry` and `/api/drills`; `static/index.html` is the interface.

## Honest limits

- The registry file is a small sample, not live SEBI data.
- Rules are heuristics. They catch common patterns but can miss new ones or flag odd genuine messages.
- Not financial or legal advice.
- The scam drill messages are English only. Screenshot OCR depends on an online library and has not been tested offline.

## Next steps

Voice-note file input, a WhatsApp/Telegram bot, more Indian languages (Bengali, Telugu, Gujarati),
translated scam-drill messages, live SEBI registry sync, and user-reported scams feeding new rules.
