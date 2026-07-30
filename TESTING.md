# Testing and evaluation

Two ways to evaluate this app. Neither needs a build step or any dependency install.

## 1. Built-in self-test (zero setup)

Open the app with `?selftest` appended to the URL:

- Live: https://rohitdvv.github.io/spark-homes-estimator/?selftest
- Local: open `index.html?selftest`

It runs the app's domain logic in isolation and shows a pass/fail panel. It writes nothing to storage. Checks include:

- Price list integrity (108 items, all well-formed) and that every room-group maps to real price items.
- Composite cell-key round-trip (`roomId|groupId|itemId`).
- Price resolution falls back to the CSV default.
- Line total = qty x unit price; grand total sums the line items.
- Contingency buffer math (buffered total = raw + %, contingency amount).
- Deal math (70% rule max offer = ARV x 0.7 - repairs).
- Snapshot diff detects an added item.
- localStorage read/write round-trip.

All checks currently pass (13/13). The self-test lives in `runSelfTest()` / `renderSelfTest()` in `index.html`, so a reviewer can read exactly what is asserted.

## 2. Lighthouse audit (objective quality bar)

Run Google Lighthouse against the app (Chrome required):

```bash
npx lighthouse "https://rohitdvv.github.io/spark-homes-estimator/" \
  --chrome-flags="--headless" \
  --only-categories=performance,accessibility,best-practices,seo \
  --view
```

Latest local run (v49):

| Category | Score |
|---|---|
| Best Practices | 100 |
| SEO | 100 |
| Accessibility | 92 |
| Performance | ~70 |

Notes:
- **Accessibility 92:** the one remaining flag is white text on the brand orange (`#d05000`), which measures 4.34:1 against a 4.5:1 target. It is kept intentionally because it is the client's brand color and it passes the large-text threshold.
- **Performance:** First/Largest Contentful Paint are the main levers. On the hosted site a chunk of the measured time is a GitHub Pages HTTP-to-HTTPS redirect (about 4 s in the throttled mobile run), which is hosting behavior, not app code. The app itself has Total Blocking Time 0 ms and Cumulative Layout Shift 0. The clearest app-side win would be shipping a smaller logo asset.
- Lighthouse 12+ removed the dedicated PWA category; installability and offline are provided by `manifest.json` and `sw.js` and can be checked in Chrome DevTools > Application.

## Manual smoke path

Open the app, tap **Load demo**, then walk Estimate (House X-Ray, groups) -> Photos -> Copilot -> Deal (type numbers, adjust the contingency slider) -> Export (client report, share QR, download ZIP). Toggle dark mode from the header. Everything works offline after the first load.
