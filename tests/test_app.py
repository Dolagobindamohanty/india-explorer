import json
import sqlite3
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import create_app, distance
from data_pipeline import import_report, validate_all_state_data, validate_database

ASSETS = Path(__file__).resolve().parents[1] / "public"


def assert_asset_exists(image_url):
    """Every referenced place image must resolve to a real file on disk."""
    assert image_url.startswith("/assets/"), image_url
    assert (ASSETS / image_url.lstrip("/")).exists(), f"missing asset file for {image_url}"


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
    assert {f['name'] for f in district['festivals']} == {'Onam', 'Nehru Trophy Boat Race', 'Aranmula Boat Race', 'Champakulam Moolam Boat Race'}
    place = client.get('/api/places/alappuzha-beach').json()
    assert place['district'] == 'Alappuzha'
    assert place['nearby'][0]['slug'] == 'alappuzha-backwaters'
    assert place['verification_status'] == 'needs_review'
    assert place['last_verified_at'] is None
    assert place['image_url'] == '/assets/places/alappuzha-beach.jpg'
    all_places = client.get('/api/places').json()
    assert len(all_places) == 1516
    assert all(item['image_url'].startswith('/assets/places/') for item in all_places)
    place_images = [item['image_url'] for item in all_places]
    assert len(place_images) == len(set(place_images))
    assert {p['slug'] for p in client.get('/api/districts/bengaluru-urban').json()['places']} == {
        'vidhana-soudha', 'lalbagh-botanical-garden', 'cubbon-park', 'bangalore-palace',
        'bannerghatta-biological-park', 'iskcon-temple-bengaluru',
    }
    assert len(client.get('/api/districts/puri').json()['places']) == 12
    assert len(client.get('/api/districts/khordha').json()['places']) == 17
    odisha = client.get('/api/states/odisha').json()
    assert len(odisha['districts']) == 30
    assert len(odisha['places']) == 111
    ap = client.get('/api/states/andhra-pradesh').json()
    assert len(ap['districts']) == 26
    assert len(ap['places']) == 69
    arunachal = client.get('/api/states/arunachal-pradesh').json()
    assert len(arunachal['districts']) == 26
    assert len(arunachal['places']) == 16
    mizoram = client.get('/api/states/mizoram').json()
    assert len(mizoram['districts']) == 11
    assert len(mizoram['places']) == 110
    assert all(place['image_url'].startswith('/assets/places/') for place in mizoram['places'])
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in mizoram['places'])
    assert client.get('/api/places/solomon-temple-aizawl').json()['district'] == 'Aizawl'
    meghalaya = client.get('/api/states/meghalaya').json()
    assert len(meghalaya['districts']) == 12
    assert len(meghalaya['places']) == 131
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in meghalaya['places'])
    assert client.get('/api/places/nohkalikai-falls').json()['district'] == 'East Khasi Hills'
    tawang = client.get('/api/places/tawang-monastery').json()
    assert tawang['district'] == 'Tawang'
    assert tawang['image_url'] == '/assets/places/tawang-monastery.jpg'
    assert_asset_exists(tawang['image_url'])
    assert {1, 10}.issubset(tawang['best_months'])
    nagaland = client.get('/api/states/nagaland').json()
    assert len(nagaland['districts']) == 17
    assert len(nagaland['places']) == 80
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in nagaland['places'])
    nagaland_districts = {place['district'] for place in nagaland['places']}
    assert nagaland_districts == {
        'Chumoukedima', 'Dimapur', 'Kiphire', 'Kohima', 'Longleng', 'Meluri',
        'Mokokchung', 'Mon', 'Niuland', 'Noklak', 'Peren', 'Phek', 'Shamator',
        'Tseminyu', 'Tuensang', 'Wokha', 'Zunheboto',
    }
    assert client.get('/api/places/dzukou-valley').json()['district'] == 'Kohima'
    assert client.get('/api/places/saramati-peak').json()['district'] == 'Kiphire'
    assert client.get('/api/places/longwa-village').json()['district'] == 'Mon'
    haryana = client.get('/api/states/haryana').json()
    assert len(haryana['districts']) == 22
    assert len(haryana['places']) == 201
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in haryana['places'])
    assert client.get('/api/places/brahma-sarovar').json()['district'] == 'Kurukshetra'
    kerala = client.get('/api/states/kerala').json()
    assert len(kerala['districts']) == 14
    assert len(kerala['places']) == 130
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in kerala['places'])
    assert client.get('/api/places/munnar').json()['district'] == 'Idukki'
    assert client.get('/api/places/fort-kochi').json()['district'] == 'Ernakulam'
    maharashtra = client.get('/api/states/maharashtra').json()
    assert len(maharashtra['districts']) == 36
    assert len(maharashtra['places']) == 126
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in maharashtra['places'])
    assert client.get('/api/places/gateway-of-india').json()['district'] == 'Mumbai'
    assert client.get('/api/places/ajanta-caves').json()['district'] == 'Chhatrapati Sambhajinagar'
    assam = client.get('/api/states/assam').json()
    assert len(assam['districts']) == 35
    assert len(assam['places']) == 130
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in assam['places'])
    assert client.get('/api/places/kamakhya-temple').json()['district'] == 'Kamrup Metro'
    assert client.get('/api/places/kaziranga-national-park').json()['district'] == 'Golaghat'
    bihar = client.get('/api/states/bihar').json()
    assert len(bihar['districts']) == 38
    assert len(bihar['places']) == 127
    assert all((ASSETS / place['image_url'].lstrip('/')).exists() for place in bihar['places'])
    assert client.get('/api/places/mahabodhi-temple').json()['district'] == 'Gaya'
    assert client.get('/api/places/nalanda-mahavihara').json()['district'] == 'Nalanda'
    karnataka = client.get('/api/states/karnataka').json()
    assert len(karnataka['districts']) == 31
    assert len(karnataka['places']) == 171
    hampi = client.get('/api/places/hampi-group-of-monuments').json()
    assert hampi['district'] == 'Vijayanagara'
    assert hampi['heritage_designation'] == 'world_heritage_site'
    assert hampi['image_url'] == '/assets/places/hampi-group-of-monuments.jpg'
    assert_asset_exists(hampi['image_url'])
    tirumala = client.get('/api/places/tirumala-venkateswara-temple').json()
    assert len(tirumala['images']) == 3
    assert tirumala['images'][0]['image_url'] == tirumala['image_url']
    north_goa = client.get('/api/districts/north-goa').json()
    assert len(north_goa['places']) == 7
    assert {p['slug'] for p in north_goa['places']} >= {'basilica-bom-jesus', 'fontainhas', 'aguada-fort', 'se-cathedral', 'anjuna-beach', 'mangueshi-temple', 'shanta-durga-temple'}
    south_goa = client.get('/api/districts/south-goa').json()
    assert {p['slug'] for p in south_goa['places']} == {'colva-beach'}
    kushavati = client.get('/api/districts/kushavati').json()
    assert len(kushavati['places']) == 5
    assert {p['slug'] for p in kushavati['places']} == {'palolem-beach', 'agonda-beach', 'dudhsagar-falls', 'cabo-de-rama-fort', 'cotigao-wildlife-sanctuary'}
    assert len(client.get('/api/states/goa').json()['places']) == 13
    assert len(client.get('/api/states/goa').json()['districts']) == 3
    sikkim = client.get('/api/states/sikkim').json()
    assert len(sikkim['districts']) == 6
    assert len(sikkim['places']) == 7
    gangtok = client.get('/api/districts/gangtok').json()
    assert any(p['slug'] == 'tsomgo-lake' for p in gangtok['places'])
    mangan = client.get('/api/districts/mangan').json()
    assert {p['slug'] for p in mangan['places']} >= {'gurudongmar-lake', 'yumthang-valley', 'khangchendzonga-national-park'}
    tripura = client.get('/api/states/tripura').json()
    assert len(tripura['districts']) == 8
    assert len(tripura['places']) == 8
    west_tripura = client.get('/api/districts/west-tripura').json()
    assert any(p['slug'] == 'ujjayanta-palace' for p in west_tripura['places'])
    gomati = client.get('/api/districts/gomati').json()
    assert {p['slug'] for p in gomati['places']} >= {'tripura-sundari-temple', 'chabimura-rock-carvings'}
    sepahijala = client.get('/api/districts/sepahijala').json()
    assert any(p['slug'] == 'neermahal-water-palace' for p in sepahijala['places'])
    unakoti = client.get('/api/districts/unakoti').json()
    assert any(p['slug'] == 'unakoti-rock-carvings' for p in unakoti['places'])
    hp = client.get('/api/states/himachal-pradesh').json()
    assert len(hp['districts']) == 12
    assert len(hp['places']) == 11
    kullu = client.get('/api/districts/kullu').json()
    assert {p['slug'] for p in kullu['places']} >= {'hidimba-devi-temple', 'rohtang-pass'}
    lahaul = client.get('/api/districts/lahaul-and-spiti').json()
    assert {p['slug'] for p in lahaul['places']} >= {'key-monastery', 'chandratal-lake', 'tabo-monastery'}
    # Union Territories comprehensive verification
    andaman = client.get('/api/states/andaman-and-nicobar-islands').json()
    assert len(andaman['districts']) == 3
    assert len(andaman['places']) == 5
    assert {p['slug'] for p in andaman['places']} >= {'cellular-jail', 'radhanagar-beach', 'ross-island-andaman', 'elephant-beach-havelock', 'baratang-island-caves'}
    delhi = client.get('/api/states/delhi').json()
    assert len(delhi['districts']) == 11
    assert len(delhi['places']) == 8
    assert {p['slug'] for p in delhi['places']} >= {'red-fort-delhi', 'qutub-minar', 'humayuns-tomb', 'india-gate', 'akshardham-temple-delhi', 'lotus-temple-delhi', 'jama-masjid-delhi', 'bangla-sahib-delhi'}
    jk = client.get('/api/states/jammu-and-kashmir').json()
    assert len(jk['districts']) == 20
    assert len(jk['places']) == 8
    assert {p['slug'] for p in jk['places']} >= {'dal-lake', 'gulmarg-gondola', 'vaishno-devi', 'martand-sun-temple', 'pahalgam-betaab-valley', 'shankaracharya-temple', 'sonamarg-thajiwas', 'nishat-shalimar-gardens'}
    ladakh = client.get('/api/states/ladakh').json()
    assert len(ladakh['districts']) == 2
    assert len(ladakh['places']) == 7
    assert {p['slug'] for p in ladakh['places']} >= {'thiksey-monastery', 'pangong-tso', 'diskit-monastery', 'leh-palace-shanti-stupa', 'sangam-indus-zanskar', 'khardung-la-pass', 'hemis-monastery'}
    puducherry = client.get('/api/states/puducherry').json()
    assert len(puducherry['districts']) == 4
    assert len(puducherry['places']) == 6
    assert {p['slug'] for p in puducherry['places']} >= {'auroville-matrimandir', 'promenade-beach-pondicherry', 'aurobindo-ashram', 'white-town-pondicherry', 'paradise-beach-pondicherry', 'sacred-heart-basilica-pondicherry'}
    chandigarh = client.get('/api/states/chandigarh').json()
    assert len(chandigarh['places']) == 23
    assert {p['slug'] for p in chandigarh['places']} >= {'rock-garden-chandigarh', 'sukhna-lake', 'rose-garden-chandigarh', 'capitol-complex-open-hand', 'leisure-valley-chandigarh', 'garden-of-fragrance', 'japanese-garden-chandigarh', 'sector-17-plaza'}
    dnh = client.get('/api/states/dadra-and-nagar-haveli-and-daman-and-diu').json()
    assert len(dnh['places']) == 5
    assert {p['slug'] for p in dnh['places']} >= {'diu-fort', 'moti-daman-fort', 'naida-caves-diu', 'nagoa-beach-diu', 'jampore-beach-daman'}
    lakshadweep = client.get('/api/states/lakshadweep').json()
    assert len(lakshadweep['places']) == 4
    assert {p['slug'] for p in lakshadweep['places']} >= {'bangaram-atoll', 'agatti-island-lagoon', 'kavaratti-island', 'kadmat-island-diving'}
    # Explicit UNESCO distinction test:
    # 1. Standalone World Heritage Site
    konark = client.get('/api/places/konark-sun-temple').json()
    assert konark['heritage_designation'] == 'world_heritage_site'
    red_fort = client.get('/api/places/red-fort-delhi').json()
    assert red_fort['heritage_designation'] == 'world_heritage_site'
    # 2. Component of larger serial site
    amber = client.get('/api/places/amber-fort').json()
    assert amber['heritage_designation'] == 'component_site'
    capitol = client.get('/api/places/capitol-complex-open-hand').json()
    assert capitol['heritage_designation'] == 'component_site'
    # 3. Tentative list site
    tabo = client.get('/api/places/tabo-monastery').json()
    assert tabo['heritage_designation'] == 'tentative_list'
    dal = client.get('/api/places/dal-lake').json()
    assert dal['heritage_designation'] == 'tentative_list'
    # 4. Non-UNESCO landmark (Shimla Ridge is not UNESCO)
    ridge = client.get('/api/places/shimla-ridge').json()
    assert ridge['heritage_id'] is None
    assert ridge['heritage_designation'] is None


