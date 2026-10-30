# India Explorer

A runnable tourism-directory MVP for travellers and new residents. Browse
State → District → Place, discover typical festival months, filter by interest
and UNESCO designation, and save destinations in your browser.

## Run in Windows Command Prompt

```cmd
cd C:\Users\ADMIN\omnirush.ai\india-explorer
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8010 --reload
```

For local development and tests, install `requirements-dev.txt` instead.

Open http://127.0.0.1:8010. Port 8010 keeps this separate from the SQL Analyst
application. Keep the terminal open; Ctrl+C stops the server.

## Deploy to Vercel

The project includes `api/index.py` and `vercel.json` for a FastAPI serverless
deployment. The included SQLite database is intentionally read-only editorial
demo storage: Vercel's filesystem is temporary, so it must not be used for
accounts, CMS changes, saved itineraries, or any other durable user data.

For a production system with mutations, provision a hosted PostgreSQL database
and migrate the schema and seed data before enabling write features. Store its
connection string as the Vercel `DATABASE_URL` environment variable and run
migrations from CI or an administrative job, not during a serverless request.
This MVP deliberately has no authenticated writes, so browser-local favorites
remain private to the visitor's device.

Install and authenticate the Vercel CLI from Command Prompt:

```cmd
npm install --global vercel
vercel login
```

From this directory, preview first:

```cmd
vercel
```

Then deploy to production:

```cmd
vercel --prod
```

The CLI will print the public URL. The frontend and API are served by the same
FastAPI deployment, so no CORS configuration is needed.

## What is included

- Search-first homepage with popular categories, trending destinations, skeleton loading states and responsive mobile navigation.
- Light/dark mode, hover-enhanced destination cards, favorites and recently viewed places stored in the browser.
- Server-rendered HTML routes for the homepage, destinations, states, districts, places, festival months and saved-place guidance; JavaScript adds navigation, theme and save interactions without replacing server-rendered route content.
- Home with **Explore** and region directory entry points.
- 28 state pages and 8 union-territory pages, a growing district directory, and 120 detailed place pages.
- Month-based festival calendar and seasonal place recommendations.
- Search and combinable state, month, category and UNESCO filters.
- District food notes, access guidance, official reference links and map links.
- Nearby destinations using straight-line coordinates (not road journey time).
- Browser-local saved places, empty states and missing-page handling.
- FastAPI, persistent SQLite database, plain HTML/CSS/JavaScript frontend.

## Database

`schema.sql` defines the relational schema. `seed.py` supplies the editorial
pilot. The app creates `data/explorer.sqlite3` at first startup and seeds it
only if the regions table is empty. Restarts preserve data. Each API request
uses short-lived database connections with foreign keys enabled.

```text
regions (state or union territory)
  └─ districts
       └─ places ── heritage_sites (official UNESCO property)
            ├─ place_months
            └─ place_tags ── tags
districts ── festival_districts ── festivals
                                  ├─ festival_months
                                  └─ festival_occurrences
```

The region model accommodates all 28 states and 8 union territories. District
boundaries and names need editorial maintenance;
The district directory is imported from `data/india-states-districts.json` and
is displayed as administrative navigation; detailed place content remains
editorial and is intentionally smaller.

Months are rows rather than comma-separated strings: winter seasons spanning
December–January work naturally. Festivals can belong to multiple districts.
Confirmed occurrences have separate start/end dates, source and verification
timestamp, so a lunar festival's typical month is never mistaken for a booking date.
Serial UNESCO properties can include multiple attractions through `heritage_sites`.

## Data and assets

This is a small illustrative pilot, not a comprehensive India dataset. Twenty
places, nine festivals, 807 district directory entries and a complete
28-state/8-union-territory region directory are provided. Official tourism/
district/UNESCO URLs are reference pointers; no claim
is made that their current contents were independently checked in this build.
All place records are marked `needs_review`; annual festival dates are unpopulated.
Seasonal guidance and coordinates are approximate. Fees and opening times are
deliberately not invented. Add confirmed information with sources before publishing.

The website stores a destination-specific image URL for every place. The 120
pilot place cards use locally stored Wikimedia Commons and Unsplash photographs selected for
the named destination and category. Region pages use iconic landmark cover
photographs representing each state and union territory. Attribution/source records are in
`static/assets/places/sources.json`; verify each file's current license and
attribution requirements before a public commercial launch. Google Fonts is
optional; system-font fallbacks and coloured backgrounds remain usable offline.

## APIs

- `GET /api/states`, `/api/states/{slug}`
- `GET /api/union-territories`
- `GET /api/districts?region=karnataka` or `?kind=ut`, `/api/districts/{slug}`
- `GET /api/places?q=&state=&district=&month=&category=&unesco=true`
- `GET /api/places/{slug}`
- `GET /api/festivals?month=8&district=alappuzha`
- `GET /healthz`; interactive API docs at `/docs`
- `GET /sitemap.xml` and `/robots.txt` for crawlable server-rendered pages

Run `python verify_data.py` to check the region counts, district foreign keys,
place image uniqueness and missing cover images. The bundled administrative
snapshot contains 807 districts across India's 28 states and 8 union
territories, matching official administrative reorganization data.
That check does not claim that every tourism description, festival date or
image has been independently verified; those require editorial review against
the linked official sources.

## Checks

```cmd
python -m pytest -q
python -m compileall -q app.py seed.py tests
```

Tests cover navigation data, composable filters, festival date honesty, invalid
inputs, missing records, persistent seeding and foreign-key constraints.

## Scope

No credentials, paid service or Node build is needed. This MVP uses hash-based
client-side routes; production SEO would require server-rendered destination
pages, canonical URLs and a sitemap. Content editing is currently through SQL
and seed data; an authenticated editorial interface, full India coverage,
accounts and itinerary routing are future work. SQLite is appropriate for this
local read-heavy pilot; PostgreSQL migration can follow when deployment and
editorial concurrency require it.
