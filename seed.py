"""Editorial pilot data and a growing India region/district directory.

The records are intentionally marked as needs_review. Place cards use local,
destination-specific photographs sourced from Wikimedia Commons and Unsplash.
Each state features its most iconic landmark photograph.
"""

import json
from pathlib import Path

STATE_COVER_IMAGES = {
    'odisha': 'https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=1200&q=82',
    'kerala': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=82',
    'rajasthan': 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=1200&q=82',
    'goa': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=82',
    'himachal-pradesh': 'https://images.unsplash.com/photo-1722915767859-08a59870d70b?auto=format&fit=crop&w=1200&q=82',
    'tamil-nadu': 'https://images.unsplash.com/photo-1563715493579-e0b3e0493b60?auto=format&fit=crop&w=1200&q=82',
    'andhra-pradesh': 'https://images.unsplash.com/photo-1733805569204-41768c7d8c0f?auto=format&fit=crop&w=1200&q=82',
    'karnataka': 'https://images.unsplash.com/photo-1722934804353-0d9f6a55ab5e?auto=format&fit=crop&w=1200&q=82',
    'uttar-pradesh': 'https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=82',
    'west-bengal': 'https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=82',
    'uttarakhand': 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=82',
    'maharashtra': 'https://images.unsplash.com/photo-1524498250077-390f9e378fc0?auto=format&fit=crop&w=1200&q=82',
    'delhi': 'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=82',
    'jammu-and-kashmir': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=82',
    'ladakh': 'https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1200&q=82',
    'punjab': 'https://images.unsplash.com/photo-1514222134-b57cbb8ce073?auto=format&fit=crop&w=1200&q=82',
    'gujarat': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=82',
    'assam': 'https://images.unsplash.com/photo-1571536802807-30451e3955d8?auto=format&fit=crop&w=1200&q=82',
    'bihar': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=82',
    'chhattisgarh': 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1200&q=82',
    'haryana': 'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=82',
    'jharkhand': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=82',
    'madhya-pradesh': 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?auto=format&fit=crop&w=1200&q=82',
    'manipur': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=82',
    'meghalaya': 'https://images.unsplash.com/photo-1497250681960-ef046c08a56e?auto=format&fit=crop&w=1200&q=82',
    'mizoram': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=82',
    'nagaland': 'https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?auto=format&fit=crop&w=1200&q=82',
    'sikkim': 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=1200&q=82',
    'telangana': 'https://images.unsplash.com/photo-1501854140801-50d01698950b?auto=format&fit=crop&w=1200&q=82',
    'tripura': 'https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=1200&q=82',
    'arunachal-pradesh': 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=82',
    'andaman-and-nicobar-islands': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=82',
    'chandigarh': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=82',
    'dadra-and-nagar-haveli-and-daman-and-diu': 'https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=82',
    'lakshadweep': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1200&q=82',
    'puducherry': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=82',
}

STATE_COVER_IMAGE = '/assets/state-cover.svg'

PLACE_IMAGE_PATHS = {
    'fort-kochi': '/assets/places/fort-kochi.jpg',
    'mattancherry-palace': '/assets/places/mattancherry-palace.jpg',
    'alappuzha-backwaters': '/assets/places/alappuzha-backwaters.jpg',
    'alappuzha-beach': '/assets/places/alappuzha-beach.jpg',
    'amber-fort': '/assets/places/amber-fort.jpg',
    'jantar-mantar': '/assets/places/jantar-mantar.jpg',
    'jaisalmer-fort': '/assets/places/jaisalmer-fort.jpg',
    'gadisar-lake': '/assets/places/gadisar-lake.jpg',
    'basilica-bom-jesus': '/assets/places/basilica-bom-jesus.jpg',
    'fontainhas': '/assets/places/fontainhas.jpg',
    'palolem-beach': '/assets/places/palolem-beach.jpg',
    'dudhsagar-falls': '/assets/places/dudhsagar-falls.jpg',
    'shimla-ridge': '/assets/places/shimla-ridge.jpg',
    'jakhu-temple': '/assets/places/jakhu-temple.jpg',
    'dharamshala': '/assets/places/dharamshala.jpg',
    'masroor-temple': '/assets/places/masroor-temple.jpg',
    'marina-beach': '/assets/places/marina-beach.jpg',
    'kapaleeshwarar-temple': '/assets/places/kapaleeshwarar-temple.jpg',
    'meenakshi-temple': '/assets/places/meenakshi-temple.jpg',
    'thirumalai-nayak-palace': '/assets/places/thirumalai-nayak-palace.jpg',
    'konark-sun-temple': '/assets/places/konark-sun-temple.jpg',
    'puri-jagannath-temple': '/assets/places/puri-jagannath-temple.jpg',
    'chilika-lake': '/assets/places/chilika-lake.jpg',
    'lingaraj-temple': '/assets/places/lingaraj-temple.jpg',
}


def state_image(slug, filename=None):
    return STATE_COVER_IMAGES.get(slug) or STATE_COVER_IMAGE


def place_image(slug):
    return PLACE_IMAGE_PATHS.get(slug, f'/assets/places/{slug}.jpg')