def test_filters_combine_and_heritage_links(client):
    result = client.get('/api/places', params={'state': 'rajasthan', 'month': 1, 'unesco': 'true'}).json()
    assert {p['slug'] for p in result} == {'amber-fort', 'jantar-mantar', 'jaisalmer-fort'}
    assert all(p['unesco_url'].startswith('https://whc.unesco.org/en/list/') for p in result)
    assert client.get('/api/places?state=kerala&unesco=true').json() == []
    assert len(client.get('/api/places?month=7').json()) == 14
    assert len(client.get('/api/places?month=6').json()) == 26
    assert len(client.get('/api/places?q=Kochi').json()) == 6
    assert client.get('/api/places', params={'q': "' OR 1=1 --"}).json() == []
    assert client.get('/api/places', params={'q': '%'}).json() == []
    assert client.get('/api/places', params={'q': '_'}).json() == []
    assert len(client.get('/api/places?q=Kochi').json()) == 6
    assert client.get('/api/places', params={'q': "' OR 1=1 --"}).json() == []
    assert client.get('/api/places', params={'q': '%'}).json() == []
    assert client.get('/api/places', params={'q': '_'}).json() == []


def test_month_calendar_does_not_invent_annual_dates(client):
    result = client.get('/api/festivals?month=8&district=alappuzha').json()
    assert len(result) == 3
    assert all(f['occurrences'] == [] for f in result)
    dec_festivals = client.get('/api/festivals?month=12').json()
    assert len(dec_festivals) >= 2
    assert any(f['name'] == 'Hornbill Festival' for f in dec_festivals)
    assert any(f['name'] == 'Konark Dance & Sand Art Festival' for f in dec_festivals)
    bali_yatra = client.get('/api/festivals?district=cuttack').json()
    assert any(f['name'] == 'Bali Yatra' for f in bali_yatra)
    all_festivals = client.get('/api/festivals').json()
    bali = next(f for f in all_festivals if f['name'] == 'Bali Yatra')
    assert bali['districts'] == [{'name': 'Cuttack', 'slug': 'cuttack', 'state': 'Odisha', 'state_slug': 'odisha'}]


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
        assert db.execute('SELECT COUNT(*) FROM places').fetchone()[0] == 1516
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
        db.execute('PRAGMA foreign_keys=ON')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (9999, 1)')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO place_months VALUES (1, 13)')


