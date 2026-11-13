# India Explorer — Full Architecture Audit

**Audit date:** 12 November 2026
**Scope:** read-only review of the repository, the runtime app, the live production site, the SQLite data, and the asset pipeline.
**Status at audit time:** no files modified. Probe scripts were kept outside the repo in `%TEMP%\opencode\`.
**Evidence base:** source files, FastAPI `TestClient` runs, live `https://traveling-ketch.vercel.app` probes, database queries, asset scans.

> This document records the project as it was at audit time. Fixes applied after approval are tracked in the [Remediation log](#9-remediation-log).

---

## 1. Executive summary

The project is a **FastAPI monolith + SQLite + vanilla-JS hybrid** that works, but it has grown two parallel rendering systems that disagree with each other. The single biggest theme: **the server-rendered app and the static/client app are fighting, and the static one wins on the most important page.**

Five issues were actively broken in production at audit time:

| # | Issue | Impact |
|---|---|---|
| 1 | `/saved` never hydrates | Favorites + itinerary + share are **dead** for every user |
| 2 | Static `public/index.html` shadows the FastAPI home | Homepage shows **stale counts (808 / 484)** and has **no canonical, no JSON-LD, no OG image** |
| 3 | Festival `kind` vs `date_type` mismatch | All **95** festival cards say "Dates vary annually" |
| 4 | Share text hardcodes `india-explorer-hazel.vercel.app` | Shared itineraries point at a **different/wrong domain** |
| 5 | `/api/places` returns everything (1,028 KB) and `enrich_places` uses a 1,000-item `IN (...)` | **Hard failure** once places exceed 999 |

Everything else is quality, scale, SEO, and hygiene work — valuable, but not on fire.

**Scale snapshot:** 36 regions (28 states + 8 UTs), 788 districts, 1516 places, 154 festivals, 19 circuits, 20 heritage sites. **0 verified places**, **16 confirmed festival dates**. 325 of 788 districts have a place; **9 states have none** (Chhattisgarh, Gujarat, Jharkhand, MP, Manipur, Punjab, Telangana, Uttarakhand, West Bengal).

---

## 2. Architecture & data flow

```
data/india-states-districts.json        (36 regions, 788 districts)
data/states/*.json                      (6 state manifests)
data/*-places.json                      (6 place documents)
            │
            ▼
     data_pipeline.py   normalize → validate → import_report
            │
            ▼
        seed.py         (hardcoded editorial data + JSON imports)
            │
            ▼
   schema.sql → SQLite  (data/explorer.sqlite3 locally,
                         /tmp/india-explorer-<hash>.sqlite3 on Vercel)
            │
            ▼
        app.py  (977 lines, one create_app())
        ├── 12 JSON APIs      /api/states, /api/places, /api/festivals, …
        ├── 14 HTML routes    /, /explore, /state/{slug}, /place/{slug}, …
        └── /sitemap.xml, /robots.txt
            │
            ├──────────────► JSON consumers: public/app.js (hash router)
            │
            └──────────────► server-rendered HTML (f-string templates,
                              inline JSON-LD, no Jinja)

Production (Vercel):
  public/*  ──► CDN static, wins at "/"  ◄── the shadowing bug
  everything else ──► api/index.py (9 lines) ──► FastAPI app
```

### Two rendering systems, one page
- `app.py` renders full HTML for `/explore`, `/state/*`, `/district/*`, `/place/*`, `/festivals`, `/saved`, `/area`, `/about`.
- `public/app.js` (850 lines) can **also** render every one of those pages client-side.
- `public/index.html` is a third, hand-written homepage.
- The result: three places to change a card, a filter, or a count — and they had already drifted (808/484 vs 802/726; "Dates vary annually"; wrong share domain).

### Routing is implicit
`vercel.json` contained only `buildCommand` and cache headers — **no `rewrites`**. `/` was served from `public/index.html` (5,988 bytes, `data-server-rendered="false"`), while `/explore` reached FastAPI (1,033,555 bytes, `data-server-rendered="true"`). This behavior was undocumented and fragile.

---

## 3. Feature & data inventory

### Features that exist
Home (hero slideshow, spotlight search, stats, featured states, recents), Explore (search + category/state/month/UNESCO filters + Leaflet map), Area (states/UTs directory), State, District, Place (gallery, map, nearby, directions, best months, tags), Circuits (19 itineraries), Circuit detail (map + stops), Festivals (month tabs), Month pages, Saved (favorites, itinerary builder, distance, WhatsApp share), About, sitemap, robots.

### APIs (12)
`/api/states`, `/api/union-territories`, `/api/states/{slug}`, `/api/districts`, `/api/districts/{slug}`, `/api/places`, `/api/places/{slug}`, `/api/festivals`, `/api/circuits`, `/api/circuits/{slug}`, `/healthz`, `/api/editorial-status`.

### Data quality
| Metric | Value |
|---|---|
| Places | 1516 |
| Verified | **0** (all 726 `needs_review`) |
| With entry fee / address | 646 / 646 (80 missing each → 160 warnings) |
| Districts with ≥1 place | 325 / 788 |
| States with 0 places | **13** (Assam, Bihar, Chhattisgarh, Gujarat, Haryana, Jharkhand, MP, Maharashtra, Manipur, Punjab, Telangana, Uttarakhand, West Bengal) |
| Festival occurrences | 0 (only recurring month windows) |
| Attribution records | 780 for 726 places (54 orphans) |
| Canonical validation | 0 errors / 0 warnings |
| DB validation | 0 errors / 160 warnings |

### Positives worth keeping
- Every one of the 726 places has an image, and **all referenced images exist on disk** (0 broken refs).
- Attribution metadata is present for every place.
- Data normalization/validation pipeline is real and CI-enforced.
- Sitemap is comprehensive (1,602 URLs) and robots.txt is correct.
- HSTS is on, static assets get `max-age=31536000, immutable`.

---

## 4. Findings by category

### 4.1 Duplicate / unnecessary code

| Finding | Where | Notes |
|---|---|---|
| Full page rendering duplicated | `app.py` HTML routes vs `public/app.js` `route()` | Cards, filters, festivals, hero, tips exist twice |
| Homepage exists twice | `public/index.html` vs `app.py:533` `home()` | Static version wins in prod |
| Hardcoded hero slides | `app.py:539-…` and `app.js` | 12 slides duplicated |
| Category tips / labels | `app.py` + `app.js` `categories` | Must be edited twice |
| ~50 one-off root scripts | `check_*.py`, `fix_*.py`, `update_*.py`, `add_*.py` | 54 root `.py` files, 0.4 MB, no folder |
| Non-test in test slot | `test_fixes.py` | Prints DB rows; pytest will try to collect it |
| Throwaway utility | `search.py` | 6-line grep of `app.py` |
| Unused symbol | `APP_VERSION` (`app.py:12`) | Never referenced |
| Unused import | `load_state_dataset` (`seed.py:11`) | Only `load_all_state_datasets` used |

### 4.2 Bugs (confirmed)

**CRITICAL — `/saved` is non-functional in production.**
`public/app.js:923`:
```js
if (document.body.dataset.serverRendered !== 'true') { … route(); }
```
`/saved` is server-rendered with `data-server-rendered="true"`, so `route()` never ran → `savedPage()` never executed → `#saved-itinerary-builder` and `#saved-cards-container` stayed empty. Favorites, itinerary generation, distances, and sharing never appeared.

**CRITICAL — Homepage is stale and SEO-poor.**
Live `/` was `public/index.html` (5,988 B) with `808` districts and `484` places. Real data: 802 / 726. It had no `<link rel="canonical">`, no JSON-LD, no `og:image`, no `og:url`. The SEO-rich FastAPI home (39 KB, with schema) was unreachable.

**CRITICAL — All festivals show the wrong date note.**
`app.py:500-502` reads `item.get('kind')`, but `schema.sql`/`seed.py` store **`date_type`**. Live `/festivals`: `"Dates vary annually"` × 95, `"Lunar calendar shifts annually"` × 0, `"Fixed season"` × 0.

**HIGH — Share link points at the wrong deployment.**
`public/app.js:396`: `https://india-explorer-hazel.vercel.app/saved`. Production is `traveling-ketch.vercel.app`.

**HIGH — `/api/places` will crash past 999 places.**
`query_places(limit=1000)` → `enrich_places()` builds three `WHERE … IN (?,?,…)` clauses with one placeholder per place (`app.py:154-176`). At 1,000 places that is 1,000 bound variables; SQLite's classic limit is 999. At audit time there were 726, so it was a time bomb, and the endpoint already shipped 1,028 KB.

**MEDIUM — `/month/{n}` duplicates `/festivals?month=n`.**
Both returned byte-identical 14,182 B pages; both were in the sitemap. Duplicate content with no canonical separation.

**MEDIUM — HTML 404s return JSON.**
Unknown page → `404 application/json` with `{"detail":"Not Found"}`. Bad for users and crawlers.

### 4.3 Performance

| Endpoint / page | Size | Time | Problem |
|---|---|---|---|
| `/api/places` | **1,028 KB** | 115 ms | No pagination; fetched repeatedly by home/saved/spotlight |
| `/explore` | **1,009 KB** local / **1,033 KB** live | 76 ms | 726 cards in one HTML doc |
| `/api/festivals` | 31 KB | **255 ms** | N+1: 3 queries × 69 festivals |
| `/api/states` | 9 KB | 119 ms cold | Cold-start dominated |
| `/sitemap.xml` | 124 KB | 13 ms | No `lastmod` |

Other:
- **Leaflet loaded from unpkg on every page**, even pages with no map (render-blocking third party).
- **Hero slideshow loads 12 full-size images eagerly** (several 300 KB–1 MB).
- `/api/circuits` also does N+1 (one stops query per circuit).
- All API responses used `Cache-Control: public, max-age=0, must-revalidate` — no CDN reuse.

### 4.4 SEO & image optimization

**SEO**
- Static home: no canonical / JSON-LD / OG image / OG URL.
- Sitemap includes `/saved` (a private, client-only page) and 12 duplicate `/month/*` URLs; **no `lastmod`**.
- OG fallback is an SVG (`/assets/state-cover.svg`) — unsupported by most social scrapers.
- Server home `<title>` duplicated the brand (`… · India Explorer`).
- No `noindex` anywhere in the codebase.
- `/saved` is indexable but always empty → thin content.

**Images**
- **214.1 MB** total assets: 823 JPG (211.8 MB), 1 PNG (1.4 MB), 28 SVG.
- **73 files > 500 KB**; largest 1,454 KB (`rangin-mahal-bidar.png`), several ~1 MB.
- **Zero** `srcset`, zero `width`/`height` attributes, zero WebP/AVIF.
- Only 5 `loading="lazy"` in `app.py`, 6 in `app.js`; hero images are eager.
- ~60 unused place images + 54 orphan attribution entries.

### 4.5 Data accuracy & missing destinations

- 14 states with **zero** places; 656 of 802 districts empty. Coverage is essentially Karnataka (171), Meghalaya (131), Odisha (111) plus pilot data.
- **No place is verified** — every card is `needs_review`.
- No real festival dates: 0 occurrences, only month windows, so "festival planning" is approximate.
- 80 places missing `entry_fee`, 80 missing `address`.
- `README.md` claims 808 districts / 485 places / 57 festivals vs actual 802 / 726 / 69.
- `trail_logistics` covers only 9 of 19 circuits.
- No duplicate place names or duplicate images (good).

### 4.6 Security & deployment

| Check | Result at audit time |
|---|---|
| HSTS | OK — `max-age=63072000; includeSubDomains; preload` |
| CSP | Missing |
| `X-Content-Type-Options` | Missing |
| `X-Frame-Options` | Missing |
| `Referrer-Policy` | Missing |
| `Permissions-Policy` | Missing |
| `/docs`, `/redoc`, `/openapi.json` | **200 in production** |
| Rate limiting | None |
| Secrets in repo | None tracked (`.env.local` gitignored, OIDC token only) |
| Inline handlers | `onerror`/`onclick` in templates → blocks strict CSP |
| Unescaped interpolation | Map popups + itinerary HTML in `app.js` |

Deployment notes:
- `vercel.json` had no `rewrites`, no security headers, and only asset cache rules.
- `.vercelignore` excludes tests/DB but **not** root scripts or data JSON — they ship to the function bundle.
- Repo pack is ~190 MB; `public/` (214 MB) is fully tracked; `.kilo/` is 322 MB (ignored).
- Branch `master`, remote `Dolagobindamohanty/india-explorer`, project `traveling-ketch`.

### 4.7 Scalability & maintainability

- **`app.py` is a 977-line monolith** with 26 routes, templates, DB access, sitemap, and SEO all in one closure.
- **`seed.py` is 1,205 lines** of hardcoded regions/places/festivals/circuits + image maps.
- **No migration tool** — schema changes are ad-hoc `ALTER TABLE` + a version hash in the `/tmp` filename.
- **No linter, formatter, or type checker**; no `ruff`/`mypy`/`black` config.
- **Tests are brittle**: `tests/test_app.py` (632 lines) hardcodes 726 places, 802 districts, 28 states — every data addition breaks CI.
- **~50 one-off scripts** at root with no documentation.
- The `IN (...)` pattern and per-item loops mean the app degrades non-linearly as data grows toward full India coverage (~4,000–6,000 places).

---

## 5. Prioritized roadmap

### CRITICAL — fix before anything else (1–2 days total)

| # | Action | Files | Effort |
|---|---|---|---|
| C1 | Fix `/saved` hydration: only skip `route()` for pages that are fully server-rendered, or explicitly hydrate saved/favorites on `/saved` | `public/app.js:923`, `app.py:915` | S |
| C2 | Stop static home shadowing: remove/rename `public/index.html` or add a Vercel rewrite `/` → function; make the homepage single-source | `public/index.html`, `vercel.json` | S–M |
| C3 | Fix festival date note: `kind` → `date_type` | `app.py:500-502` | S |
| C4 | Fix share domain to `SITE_URL` / `location.origin` | `public/app.js:396` | S |
| C5 | Paginate `/api/places` and chunk `enrich_places` `IN` clauses (≤ 400 per batch); add explicit `limit`/`offset` | `app.py:147-192, 250-267` | M |

### HIGH — next sprint (3–5 days)

| # | Action | Effort |
|---|---|---|
| H1 | Add security headers (CSP, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`) via `vercel.json`; disable `/docs`, `/redoc`, `/openapi.json` in prod | S |
| H2 | Reduce `/explore` payload: server-render first N cards + paginate, or switch to paginated API + client render | M |
| H3 | Batch the N+1 queries in `festivals()` and `circuits()` (single join query each) | S–M |
| H4 | Image pipeline: generate WebP/AVIF + `srcset` + `width`/`height`; lazy-load below the fold; shrink the 73 files > 500 KB | M–L |
| H5 | Remove `/saved` and duplicate `/month/*` from sitemap; add `lastmod`; add `noindex` to `/saved` | S |
| H6 | Defer hero slideshow (lazy + `fetchpriority`), load Leaflet only on map pages, self-host or preconnect | S |
| H7 | Fix static home SEO: canonical, OG image (JPG), JSON-LD, correct counts — or delete it (see C2) | S |

### MEDIUM — next 2–3 weeks

| # | Action | Effort |
|---|---|---|
| M1 | Unify rendering: one source of truth for cards/filters (server templates **or** client), delete the duplicate path | L |
| M2 | Add HTML 404 page instead of JSON | S |
| M3 | Editorial workflow: promote places out of `needs_review`, fill 160 missing fields, add real `festival_occurrences` | M (ongoing) |
| M4 | Data coverage plan for the 14 zero-place states / 656 empty districts (or explicit "coming soon" states) | L (ongoing) |
| M5 | Move ~50 root scripts into `scripts/` + `archive/`; delete `search.py`, rename `test_fixes.py` | S–M |
| M6 | Make tests data-driven (derive expected counts from seed/DB instead of literals) | S |
| M7 | Add `ruff` + `mypy` + `pytest` config and run in CI | M |
| M8 | Add API caching (`s-maxage`, `stale-while-revalidate`) and basic rate limiting | M |
| M9 | Update README counts; fix duplicated `<title>`; replace SVG OG fallback | S |

### LOW — backlog

| # | Action | Effort |
|---|---|---|
| L1 | Remove `APP_VERSION` and unused imports; replace ad-hoc `ALTER TABLE` with a migration tool | M |
| L2 | Move 214 MB of images to a CDN/object store or Git LFS; shrink repo pack | L |
| L3 | Expand `trail_logistics` to all 19 circuits | M |
| L4 | Escape all interpolated strings in map popups/itinerary HTML; remove inline handlers to allow strict CSP | M |
| L5 | Accessibility pass (alt text quality, focus states, aria on map controls) | M |
| L6 | Split `app.py` into routers (`routers/states.py`, `places.py`, `festivals.py`, `pages.py`) | L |

---

## 6. Suggested execution order

1. **Day 1:** C3, C4 (one-liners) + C1 (saved hydration) → restore core user flows.
2. **Day 2:** C2 + H7 (homepage single source + SEO).
3. **Day 3:** C5 + H3 (API pagination + N+1) → stops the scaling cliff.
4. **Week 2:** H1, H2, H5, H6 (security, explore payload, SEO hygiene).
5. **Week 3+:** H4 image pipeline, then M-series.

---

## 7. Verification checklist used

- `python validate_data.py` — 0 errors.
- `python -m pytest tests/test_app.py -q`.
- Local `TestClient` probes of all API and HTML routes.
- Live header/body probes of `/`, `/explore`, `/saved`, `/festivals`, `/sitemap.xml`, `/robots.txt`, `/docs`, `/openapi.json`.
- DB queries for counts, coverage, duplicates, and verification status.
- Asset scan for total size, largest files, extension mix, broken references, and unused files.

---

## 8. Out of scope for this audit

- Content/editorial fact-checking of individual destinations.
- Legal review of image licences (attribution records exist, but licences were not re-verified).
- Load testing beyond single-request timing.
- Browser-based visual regression testing.

---

## 9. Remediation log

| Item | Status | Notes |
|---|---|---|
| C1 | Done | `/saved` now hydrates from localStorage on the server-rendered shell; save-button toggles refresh the list |
| C2 | Done | `public/index.html` removed; `/` rewritten to the FastAPI home so there is one homepage |
| C3 | Done | `server_festival_card` now reads `date_type`; 42 lunar, 31 fixed, 22 varies |
| C4 | Done | Share text uses `location.origin` |
| C5 | Done | `/api/places` supports `limit`/`offset`; `enrich_places` batches lookups in chunks of 400 |
| H1 | Done | CSP, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` added; docs/redoc/openapi return 404 when `VERCEL` is set |
| H7 | Done | Home title de-duplicated, canonical + JSON-LD + OG image confirmed, stale 808/484 counts gone |
| H3 | Done | `/api/festivals` and `/api/circuits` use one chunked query each; 69 festivals in 30 ms, 19 circuits / 112 stops in 21 ms |
| H5 | Done | Sitemap drops `/saved` and `/month/*`, re-adds `/festivals?month=N` and emits `<lastmod>`; `/saved` is `noindex, follow` |
| H8 | Done | `/month/{n}` now 301s to `/festivals?month=n`; invalid months still return 422 |
| M2 | Done | Unknown HTML routes render a noindex 404 page; `/api/*` and asset paths keep JSON |
| M5 | Done | 3 active helpers in `scripts/`, 49 one-off scripts + 11 artifacts in `scripts/legacy/`; `search.py` deleted, `test_fixes.py` renamed; `scripts/` excluded from Vercel uploads |
| M9 | Done | README counts corrected to 726 places / 69 festivals / 802 districts, plus asset and script paths |
| M10 | Done | Added Meluri, Nagaland's 17th district, to the source directory and seeded database (788 district entries in total) |
| M11 | Done | Added 80 Nagaland place pages (one per official district-map entry) and 21 Nagaland festivals to the calendar |
| M12 | Done | Added 201 Haryana place pages from haryanatourism.gov.in and 21 Haryana festivals to the calendar |
| M13 | Done | Added 130 Kerala place pages and 10 Kerala festivals (Vishu, Thrissur Pooram, Attukal Pongala, Theyyam, etc.) |
| M15 | Done | Added 82 Maharashtra place pages and 10 Maharashtra festivals; totals now 1215 places / 131 festivals |
| M16 | Done | Added 130 Assam place pages (all 35 districts) and 10 Assam festivals; totals now 1389 places / 141 festivals |
| M17 | Done | Added 127 Bihar place pages (all 38 districts) and 10 Bihar festivals; totals now 1516 places / 151 festivals |
| L1 | Done | `APP_VERSION` and the unused `load_state_dataset` import removed |
| D1 | Done | Fixed the failing `avathi-hills` attribution record (see below) |
| D2 | Done | Preview deployments restored after disconnecting the Vercel Git integration (see below) |
| D3 | Done | Deleted 57 unreferenced assets (2.80 MB) and 26 dead attribution records; every remaining asset is referenced |

### D1 — attribution record for four Karnataka places

`tests/test_app.py::test_karnataka_and_arunachal_use_real_photographs` was failing on `avathi-hills`. Investigation showed the problem was broader than one record:

- `avathi-hills`, `vajrapoha-falls`, `upli-buruj` and `basaveshwara-temple-basavana-bagewadi` served real 800 px JPEG photographs, but their `sources.json` records claimed "Original vector editorial illustration".
- The matching `.svg` files were **byte-identical copies of the JPEGs** (JPEG magic bytes with an `.svg` extension), so they could never have rendered as SVG.
- Commons has no photograph of any of the four places (verified via the Commons and Wikipedia APIs, including spelling variants), so the photos could not be re-sourced or attributed.
- The test already budgets up to 8 labelled vector places per state pair, which is the project's documented pattern for "no Commons photo exists".

Resolution (approved by the user): keep the label, fix the artifact.

- Wrote four genuine SVG illustrations (1200×700, `role="img"`, labelled) matching the existing placeholder style.
- Pointed `image_url` at the `.svg` files in `data/karnataka-places.json`.
- Deleted the four unattributed JPEGs so no unlicensed photo is served.
- Place pages fall back to the raster state cover for `og:image`, because social scrapers do not render SVG.
- Result: 4 vector places (budget 8) and 183 Commons-attributed photos (floor 170).

Note: the 19 remaining vector-labelled records were orphan attribution entries for a removed Mizoram dataset (they had no matching place) and their `.jpg` counterparts were 1×1 placeholder pixels. They were harmless but were part of the orphan-attribution finding in §4.1 and were deleted with the dead-data cleanup in D3 below.

### D2 — preview deployments without the Vercel Git integration

The Vercel Git link for `traveling-ketch` is disconnected on purpose, so a push to `master` cannot publish to production by itself. That also removed Vercel's automatic preview deployments, which used to appear on every pull request.

- `.github/workflows/preview.yml` deploys a preview on `pull_request` (opened/synchronize/reopened) and comments the URL on the PR.
- It also supports `workflow_dispatch`, so the secret can be verified from the Actions tab without opening a PR.
- Without a `VERCEL_TOKEN` repository secret the job still succeeds: it emits a warning and skips the deploy, so forks and fresh clones never fail.
- Production is unchanged: still manual via `vercel --prod --yes` (see `AGENTS.md`).

Verification: with `VERCEL_TOKEN` set, a manual dispatch deployed a preview and a throwaway pull request received the bot comment `Preview deployment: https://traveling-ketch-…vercel.app`; both preview URLs served `/style.css`, `/explore` and `/place/avathi-hills` with 200. Production was untouched (`dpl_HyG4WCMS1o8VoSqsat9JBUymhJ76` still holds the alias).

### H8 — one canonical festival calendar

`/month/{n}` and `/festivals?month=n` returned byte-identical pages and both appeared in the sitemap, so search engines saw duplicate content with no canonical separation.

- `/month/{n}` now returns `301` to `/festivals?month=n`; `/festivals?month=n` is the single canonical page.
- Months outside 1–12 still return `422` before any redirect.
- The sitemap lists the 12 canonical festival URLs and no `/month/*` entries.

### D3 — dead assets and attribution records

After D1, `sources.json` still held 780 records for 726 places, and `public/assets/places/` contained files that nothing served.

- References were recomputed from the API (`image_url` plus `images`, including the 28 legitimate `-gallery-2/3` entries), not from the per-state JSON files alone, which had overstated the dead set.
- Deleted 57 unreferenced files (2.80 MB): 1×1 Mizoram placeholders left by an earlier import, old-slug duplicates for Odisha places, and eight orphaned Chandigarh photographs.
- Deleted 26 dead non-gallery attribution records. All 28 gallery records were kept because each still attributes a live `images` entry.
- `sources.json` now has 754 records. A re-scan reports **0** unreferenced assets.

### Verification after remediation

- `python -m compileall` — OK.
- `node --check public/app.js` — OK.
- `python validate_data.py` — passed (160 pre-existing warnings).
- `python -m pytest tests/test_app.py -q` — **23 passed**.
- Local `TestClient` checks: home title/canonical/JSON-LD/theme-color present, no 808/484, 802/726 present; festival labels 42/31/22; `/saved` shell + containers + `app.js`; `/api/places` 726 total and `limit=5&offset=5` returns 5; invalid pagination returns 422; `/explore` 726 cards; `/docs`, `/redoc`, `/openapi.json` 200 locally, 404 with `VERCEL=1`.
- Route checks: `/month/8` → `301` `/festivals?month=8`, `/month/13` → `422`; `/no-such-page` → HTML 404 with `noindex` meta and `X-Robots-Tag`; `/api/no-such-page` and `/assets/...` → JSON 404; sitemap 1,601 URLs, `<lastmod>` present, no `/saved` or `/month/`; `/saved` carries `noindex, follow`.
- API checks: `/api/festivals` 69 items in 30 ms; `/api/circuits` 19 items / 112 stops in 21 ms; list and detail stops payloads match.
- Data checks: `sources.json` 754 records; 0 unreferenced assets under `public/assets/places/`.
- Attribution check: all four new `.svg` assets return 200 `image/svg+xml`; `/place/*`, `/state/karnataka` and `/explore` reference the `.svg` and no longer reference the deleted `.jpg`; `og:image` for those four places resolves to `/assets/states/karnataka.jpg`.

_Update this table as each item is implemented and verified._

### L7 — real accounts and cross-device sync (deferred)

The traveler profile, favorites, avatar, recent history and collections are
device-local by design: they live in `localStorage` under `india-locally-*` keys,
and the read-only Vercel filesystem cannot store them. Real accounts would add
cross-device sync, recovery and sharing between signed-in users, but they are a
separate project:

- authentication (email magic link or OAuth) with session cookies;
- hosted PostgreSQL (Vercel Postgres, Neon or Supabase) and migrations;
- per-user rows for profiles, favorites, recent history and collections;
- an export/delete flow and a privacy policy covering the stored personal data;
- a migration path that lets existing device-local data be claimed at first sign-in.

Deferred deliberately: none of the four profile upgrades shipped in November 2026
depends on it. When it is built, it should extend the existing device-local layer
rather than replace it, so the site keeps working without an account.

