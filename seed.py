"""Editorial pilot data and a growing India region/district directory.

The records are intentionally marked as needs_review. Place cards use local,
destination-labelled illustrations until individually licensed photographs are
editorially verified; state covers remain separate landscape/heritage images.
"""

import json
from pathlib import Path
from urllib.parse import quote
UNSPLASH_IDS = [
    '1602216056096-3b40cc0c9944', '1599661046827-dacff0c0f09a',
    '1512343879784-a960bf40e7f2', '1548013146-72479768bada',
    '1564507592333-c60657eea523', '1477587458883-47145ed94245',
    '1524492412937-b28074a5d7da', '1582510003544-4d00b7f74220',
    '1500530855697-b586d89ba3ee', '1464822759023-fed622ff2c3b',
    '1500534623283-312aade485b7', '1469854523086-cc02fe5d8800',
    '1501785888041-af3ef285b470', '1507525428034-b723cf961d3e',
    '1518548419970-58e3b4079ab2', '1524498250077-390f9e378fc0',
    '1470770841072-f978cf4d019e', '1441974231531-c6227db76b6e',
    '1497250681960-ef046c08a56e', '1470071459604-3b5ec3a7fe05',
    '1465146344425-f00d5f5c8f07', '1519681393784-d120267933ba',
    '1511497584788-876760111969', '1482192596544-9eb780fc7f66',
    '1480714378408-67cf0d13bc1b', '1501854140801-50d01698950b',
    '1518005020951-eccb494ad742', '1472396961693-142e6e269027',
    '1497436072909-60f360e1d4b1', '1493246507139-91e8fad9978e',
    '1524231757912-21f4fe3a7200',
]
_assigned_images = {}
_image_cursor = 0
STATE_COVER_IMAGES = {
    # These are selected for the state's own landscape/heritage, not from a
    # generic India search. The three reported as incorrect are explicit here.
    'kerala': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=82',
    'rajasthan': 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=1200&q=82',
    'goa': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=82',
    'himachal-pradesh': 'https://images.unsplash.com/photo-1722915767859-08a59870d70b?auto=format&fit=crop&w=1200&q=82',
    'tamil-nadu': 'https://images.unsplash.com/photo-1563715493579-e0b3e0493b60?auto=format&fit=crop&w=1200&q=82',
    'andhra-pradesh': 'https://images.unsplash.com/photo-1733805569204-41768c7d8c0f?auto=format&fit=crop&w=1200&q=82',
    'karnataka': 'https://images.unsplash.com/photo-1722934804353-0d9f6a55ab5e?auto=format&fit=crop&w=1200&q=82',
    'uttar-pradesh': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1200&q=82',
    'west-bengal': 'https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=82',
    'uttarakhand': 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=82',
    'maharashtra': 'https://images.unsplash.com/photo-1524498250077-390f9e378fc0?auto=format&fit=crop&w=1200&q=82',
    'delhi': 'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=82',
    'jammu-and-kashmir': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=82',
    'ladakh': 'https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1200&q=82',
}
PLACE_IMAGE_PATHS = {
    'fort-kochi': '/assets/places/fort-kochi.svg',
    'mattancherry-palace': '/assets/places/mattancherry-palace.svg',
    'alappuzha-backwaters': '/assets/places/alappuzha-backwaters.svg',
    'alappuzha-beach': '/assets/places/alappuzha-beach.svg',
    'amber-fort': '/assets/places/amber-fort.svg',
    'jantar-mantar': '/assets/places/jantar-mantar.svg',
    'jaisalmer-fort': '/assets/places/jaisalmer-fort.svg',
    'gadisar-lake': '/assets/places/gadisar-lake.svg',
    'basilica-bom-jesus': '/assets/places/basilica-bom-jesus.svg',
    'fontainhas': '/assets/places/fontainhas.svg',
    'palolem-beach': '/assets/places/palolem-beach.svg',
    'dudhsagar-falls': '/assets/places/dudhsagar-falls.svg',
    'shimla-ridge': '/assets/places/shimla-ridge.svg',
    'jakhu-temple': '/assets/places/jakhu-temple.svg',
    'dharamshala': '/assets/places/dharamshala.svg',
    'masroor-temple': '/assets/places/masroor-temple.svg',
    'marina-beach': '/assets/places/marina-beach.svg',
    'kapaleeshwarar-temple': '/assets/places/kapaleeshwarar-temple.svg',
    'meenakshi-temple': '/assets/places/meenakshi-temple.svg',
    'thirumalai-nayak-palace': '/assets/places/thirumalai-nayak-palace.svg',
}


