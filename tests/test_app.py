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
    assert {s['name'] for s in states} >= {'Kerala', 'Rajasthan', 'Goa', 'Himachal Pradesh', 'Tamil Nadu', 'Karnataka'}
    assert all(s['cover_image_url'].startswith(('https://images.unsplash.com/', 'https://picsum.photos/')) for s in states)
    covers = {s['slug']: s['cover_image_url'] for s in states}
    assert 'photo-1722915767859-08a59870d70b' in covers['himachal-pradesh']
    assert 'photo-1733805569204-41768c7d8c0f' in covers['andhra-pradesh']
    assert 'photo-1563715493579-e0b3e0493b60' in covers['tamil-nadu']
    assert len(set(covers.values())) == len(covers)
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
    assert place['image_url'].startswith(('https://images.unsplash.com/', 'https://picsum.photos/'))
    place_images = [item['image_url'] for item in client.get('/api/places').json()]
    assert len(place_images) == len(set(place_images))
    assert client.get('/api/districts/bengaluru-urban').json()['places'] == []


def test_filters_combine_and_heritage_links(client):
    result = client.get('/api/places', params={'state': 'rajasthan', 'month': 1, 'unesco': 'true'}).json()
    assert {p['slug'] for p in result} == {'amber-fort', 'jantar-mantar', 'jaisalmer-fort'}
    assert all(p['unesco_url'].startswith('https://whc.unesco.org/en/list/') for p in result)
    assert client.get('/api/places?state=kerala&unesco=true').json() == []
    assert client.get('/api/places?month=6').json() == []
    assert len(client.get('/api/places?q=Kochi').json()) == 2
    assert client.get('/api/places', params={'q': "' OR 1=1 --"}).json() == []


def test_month_calendar_does_not_invent_annual_dates(client):
    result = client.get('/api/festivals?month=8&district=alappuzha').json()
    assert len(result) == 2
    assert all(f['occurrences'] == [] for f in result)
    assert client.get('/api/festivals?month=12').json() == []


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
        assert db.execute('SELECT COUNT(*) FROM places').fetchone()[0] == 20
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
        db.execute('PRAGMA foreign_keys=ON')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (9999, 1)')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (1, 13)')


def test_website_and_health(client):
    assert 'india' in client.get('/').text
    assert client.get('/app.js').status_code == 200
    assert client.get('/style.css').status_code == 200
    assert client.get('/healthz').json() == {'status': 'ok', 'places': 20}
    assert distance({'latitude': 0, 'longitude': 0}, {'latitude': 0, 'longitude': 0}) == 0