def test_seed_refreshes_corrected_odisha_records(tmp_path):
    path = tmp_path / 'odisha-correction.sqlite3'
    create_app(path)
    with sqlite3.connect(path) as db:
        db.execute(
            "UPDATE places SET description=? WHERE slug='ananta-basudeva-temple'",
            ('T–h–i–s– –i–s– –c–o–r–r–u–p–t–e–d',),
        )
        db.commit()

    create_app(path)

    with sqlite3.connect(path) as db:
        description = db.execute(
            "SELECT description FROM places WHERE slug='ananta-basudeva-temple'"
        ).fetchone()[0]
    assert description.startswith('Located near the sacred Bindusagar tank')
    assert '–' not in description


def test_places_reparent_by_name_when_district_ids_shift(tmp_path):
    # Karnataka's Kanakapura/Ramanagara belt sits in Bengaluru South district
    # (renamed from Ramanagara on 23 May 2025). District membership must be
    # resolved by name, because inserting one district renumbers every later
    # dynamically allocated district id in a fresh database.
    path = tmp_path / 'district-shift.sqlite3'
    create_app(path)
    with sqlite3.connect(path) as db:
        def district_of(slug):
            row = db.execute(
                'SELECT d.slug, r.slug FROM places p'
                ' JOIN districts d ON d.id = p.district_id'
                ' JOIN regions r ON r.id = d.region_id'
                " WHERE p.slug = ?", (slug,),
            ).fetchone()
            return row

        assert district_of('mekedatu') == ('bengaluru-south', 'karnataka')
        assert district_of('savandurga') == ('bengaluru-south', 'karnataka')
        assert district_of('hampi-group-of-monuments') == ('vijayanagara', 'karnataka')
        assert district_of('gokarna-and-om-beach') == ('uttara-kannada', 'karnataka')
        assert district_of('barabati-fort') == ('cuttack', 'odisha')
        assert district_of('chandipur-beach') == ('balasore', 'odisha')
        assert district_of('satkosia-gorge') == ('nayagarh', 'odisha')
        assert district_of('tawang-monastery') == ('tawang', 'arunachal-pradesh')
        assert db.execute(
            'SELECT COUNT(*) FROM places p'
            ' JOIN districts d ON d.id = p.district_id'
            ' JOIN regions r ON r.id = d.region_id'
            " WHERE r.slug = 'karnataka'"
        ).fetchone()[0] == 171
        assert db.execute(
            'SELECT COUNT(*) FROM places p JOIN districts d ON d.id = p.district_id'
            " WHERE d.slug = 'bengaluru-south'"
        ).fetchone()[0] == 5