def image(filename):
    global _image_cursor
    if filename in _assigned_images:
        return _assigned_images[filename]
    reserved = set(STATE_COVER_IMAGES.values())
    used = set(_assigned_images.values())
    while True:
        if _image_cursor < len(UNSPLASH_IDS):
            photo_id = UNSPLASH_IDS[_image_cursor]
            url = f'https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=1200&q=82'
        else:
            stem = quote(filename.rsplit('.', 1)[0].replace(' ', '-'), safe='')
            url = f'https://picsum.photos/seed/india-{stem}-{_image_cursor}/1200/800'
        _image_cursor += 1
        if url not in reserved and url not in used:
            break
    _assigned_images[filename] = url
    return url


def state_image(slug, filename):
    return STATE_COVER_IMAGES.get(slug) or image(filename)


def place_image(slug):
    return PLACE_IMAGE_PATHS[slug]


def seed(db):
    regions = [
        (1, 'Kerala', 'kerala', 'state', 'Backwaters, coastal neighbourhoods and living traditions along the Malabar coast.', 'https://www.keralatourism.org/', state_image('kerala', 'Kerala backwaters.jpg')),
        (2, 'Rajasthan', 'rajasthan', 'state', 'Explore desert landscapes, historic cities, forts and colourful local celebrations.', 'https://www.tourism.rajasthan.gov.in/', state_image('rajasthan', 'Jaisalmer Fort.jpg')),
        (3, 'Goa', 'goa', 'state', 'A small coastal state of beaches, old quarters, churches, spice-growing landscapes and seasonal celebrations.', 'https://www.goa-tourism.com/', state_image('goa', 'Palolem beach.jpg')),
        (4, 'Himachal Pradesh', 'himachal-pradesh', 'state', 'Mountain towns, valleys, monasteries and slower journeys across the western Himalaya.', 'https://himachaltourism.gov.in/', state_image('himachal-pradesh', 'Shimla Ridge.jpg')),
        (5, 'Tamil Nadu', 'tamil-nadu', 'state', 'Temple cities, coastal neighbourhoods, classical traditions and a deep food culture.', 'https://www.tamilnadutourism.com/', state_image('tamil-nadu', 'Meenakshi Amman Temple.jpg')),
        (6, 'Andhra Pradesh', 'andhra-pradesh', 'state', 'Coastal landscapes, historic cities, temples and a rich food culture.', 'https://tourism.ap.gov.in/', state_image('andhra-pradesh', 'Tirupati heritage.jpg')),
        (7, 'Arunachal Pradesh', 'arunachal-pradesh', 'state', 'Mountain valleys, monasteries and living traditions in India’s eastern Himalaya.', 'https://arunachaltourism.com/', ''),
        (8, 'Assam', 'assam', 'state', 'River landscapes, tea country, wildlife and distinctive cultural traditions.', 'https://tourism.assam.gov.in/', ''),
        (9, 'Bihar', 'bihar', 'state', 'Ancient learning centres, Buddhist heritage and river plains.', 'https://tourism.bihar.gov.in/', ''),
        (10, 'Chhattisgarh', 'chhattisgarh', 'state', 'Forests, waterfalls, tribal arts and archaeological landscapes.', 'https://tourism.cgstate.gov.in/', ''),
        (11, 'Gujarat', 'gujarat', 'state', 'Craft traditions, historic cities, coastlines and wildlife landscapes.', 'https://www.gujarattourism.com/', ''),
        (12, 'Haryana', 'haryana', 'state', 'Historic pilgrimage routes, wetlands and a landscape close to Delhi.', 'https://haryanatourism.gov.in/', image('Kurukshetra Haryana heritage.jpg')),
        (13, 'Jharkhand', 'jharkhand', 'state', 'Waterfalls, forests, plateau landscapes and living cultural traditions.', 'https://tourism.jharkhand.gov.in/', ''),
        (14, 'Karnataka', 'karnataka', 'state', 'Heritage cities, coffee country, coastlines and diverse landscapes.', 'https://karnatakatourism.org/', ''),
        (15, 'Madhya Pradesh', 'madhya-pradesh', 'state', 'Wildlife, historic cities, temples and central Indian heritage.', 'https://www.mptourism.com/', ''),
        (16, 'Maharashtra', 'maharashtra', 'state', 'Urban culture, hill stations, forts, caves and a long western coastline.', 'https://aai-portal.maharashtratourism.gov.in/', ''),
        (17, 'Manipur', 'manipur', 'state', 'Hills, lakes, handloom traditions and distinctive performing arts.', 'https://manipurtourism.gov.in/', ''),
        (18, 'Meghalaya', 'meghalaya', 'state', 'Living root bridges, waterfalls, caves and highland villages.', 'https://www.meghalayatourism.in/', ''),
        (19, 'Mizoram', 'mizoram', 'state', 'Hills, bamboo craft, community traditions and scenic roads.', 'https://tourism.mizoram.gov.in/', ''),
        (20, 'Nagaland', 'nagaland', 'state', 'Hill communities, craft traditions and seasonal cultural gatherings.', 'https://tourism.nagaland.gov.in/', ''),
        (21, 'Odisha', 'odisha', 'state', 'Temple architecture, coastal wetlands, crafts and classical dance traditions.', 'https://odishatourism.gov.in/', ''),
        (22, 'Punjab', 'punjab', 'state', 'Living Sikh heritage, farms, food traditions and historic cities.', 'https://punjabtourism.punjab.gov.in/', ''),
        (23, 'Sikkim', 'sikkim', 'state', 'Mountain monasteries, high valleys and carefully paced journeys.', 'https://www.sikkimtourism.gov.in/', ''),
        (24, 'Telangana', 'telangana', 'state', 'Deccan history, food, lakes and the layered city of Hyderabad.', 'https://tourism.telangana.gov.in/', ''),
        (25, 'Tripura', 'tripura', 'state', 'Palaces, lakes, forests and a meeting of regional traditions.', 'https://tripuratourism.gov.in/', ''),
        (26, 'Uttar Pradesh', 'uttar-pradesh', 'state', 'Sacred rivers, Mughal heritage, craft cities and living pilgrimage routes.', 'https://www.uptourism.gov.in/', ''),
        (27, 'Uttarakhand', 'uttarakhand', 'state', 'Himalayan towns, pilgrimage routes, forests and alpine landscapes.', 'https://uttarakhandtourism.gov.in/', ''),
        (28, 'West Bengal', 'west-bengal', 'state', 'River deltas, cultural cities, tea hills and coastal landscapes.', 'https://wbtourism.gov.in/', ''),
        (29, 'Andaman and Nicobar Islands', 'andaman-and-nicobar-islands', 'union_territory', 'Island landscapes, marine life and coastal histories in the Bay of Bengal.', 'https://www.andamantourism.gov.in/', ''),
        (30, 'Chandigarh', 'chandigarh', 'union_territory', 'A planned city known for modernist architecture, gardens and civic spaces.', 'https://chandigarhtourism.gov.in/', ''),
        (31, 'Dadra and Nagar Haveli and Daman and Diu', 'dadra-and-nagar-haveli-and-daman-and-diu', 'union_territory', 'Coastal forts, beaches, forested interiors and local craft traditions.', 'https://dnhddtourism.in/', ''),
        (32, 'Delhi', 'delhi', 'union_territory', 'A historic capital layered with empires, markets, museums and neighbourhood food.', 'https://delhitourism.gov.in/', ''),
        (33, 'Jammu and Kashmir', 'jammu-and-kashmir', 'union_territory', 'Mountain valleys, lakes, gardens and living craft traditions.', 'https://jammutourism.jk.gov.in/', ''),
        (34, 'Ladakh', 'ladakh', 'union_territory', 'High-altitude landscapes, monasteries and journeys shaped by mountain weather.', 'https://ladakh.gov.in/tourism/', ''),
        (35, 'Lakshadweep', 'lakshadweep', 'union_territory', 'Coral islands, lagoons and carefully managed coastal experiences.', 'https://lakshadweep.gov.in/tourism/', ''),
        (36, 'Puducherry', 'puducherry', 'union_territory', 'A coastal union territory with Tamil heritage, French-era streets and beaches.', 'https://tourism.py.gov.in/', ''),
    ]
    db.executemany('''INSERT OR IGNORE INTO regions
        (id,name,slug,kind,description,source_url,cover_image_url) VALUES (?,?,?,?,?,?,?)''', regions)
    db.executemany('UPDATE regions SET cover_image_url=?, source_url=? WHERE id=?', [(STATE_COVER_IMAGES.get(r[2]) or r[6] or image(r[1] + ' heritage.jpg'), r[5], r[0]) for r in regions])

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
        (13, 16, 'Mumbai City', 'mumbai-city', 'A dense island-city district of waterfronts, markets, food and historic architecture.', 'Try vada pav, coastal seafood and Irani café traditions.', 'https://aai-portal.maharashtratourism.gov.in/'),
        (14, 16, 'Pune', 'pune', 'A cultural and educational city with forts and food traditions nearby.', 'Try misal, bhakri and seasonal Maharashtrian dishes.', 'https://aai-portal.maharashtratourism.gov.in/'),
        (15, 26, 'Agra', 'agra', 'A historic city shaped by Mughal architecture, river landscapes and craft markets.', 'Try petha, Mughlai dishes and local street food.', 'https://www.uptourism.gov.in/'),
        (16, 26, 'Varanasi', 'varanasi', 'A river city of ghats, music, craft and pilgrimage traditions.', 'Try kachori-sabzi, local sweets and seasonal drinks.', 'https://www.uptourism.gov.in/'),
        (17, 28, 'Kolkata', 'kolkata', 'A cultural capital of books, theatre, colonial-era streets and Bengali food.', 'Try mishti doi, fish preparations and Kolkata street food.', 'https://wbtourism.gov.in/'),
        (18, 28, 'Darjeeling', 'darjeeling', 'A hill town of tea gardens, mountain views and railway heritage.', 'Try Darjeeling tea, momos and local bakery cafés.', 'https://wbtourism.gov.in/'),
        (19, 27, 'Dehradun', 'dehradun', 'A valley city and practical base for exploring Uttarakhand’s nearby hills.', 'Try Garhwali and Kumaoni dishes where available.', 'https://uttarakhandtourism.gov.in/'),
        (20, 27, 'Nainital', 'nainital', 'A lake town surrounded by forested hills and walking routes.', 'Try local mountain produce and seasonal café food.', 'https://uttarakhandtourism.gov.in/'),
        (21, 32, 'New Delhi', 'new-delhi', 'A planned capital district with museums, gardens, memorials and public avenues.', 'Explore regional food from across India in its markets and restaurants.', 'https://delhitourism.gov.in/'),
        (22, 33, 'Srinagar', 'srinagar', 'A lake city known for gardens, houseboats and Kashmiri craft traditions.', 'Try wazwan traditions, kahwa and seasonal Kashmiri dishes.', 'https://jammutourism.jk.gov.in/'),
        (23, 33, 'Jammu', 'jammu', 'A gateway city with temples, markets and routes toward the hills.', 'Try rajma, kaladi cheese and Dogra food traditions.', 'https://jammutourism.jk.gov.in/'),
        (24, 34, 'Leh', 'leh', 'A high-altitude town and base for monastery, valley and mountain journeys.', 'Try skyu, thukpa and locally grown apricots in season.', 'https://ladakh.gov.in/tourism/'),
        (25, 36, 'Puducherry', 'puducherry-district', 'A coastal district of Tamil streets, cafés, heritage buildings and beaches.', 'Try Tamil coastal food alongside the city’s café traditions.', 'https://tourism.py.gov.in/'),
        (26, 30, 'Chandigarh', 'chandigarh-district', 'A union territory and planned city of gardens, architecture and public art.', 'Try Punjabi and North Indian food across the city’s sectors.', 'https://chandigarhtourism.gov.in/'),
    ]
    db.executemany('''INSERT OR IGNORE INTO districts
        (id,region_id,name,slug,description,food_notes,source_url) VALUES (?,?,?,?,?,?,?)''', districts)

    # Directory coverage for every region. These are navigation records; a
    # district becomes a full editorial destination only after places,
    # festivals and sources are added and reviewed.
    directory = {
        6: ['Visakhapatnam', 'Tirupati', 'Vijayawada', 'Guntur', 'Kurnool'],
        7: ['Tawang', 'West Kameng', 'Papum Pare', 'East Siang', 'Lower Subansiri'],
        8: ['Kamrup Metropolitan', 'Dibrugarh', 'Jorhat', 'Sonitpur', 'Cachar', 'Tinsukia'],
        9: ['Patna', 'Gaya', 'Nalanda', 'Muzaffarpur', 'Bhagalpur'],
        10: ['Raipur', 'Bastar', 'Bilaspur', 'Korba', 'Durg'],
        11: ['Ahmedabad', 'Kutch', 'Gir Somnath', 'Vadodara', 'Surat', 'Rajkot'],
        12: ['Gurugram', 'Faridabad', 'Panipat', 'Kurukshetra', 'Hisar'],
        13: ['Ranchi', 'East Singhbhum', 'Deoghar', 'Hazaribagh', 'Dhanbad'],
        14: ['Kodagu', 'Vijayanagara', 'Dakshina Kannada', 'Udupi'],
        15: ['Bhopal', 'Indore', 'Ujjain', 'Chhatarpur', 'Gwalior', 'Jabalpur'],
        16: ['Mumbai Suburban', 'Nashik', 'Chhatrapati Sambhajinagar', 'Ratnagiri', 'Nagpur'],
        17: ['Imphal West', 'Bishnupur', 'Churachandpur', 'Ukhrul'],
        18: ['East Khasi Hills', 'West Garo Hills', 'Jaintia Hills', 'Ri-Bhoi'],
        19: ['Aizawl', 'Champhai', 'Lunglei', 'Serchhip'],
        20: ['Kohima', 'Dimapur', 'Mon', 'Mokokchung'],
        21: ['Khordha', 'Puri', 'Cuttack', 'Koraput', 'Ganjam', 'Mayurbhanj'],
        22: ['Amritsar', 'Ludhiana', 'Patiala', 'Rupnagar', 'Bathinda'],
        23: ['East Sikkim', 'West Sikkim', 'North Sikkim', 'South Sikkim'],
        24: ['Hyderabad', 'Hanumakonda', 'Nalgonda', 'Nizamabad', 'Adilabad'],
        25: ['West Tripura', 'Gomati', 'North Tripura', 'Dhalai'],
        26: ['Lucknow', 'Prayagraj', 'Mathura', 'Ayodhya', 'Gorakhpur'],
        27: ['Haridwar', 'Chamoli', 'Pauri Garhwal', 'Almora', 'Rudraprayag'],
        28: ['Hooghly', 'South 24 Parganas', 'Kalimpong', 'Murshidabad', 'Jalpaiguri'],
        29: ['South Andaman', 'North and Middle Andaman', 'Nicobar'],
        30: ['Chandigarh'],
        31: ['Dadra and Nagar Haveli', 'Daman', 'Diu'],
        32: ['New Delhi', 'Central Delhi', 'South Delhi', 'North Delhi', 'East Delhi', 'West Delhi'],
        33: ['Srinagar', 'Jammu', 'Anantnag', 'Baramulla', 'Kupwara', 'Kathua'],
        34: ['Leh', 'Kargil'],
        35: ['Kavaratti', 'Agatti', 'Minicoy'],
        36: ['Puducherry', 'Karaikal', 'Mahe', 'Yanam'],
    }
    existing_slugs = {row[0] for row in db.execute('SELECT slug FROM districts')}
    existing_names = {(row[0], row[1].lower()) for row in db.execute('SELECT region_id, name FROM districts')}
    next_id = db.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM districts').fetchone()[0]
    region_sources = {row[0]: row[1] for row in db.execute('SELECT id, source_url FROM regions')}
    for region_id, names in directory.items():
        for name in names:
            slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in name).strip('-')
            while '--' in slug:
                slug = slug.replace('--', '-')
            if slug in existing_slugs or (region_id, name.lower()) in existing_names:
                continue
            db.execute('''INSERT INTO districts
                (id, region_id, name, slug, description, food_notes, source_url)
                VALUES (?,?,?,?,?,?,?)''', (next_id, region_id, name, slug,
                f'{name} district directory entry. Destination coverage is being expanded and reviewed.',
                'Local food notes will be added with verified editorial sources.', region_sources[region_id]))
            existing_slugs.add(slug)
            existing_names.add((region_id, name.lower()))
            next_id += 1

    # Import the complete state/UT district index downloaded from the public
    # government-source dataset in data/india-states-districts.json. The
    # curated records above provide friendly pilot descriptions; this import
    # fills every remaining administrative district for navigation.
    source_file = Path(__file__).with_name('data') / 'india-states-districts.json'
    if source_file.is_file():
        official_directory = json.loads(source_file.read_text(encoding='utf-8'))
        region_ids = {row[0].lower(): row[1] for row in db.execute('SELECT name, id FROM regions')}
        region_slugs = {row[0]: row[1] for row in db.execute('SELECT id, slug FROM regions')}
        for entry in official_directory:
            region_id = region_ids.get(entry.get('state', '').lower())
            if not region_id:
                continue
            for name in entry.get('districts', []):
                slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in name).strip('-')
                while '--' in slug:
                    slug = slug.replace('--', '-')
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
    ]
    db.executemany('''INSERT OR IGNORE INTO places
        (id,district_id,slug,name,description,category,latitude,longitude,how_to_reach,practical_notes,heritage_id,source_url,image_url)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', places)
    # Also repairs image metadata for records created by the first pilot version.
    db.executemany('UPDATE places SET image_url=? WHERE id=?', [(p[12], p[0]) for p in places])

    for place in places:
        months = [10, 11, 12, 1, 2, 3] if place[1] in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) else [10, 11, 12, 1, 2]
        db.executemany('INSERT OR IGNORE INTO place_months VALUES (?,?)', [(place[0], m) for m in months])
    tags = ['heritage', 'culture', 'nature', 'beach', 'spiritual']
    db.executemany('INSERT OR IGNORE INTO tags(id,name) VALUES (?,?)', [(i, tag) for i, tag in enumerate(tags, 1)])
    db.executemany('INSERT OR IGNORE INTO place_tags SELECT id, ? FROM places WHERE category = ?', [(i, tag) for i, tag in enumerate(tags, 1)])

    festivals = [
        (1, 'Onam', 'Kerala’s harvest celebrations include floral displays, feasts and local cultural events. Dates vary by year.', 'lunar', 'https://www.keralatourism.org/', None),
        (2, 'Nehru Trophy Boat Race', 'A boat-racing event associated with Punnamada Lake. The organiser announces the annual schedule.', 'varies_annually', 'https://www.keralatourism.org/', None),
        (3, 'Teej in Jaipur', 'Monsoon-season celebrations with cultural traditions and processions; verify the annual programme.', 'lunar', 'https://www.tourism.rajasthan.gov.in/', None),
        (4, 'Jaisalmer Desert Festival', 'A cultural festival showcasing desert-region music and performances; dates are announced annually.', 'varies_annually', 'https://www.tourism.rajasthan.gov.in/', None),
        (5, 'Goa Carnival', 'A colourful pre-Lenten celebration with public processions and cultural events. Annual dates vary.', 'varies_annually', 'https://www.goa-tourism.com/', None),
        (6, 'Shigmo', 'A spring festival in Goa with processions, music and local traditions. Confirm the district programme each year.', 'lunar', 'https://www.goa-tourism.com/', None),
        (7, 'Shimla Summer Festival', 'A seasonal cultural programme with music and local performances; dates are announced annually.', 'varies_annually', 'https://himachaltourism.gov.in/', None),
        (8, 'Pongal', 'Tamil Nadu’s harvest festival, observed with regional customs, food and community celebrations.', 'fixed', 'https://www.tamilnadutourism.com/', None),
        (9, 'Chithirai Festival', 'A major Madurai festival period connected with temple traditions; dates follow the annual calendar.', 'lunar', 'https://www.tamilnadutourism.com/', None),
    ]
    db.executemany('INSERT OR IGNORE INTO festivals VALUES (?,?,?,?,?,?)', festivals)
    links = [(1, 1), (1, 2), (2, 2), (3, 3), (4, 4), (5, 5), (5, 6), (6, 5), (7, 7), (8, 9), (8, 10), (9, 10)]
    db.executemany('INSERT OR IGNORE INTO festival_districts VALUES (?,?)', links)
    months = [(1, 8), (1, 9), (2, 8), (3, 7), (3, 8), (4, 2), (5, 2), (6, 3), (7, 6), (8, 1), (9, 4)]
    db.executemany('INSERT OR IGNORE INTO festival_months VALUES (?,?)', months)
