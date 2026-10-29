import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import create_app, distance


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / 'test.sqlite3')) as client:
        yield client


def test_full_destination_journey(client):
    states = client.get('/api/states').json()
    assert len(states) == 28
    assert {s['name'] for s in states} >= {'Kerala', 'Rajasthan', 'Goa', 'Himachal Pradesh', 'Tamil Nadu', 'Karnataka', 'Odisha'}
    covers = {s['slug']: s['cover_image_url'] for s in states}
    assert all(url.startswith('/assets/states/') for url in covers.values())
    assert covers['odisha'] == '/assets/states/odisha.jpg'
    assert covers['haryana'] == '/assets/states/haryana.jpg'
    assert covers['west-bengal'] == '/assets/states/west-bengal.jpg'
    assert covers['maharashtra'] == '/assets/states/maharashtra.jpg'
    assert covers['manipur'] == '/assets/states/manipur.jpg'
    assert covers['nagaland'] == '/assets/states/nagaland.jpg'
    assert covers['uttar-pradesh'] == '/assets/states/uttar-pradesh.jpg'
    territories = client.get('/api/union-territories').json()
    assert len(territories) == 8
    assert {t['name'] for t in territories} == {'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'}
    assert client.get('/api/states/delhi').status_code == 200
    assert len(client.get('/api/districts?kind=ut').json()) >= 45
    assert len(client.get('/api/districts?region=karnataka').json()) >= 31
    assert {d['name'] for d in client.get('/api/districts?region=karnataka').json()} >= {'Bengaluru Urban', 'Mysuru', 'Kodagu', 'Vijayanagara', 'Dakshina Kannada', 'Udupi'}
    kerala = client.get('/api/states/kerala').json()
    assert len(kerala['districts']) == 14
    district = client.get('/api/districts/alappuzha').json()
    assert {f['name'] for f in district['festivals']} == {'Onam', 'Nehru Trophy Boat Race'}
    place = client.get('/api/places/alappuzha-beach').json()
    assert place['district'] == 'Alappuzha'
    assert place['nearby'][0]['slug'] == 'alappuzha-backwaters'
    assert place['verification_status'] == 'needs_review'
    assert place['last_verified_at'] is None
    assert place['image_url'] == '/assets/places/alappuzha-beach.jpg'
    all_places = client.get('/api/places').json()
    assert len(all_places) == 31
    assert all(item['image_url'] == f"/assets/places/{item['slug']}.jpg" for item in all_places)
    place_images = [item['image_url'] for item in all_places]
    assert len(place_images) == len(set(place_images))
    assert client.get('/api/districts/bengaluru-urban').json()['places'] == []
    assert len(client.get('/api/districts/puri').json()['places']) == 3
    north_goa = client.get('/api/districts/north-goa').json()
    assert len(north_goa['places']) == 5
    assert {p['slug'] for p in north_goa['places']} >= {'basilica-bom-jesus', 'fontainhas', 'aguada-fort', 'se-cathedral', 'anjuna-beach'}
    south_goa = client.get('/api/districts/south-goa').json()
    assert len(south_goa['places']) == 6
    assert {p['slug'] for p in south_goa['places']} >= {'palolem-beach', 'dudhsagar-falls', 'mangueshi-temple', 'cabo-de-rama-fort', 'shanta-durga-temple', 'agonda-beach'}
    assert len(client.get('/api/states/goa').json()['places']) == 11


def test_filters_combine_and_heritage_links(client):
    result = client.get('/api/places', params={'state': 'rajasthan', 'month': 1, 'unesco': 'true'}).json()
    assert {p['slug'] for p in result} == {'amber-fort', 'jantar-mantar', 'jaisalmer-fort'}
    assert all(p['unesco_url'].startswith('https://whc.unesco.org/en/list/') for p in result)
    assert client.get('/api/places?state=kerala&unesco=true').json() == []
    assert client.get('/api/places?month=6').json() == []
    assert len(client.get('/api/places?q=Kochi').json()) == 2
    assert client.get('/api/places', params={'q': "' OR 1=1 --"}).json() == []
    assert client.get('/api/places', params={'q': '%'}).json() == []
    assert client.get('/api/places', params={'q': '_'}).json() == []