def seed(db):
    regions = [
        (1, 'Kerala', 'kerala', 'state', 'Backwaters, coastal neighbourhoods and living traditions along the Malabar coast.', 'https://www.keralatourism.org/', state_image('kerala')),
        (2, 'Rajasthan', 'rajasthan', 'state', 'Explore desert landscapes, historic cities, forts and colourful local celebrations.', 'https://www.tourism.rajasthan.gov.in/', state_image('rajasthan')),
        (3, 'Goa', 'goa', 'state', 'A small coastal state of beaches, old quarters, churches, spice-growing landscapes and seasonal celebrations.', 'https://www.goa-tourism.com/', state_image('goa')),
        (4, 'Himachal Pradesh', 'himachal-pradesh', 'state', 'Mountain towns, valleys, monasteries and slower journeys across the western Himalaya.', 'https://himachaltourism.gov.in/', state_image('himachal-pradesh')),
        (5, 'Tamil Nadu', 'tamil-nadu', 'state', 'Temple cities, coastal neighbourhoods, classical traditions and a deep food culture.', 'https://www.tamilnadutourism.com/', state_image('tamil-nadu')),
        (6, 'Andhra Pradesh', 'andhra-pradesh', 'state', 'Coastal landscapes, historic cities, temples and a rich food culture.', 'https://tourism.ap.gov.in/', state_image('andhra-pradesh')),
        (7, 'Arunachal Pradesh', 'arunachal-pradesh', 'state', 'Mountain valleys, monasteries and living traditions in India’s eastern Himalaya.', 'https://arunachaltourism.com/', state_image('arunachal-pradesh')),
        (8, 'Assam', 'assam', 'state', 'River landscapes, tea country, wildlife and distinctive cultural traditions.', 'https://tourism.assam.gov.in/', state_image('assam')),
        (9, 'Bihar', 'bihar', 'state', 'Ancient learning centres, Buddhist heritage and river plains.', 'https://tourism.bihar.gov.in/', state_image('bihar')),
        (10, 'Chhattisgarh', 'chhattisgarh', 'state', 'Forests, waterfalls, tribal arts and archaeological landscapes.', 'https://tourism.cgstate.gov.in/', state_image('chhattisgarh')),
        (11, 'Gujarat', 'gujarat', 'state', 'Craft traditions, historic cities, coastlines and wildlife landscapes.', 'https://www.gujarattourism.com/', state_image('gujarat')),
        (12, 'Haryana', 'haryana', 'state', 'Historic pilgrimage routes, wetlands and a landscape close to Delhi.', 'https://haryanatourism.gov.in/', state_image('haryana')),
        (13, 'Jharkhand', 'jharkhand', 'state', 'Waterfalls, forests, plateau landscapes and living cultural traditions.', 'https://tourism.jharkhand.gov.in/', state_image('jharkhand')),
        (14, 'Karnataka', 'karnataka', 'state', 'Heritage cities, coffee country, coastlines and diverse landscapes.', 'https://karnatakatourism.org/', state_image('karnataka')),
        (15, 'Madhya Pradesh', 'madhya-pradesh', 'state', 'Wildlife, historic cities, temples and central Indian heritage.', 'https://www.mptourism.com/', state_image('madhya-pradesh')),
        (16, 'Maharashtra', 'maharashtra', 'state', 'Urban culture, hill stations, forts, caves and a long western coastline.', 'https://aai-portal.maharashtratourism.gov.in/', state_image('maharashtra')),
        (17, 'Manipur', 'manipur', 'state', 'Hills, lakes, handloom traditions and distinctive performing arts.', 'https://manipurtourism.gov.in/', state_image('manipur')),
        (18, 'Meghalaya', 'meghalaya', 'state', 'Living root bridges, waterfalls, caves and highland villages.', 'https://www.meghalayatourism.in/', state_image('meghalaya')),
        (19, 'Mizoram', 'mizoram', 'state', 'Hills, bamboo craft, community traditions and scenic roads.', 'https://tourism.mizoram.gov.in/', state_image('mizoram')),
        (20, 'Nagaland', 'nagaland', 'state', 'Hill communities, craft traditions and seasonal cultural gatherings.', 'https://tourism.nagaland.gov.in/', state_image('nagaland')),
        (21, 'Odisha', 'odisha', 'state', 'Land of temples, classical Odissi dance, tribal crafts, coastal wetlands and one of the world\'s largest annual pilgrimages at Puri.', 'https://odishatourism.gov.in/', state_image('odisha')),
        (22, 'Punjab', 'punjab', 'state', 'Living Sikh heritage, farms, food traditions and historic cities.', 'https://punjabtourism.punjab.gov.in/', state_image('punjab')),
        (23, 'Sikkim', 'sikkim', 'state', 'Mountain monasteries, high valleys and carefully paced journeys.', 'https://www.sikkimtourism.gov.in/', state_image('sikkim')),
        (24, 'Telangana', 'telangana', 'state', 'Deccan history, food, lakes and the layered city of Hyderabad.', 'https://tourism.telangana.gov.in/', state_image('telangana')),
        (25, 'Tripura', 'tripura', 'state', 'Palaces, lakes, forests and a meeting of regional traditions.', 'https://tripuratourism.gov.in/', state_image('tripura')),
        (26, 'Uttar Pradesh', 'uttar-pradesh', 'state', 'Sacred rivers, Mughal heritage, craft cities and living pilgrimage routes.', 'https://www.uptourism.gov.in/', state_image('uttar-pradesh')),
        (27, 'Uttarakhand', 'uttarakhand', 'state', 'Himalayan towns, pilgrimage routes, forests and alpine landscapes.', 'https://uttarakhandtourism.gov.in/', state_image('uttarakhand')),
        (28, 'West Bengal', 'west-bengal', 'state', 'River deltas, cultural cities, tea hills and coastal landscapes.', 'https://wbtourism.gov.in/', state_image('west-bengal')),
        (29, 'Andaman and Nicobar Islands', 'andaman-and-nicobar-islands', 'union_territory', 'Island landscapes, marine life and coastal histories in the Bay of Bengal.', 'https://www.andamantourism.gov.in/', state_image('andaman-and-nicobar-islands')),
        (30, 'Chandigarh', 'chandigarh', 'union_territory', 'A planned city known for modernist architecture, gardens and civic spaces.', 'https://chandigarhtourism.gov.in/', state_image('chandigarh')),
        (31, 'Dadra and Nagar Haveli and Daman and Diu', 'dadra-and-nagar-haveli-and-daman-and-diu', 'union_territory', 'Coastal forts, beaches, forested interiors and local craft traditions.', 'https://dnhddtourism.in/', state_image('dadra-and-nagar-haveli-and-daman-and-diu')),
        (32, 'Delhi', 'delhi', 'union_territory', 'A historic capital layered with empires, markets, museums and neighbourhood food.', 'https://delhitourism.gov.in/', state_image('delhi')),
        (33, 'Jammu and Kashmir', 'jammu-and-kashmir', 'union_territory', 'Mountain valleys, lakes, gardens and living craft traditions.', 'https://jammutourism.jk.gov.in/', state_image('jammu-and-kashmir')),
        (34, 'Ladakh', 'ladakh', 'union_territory', 'High-altitude landscapes, monasteries and journeys shaped by mountain weather.', 'https://ladakh.gov.in/tourism/', state_image('ladakh')),
        (35, 'Lakshadweep', 'lakshadweep', 'union_territory', 'Coral islands, lagoons and carefully managed coastal experiences.', 'https://lakshadweep.gov.in/tourism/', state_image('lakshadweep')),
        (36, 'Puducherry', 'puducherry', 'union_territory', 'A coastal union territory with Tamil heritage, French-era streets and beaches.', 'https://tourism.py.gov.in/', state_image('puducherry')),
    ]
    db.executemany('''INSERT OR IGNORE INTO regions
        (id,name,slug,kind,description,source_url,cover_image_url) VALUES (?,?,?,?,?,?,?)''', regions)
    db.executemany('UPDATE regions SET cover_image_url=?, source_url=? WHERE id=?', [(r[6], r[5], r[0]) for r in regions])

    districts = [
        (1, 1, 'Ernakulam', 'ernakulam', 'A starting point for Kochi’s maritime heritage and coastal communities.', 'Try puttu with kadala curry and Kerala-style meals.', 'https://ernakulam.nic.in/'),
        (2, 1, 'Alappuzha', 'alappuzha', 'Slow down beside canals, backwaters and the Arabian Sea.', 'Look for appam, vegetable stew and local rice dishes.', 'https://alappuzha.nic.in/'),
        (3, 2, 'Jaipur', 'jaipur', 'Discover the Pink City’s architecture, observatory and nearby hill forts.', 'Try dal baati churma, ghewar and regional thalis.', 'https://www.tourism.rajasthan.gov.in/jaipur.html'),
        (4, 2, 'Jaisalmer', 'jaisalmer', 'A living sandstone fort city at the edge of the Thar Desert.', 'Try ker sangri, bajra roti and local sweets.', 'https://www.tourism.rajasthan.gov.in/jaisalmer.html'),
        (5, 3, 'North Goa', 'north-goa', 'A lively mix of old quarters, beaches, markets and historic churches.', 'Try fish curry rice, bebinca and local bakery snacks.', 'https://www.goa-tourism.com/'),
        (6, 3, 'South Goa', 'south-goa', 'Quieter beaches, forested interiors and heritage villages.', 'Look for local poi bread, seafood and coconut-based dishes.', 'https://www.goa-tourism.com/'),
        (7, 4, 'Shimla', 'shimla', 'A historic hill town with walking streets, colonial-era buildings and mountain views.', 'Try Himachali dham and local siddu where available.', 'https://himachaltourism.gov.in/destination/shimla/'),
        (8, 4, 'Kangra', 'kangra', 'A valley landscape of temples, tea gardens and views toward the Dhauladhar range.', 'Try dham-style meals and Kangra tea.', 'https://himachaltourism.gov.in/'),
        (9, 5, 'Chennai', 'chennai', 'A coastal city of music, temples, food and neighbourhood histories.', 'Try idli, dosa, filter coffee and seasonal local dishes.', 'https://www.tamilnadutourism.com/'),
        (10, 5, 'Madurai', 'madurai', 'A temple city shaped by ritual, markets, architecture and long food traditions.', 'Try jigarthanda, parotta and a Madurai-style meal.', 'https://www.tamilnadutourism.com/'),
        (11, 14, 'Bengaluru Urban', 'bengaluru-urban', 'A city district where technology, public parks, food and layered neighbourhoods meet.', 'Try local darshini breakfasts, filter coffee and regional meals.', 'https://karnatakatourism.org/'),
        (12, 14, 'Mysuru', 'mysuru', 'A palace city with markets, gardens and a strong cultural calendar.', 'Try Mysuru pak, dosas and local Karnataka meals.', 'https://karnatakatourism.org/'),
        (13, 16, 'Mumbai', 'mumbai', 'A dense island-city district of waterfronts, markets, food and historic architecture. The city blends Koli fishing traditions, Victorian gothic buildings, art deco boulevards and Irani café culture.', 'Try vada pav, coastal seafood and Irani café traditions.', 'https://aai-portal.maharashtratourism.gov.in/'),
        (14, 16, 'Pune', 'pune', 'A cultural and educational city with forts and food traditions nearby.', 'Try misal, bhakri and seasonal Maharashtrian dishes.', 'https://aai-portal.maharashtratourism.gov.in/'),
        (15, 26, 'Agra', 'agra', 'A historic city shaped by Mughal architecture, river landscapes and craft markets.', 'Try petha, Mughlai dishes and local street food.', 'https://www.uptourism.gov.in/'),
        (16, 26, 'Varanasi', 'varanasi', 'A river city of ghats, music, craft and pilgrimage traditions.', 'Try kachori-sabzi, local sweets and seasonal drinks.', 'https://www.uptourism.gov.in/'),
        (17, 28, 'Kolkata', 'kolkata', 'A cultural capital of books, theatre, colonial-era streets and Bengali food.', 'Try mishti doi, fish preparations and Kolkata street food.', 'https://wbtourism.gov.in/'),
        (18, 28, 'Darjeeling', 'darjeeling', 'A hill town of tea gardens, mountain views and railway heritage.', 'Try Darjeeling tea, momos and local bakery cafés.', 'https://wbtourism.gov.in/'),
        (19, 27, 'Dehradun', 'dehradun', 'A valley city connecting the foothills, institutions and routes toward the hills.', 'Try local bakery treats, garhwali dishes and seasonal fruits.', 'https://uttarakhandtourism.gov.in/'),
        (20, 27, 'Nainital', 'nainital', 'A lakeside town framed by forested ridges and mountain views.', 'Try bal mithai, ras and kumaoni food in town markets.', 'https://uttarakhandtourism.gov.in/'),
        (21, 32, 'New Delhi', 'new-delhi', 'The ceremonial and institutional capital, home to museums, gardens, street life and monument complexes.', 'Try chaat, Mughlai dishes, parathas and regional cooking from across the country.', 'https://delhitourism.gov.in/'),
        (22, 33, 'Srinagar', 'srinagar', 'A city shaped by Dal Lake, Mughal gardens, wooden architecture and living craft traditions.', 'Try wazwan, kahwa and local bakery breads.', 'https://jammutourism.jk.gov.in/'),
        (23, 33, 'Jammu', 'jammu', 'The winter hub and city of temples set beside the Tawi river, connecting the plains with the Pir Panjal range.', 'Try rajma chawal, kaladi cheese and local sweets.', 'https://jammutourism.jk.gov.in/'),
        (24, 34, 'Leh', 'leh', 'A high-altitude town and base for monastery, valley and mountain journeys. Leh sits at 3500 m and is the gateway to Pangong Lake, Nubra Valley and the Khardung La pass.', 'Try skyu, thukpa and locally grown apricots in season.', 'https://ladakh.gov.in/tourism/'),
        (25, 36, 'Puducherry', 'puducherry-district', 'A coastal town with French-era streetscapes, Tamil quarters, beaches and quiet courtyards.', 'Try French-influenced bakery items, coastal seafood and south Indian filter coffee.', 'https://tourism.py.gov.in/'),
        (26, 30, 'Chandigarh', 'chandigarh-district', 'A union territory and planned city of gardens, architecture and public art.', 'Try Punjabi and North Indian food across the city\'s sectors.', 'https://chandigarhtourism.gov.in/'),
        (27, 21, 'Puri', 'puri', 'Home to the sacred Shree Jagannath Temple, the ancient Sun Temple at nearby Konark, and sweeping Bay of Bengal beaches. One of India’s four holy Char Dham pilgrimage sites, famous worldwide for the grand Rath Yatra.', 'Taste Mahaprasad from the Jagannath Temple’s Anand Bazar (dalma, kanika rice, besara), crisp Puri khaja, rasabali, and fresh coastal seafood.', 'https://odishatourism.gov.in/content/tourism/en/discover/districts/puri.html'),
        (28, 21, 'Khordha', 'khordha', 'Encompassing Bhubaneswar—the City of Temples—with over 500 historic shrines including Lingaraj and Mukteshwar, alongside the ancient rock-cut caves of Udayagiri & Khandagiri and Ashoka’s edicts at Dhauli Hill.', 'Savour authentic Odia cuisine: dalma, pakhala bhata with badi chura, chhena poda (baked cheese cake), rasagola, and street delicacies.', 'https://odishatourism.gov.in/content/tourism/en/discover/districts/khurdha.html'),
    ]
    db.executemany('''INSERT OR IGNORE INTO districts
        (id,region_id,name,slug,description,food_notes,source_url) VALUES (?,?,?,?,?,?,?)''', districts)

    source_file = Path(__file__).with_name('data') / 'india-states-districts.json'
    if source_file.exists():
        existing_slugs = {row[0] for row in db.execute('SELECT slug FROM districts')}
        existing_names = {(row[0], row[1].lower()) for row in db.execute('SELECT region_id, name FROM districts')}
        next_id = db.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM districts').fetchone()[0]
        region_sources = {row[0]: row[1] for row in db.execute('SELECT id, source_url FROM regions')}
        official_directory = json.loads(source_file.read_text(encoding='utf-8'))
        region_ids = {row[0].lower(): row[1] for row in db.execute('SELECT name, id FROM regions')}
        region_slugs = {row[0]: row[1] for row in db.execute('SELECT id, slug FROM regions')}
        for entry in official_directory:
            region_id = region_ids.get(entry.get('state', '').lower())
            if not region_id:
                continue
            for name in entry.get('districts', []):
                slug = name.lower().replace(' & ', '-').replace('&', '-').replace(' ', '-').replace("'", '')
                if (region_id, name.lower()) in existing_names:
                    continue
                if slug in existing_slugs:
                    slug = f'{region_slugs[region_id]}-{slug}'
                db.execute('''INSERT INTO districts
                    (id, region_id, name, slug, description, food_notes, source_url)
                    VALUES (?,?,?,?,?,?,?)''', (next_id, region_id, name, slug,
                    f'{name} district directory entry. Destination coverage is being expanded and reviewed.',
                    'Local food notes will be added with verified editorial sources.', region_sources[region_id]))
                existing_slugs.add(slug)
                existing_names.add((region_id, name.lower()))
                next_id += 1

    heritage = [
        (1, 'Hill Forts of Rajasthan', 'https://whc.unesco.org/en/list/247/'),
        (2, 'The Jantar Mantar, Jaipur', 'https://whc.unesco.org/en/list/1338/'),
        (3, 'Churches and Convents of Goa', 'https://whc.unesco.org/en/list/234/'),
        (4, 'Sun Temple, Konârak', 'https://whc.unesco.org/en/list/246/'),
    ]
    db.executemany('INSERT OR IGNORE INTO heritage_sites VALUES (?,?,?)', heritage)

    places = [
        (1, 1, 'fort-kochi', 'Fort Kochi', 'Walk through a coastal neighbourhood shaped by maritime trade, historic streets and public waterfront spaces.', 'culture', 9.9658, 76.2421, 'Reach Kochi by rail or air, then continue by local bus, taxi or ferry where available.', 'This is a neighbourhood, not a single ticketed attraction. Check individual venues separately.', None, 'https://www.keralatourism.org/', place_image('fort-kochi')),
        (2, 1, 'mattancherry-palace', 'Mattancherry Palace', 'Discover Kerala murals and the history of Kochi’s royal household.', 'heritage', 9.9583, 76.2594, 'Continue from central Kochi to Mattancherry by local transport.', 'Museum opening days and ticket rates should be checked before visiting.', None, 'https://www.keralatourism.org/', place_image('mattancherry-palace')),
        (3, 2, 'alappuzha-backwaters', 'Alappuzha Backwaters', 'Explore the canals and waterways around Alappuzha with a locally operated boat trip.', 'nature', 9.5010, 76.3500, 'Alappuzha railway station connects to the town; boat departure points vary by operator.', 'Coordinate is an approximate town-area starting point. Agree on route and price before booking.', None, 'https://www.keralatourism.org/', place_image('alappuzha-backwaters')),
        (4, 2, 'alappuzha-beach', 'Alappuzha Beach', 'Spend an evening on the coast near Alappuzha town.', 'beach', 9.4929, 76.3177, 'Take local transport from Alappuzha town or railway station.', 'Follow local swimming restrictions and sea-condition advice.', None, 'https://www.keralatourism.org/', place_image('alappuzha-beach')),
        (5, 3, 'amber-fort', 'Amber Fort', 'Explore courtyards, gateways and hilltop architecture at a component of the Hill Forts of Rajasthan World Heritage property.', 'heritage', 26.9855, 75.8513, 'Travel from Jaipur to Amer by bus or taxi.', 'Allow time for walking and steps; check current tickets and opening hours.', 1, 'https://www.tourism.rajasthan.gov.in/jaipur.html', place_image('amber-fort')),
        (6, 3, 'jantar-mantar', 'Jantar Mantar, Jaipur', 'Explore monumental astronomical instruments at this UNESCO World Heritage Site.', 'heritage', 26.9248, 75.8246, 'Located in Jaipur’s old city near City Palace.', 'A guide can help explain the instruments. Confirm current entry arrangements.', 2, 'https://whc.unesco.org/en/list/1338/', place_image('jantar-mantar')),
        (7, 4, 'jaisalmer-fort', 'Jaisalmer Fort', 'Walk through a living sandstone fort that forms part of the Hill Forts of Rajasthan World Heritage property.', 'heritage', 26.9124, 70.9120, 'Reach Jaisalmer by rail or road, then continue to the old town.', 'Respect residents and check entry rules for individual monuments.', 1, 'https://www.tourism.rajasthan.gov.in/jaisalmer.html', place_image('jaisalmer-fort')),
        (8, 4, 'gadisar-lake', 'Gadisar Lake', 'Visit a historic water body framed by gateways and small shrines near Jaisalmer.', 'nature', 26.9083, 70.9232, 'A short local journey from Jaisalmer’s old town.', 'Visit early or late in the day; boat services depend on local conditions.', None, 'https://www.tourism.rajasthan.gov.in/jaisalmer.html', place_image('gadisar-lake')),
        (9, 5, 'basilica-bom-jesus', 'Basilica of Bom Jesus', 'Visit the historic basilica in Old Goa, part of the Churches and Convents of Goa World Heritage property.', 'heritage', 15.5009, 73.9116, 'Reach Old Goa from Panaji by bus, taxi or other local transport.', 'Respect the active religious setting and check visitor arrangements.', 3, 'https://www.goa-tourism.com/', place_image('basilica-bom-jesus')),
        (10, 5, 'fontainhas', 'Fontainhas', 'Walk through Panaji’s Latin Quarter, known for colourful façades and old streets.', 'culture', 15.4958, 73.8278, 'Located in central Panaji and accessible by local transport.', 'Use a quiet walking route and respect residential streets.', None, 'https://www.goa-tourism.com/', place_image('fontainhas')),
        (11, 6, 'palolem-beach', 'Palolem Beach', 'A curved South Goa beach with a relaxed coastal atmosphere and seasonal activities.', 'beach', 15.0100, 74.0232, 'Reach Canacona by rail or road, then continue locally to the beach.', 'Beach conditions and seasonal businesses change; follow local safety advice.', None, 'https://www.goa-tourism.com/', place_image('palolem-beach')),
        (12, 6, 'dudhsagar-falls', 'Dudhsagar Falls', 'A dramatic waterfall landscape in the Western Ghats, best planned with current access information.', 'nature', 15.3144, 74.3144, 'Access rules and permitted routes vary; check the official forest/tourism guidance first.', 'Do not enter restricted areas. Monsoon access and water conditions can change quickly.', None, 'https://www.goa-tourism.com/', place_image('dudhsagar-falls')),
        (13, 7, 'shimla-ridge', 'The Ridge, Shimla', 'A broad hilltop promenade with mountain views and a close connection to Shimla’s public life.', 'culture', 31.1048, 77.1734, 'Shimla is connected by road; the historic railway route reaches nearby areas.', 'Walking in the hill town involves slopes and steps. Check weather before travel.', None, 'https://himachaltourism.gov.in/destination/shimla/', place_image('shimla-ridge')),
        (14, 7, 'jakhu-temple', 'Jakhu Temple', 'A hilltop temple reached through Shimla’s wooded slopes, with broad views over the town.', 'spiritual', 31.1046, 77.1820, 'Continue from Shimla by local taxi or on foot where appropriate.', 'Follow temple customs and take care around steep paths and local wildlife.', None, 'https://himachaltourism.gov.in/destination/shimla/', place_image('jakhu-temple')),
        (15, 8, 'dharamshala', 'Dharamshala', 'A mountain destination connecting Tibetan cultural life, hillside walks and Dhauladhar views.', 'nature', 32.2190, 76.3234, 'Reach by road or via Kangra airport, then use local transport between settlements.', 'The area spans different elevations; allow time for weather and road changes.', None, 'https://himachaltourism.gov.in/', place_image('dharamshala')),
        (16, 8, 'masroor-temple', 'Masroor Rock-Cut Temples', 'Explore a remarkable group of temples carved from rock in the Kangra landscape.', 'heritage', 32.0108, 76.0907, 'Plan a road journey from Kangra or Dharamshala and check local access.', 'Treat this as a heritage site; avoid climbing or touching carved surfaces.', None, 'https://himachaltourism.gov.in/', place_image('masroor-temple')),
        (17, 9, 'marina-beach', 'Marina Beach', 'See Chennai’s long urban shoreline and the city’s evening public life.', 'beach', 13.0500, 80.2824, 'Accessible from central Chennai by local bus, rail or taxi.', 'The sea can be dangerous; follow local warnings and do not assume swimming is safe.', None, 'https://www.tamilnadutourism.com/', place_image('marina-beach')),
        (18, 9, 'kapaleeshwarar-temple', 'Kapaleeshwarar Temple', 'Visit a major Chennai temple surrounded by the streets and food culture of Mylapore.', 'spiritual', 13.0338, 80.2697, 'Reach Mylapore by local bus, rail or taxi.', 'Check temple visitor customs and opening hours before visiting.', None, 'https://www.tamilnadutourism.com/', place_image('kapaleeshwarar-temple')),
        (19, 10, 'meenakshi-temple', 'Meenakshi Amman Temple', 'Explore the temple complex and living streets of Madurai’s historic centre.', 'spiritual', 9.9195, 78.1193, 'Madurai is connected by air, rail and road; the temple is in the city centre.', 'Follow photography and dress guidance issued at the temple.', None, 'https://www.tamilnadutourism.com/', place_image('meenakshi-temple')),
        (20, 10, 'thirumalai-nayak-palace', 'Thirumalai Nayak Palace', 'See the monumental court architecture of a seventeenth-century palace in Madurai.', 'heritage', 9.9145, 78.1193, 'A short local journey from Meenakshi Temple and central Madurai.', 'Check current light-and-sound schedules separately from daytime access.', None, 'https://www.tamilnadutourism.com/', place_image('thirumalai-nayak-palace')),
        (21, 27, 'konark-sun-temple', 'Konark Sun Temple', 'Marvel at the 13th-century Sun Temple designed as a colossal chariot with intricately carved stone wheels and horses. A UNESCO World Heritage property on the Bay of Bengal coast.', 'heritage', 19.8876, 86.0945, 'Located 35 km from Puri and 65 km from Bhubaneswar; easily reached by road via Marine Drive.', 'Open sunrise to sunset. Ticketed entry (ASI monument). Visit during early morning or late afternoon for golden hour photography.', 4, 'https://whc.unesco.org/en/list/246/', place_image('konark-sun-temple')),
        (22, 27, 'puri-jagannath-temple', 'Shree Jagannath Temple, Puri', 'One of India’s four holy Char Dham pilgrimage sites, this monumental 12th-century temple is dedicated to Lord Jagannath, Balabhadra and Subhadra. Renowned for its towering shikhara, massive kitchen serving Mahaprasad, and the world-famous Rath Yatra.', 'spiritual', 19.8049, 85.8179, 'Located in the heart of Puri town; connected by rail and a 60 km expressway from Bhubaneswar airport.', 'Strict dress and entry protocols apply. Electronic devices and leather items must be deposited outside. Don\'t miss tasting the sacred Ananda Bazar Mahaprasad.', None, 'https://odishatourism.gov.in/', place_image('puri-jagannath-temple')),
        (23, 27, 'chilika-lake', 'Chilika Lake', 'Asia’s largest brackish water lagoon, a Ramsar wetland sanctuary home to endangered Irrawaddy dolphins and a winter haven for over a million migratory birds from Siberia and Central Asia.', 'nature', 19.7167, 85.3167, 'Major boat boarding points are at Satapada (50 km from Puri) and Barkul / Rambha along NH-16.', 'Early morning boat rides offer the best chances of dolphin sightings near Satapada and bird watching around Mangalajodi wetlands.', None, 'https://odishatourism.gov.in/', place_image('chilika-lake')),
        (24, 28, 'lingaraj-temple', 'Lingaraj Temple, Bhubaneswar', 'The crowning jewel of Kalinga architecture in Bhubaneswar, the 11th-century Lingaraj Temple rises 55 metres over the old town. Dedicated to Harihara, it is surrounded by over 150 smaller shrines and the sacred Bindu Sagar tank.', 'heritage', 20.2382, 85.8336, 'Located in the Old Town area of Bhubaneswar, easily reached by auto-rickshaw or taxi from anywhere in the capital.', 'A viewing platform is located near the northern perimeter wall offering panoramas of the temple courtyards for visitors.', None, 'https://odishatourism.gov.in/', place_image('lingaraj-temple')),
    ]
    db.executemany('''INSERT OR IGNORE INTO places
        (id,district_id,slug,name,description,category,latitude,longitude,how_to_reach,practical_notes,heritage_id,source_url,image_url)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', places)
    db.executemany('UPDATE places SET image_url=? WHERE id=?', [(p[12], p[0]) for p in places])

    for place in places:
        months = [10, 11, 12, 1, 2, 3] if place[1] in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 27, 28) else [10, 11, 12, 1, 2]
        db.executemany('INSERT OR IGNORE INTO place_months VALUES (?,?)', [(place[0], m) for m in months])
    tags = ['heritage', 'culture', 'nature', 'beach', 'spiritual']
    db.executemany('INSERT OR IGNORE INTO tags(id,name) VALUES (?,?)', [(i, tag) for i, tag in enumerate(tags, 1)])
    db.executemany('INSERT OR IGNORE INTO place_tags SELECT id, ? FROM places WHERE category = ?', [(i, tag) for i, tag in enumerate(tags, 1)])

    festivals_data = [
        (1, 'Onam', 'Kerala’s harvest festival celebrated with grand pookkalam floral designs, boat races, Onasadya feasts and Kathakali dances.', 'lunar', 'https://www.keralatourism.org/', [('kerala', 'ernakulam'), ('kerala', 'alappuzha')], [8, 9]),
        (2, 'Nehru Trophy Boat Race', 'The world-famous snake boat spectacle on Punnamada Lake where majestic chundan vallams race to rhythmic vanchipattu songs.', 'varies_annually', 'https://www.keralatourism.org/', [('kerala', 'alappuzha')], [8]),
        (3, 'Teej Festival', 'Monsoon festival welcoming the rains, celebrated with vibrant processions of Goddess Parvati, swings and traditional song in the Pink City.', 'lunar', 'https://www.tourism.rajasthan.gov.in/', [('rajasthan', 'jaipur')], [7, 8]),
        (4, 'Jaisalmer Desert Festival', 'A vibrant cultural spectacle in the Thar Desert showcasing Rajasthani folk music, Kalbelia dance, camel polo and turban tying competitions.', 'varies_annually', 'https://www.tourism.rajasthan.gov.in/', [('rajasthan', 'jaisalmer')], [2]),
        (5, 'Goa Carnival', 'A colourful four-day celebration with King Momo, street parades, music, dance and floats through old Panaji streets before Lent.', 'varies_annually', 'https://www.goa-tourism.com/', [('goa', 'north-goa'), ('goa', 'south-goa')], [2]),
        (6, 'Shigmo', 'Goa’s grand spring festival celebrated with traditional folk dances, drumbeats, vibrant mythological pageants and coloured powders.', 'lunar', 'https://www.goa-tourism.com/', [('goa', 'north-goa')], [3]),
        (7, 'Shimla Summer Festival', 'An annual cultural extravaganza celebrating the arrival of summer with classical and folk music, floral displays and arts.', 'varies_annually', 'https://himachaltourism.gov.in/', [('himachal-pradesh', 'shimla')], [6]),
        (8, 'Pongal', 'Tamil Nadu’s joyous four-day harvest festival giving thanks to nature and the Sun God, celebrated with clay pots of freshly boiled sweet rice.', 'fixed', 'https://www.tamilnadutourism.com/', [('tamil-nadu', 'chennai'), ('tamil-nadu', 'madurai')], [1]),
        (9, 'Chithirai Festival', 'A spectacular month-long temple festival commemorating the celestial wedding of Goddess Meenakshi and Lord Sundareswarar.', 'lunar', 'https://www.tamilnadutourism.com/', [('tamil-nadu', 'madurai')], [4]),
        (10, 'Rath Yatra of Puri', 'The legendary Festival of Chariots where Lord Jagannath, Balabhadra and Subhadra journey on colossal wooden chariots pulled by millions of devotees along the Grand Road.', 'lunar', 'https://odishatourism.gov.in/', [('odisha', 'puri')], [6, 7]),
        (11, 'Konark Dance & Sand Art Festival', 'An open-air classical dance festival set against the illuminated backdrop of the Sun Temple, accompanied by master sand sculptures on Chandrabhaga beach.', 'fixed', 'https://odishatourism.gov.in/', [('odisha', 'puri')], [12]),
        (12, 'Bali Yatra', 'Asia’s largest open-air trade and cultural fair on the banks of the Mahanadi, commemorating ancient Kalinga mariners who sailed to Bali, Java and Sumatra.', 'lunar', 'https://odishatourism.gov.in/', [('odisha', 'kataka')], [11]),
        (13, 'Nuakhai', 'Western Odisha’s premier agricultural festival welcoming the new rice harvest with family reunions, offerings to Maa Samaleswari and community folk dances.', 'lunar', 'https://odishatourism.gov.in/', [('odisha', 'sambalpur')], [9]),
        (14, 'Makar Sankranti & International Kite Festival', 'The winter solstice festival marked by flying colourful kites across clear blue skies, sacred river baths and til-gul sweets.', 'fixed', 'https://www.gujarattourism.com/', [('gujarat', 'ahmedabad')], [1]),
        (15, 'Maha Shivratri', 'The Great Night of Shiva celebrated with midnight prayers, spiritual chants and riverbank rituals along the holy ghats.', 'lunar', 'https://www.uptourism.gov.in/', [('uttar-pradesh', 'varanasi')], [2, 3]),
        (16, 'Holi & Lathmar Holi', 'The euphoric festival of colours celebrating the arrival of spring and divine love, famous for unique folk traditions in the Braj region.', 'lunar', 'https://www.uptourism.gov.in/', [('uttar-pradesh', 'mathura')], [3]),
        (17, 'Baisakhi', 'Punjab’s joyous harvest festival and the founding day of the Khalsa, celebrated with energetic Bhangra, Nagar Kirtan processions and feasts.', 'fixed', 'https://punjabtourism.punjab.gov.in/', [('punjab', 'amritsar')], [4]),
        (18, 'Buddha Purnima', 'Commemorating the birth, enlightenment and Mahaparinirvana of Gautama Buddha with prayer ceremonies, butter lamps and meditation under the Bodhi Tree.', 'lunar', 'https://tourism.bihar.gov.in/', [('bihar', 'gaya')], [5]),
        (19, 'Hemis Festival', 'A vibrant monastic festival in Ladakh featuring sacred masked Cham dances by lamas and traditional trumpet music celebrating Guru Padmasambhava.', 'lunar', 'https://ladakh.gov.in/tourism/', [('ladakh', 'leh')], [6, 7]),
        (20, 'Ganesh Chaturthi', 'Maharashtra’s most beloved celebration welcoming Lord Ganesha with home shrines, giant public pandals, dhol-tasha drumbeats and grand visarjan immersions.', 'lunar', 'https://aai-portal.maharashtratourism.gov.in/', [('maharashtra', 'mumbai'), ('maharashtra', 'pune')], [8, 9]),
        (21, 'Durga Puja', 'UNESCO Intangible Cultural Heritage celebration honouring Goddess Durga, transforming the city with awe-inspiring artistic pandals, dhak drums and dhunuchi dance.', 'lunar', 'https://wbtourism.gov.in/', [('west-bengal', 'kolkata')], [10]),
        (22, 'Dev Deepawali', 'The Festival of Gods in Varanasi where all 84 ghats along the sacred Ganges are illuminated with over a million earthen oil lamps (diyas).', 'lunar', 'https://www.uptourism.gov.in/', [('uttar-pradesh', 'varanasi')], [11]),
        (23, 'Pushkar Camel Fair', 'One of the world’s largest livestock fairs, bringing thousands of decked camels, desert nomads, cultural competitions and holy dips in Pushkar Lake.', 'lunar', 'https://www.tourism.rajasthan.gov.in/', [('rajasthan', 'ajmer')], [11]),
        (24, 'Hornbill Festival', 'The Festival of Festivals held in Kisama Heritage Village, uniting all 16 Naga tribes to showcase traditional dance, warrior songs, indigenous crafts and music.', 'fixed', 'https://tourism.nagaland.gov.in/', [('nagaland', 'kohima')], [12]),
        (25, 'Mysuru Dasara', 'A regal 10-day state celebration culminating in the majestic Jumboo Savari elephant procession carrying the golden idol of Goddess Chamundeshwari from the illuminated Mysore Palace.', 'lunar', 'https://karnatakatourism.org/', [('karnataka', 'mysuru')], [10]),
    ]

    def resolve_district_id(region_slug, district_slug):
        row = db.execute('''SELECT d.id FROM districts d
            JOIN regions r ON r.id=d.region_id
            WHERE r.slug=? AND (d.slug=? OR d.slug LIKE ? OR d.name LIKE ?)''',
            (region_slug, district_slug, f'%{district_slug}%', f'%{district_slug}%')).fetchone()
        return row[0] if row else None

    db.executemany('INSERT OR IGNORE INTO festivals (id,name,description,date_type,source_url) VALUES (?,?,?,?,?)',
                   [(f[0], f[1], f[2], f[3], f[4]) for f in festivals_data])

    fest_dist_rows = []
    for f in festivals_data:
        fid = f[0]
        for rslug, dslug in f[5]:
            did = resolve_district_id(rslug, dslug)
            if did:
                fest_dist_rows.append((fid, did))
    db.executemany('INSERT OR IGNORE INTO festival_districts (festival_id, district_id) VALUES (?,?)', fest_dist_rows)

    fest_month_rows = []
    for f in festivals_data:
        fid = f[0]
        for m in f[6]:
            fest_month_rows.append((fid, m))
    db.executemany('INSERT OR IGNORE INTO festival_months (festival_id, month) VALUES (?,?)', fest_month_rows)
