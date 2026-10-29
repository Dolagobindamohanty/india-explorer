PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK(kind IN ('state', 'union_territory')),
    description TEXT NOT NULL,
    source_url TEXT NOT NULL,
    cover_image_url TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    food_notes TEXT NOT NULL DEFAULT '',
    source_url TEXT NOT NULL,
    UNIQUE(region_id, name)
);
CREATE TABLE IF NOT EXISTS heritage_sites (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    unesco_url TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY,
    district_id INTEGER NOT NULL REFERENCES districts(id),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
    longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
    how_to_reach TEXT NOT NULL,
    practical_notes TEXT NOT NULL,
    heritage_id INTEGER REFERENCES heritage_sites(id),
    source_url TEXT NOT NULL,
    image_url TEXT NOT NULL DEFAULT '',
    verification_status TEXT NOT NULL DEFAULT 'needs_review'
        CHECK(verification_status IN ('needs_review', 'verified')),
    last_verified_at TEXT,
    CHECK(verification_status != 'verified' OR last_verified_at IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS place_months (
    place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
    PRIMARY KEY(place_id, month)
);
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS place_tags (
    place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    PRIMARY KEY(place_id, tag_id)
);
CREATE TABLE IF NOT EXISTS festivals (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    date_type TEXT NOT NULL CHECK(date_type IN ('fixed', 'lunar', 'seasonal', 'varies_annually')),
    source_url TEXT NOT NULL,
    last_verified_at TEXT
);
-- Festivals can span several districts. Months can cross the year boundary.
CREATE TABLE IF NOT EXISTS festival_districts (
    festival_id INTEGER NOT NULL REFERENCES festivals(id) ON DELETE CASCADE,
    district_id INTEGER NOT NULL REFERENCES districts(id),
    PRIMARY KEY(festival_id, district_id)
);
CREATE TABLE IF NOT EXISTS festival_months (
    festival_id INTEGER NOT NULL REFERENCES festivals(id) ON DELETE CASCADE,
    month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
    PRIMARY KEY(festival_id, month)
);
CREATE TABLE IF NOT EXISTS festival_occurrences (
    id INTEGER PRIMARY KEY,
    festival_id INTEGER NOT NULL REFERENCES festivals(id) ON DELETE CASCADE,
    starts_on TEXT NOT NULL,
    ends_on TEXT NOT NULL,
    source_url TEXT NOT NULL,
    verified_at TEXT NOT NULL,
    CHECK(starts_on <= ends_on)
);

CREATE TABLE IF NOT EXISTS circuits (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    tagline TEXT NOT NULL,
    description TEXT NOT NULL,
    duration TEXT NOT NULL,
    best_season TEXT NOT NULL,
    cover_image_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS circuit_places (
    circuit_id INTEGER NOT NULL REFERENCES circuits(id) ON DELETE CASCADE,
    place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    stop_order INTEGER NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    PRIMARY KEY(circuit_id, place_id)
);

CREATE INDEX IF NOT EXISTS idx_district_region ON districts(region_id);
CREATE INDEX IF NOT EXISTS idx_place_district ON places(district_id);
CREATE INDEX IF NOT EXISTS idx_month_places ON place_months(month);