def test_reverified_karnataka_places_land_in_correct_districts(client):
    # Entries initially held back and re-verified against district-administration
    # and reference sources: Mudgal is Raichur district (Karnataka), not Andhra.
    expected = {
        'mudgal-fort': ('raichur', 'karnataka'),
        'jhari-falls': ('chikkamagaluru', 'karnataka'),
        'kumaraswamy-temple-kraunchagiri': ('ballari', 'karnataka'),
        'kanakagiri-fort': ('koppal', 'karnataka'),
        'pavagada-fort': ('tumakuru', 'karnataka'),
        'kunduvada-lake': ('davanagere', 'karnataka'),
    }
    for slug, (district, state) in expected.items():
        place = client.get(f'/api/places/{slug}').json()
        assert place['district'].lower().replace(' ', '-') == district, slug
        assert place['state_slug'] == state, slug
        assert place['image_url'] == f'/assets/places/{slug}.' + place['image_url'].rsplit('.', 1)[1], slug
        assert_asset_exists(place['image_url'])
    karnataka_photos = {p['slug']: p['image_url'] for p in client.get('/api/places?state=karnataka').json()}
    assert sum(1 for url in karnataka_photos.values() if url.endswith(('.jpg', '.png'))) >= 164
    mudgal = client.get('/api/places/mudgal-fort').json()
    assert mudgal['state'] == 'Karnataka'
    assert 'Raichur' in mudgal['district']

    # Basavana Bagewadi (Vijayapura) and the Kalaburagi city temple are different
    # places; one record used to conflate them.
    bagewadi = client.get('/api/places/basaveshwara-temple-basavana-bagewadi').json()
    assert bagewadi['district'] == 'Vijayapura'
    assert 'Basavana Bagewadi' in bagewadi['address']
    sharana = client.get('/api/places/sharana-basaveshwara-temple').json()
    assert sharana['district'] == 'Kalaburagi'
    assert sharana['image_url'] == '/assets/places/sharana-basaveshwara-temple.jpg'
    kalaburagi = {p['slug'] for p in client.get('/api/districts/kalaburagi').json()['places']}
    assert 'sharana-basaveshwara-temple' in kalaburagi
    assert 'basaveshwara-temple-basavana-bagewadi' not in kalaburagi