def test_month_calendar_does_not_invent_annual_dates(client):
    result = client.get('/api/festivals?month=8&district=alappuzha').json()
    assert len(result) == 2
    assert all(f['occurrences'] == [] for f in result)
    dec_festivals = client.get('/api/festivals?month=12').json()
    assert len(dec_festivals) >= 2
    assert any(f['name'] == 'Hornbill Festival' for f in dec_festivals)
    assert any(f['name'] == 'Konark Dance & Sand Art Festival' for f in dec_festivals)


@pytest.mark.parametrize('url', ['/api/places?month=13', '/api/festivals?month=0'])
def test_invalid_month(client, url):
    assert client.get(url).status_code == 422


@pytest.mark.parametrize('url', ['/api/states/missing', '/api/districts/missing', '/api/places/missing'])
def test_missing_destination(client, url):
    assert client.get(url).status_code == 404


def test_seed_is_persistent_and_idempotent(tmp_path):
    path = tmp_path / 'persistent.sqlite3'
    create_app(path)
    create_app(path)
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT COUNT(*) FROM places').fetchone()[0] == 31
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
        db.execute('PRAGMA foreign_keys=ON')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (9999, 1)')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (1, 13)')


def test_website_and_health(client):
    homepage = client.get('/').text
    assert 'india' in homepage
    assert 'Explore Incredible India' in homepage
    assert '28' in homepage and '807' in homepage
    assert 'Featured destinations' in homepage
    assert 'href="/explore"' in homepage
    assert 'href="/state/' in homepage
    assert 'Featured States' in homepage
    assert client.get('/app.js').status_code == 200
    assert client.get('/style.css').status_code == 200
    assert client.get('/assets/state-cover.svg').status_code == 200
    assert client.get('/assets/states/odisha.jpg').status_code == 200
    assert client.get('/assets/states/haryana.jpg').status_code == 200
    assert client.get('/assets/states/uttar-pradesh.jpg').status_code == 200
    assert client.get('/healthz').json() == {'status': 'ok', 'places': 31}
    assert distance({'latitude': 0, 'longitude': 0}, {'latitude': 0, 'longitude': 0}) == 0


def test_server_rendered_routes_are_crawlable(client):
    explore = client.get('/explore').text
    assert 'Find your kind of place' in explore
    assert 'class="art-title"' in explore
    assert 'Alappuzha Backwaters' in explore
    assert 'Kerala' in client.get('/state/kerala').text
    assert 'Alappuzha' in client.get('/district/alappuzha').text
    assert 'Alappuzha Beach' in client.get('/place/alappuzha-beach').text
    assert 'Festival calendar' in client.get('/month/8').text
    assert 'Festivals in August' in client.get('/month/8').text
    assert 'Typically in August' in client.get('/district/alappuzha').text
    assert 'Typical months: January, February, March, October' in client.get('/place/alappuzha-beach').text
    assert 'Saved places' in client.get('/saved').text
    area = client.get('/area').text
    assert 'Choose a state' in area
    assert 'Kerala' in area and 'Puducherry' in area
    assert '<link rel="canonical" href="https://india-explorer-hazel.vercel.app/explore">' in explore
    sitemap = client.get('/sitemap.xml')
    assert sitemap.status_code == 200
    assert '/state/kerala' in sitemap.text
    assert 'Sitemap:' in client.get('/robots.txt').text
    assert 'data-server-rendered="true"' in explore
    festivals_page = client.get('/festivals').text
    assert 'Celebrations across India' in festivals_page
    assert 'month-selector-tabs' in festivals_page


def test_editorial_status(client):
    assert client.get('/api/editorial-status').json() == {
        'detailed_places': 31,
        'reviewed_places': 0,
        'unreviewed_places': 31,
        'confirmed_festival_dates': 0,
    }
