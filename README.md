# Spark Homes — Repair Cost Estimator

A mobile-first, offline-first **Progressive Web App** for Spark Homes acquisition
agents. Walk a property room by room, check off needed repairs, capture photos,
and export a complete cost breakdown — all on a phone, with no signal required.

Built for the Spark Homes developer contest. Single self-contained app, no build
step, no server.

---

## Run it locally

It's a static app — any static file server works.

```bash
# from the project root
python3 -m http.server 4173
# then open http://localhost:4173 on your phone or desktop
```

Or just open `index.html` directly. For full PWA install + offline behavior,
serve over `http://` or `https://` (service workers don't run from `file://`).

**Install to home screen:** open the hosted URL in Chrome (Android) or Safari
(iOS) → "Add to Home Screen". It launches standalone and works fully offline
after the first load.

---

## What's implemented (against the brief)

| Requirement | Status |
|---|---|
| Single self-contained HTML, no build tools / framework | ✅ `index.html` (vanilla JS) |
| Works offline (service worker + manifest) | ✅ `sw.js` + `manifest.json` |
| Installable PWA (Android + iOS), standalone | ✅ icons + manifest |
| Data persisted in `localStorage`, no backend | ✅ |
| Multiple projects, switch without data loss | ✅ |
| 75+ line items / 5 sections / collapsible groups | ✅ all **108** price-list items, **25** groups (the 19 required + 6 extra so no item is dropped) |
| "No Action Needed" per group | ✅ |
| Item shows name, unit, qty, unit cost, line total | ✅ |
| Price override — per project **and** global standard pricing | ✅ |
| Running total always visible | ✅ sticky header |
| Add / remove line items per-item | ✅ custom items + delete |
| Adjustable rooms (add/remove instances, per-type groups) | ✅ 7 room types, free add/remove |
| Progress bar, per-group completion across all rooms | ✅ |
| Photo capture (camera), thumbnails, individual remove | ✅ `capture="environment"` |
| Serial-number parsing from photos | ✅ on-device OCR (Tesseract.js) |
| Export ZIP (Excel breakdown + photos), auto-download | ✅ SheetJS + JSZip |
| Creative addition | ✅ **Deal Analyzer** + **AI Copilot** + **Live Capture** (see below) |

### Room types → repair groups

`Interior/General`, `Systems & Structure`, `Exterior` are house-wide singletons.
`Kitchen`, `Bathroom`, `Bedroom`, `Living/Common` can be added as multiple
instances (`Bathroom 1`, `Bathroom 2`, …), each carrying its own groups. Every
one of the 108 official price-list items is mapped into a group — the reference
implementation left ~25 items ungrouped; this version places all of them.

### Creative addition — Deal Analyzer

The brief says the most important number is the repair estimate, and the whole
point of getting it right is the deal math. The Deal Analyzer closes that loop:
enter ARV, purchase price, holding time/cost, and selling costs, and it pulls the
**live** repair total to project profit, return-on-cost, and a 70%-rule Max
Allowable Offer — with a GO / CAUTION / NO-GO verdict. The agent gets a buy/walk
answer while still standing in the house. It's also written into the exported
Excel as its own sheet.

### AI Copilot — an offline, client-side "multi-agent" layer

A second creative pillar. The Copilot tab runs a set of **specialist modules**
over the live estimate, entirely on-device (no network, no API key, no server —
so it never breaks the offline rule):

- **Inspection Coverage** (intake + validation): flags unreviewed groups and
  guards the big-ticket systems the brief says must never be missed (HVAC,
  foundation, rewire, plumbing).
- **Recommendations**: a rule engine for commonly-paired work — new flooring →
  trim-out, furnace → duct cleaning, rewire → drywall, tub tear-out → tile,
  plus whole-house close-out (haul-off, final cleaning). One tap adds the item.
- **Anomaly & Risk** (fraud-style outlier detection): catches unrealistic
  quantities, price overrides far from the list default, and conflicting scope
  (e.g. reglaze *and* tear-out on the same tub).
- **Assistant**: a chat that answers from live estimate facts (total, biggest
  cost driver, what's missing, profit math) plus **semantic retrieval** over an
  embedded repair-guidelines knowledge base. Retrieval runs a real on-device
  embedding model (Transformers.js + `all-MiniLM-L6-v2`, lazy-loaded and
  service-worker-cached, so it works offline after first load) — questions map
  to the right guidance by meaning, not keywords, with a similarity threshold so
  off-topic questions get an honest "I don't know" instead of a wrong canned
  answer. Falls back to whole-word keyword matching if the model can't load.
  Voice input via Web Speech API.

This is a deliberate, contest-legal interpretation of the requested multi-agent /
RAG / recommendation / chatbot features: the *architecture* (specialist agents
collaborating on one workflow) and the *value* are delivered without a backend.
The code is structured so a real LLM/vision layer could plug in when online,
while the offline core keeps working.

### Live Capture + Audio

The Photos tab offers **Live Capture**: open the device camera as a video feed
and grab frames as timestamped evidence (in addition to standard photo upload).
During capture you can record a **voice note** that transcribes to the frame's
caption (Web Speech API, graceful fallback where unsupported). Any captured
serial plate can be OCR'd on-device.

During Live Capture, an **AI scope detector** ("Detect" button) runs an
on-device zero-shot image classifier (Transformers.js + CLIP, lazy-loaded and
service-worker-cached) over the current frame. It scores the view against a set
of labels tied to line items (fixtures like fridge, toilet, water heater, plus
coarse defects like cracked tile, water-stained ceiling, peeling paint) and
surfaces ranked suggestions. Each is a one-tap **Add** that drops the item into
the right room and group. Suggestions are advisory and require the agent to
confirm; they never auto-add. The detection path (`suggestScope`) is structured
so an online vision model can plug in for higher accuracy when there is signal,
falling back to the offline classifier otherwise.

### Field-workflow innovations

Four features built around how the job actually happens (hands full, many
houses, work shared and presented):

- **Hands-free Voice Walkthrough** (Estimate tab): the agent narrates repairs
  ("kitchen, new cabinets and a range; master bath, cracked tub"). The app
  transcribes (Web Speech API), splits the speech into phrases, semantically
  maps each to a line item (reusing the on-device embedding model), infers the
  room, extracts a quantity, and adds it live with an undo feed. Saying just a
  room name only sets the room context.
- **Property comparison** (home screen): rank every saved estimate side by side
  by repairs, projected profit, return, and GO/CAUTION/NO-GO, to decide which
  property to pursue. Turns the app from a calculator into a decision tool.
- **Backendless handoff** (Export tab): share a full estimate to another phone
  by compressing it into the URL hash and showing a QR code / copy link. Opening
  that link on any device imports it. No server (photos are not included in the
  link).
- **Branded client report** (Export tab): one tap opens a print-ready, branded
  report (verdict, cost-by-section, full scope of work, photos) to save as PDF
  or print, beyond the raw Excel.

---

## How pricing works

`Pricing List.csv` is the single source of truth. It's embedded verbatim in
`index.html` as `PRICE_LIST` (so the app needs no fetch and works offline).
Effective price for any item resolves as:

```
per-project override  →  global standard-price override  →  CSV default
```

Both override paths are editable from the UI (tap any price). Global edits are
managed from the home screen ("Manage standard pricing").

---

## Tech / libraries

- **Vanilla JS + HTML + CSS** — no framework, no build.
- **Tailwind CSS** (CDN) — utility styling + custom transitions.
- **SheetJS / xlsx** (CDN) — Excel generation.
- **JSZip** (CDN) — bundles xlsx + photos into one ZIP.
- **Tesseract.js** (CDN, lazy-loaded on first scan) — on-device serial-number OCR.
- **Transformers.js** (CDN, lazy-loaded on first Copilot question) — on-device
  sentence embeddings (`all-MiniLM-L6-v2`) for the semantic assistant, and
  zero-shot image classification (`clip-vit-base-patch32`) for the Live Capture
  AI scope detector.

All CDN libraries are runtime-cached by the service worker, so the second launch
works with no network.

## Files

```
index.html        the entire app
sw.js             service worker (offline cache)
manifest.json     PWA manifest
icon-*.png        PWA / home-screen icons
spark-logo.png    brand logo
```

> Confidential contest materials (the brief, the reference app, the raw price
> list) are git-ignored and not published.