def test_vercel_database_path_is_versioned(monkeypatch):
    monkeypatch.setenv('VERCEL', '1')
    app = create_app()
    response = TestClient(app).get('/healthz')
    assert response.json() == {'status': 'ok', 'places': 1516}


def test_rendering_repairs_legacy_odisha_dash_corruption(tmp_path):
    path = tmp_path / 'legacy-odisha.sqlite3'
    app = create_app(path)
    with sqlite3.connect(path) as db:
        db.execute(
            "UPDATE places SET description=? WHERE slug='ananta-basudeva-temple'",
            ('L–o–c–a–t–e–d– –n–e–a–r– –B–h–u–b–a–n–e–s–w–a–r–',),
        )
        db.commit()

    client = TestClient(app)
    assert 'L–o–c–a–t–e–d' not in client.get('/state/odisha').text
    assert client.get('/api/places/ananta-basudeva-temple').json()['description'] == 'Located near Bhubaneswar'


def test_startup_repairs_all_legacy_odisha_text_fields(tmp_path):
    path = tmp_path / 'legacy-odisha-all-fields.sqlite3'
    create_app(path)
    dash = '\u2013'
    corrupt = lambda value: dash + dash.join(value) + dash
    with sqlite3.connect(path) as db:
        db.execute("UPDATE regions SET description=? WHERE slug='odisha'", (corrupt('Temple state'),))
        db.execute(
            "UPDATE districts SET name=?, description=?, food_notes=? WHERE slug='khordha'",
            (corrupt('Khordha'), corrupt('Temple district'), corrupt('Odia food'),),
        )
        db.execute(
            '''UPDATE places SET name=?, description=?, how_to_reach=?, practical_notes=?, entry_fee=?, address=?
               WHERE slug='ananta-basudeva-temple' ''',
            (
                corrupt('Ananta'), corrupt('Sacred temple'), corrupt('Bhubaneswar'),
                corrupt('Open daily'), corrupt('No entry fee'), corrupt('Bhubaneswar'),
            ),
        )
        db.commit()

    client = TestClient(create_app(path))
    odisha = client.get('/api/states/odisha').json()
    khordha = next(district for district in odisha['districts'] if district['slug'] == 'khordha')
    place = client.get('/api/places/ananta-basudeva-temple').json()

    assert odisha['description'] == 'Temple state'
    assert khordha['name'] == 'Khordha'
    assert khordha['description'] == 'Temple district'
    assert khordha['food_notes'] == 'Odia food'
    assert place['name'] == 'Ananta Basudeva Temple'
    assert place['entry_fee'] == 'No entry fee'
    assert place['address'] == 'Bhubaneswar, Khordha'
    assert re.search(r'(?:\u2013.){3,}', client.get('/state/odisha').text) is None


def test_canonical_data_and_seeded_catalogue_validate(tmp_path):
    errors, warnings = validate_all_state_data()
    assert errors == []
    assert warnings == []
    path = tmp_path / 'quality.sqlite3'
    create_app(path)
    with sqlite3.connect(path) as db:
        db.row_factory = sqlite3.Row
        errors, warnings = validate_database(db)
    assert errors == []
    assert warnings
    report = import_report()
    assert report['errors'] == []
    state_slugs = {s['slug']: s for s in report['states']}
    assert 'odisha' in state_slugs
    assert state_slugs['odisha']['place_count'] == 83
    assert 'andhra-pradesh' in state_slugs
    assert state_slugs['andhra-pradesh']['place_count'] == 69


def test_every_state_and_union_territory_route_is_clean(client):
    for region in client.get('/api/states').json() + client.get('/api/union-territories').json():
        response = client.get(f"/api/states/{region['slug']}")
        assert response.status_code == 200
        data = response.json()
        assert data['name'] and data['description']
        assert data['districts']
        assert re.search(r'(?:\u2013.){3,}', response.text) is None
        assert all(district['name'] and district['description'] for district in data['districts'])
        assert all(
            place['name'] and place['description'] and place['source_url'].startswith('https://')
            and place['image_url'].startswith('/assets/places/')
            for place in data['places']
        )


