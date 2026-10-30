"""Canonical state-data loading, normalization, validation, and import reporting."""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
STATE_DATA_DIR = DATA_DIR / 'states'
PLACE_FIELDS = (
    'slug', 'name', 'district_id', 'category', 'latitude', 'longitude', 'description',
    'how_to_reach', 'practical_notes', 'source_url', 'image_url', 'id',
)
TEXT_FIELDS = ('name', 'description', 'how_to_reach', 'practical_notes', 'entry_fee', 'address')
DASH_CORRUPTION = re.compile(r'(?:\u2013.){3,}\u2013?')
MOJIBAKE = re.compile(r'(?:Ã.|Â.|â.|\ufffd)')
INDIA_BOUNDS = (6.0, 38.5, 68.0, 98.5)


def normalize_text(value):
    """Normalize Unicode and repair the known legacy dash-import corruption."""
    if not isinstance(value, str):
        return value
    value = unicodedata.normalize('NFC', value)
    return DASH_CORRUPTION.sub(lambda match: match.group().replace('\u2013', ''), value).strip()


def state_manifest_paths():
    return sorted(STATE_DATA_DIR.glob('*.json')) if STATE_DATA_DIR.exists() else []


def dataset_version_bytes():
    """Return all canonical data bytes so deployment DB versions change with data."""
    paths = [DATA_DIR / 'india-states-districts.json', DATA_DIR / 'odisha-places.json']
    paths.extend(state_manifest_paths())
    return b''.join(path.read_bytes() for path in paths if path.exists())


def load_state_dataset(state_slug):
    """Load a state manifest and, where configured, its external places document."""
    manifest_path = STATE_DATA_DIR / f'{state_slug}.json'
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('slug') != state_slug:
        raise ValueError(f'{manifest_path} slug does not match its filename')
    places_path = manifest.get('places_file')
    if places_path:
        resolved_path = (manifest_path.parent / places_path).resolve()
        manifest['places'] = json.loads(resolved_path.read_text(encoding='utf-8'))
    manifest.setdefault('places', [])
    return manifest


def normalize_place(place):
    normalized = dict(place)
    for field in TEXT_FIELDS:
        normalized[field] = normalize_text(normalized.get(field, ''))
    return normalized


def validate_state_dataset(dataset, static_dir=ROOT / 'static'):
    """Return data-quality errors and warnings without mutating source data."""
    errors, warnings = [], []
    state = dataset.get('slug', '<unknown>')
    places = dataset.get('places', [])
    if not isinstance(places, list):
        return [f'{state}: places must be a list'], warnings
    slugs = Counter()
    coordinates = Counter()
    image_sources_path = static_dir / 'assets' / 'places' / 'sources.json'
    image_sources = json.loads(image_sources_path.read_text(encoding='utf-8')) if image_sources_path.exists() else {}
    for index, place in enumerate(places):
        label = f'{state}: places[{index}]'
        missing = [field for field in PLACE_FIELDS if field not in place or place[field] in (None, '')]
        if missing:
            errors.append(f'{label}: missing required fields: {", ".join(missing)}')
            continue
        slug = place['slug']
        slugs[slug] += 1
        for field in TEXT_FIELDS:
            value = place.get(field, '')
            if not isinstance(value, str) or DASH_CORRUPTION.search(value) or MOJIBAKE.search(value):
                errors.append(f'{label}: invalid text in {field}')
            elif not value:
                warnings.append(f'{label}: missing {field}')
        parsed = urlparse(place['source_url'])
        if parsed.scheme != 'https' or not parsed.netloc:
            errors.append(f'{label}: source_url must be an HTTPS URL')
        latitude, longitude = place['latitude'], place['longitude']
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            errors.append(f'{label}: coordinates must be numeric')
        elif not (INDIA_BOUNDS[0] <= latitude <= INDIA_BOUNDS[1] and INDIA_BOUNDS[2] <= longitude <= INDIA_BOUNDS[3]):
            errors.append(f'{label}: coordinates are outside India')
        else:
            coordinates[(latitude, longitude)] += 1
        image_path = static_dir / place['image_url'].lstrip('/')
        if not image_path.exists():
            errors.append(f'{label}: image asset does not exist: {place["image_url"]}')
        if slug not in image_sources:
            warnings.append(f'{label}: image attribution is missing')
    errors.extend(f'{state}: duplicate place slug: {slug}' for slug, count in slugs.items() if count > 1)
    warnings.extend(f'{state}: duplicated coordinates: {latitude}, {longitude}' for (latitude, longitude), count in coordinates.items() if count > 1)
    return errors, warnings