def test_website_and_health(client):
    homepage = client.get('/').text
    assert 'india' in homepage
    assert '<title>India Explorer — Discover somewhere new</title>' in homepage
    assert '28' in homepage and '788' in homepage
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
    assert client.get('/healthz').json() == {'status': 'ok', 'places': 1516}
    assert distance({'latitude': 0, 'longitude': 0}, {'latitude': 0, 'longitude': 0}) == 0


def test_server_rendered_routes_are_crawlable(client):
    explore = client.get('/explore').text
    assert 'Find your kind of place' in explore
    assert 'class="art"' in explore
    assert 'Alappuzha Backwaters' in explore
    kerala_page = client.get('/state/kerala').text
    assert 'Kerala' in kerala_page
    assert 'state-marquee-wrap' in kerala_page
    assert 'state-marquee-item' in kerala_page
    assert 'aria-hidden="true" tabindex="-1"' in kerala_page
    assert 'back-to-top' in explore
    assert 'footer-links' in explore
    assert 'brand-emblem' in explore
    assert 'Alappuzha' in client.get('/district/alappuzha').text
    assert 'Alappuzha Beach' in client.get('/place/alappuzha-beach').text
    tirumala_page = client.get('/place/tirumala-venkateswara-temple').text
    assert 'place-gallery' in tirumala_page
    assert 'Photo 1 of 3' in tirumala_page
    assert 'Festival calendar' in client.get('/month/8').text
    assert 'Festivals in August' in client.get('/month/8').text
    assert 'Typically in August' in client.get('/district/alappuzha').text
    assert 'January, February, March, October' in client.get('/place/alappuzha-beach').text
    assert 'Saved places' in client.get('/saved').text
    area = client.get('/area').text
    assert 'Choose a state' in area
    assert 'Kerala' in area and 'Puducherry' in area
    assert '<link rel="canonical" href="https://traveling-ketch.vercel.app/explore">' in explore
    sitemap = client.get('/sitemap.xml')
    assert sitemap.status_code == 200
    assert '/state/kerala' in sitemap.text
    assert '/circuits' in sitemap.text
    assert 'Sitemap:' in client.get('/robots.txt').text
    assert 'data-server-rendered="true"' in explore
    festivals_page = client.get('/festivals').text
    assert 'Celebrations across India' in festivals_page
    assert 'month-selector-tabs' in festivals_page
    circuits_page = client.get('/circuits').text
    assert 'Curated travel trails' in circuits_page
    assert 'The Golden Triangle' in circuits_page
    gt_page = client.get('/circuit/golden-triangle').text
    assert 'Stop 1' in gt_page
    assert 'Qutb Minar' in gt_page
    assert 'Taj Mahal' in gt_page
    assert 'Amber Fort' in gt_page
    kashmir_page = client.get('/circuit/paradise-kashmir-trail').text
    assert 'Dal Lake' in kashmir_page
    assert 'Gulmarg' in kashmir_page
    island_page = client.get('/circuit/tropical-island-corals').text
    assert 'Cellular Jail' in island_page
    assert 'Radhanagar Beach' in island_page
    puducherry_page = client.get('/circuit/french-coastal-puducherry').text
    assert 'White Town' in puducherry_page
    assert 'Paradise Beach' in puducherry_page
    chd_page = client.get('/circuit/chandigarh-modernist-trail').text
    assert 'Le Corbusier' in chd_page
    assert 'Nek Chand' in chd_page
    odisha_trail = client.get('/circuit/tribal-odisha-waterfalls').text
    assert 'Deomali' in odisha_trail
    assert 'Duduma' in odisha_trail


def test_traveler_profile_shell_is_present_on_every_page(client):
    for path in ('/', '/explore', '/saved', '/festivals', '/no-such-page'):
        html = client.get(path).text
        assert 'id="profile-toggle"' in html, path
        assert 'aria-controls="profile-drawer"' in html, path
        assert 'id="profile-drawer"' in html, path
        assert 'id="profile-form"' in html, path
        assert 'Saved on this device' in html, path
    home = client.get('/').text
    assert 'No account needed' in home
    assert 'aria-expanded="false"' in home


def test_profile_upgrades_have_shells_and_accessible_drawer(client):
    home = client.get('/').text
    # Personalised row the client fills from /api/places once interests exist.
    assert 'id="personalised-section"' in home
    assert 'id="personalised-cards"' in home
    assert 'id="personalised-heading"' in home
    # Avatar picker: presets plus an upload that is downscaled in the browser.
    assert 'id="profile-avatar-options"' in home
    assert 'id="profile-avatar-upload"' in home
    assert 'accept="image/*"' in home
    # Collections with a create form and list.
    assert 'id="collection-form"' in home
    assert 'id="collection-name"' in home
    assert 'id="profile-collection-list"' in home
    # Drawer behaves like a modal dialog and can receive focus itself.
    assert 'role="dialog" aria-modal="true"' in home
    assert 'id="profile-drawer"' in home and 'tabindex="-1"' in home


def test_saved_page_accepts_shared_collection_query(client):
    response = client.get('/saved?places=alappuzha-beach,taj-mahal&name=Kerala%20and%20Agra')
    assert response.status_code == 200
    assert 'id="profile-drawer"' in response.text
    assert 'noindex' in response.text


def test_nagaland_directory_lists_all_17_districts(client):
    expected = {
        'Chumoukedima', 'Dimapur', 'Kiphire', 'Kohima', 'Longleng', 'Meluri',
        'Mokokchung', 'Mon', 'Niuland', 'Noklak', 'Peren', 'Phek', 'Shamator',
        'Tseminyu', 'Tuensang', 'Wokha', 'Zunheboto',
    }
    nagaland = client.get('/api/states/nagaland').json()
    names = {district['name'] for district in nagaland['districts']}
    assert names == expected
    assert len(nagaland['districts']) == 17
    state_page = client.get('/state/nagaland').text
    assert '17' in state_page
    assert 'Meluri' in state_page
    meluri = client.get('/district/meluri')
    assert meluri.status_code == 200
    assert 'Meluri' in meluri.text


def test_nagaland_festival_calendar(client):
    festivals = {festival['name']: festival for festival in client.get('/api/festivals').json()}
    expected_months = {
        'Sekrenyi': 2, 'Tsükhenyie': 4, 'Moatsü': 5, 'Tuluni': 7,
        'Mungmung': 9, 'Tsokum': 10, 'Yemshe': 10, 'Ngada': 11, 'Hornbill Festival': 12,
    }
    for name, month in expected_months.items():
        assert name in festivals, name
        assert month in festivals[name]['months'], name
    sekrenyi = festivals['Sekrenyi']
    assert any(d['slug'] == 'kohima' for d in sekrenyi['districts'])
    yemshe = festivals['Yemshe']
    assert any(d['slug'] == 'meluri' for d in yemshe['districts'])
    october = {f['name'] for f in client.get('/api/festivals?month=10').json()}
    assert {'Yemshe', 'Tsokum', 'Tsonglaknyi'}.issubset(october)
    haryana_festivals = [
        f for f in festivals.values()
        if any(d['state_slug'] == 'haryana' for d in f['districts'])
    ]
    assert len(haryana_festivals) == 21
    assert 'Surajkund International Crafts Mela' in festivals
    assert 'Kurukshetra Mahotsav and Gita Jayanti' in festivals
    bihar_festivals = [
        f for f in festivals.values()
        if any(d['state_slug'] == 'bihar' for d in f['districts'])
    ]
    assert len(bihar_festivals) == 11
    assert 'Chhath Puja (Bihar)' in festivals
    assert 'Mahabodhi Temple' not in festivals
    assam_festivals = [
        f for f in festivals.values()
        if any(d['state_slug'] == 'assam' for d in f['districts'])
    ]
    assert len(assam_festivals) == 10
    assert 'Rongali Bihu' in festivals
    assert 'Ambubachi Mela' in festivals
    maharashtra_festivals = [
        f for f in festivals.values()
        if any(d['state_slug'] == 'maharashtra' for d in f['districts'])
    ]
    assert len(maharashtra_festivals) == 11
    assert 'Ganesh Chaturthi (Maharashtra)' in festivals
    assert 'Gudi Padwa' in festivals
    kerala_festivals = [
        f for f in festivals.values()
        if any(d['state_slug'] == 'kerala' for d in f['districts'])
    ]
    assert len(kerala_festivals) == 12
    assert 'Onam' in festivals
    assert 'Thrissur Pooram' in festivals
    kerala_festivals = [
        f for f in festivals.values()
        if any(d['state_slug'] == 'kerala' for d in f['districts'])
    ]
    assert len(kerala_festivals) == 12
    assert 'Onam' in festivals
    assert 'Thrissur Pooram' in festivals
    nagaland_festivals = [
        f for f in festivals.values()
        if any(d['state_slug'] == 'nagaland' for d in f['districts'])
    ]
    assert len(nagaland_festivals) == 22


def test_editorial_status(client):
    assert client.get('/api/editorial-status').json() == {
        'detailed_places': 1516,
        'reviewed_places': 0,
        'unreviewed_places': 1516,
        'confirmed_festival_dates': 0,
    }