def validate_all_state_data():
    """Validate every canonical manifest; Odisha remains the first migrated state."""
    errors, warnings = [], []
    for path in state_manifest_paths():
        dataset = load_state_dataset(path.stem)
        state_errors, state_warnings = validate_state_dataset(dataset)
        errors.extend(state_errors)
        warnings.extend(state_warnings)
    return errors, warnings


def validate_database(db, static_dir=ROOT / 'static'):
    """Validate the entire seeded catalogue, including legacy seed records."""
    errors, warnings = [], []
    sources_path = static_dir / 'assets' / 'places' / 'sources.json'
    image_sources = json.loads(sources_path.read_text(encoding='utf-8')) if sources_path.exists() else {}
    regions = db.execute('SELECT id, slug, name, description FROM regions').fetchall()
    region_ids = {region['id'] for region in regions}
    for region in regions:
        for field in ('name', 'description'):
            value = region[field]
            if not value or DASH_CORRUPTION.search(value) or MOJIBAKE.search(value):
                errors.append(f"{region['slug']}: invalid region {field}")
    districts = db.execute('SELECT id, region_id, slug, name, description, food_notes FROM districts').fetchall()
    district_ids = {district['id'] for district in districts}
    seen_districts = Counter()
    for district in districts:
        if district['region_id'] not in region_ids:
            errors.append(f"{district['slug']}: unknown region")
        seen_districts[(district['region_id'], district['name'].casefold())] += 1
        for field in ('name', 'description', 'food_notes'):
            value = district[field]
            if not value or DASH_CORRUPTION.search(value) or MOJIBAKE.search(value):
                errors.append(f"{district['slug']}: invalid district {field}")
    errors.extend(
        f'duplicate district name: {name}' for (_, name), count in seen_districts.items() if count > 1
    )
    places = db.execute('''SELECT id, district_id, slug, name, description, category, latitude, longitude,
        how_to_reach, practical_notes, source_url, image_url, entry_fee, address FROM places''').fetchall()
    seen_slugs, coordinates = Counter(), Counter()
    for place in places:
        label = place['slug']
        seen_slugs[label] += 1
        if place['district_id'] not in district_ids:
            errors.append(f'{label}: unknown district')
        for field in TEXT_FIELDS:
            value = place[field]
            if DASH_CORRUPTION.search(value) or MOJIBAKE.search(value):
                errors.append(f'{label}: invalid place {field}')
            elif not value:
                warnings.append(f'{label}: missing place {field}')
        if not place['category']:
            errors.append(f'{label}: missing category')
        parsed = urlparse(place['source_url'])
        if parsed.scheme != 'https' or not parsed.netloc:
            errors.append(f'{label}: source_url must be an HTTPS URL')
        if not (INDIA_BOUNDS[0] <= place['latitude'] <= INDIA_BOUNDS[1] and INDIA_BOUNDS[2] <= place['longitude'] <= INDIA_BOUNDS[3]):
            errors.append(f'{label}: coordinates are outside India')
        coordinates[(place['latitude'], place['longitude'])] += 1
        if not (static_dir / place['image_url'].lstrip('/')).exists():
            errors.append(f'{label}: image asset does not exist')
        if label not in image_sources:
            warnings.append(f'{label}: image attribution is missing')
    errors.extend(f'duplicate place slug: {slug}' for slug, count in seen_slugs.items() if count > 1)
    warnings.extend(f'duplicated coordinates: {latitude}, {longitude}' for (latitude, longitude), count in coordinates.items() if count > 1)
    return errors, warnings


def import_report():
    """Produce a machine-readable import readiness report for every state dataset."""
    report = {'states': [], 'errors': [], 'warnings': []}
    for path in state_manifest_paths():
        dataset = load_state_dataset(path.stem)
        errors, warnings = validate_state_dataset(dataset)
        places = dataset['places']
        report['states'].append({
            'slug': dataset['slug'],
            'name': dataset.get('name', dataset['slug']),
            'district_count': len({place['district_id'] for place in places}),
            'place_count': len(places),
            'missing_images': sum(not (ROOT / 'static' / place['image_url'].lstrip('/')).exists() for place in places),
            'missing_sources': sum(not place.get('source_url') for place in places),
            'unverified_records': len(places),
            'errors': errors,
            'warnings': warnings,
        })
        report['errors'].extend(errors)
        report['warnings'].extend(warnings)
    return report