def test_audit_fixes_and_structured_data(client):
    stadium = client.get('/api/places/birsa-munda-international-hockey-stadium').json()
    assert stadium['category'] == 'landmark'
    assert 'beach' not in stadium['category'].lower()

    astaranga = client.get('/api/places/astaranga-beach').json()
    assert 'Puri Beach' not in astaranga['description']
    assert 'twilight' in astaranga['description'].lower() or 'sunset' in astaranga['description'].lower()

    odisha = client.get('/api/states/odisha').json()
    district_names = {d['name']: d['slug'] for d in odisha['districts']}
    assert 'Cuttack' in district_names and district_names['Cuttack'] == 'cuttack'
    assert 'Angul' in district_names and district_names['Angul'] == 'angul'
    assert 'Bargarh' in district_names and district_names['Bargarh'] == 'bargarh'
    assert 'Kandhamal' in district_names and district_names['Kandhamal'] == 'kandhamal'
    assert 'Balasore' in district_names and district_names['Balasore'] == 'balasore'
    assert 'Sundargarh' in district_names and district_names['Sundargarh'] == 'sundargarh'
    assert 'Kataka' not in district_names
    assert 'Anugola' not in district_names

    home = client.get('/').text
    assert 'application/ld+json' in home
    assert '"@type": "WebSite"' in home
    assert 'SearchAction' in home
    assert '<meta property="og:image"' in home
    assert '<title>India Explorer — Discover somewhere new</title>' in home
    assert 'recent-places-section" hidden' in home
    assert 'Incredible India' not in home

    amber = client.get('/place/amber-fort').text
    assert 'application/ld+json' in amber
    assert '"@type": "TouristAttraction"' in amber
    assert '"@type": "BreadcrumbList"' in amber
    assert 'og:image' in amber

    district = client.get('/district/cuttack').text
    assert 'og:image' in district

    trails = client.get('/circuits').text
    assert 'og:image' in trails

    char_dham = client.get('/circuit/sacred-char-dham-shakti-peethas').text
    assert '10–12 Days · Allow a flight and recovery day between regions' in char_dham

    circuit = client.get('/circuit/golden-triangle').text
    assert 'Suggested Transport' in circuit
    assert 'Estimated Trip Budget' in circuit
    assert 'circuit-leaflet-map' in circuit
    assert '"@type": "TouristTrip"' in circuit

    area = client.get('/area').text
    assert 'state-sort-select' in area
    assert 'destinations covered' in area
    assert 'og:image' in area

    festivals = client.get('/festivals').text
    assert festivals.index('>January<') < festivals.index('>February<') < festivals.index('>March<')
    assert 'Traditional Celebration' not in festivals
    assert 'Pan-India' not in festivals

    all_festivals = client.get('/api/festivals').json()
    festival_names = [f['name'] for f in all_festivals]
    assert len(festival_names) == len(set(festival_names)), 'Duplicate festival names in API'
    assert len(all_festivals) == 151
    karnataka = client.get('/').text
    assert 'href="/state/karnataka"' in karnataka

    # Verify JSON-LD does not emit unescaped closing script tags
    assert '</script>' not in home.split('<script type="application/ld+json">')[1].split('</script>')[0]


def test_every_place_image_resolves_to_a_real_file(client):
    """Guard against image URLs pointing at artwork that was never written, or left behind after a photo swap."""
    problems = []
    for place in client.get('/api/places').json():
        url = place['image_url']
        if not url.startswith('/assets/places/'):
            problems.append(f"{place['slug']}: bad prefix {url}")
            continue
        target = ASSETS / url.lstrip('/')
        if not target.exists():
            problems.append(f"{place['slug']}: missing {url}")
            continue
        if target.stat().st_size == 0:
            problems.append(f"{place['slug']}: empty asset {url}")
            continue
        if url.endswith(('.jpg', '.png')) and target.stat().st_size < 3000:
            problems.append(f"{place['slug']}: suspiciously small raster asset {url}")
    assert not problems, "image asset problems:\n" + "\n".join(problems[:25])


def test_karnataka_and_arunachal_use_real_photographs(client):
    """The catalogue standard is Commons-sourced photographs with attribution; vector art needs an explicit note."""
    sources = json.loads((ASSETS / 'assets' / 'places' / 'sources.json').read_text(encoding='utf-8'))
    photo_slugs, vector_slugs = [], []
    for place in client.get('/api/places').json():
        if place['state_slug'] not in ('karnataka', 'arunachal-pradesh'):
            continue
        src = sources.get(place['slug'])
        assert src, f"{place['slug']} has no attribution record"
        if place['image_url'].endswith('.svg'):
            vector_slugs.append(place['slug'])
            assert 'vector' in src['file'].lower(), f"{place['slug']} artwork record must be labelled"
            continue
        photo_slugs.append(place['slug'])
        assert 'commons.wikimedia.org' in src['source_page'], f"{place['slug']} missing Commons source page"
        assert src['download_url'].startswith('https://'), f"{place['slug']} missing download url"
        assert 'vector' not in src['file'].lower(), f"{place['slug']} still labelled artwork"
    assert len(vector_slugs) <= 8, f"too many places still without a photo: {sorted(vector_slugs)}"
    assert len(photo_slugs) >= 170, f"expected near-complete photographic coverage, got {len(photo_slugs)}"
