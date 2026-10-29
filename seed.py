"""Editorial pilot data and a growing India region/district directory.

The records are intentionally marked as needs_review. Place cards use local,
destination-specific photographs sourced from Wikimedia Commons and Unsplash.
Each state features its most iconic landmark photograph.
"""

import json
from pathlib import Path

STATE_COVER_IMAGES = {
    'odisha': '/assets/states/odisha.jpg',
    'kerala': '/assets/states/kerala.jpg',
    'rajasthan': '/assets/states/rajasthan.jpg',
    'goa': '/assets/states/goa.jpg',
    'himachal-pradesh': '/assets/states/himachal-pradesh.jpg',
    'tamil-nadu': '/assets/states/tamil-nadu.jpg',
    'andhra-pradesh': '/assets/states/andhra-pradesh.jpg',
    'karnataka': '/assets/states/karnataka.jpg',
    'uttar-pradesh': '/assets/states/uttar-pradesh.jpg',
    'west-bengal': '/assets/states/west-bengal.jpg',
    'uttarakhand': '/assets/states/uttarakhand.jpg',
    'maharashtra': '/assets/states/maharashtra.jpg',
    'delhi': '/assets/states/delhi.jpg',
    'jammu-and-kashmir': '/assets/states/jammu-and-kashmir.jpg',
    'ladakh': '/assets/states/ladakh.jpg',
    'punjab': '/assets/states/punjab.jpg',
    'gujarat': '/assets/states/gujarat.jpg',
    'assam': '/assets/states/assam.jpg',
    'bihar': '/assets/states/bihar.jpg',
    'chhattisgarh': '/assets/states/chhattisgarh.jpg',
    'haryana': '/assets/states/haryana.jpg',
    'jharkhand': '/assets/states/jharkhand.jpg',
    'madhya-pradesh': '/assets/states/madhya-pradesh.jpg',
    'manipur': '/assets/states/manipur.jpg',
    'meghalaya': '/assets/states/meghalaya.jpg',
    'mizoram': '/assets/states/mizoram.jpg',
    'nagaland': '/assets/states/nagaland.jpg',
    'sikkim': '/assets/states/sikkim.jpg',
    'telangana': '/assets/states/telangana.jpg',
    'tripura': '/assets/states/tripura.jpg',
    'arunachal-pradesh': '/assets/states/arunachal-pradesh.jpg',
    'andaman-and-nicobar-islands': '/assets/states/andaman-and-nicobar-islands.jpg',
    'chandigarh': '/assets/states/chandigarh.jpg',
    'dadra-and-nagar-haveli-and-daman-and-diu': '/assets/states/dadra-and-nagar-haveli-and-daman-and-diu.jpg',
    'lakshadweep': '/assets/states/lakshadweep.jpg',
    'puducherry': '/assets/states/puducherry.jpg',
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
    'aguada-fort': '/assets/places/aguada-fort.jpg',
    'se-cathedral': '/assets/places/se-cathedral.jpg',
    'anjuna-beach': '/assets/places/anjuna-beach.jpg',
    'mangueshi-temple': '/assets/places/mangueshi-temple.jpg',
    'cabo-de-rama-fort': '/assets/places/cabo-de-rama-fort.jpg',
    'shanta-durga-temple': '/assets/places/shanta-durga-temple.jpg',
    'agonda-beach': '/assets/places/agonda-beach.jpg',
    'tsomgo-lake': '/assets/places/tsomgo-lake.jpg',
    'rumtek-monastery': '/assets/places/rumtek-monastery.jpg',
    'gurudongmar-lake': '/assets/places/gurudongmar-lake.jpg',
    'yumthang-valley': '/assets/places/yumthang-valley.jpg',
    'pemayangtse-monastery': '/assets/places/pemayangtse-monastery.jpg',
    'solophok-char-dham': '/assets/places/solophok-char-dham.jpg',
    'khangchendzonga-national-park': '/assets/places/khangchendzonga-national-park.jpg',
}


def state_image(slug, filename=None):
    return STATE_COVER_IMAGES.get(slug) or STATE_COVER_IMAGE


def place_image(slug):
    return PLACE_IMAGE_PATHS.get(slug, f'/assets/places/{slug}.jpg')


def seed(db):
    regions = [
        (1, 'Kerala', 'kerala', 'state', 'Backwaters, coastal neighbourhoods and living traditions along the Malabar coast.', 'https://www.keralatourism.org/', state_image('kerala')),
        (2, 'Rajasthan', 'rajasthan', 'state', 'Explore desert landscapes, historic cities, forts and colourful local celebrations.', 'https://www.tourism.rajasthan.gov.in/', state_image('rajasthan')),
        (3, 'Goa', 'goa', 'state', 'A radiant coastal state along the Arabian Sea, Goa blends over 450 years of Portuguese heritage with Konkani traditions. Known for golden beaches, UNESCO World Heritage cathedrals of Velha Goa, ancient Sahyadri spice plantations, hidden waterfall sanctuaries, and a vibrant susegad lifestyle.', 'https://www.goa-tourism.com/', state_image('goa')),
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
        (23, 'Sikkim', 'sikkim', 'state', 'Nestled under the majestic shadow of Mount Kangchenjunga, Sikkim is India’s first fully organic state. A wonderland of ancient Tibetan Buddhist monasteries, sacred glacial lakes, rhododendron valleys, and vibrant Bhutia, Lepcha and Nepali traditions.', 'https://www.sikkimtourism.gov.in/', state_image('sikkim')),
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
        (5, 3, 'North Goa', 'north-goa', 'Goa’s vibrant northern district encompasses the state capital Panaji, the historic Latin Quarter of Fontainhas, the UNESCO World Heritage monuments of Old Goa, and a world-renowned coastline from Candolim and Calangute to Anjuna, Vagator, and the serene beaches of Morjim and Arambol. North Goa is defined by dramatic red-laterite sea forts like Fort Aguada and Chapora Fort, 16th-century Portuguese-Manueline cathedrals, mangrove estuarine sanctuaries along the Mandovi River, bustling night markets, and an energetic coastal arts and music scene.', 'Indulge in authentic Goan coastal fare: prawn and fish curry rice with crispy rava-fried kingfish, pork vindaloo (slow-cooked with coconut vinegar, garlic and Kashmiri chillies), chicken cafreal (marinated in coriander, green chillies and whole spices), choris pav (spiced Goan pork sausage stuffed in warm crusty poi bread), crab xacuti with roasted coconut, and traditional multi-layered bebinca and serradura for dessert. Don’t miss freshly tapped cashew urrak and feni during spring.', 'https://www.goa-tourism.com/'),
        (6, 3, 'South Goa', 'south-goa', 'Quieter, greener, and culturally profound, South Goa stretches from the historic commercial hub of Margao and the peaceful coastal villages of Colva, Benaulim, Cavelossim, and Agonda down to the iconic crescent of Palolem Beach and the secluded coves of Canacona. Inland, the district shelters the lush Western Ghats of Bhagwan Mahaveer Sanctuary, the four-tiered cascade of Dudhsagar Falls, 17th-century aristocratic Indo-Portuguese palacios in Chandor and Quepem, and the sacred temple heartland of Ponda home to ancient shrines like Shree Manguesh and Shanta Durga.', 'Explore rich Saraswat Hindu and Catholic culinary traditions: authentic South Goan fish thali with kismoor (dried prawn coconut relish), prawn balchão (tangy-sweet fiery pickle curry), crab xec xec (rich roasted-coconut crab gravy), ambot tik (sour and spicy shark curry), freshly baked village poi and unndo from local padeiros, sol kadhi (kokum and coconut milk digestive), and alle belle (Goan coconut and jaggery crepes).', 'https://www.goa-tourism.com/'),
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
        (29, 23, 'Gangtok', 'gangtok', 'Surrounding the capital town on a forested Himalayan ridge, Gangtok district is the cultural and administrative hub of Sikkim. Known for sweeping views of Mount Kangchenjunga, the Namgyal Institute of Tibetology, bustling MG Marg, Enchey Monastery, and the sacred high-altitude alpine lake of Tsomgo leading to the historic Silk Route at Nathu La.', 'Try authentic steamed momos with fiery dalle khursani chili paste, hearty thukpa noodle soup, sha phaley (crispy beef or chicken stuffed pastry), fermented gundruk jhol, chhurpi soup with fiddlehead ferns (ningro), and warming tongba (fermented millet beer in wooden casks).', 'https://www.sikkimtourism.gov.in/'),
        (30, 23, 'Gyalshing', 'gyalshing', 'The historical and spiritual cradle of Sikkim where the first Chogyal was crowned at Yuksom in 1642. Gyalshing is home to Pemayangtse Monastery (premier seat of the Nyingma order), the ancient royal stone palace ruins of Rabdentse, the sacred wish-fulfilling Khecheopalri Lake, and the dizzying Singshore Bridge. It is also the gateway for the legendary Goecha La trek toward Kangchenjunga.', 'Savour traditional Bhutia and Lepcha delicacies: buckwheat pancakes, ningro chhurpi (wild fiddlehead ferns cooked with indigenous cottage cheese), sinki soup, kinema (fermented soybean curry), and country chicken curry infused with timur (Himalayan Sichuan pepper).', 'https://www.sikkimtourism.gov.in/'),
        (31, 23, 'Mangan', 'mangan', 'Sikkim’s largest district by area, spanning monumental Himalayan landscapes from sub-tropical river gorges to arctic glacial summits. Mangan encompasses the breathtaking Yumthang Valley of Flowers, natural thermal springs, the high-altitude tribal villages of Lachen and Lachung, and the sacred glacial waters of Gurudongmar Lake at 5,430 metres near the Tibetan frontier. It also holds the core wilderness of Khangchendzonga National Park.', 'Enjoy robust high-altitude mountain meals: hot bowls of thenthuk (hand-pulled square pasta in rich broth), gyathuk, dried yak cheese (chhurpi), salted Tibetan butter tea (po cha), tsampa (roasted barley flour porridge), and momos with hot broth.', 'https://www.sikkimtourism.gov.in/'),
        (32, 23, 'Namchi', 'namchi', 'The cultural and pilgrimage heartland of southern Sikkim, set against rolling hills and tea gardens. Renowned for Siddhesvara Dhaam at Solophok (featuring a 108-foot statue of Lord Shiva and replicas of India’s four holy Char Dham shrines), Samdruptse Hill with its 138-foot gilded statue of Guru Padmasambhava, Ngadak Monastery, and Temi Tea Estate—Sikkim’s only tea garden producing prize-winning organic orthodox teas.', 'Sip fresh organic Temi black tea paired with golden sel roti (crisp Nepali rice doughnuts), spicy aloo dum in sesame gravy, sisnu (wild stinging nettle soup rich in iron), fermented kinema with rice, and momos accompanied by fresh tomato-dalle chutney.', 'https://www.sikkimtourism.gov.in/'),
        (33, 23, 'Pakyong', 'pakyong', 'A verdant eastern district hosting Sikkim’s greenfield airport perched atop mountain terraces. Home to the world-renowned Rumtek Monastery (Dharma Chakra Centre), the sacred 16th-century seat of the Gyalwang Karmapa. Pakyong also encompasses the peaceful hamlet of Aritar with its boot-shaped Lampokhari Lake, lush orchid cultivation centers, and the dramatic zigzag loops of the Old Silk Route at Zuluk.', 'Indulge in organic village thalis: dal bhat tarkari with seasonal wild mushrooms, smoked pork stir-fried with tender bamboo shoots, fermented mustard greens (gundruk), phagshapa (pork stewed with radishes and dried chillies), and festive sweet khapse pastries.', 'https://www.sikkimtourism.gov.in/'),
        (34, 23, 'Soreng', 'soreng', 'A tranquil southwestern district blessed with close-up panoramas of Mount Kangchenjunga and lush forest ridges. Soreng is celebrated for the Barsey Rhododendron Sanctuary, where dense canopy forests blaze with over 40 species of blooming rhododendrons in spring. Also known for Jorethang town along the Rangeet River, Chakung viewpoint, and peaceful eco-villages pioneering organic agriculture and community homestays.', 'Experience true farm-to-table village food: wholesome millet rotis (kodo ko roti) with fresh churned cow butter, stinging nettle broth (sisnu ko jhol), wild forest ferns with churpi, spicy radish gorkhali achar, and wild mountain berry fruit wines.', 'https://www.sikkimtourism.gov.in/'),
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
        (5, 'Khangchendzonga National Park', 'https://whc.unesco.org/en/list/1513/'),
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
        (25, 5, 'aguada-fort', 'Fort Aguada & Lighthouse', 'A monumental 17th-century Portuguese fortress and four-tiered lighthouse overlooking the Arabian Sea and the mouth of the Mandovi River. Built in 1612 with a massive 79-gun battery and a 2.3-million-gallon freshwater cistern that once replenished passing merchant ships.', 'heritage', 15.4925, 73.7736, 'Located in Sinquerim, Candolim; approximately 15 km from Panaji. Easily accessible by taxi, auto-rickshaw, or rented two-wheeler along the coastal road.', 'Open daily 9:30 AM to 6:00 PM. Ticketed entry through ASI. Carry water and sun protection when walking along the upper battlements. Stunning sunset views over the Arabian Sea.', None, 'https://www.goa-tourism.com/', place_image('aguada-fort')),
        (26, 5, 'se-cathedral', 'Se Cathedral, Old Goa', 'One of the largest churches in Asia and part of the UNESCO World Heritage Churches and Convents of Goa. Dedicated to St. Catherine of Alexandria, it features magnificent Tuscan-Manueline architecture, gilded Corinthian altars, and the famous Golden Bell known for its rich acoustic resonance.', 'heritage', 15.5039, 73.9122, 'Located in Old Goa (Velha Goa), 10 km east of Panaji. Reachable via NH-748 by local bus, taxi or rental vehicle.', 'Open daily 7:30 AM to 6:00 PM. Free entry. Modest attire covering shoulders and knees is strictly required for entry. Photography is restricted inside the active prayer sanctuary.', 3, 'https://whc.unesco.org/en/list/234/', place_image('se-cathedral')),
        (27, 5, 'anjuna-beach', 'Anjuna Beach', 'A legendary coastline framed by volcanic red laterite cliffs, swaying coconut groves, and sea-facing rocky headlands. Known globally for its counter-culture history, the bustling Wednesday Flea Market, sunset drum circles, and open-air beachfront cafes.', 'beach', 15.5733, 73.7410, 'Situated in Bardez taluka, about 18 km from Panaji and 8 km from Mapusa. Best explored on a rented scooter or via coastal taxis.', 'Swimming requires caution due to underwater laterite rock formations; swim only in designated lifeguard-patrolled zones. The Wednesday flea market operates from morning till sunset.', None, 'https://www.goa-tourism.com/', place_image('anjuna-beach')),
        (28, 6, 'mangueshi-temple', 'Shree Manguesh Temple, Priol', 'A 450-year-old architectural gem nestled among lush forested hills in Ponda. Dedicated to Lord Manguesh (an incarnation of Shiva), the temple features a distinctive seven-story octagonal deepstambha (lamp tower), sparkling Sabha Griha chandeliers, and a sacred water tank.', 'spiritual', 15.4419, 73.9686, 'Located in Priol, Ponda taluka, along the Panaji–Ponda highway (21 km from Panaji, 26 km from Margao). Readily connected by state buses and taxis.', 'Open daily 6:00 AM to 9:00 PM. Dress code is strictly traditional/modest. Leather items and footwear must be deposited at the outer gate before entering the courtyard.', None, 'https://www.goa-tourism.com/', place_image('mangueshi-temple')),
        (29, 6, 'cabo-de-rama-fort', 'Cabo de Rama Fort', 'A wild, evocative coastal clifftop fortress standing high above the Arabian Sea at the southern promontory of Canacona. Rich in legend as the sanctuary where Lord Rama and Sita stayed during their fourteen-year exile, with ancient stone ramparts, historic cannons, and the charming whitewashed Church of St. Antonio.', 'heritage', 15.0898, 73.9219, 'Located 30 km south of Margao and 18 km north of Palolem. Accessible via winding scenic rural roads by car, taxi or rented scooter.', 'Open daily 9:00 AM to 5:30 PM. Free entry. The clifftop drops sheer to the sea below—exercise care near the cliff edges. Unmatched 360-degree panoramic ocean views at sunset.', None, 'https://www.goa-tourism.com/', place_image('cabo-de-rama-fort')),
        (30, 6, 'shanta-durga-temple', 'Shanta Durga Temple, Kavlem', 'One of Goa’s largest and most revered Hindu pilgrimage shrines, dedicated to Goddess Shanta Durga, the peaceful mediator between Lord Shiva and Lord Vishnu. Set in a verdant valley in Ponda with a striking five-tiered deepstambha, a golden palanquin, and terracotta tile roofs blending Konkani and Portuguese design elements.', 'spiritual', 15.3942, 73.9856, 'Located at the foothills of Kavlem in Ponda taluka, 28 km from Panaji and 18 km from Margao. Direct road access via Ponda city.', 'Open daily 6:00 AM to 8:30 PM. Follow temple dress etiquette. The annual Jatra festival in Magha (January/February) features elaborate temple chariot processions.', None, 'https://www.goa-tourism.com/', place_image('shanta-durga-temple')),
        (31, 6, 'agonda-beach', 'Agonda Beach', 'A serene and uncommercialised 3-kilometre expanse of pristine golden sand fringed by palm groves and gentle surf. Designated as a protected eco-sensitive nesting site for Olive Ridley sea turtles, ideal for quiet coastal walks, yoga retreats, and dolphin watching in calm morning waters.', 'beach', 15.0442, 73.9878, 'Located in Canacona taluka, 70 km south of Dabolim airport and 10 km north of Palolem Beach. Connected by rural bus and local taxi services.', 'Strict silent-beach regulations are enforced at night to protect nesting turtles. Boat trips for dolphin spotting can be arranged from local fishers in the morning.', None, 'https://www.goa-tourism.com/', place_image('agonda-beach')),
        (32, 29, 'tsomgo-lake', 'Tsomgo Lake (Changu Lake)', 'A sacred glacial alpine lake sitting at 3,753 metres (12,313 ft) in the East Himalayas, framed by rugged snow-dusted peaks. Revered by local Buddhist monks for centuries, the lake remains frozen in winter and is surrounded by blooming alpine rhododendrons and primulas in spring and summer.', 'nature', 27.3742, 88.7619, 'Located 40 km northeast of Gangtok along Jawaharlal Nehru Road toward Nathu La. Reachable by shared or private four-wheel-drive taxis from Gangtok.', 'A Protected Area Permit (PAP) is mandatory for all visitors, obtainable through registered Sikkim travel agents in Gangtok. Acclimatise properly due to the high altitude.', None, 'https://www.sikkimtourism.gov.in/', place_image('tsomgo-lake')),
        (33, 33, 'rumtek-monastery', 'Rumtek Monastery', 'The premier seat-in-exile of the Gyalwang Karmapa, head of the Karma Kagyu lineage of Tibetan Buddhism. Rebuilt in the 1960s as a replica of Tsurphu Monastery in Tibet, the grand complex features magnificent Tibetan religious murals, golden stupas holding sacred relics, intricate thangkas, and a monastic college.', 'spiritual', 27.3039, 88.5475, 'Situated 24 km southwest of Gangtok on the opposite hillside; easily accessible by taxi or local bus via the Ranipool-Rumtek road.', 'Open daily 6:00 AM to 6:00 PM. Visitors must present photo ID at the entrance gate. Photography is restricted inside the main prayer hall. The early morning chanting ceremony is deeply meditative.', None, 'https://www.sikkimtourism.gov.in/', place_image('rumtek-monastery')),
        (34, 31, 'gurudongmar-lake', 'Gurudongmar Lake', 'One of the highest lakes in the world, sitting at a staggering elevation of 5,430 metres (17,800 ft) amidst the barren, windswept Tibetan plateau. Blessed by Guru Padmasambhava and Guru Nanak, a portion of the crystal-clear azure waters remains miraculously unfrozen even during harsh sub-zero Himalayan winters.', 'nature', 28.0258, 88.7089, 'Located in North Sikkim, 175 km from Gangtok via Mangan, Chungthang, and Lachen. Requires a two-day journey with an overnight halt at Lachen village.', 'Special Protected Area Permit (PAP) required. Open only to Indian nationals due to proximity to the international border. Extremely low oxygen levels—consult a physician before visiting and leave early morning before high winds start.', None, 'https://www.sikkimtourism.gov.in/', place_image('gurudongmar-lake')),
        (35, 31, 'yumthang-valley', 'Yumthang Valley of Flowers', 'A spectacular alpine grazing meadow at 3,564 metres (11,693 ft), surrounded by the snow-capped Himalayan peaks of the Shingba Rhododendron Sanctuary. In spring, the valley carpet erupts in a riot of colours with over 24 species of wild rhododendrons, primulas, and irises, accompanied by natural sulfur hot springs and grazing yaks.', 'nature', 27.8286, 88.6947, 'Located 140 km from Gangtok via Lachung village. Typically visited on a 2-day/1-night trip with base camp at Lachung.', 'Best visited from April to June for wildflowers, or December to February for thick snow. Permits are required and issued in Gangtok.', None, 'https://www.sikkimtourism.gov.in/', place_image('yumthang-valley')),
        (36, 30, 'pemayangtse-monastery', 'Pemayangtse Monastery', 'Founded in 1705 by Lama Lhatsun Chempo, Pemayangtse is one of Sikkim’s oldest, most prestigious Nyingma Buddhist monasteries. Perched at 2,085 metres, it commands panoramic views of Mount Kangchenjunga and houses the legendary seven-tiered wooden masterpiece depicting Guru Padmasambhava’s celestial palace, Sangthokpalri.', 'spiritual', 27.3047, 88.2528, 'Located 2 km from Pelling and 110 km from Gangtok via Ravangla. Well connected by shared and private taxis from Pelling town.', 'Open daily 9:00 AM to 6:00 PM. Modest dress required. The ancient Rabdentse Palace ruins are located within a scenic 15-minute forested walk from the monastery gate.', None, 'https://www.sikkimtourism.gov.in/', place_image('pemayangtse-monastery')),
        (37, 32, 'solophok-char-dham', 'Siddhesvara Dhaam (Char Dham), Namchi', 'A grand pilgrimage and cultural complex atop Solophok Hill in southern Sikkim, featuring a colossal 108-foot statue of Lord Shiva seated above a temple with twelve Jyotirlinga shrines. The complex also features authentic scaled replicas of India’s four sacred Char Dham temples set against breathtaking Himalayan vistas.', 'heritage', 27.1642, 88.3375, 'Located 5 km from Namchi town and 78 km from Gangtok. Accessible by taxi or bus via the Namchi-Melli highway.', 'Open daily 6:30 AM to 8:30 PM. Wheelchair accessible with paved walkways, vegetarian dining facilities, musical fountain evening shows, and extensive parking.', None, 'https://www.sikkimtourism.gov.in/', place_image('solophok-char-dham')),
        (38, 31, 'khangchendzonga-national-park', 'Khangchendzonga National Park', 'India’s only Mixed UNESCO World Heritage Site, covering an extraordinary altitudinal range from subtropical valleys to the snow-capped summit of Mount Kangchenjunga (8,586 m, the world’s third-highest peak). Revered in Sikkimese culture as a sacred Beyul (hidden holy land), it shelters rare Himalayan wildlife including the snow leopard and red panda.', 'heritage', 27.7000, 88.1500, 'Trekking entry points begin at Yuksom in Gyalshing district or Lachen in Mangan district. Reached by road from Gangtok to Yuksom (125 km).', 'UNESCO World Heritage inscribed property. Trekking requires prior forest department permits, certified local guides, and proper mountaineering gear. Best trekking seasons are March-May and October-November.', 5, 'https://whc.unesco.org/en/list/1513/', place_image('khangchendzonga-national-park')),
    ]
    db.executemany('''INSERT OR IGNORE INTO places
        (id,district_id,slug,name,description,category,latitude,longitude,how_to_reach,practical_notes,heritage_id,source_url,image_url)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', places)
    db.executemany('UPDATE places SET image_url=? WHERE id=?', [(p[12], p[0]) for p in places])

    for place in places:
        if place[1] in (29, 30, 31, 32, 33, 34):
            months = [3, 4, 5, 10, 11, 12]
        elif place[1] in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 27, 28):
            months = [10, 11, 12, 1, 2, 3]
        else:
            months = [10, 11, 12, 1, 2]
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
        (26, 'Sao Joao Festival', 'Goa’s joyous monsoon water festival celebrated on the Feast of St. John the Baptist. Revellers wearing vibrant kopel floral crowns dance to traditional songs and jump into village wells, ponds and streams to celebrate new beginnings.', 'fixed', 'https://www.goa-tourism.com/', [('goa', 'north-goa')], [6]),
        (27, 'Feast of St. Francis Xavier', 'The grand annual feast celebrated at the Basilica of Bom Jesus in Old Goa, drawing tens of thousands of pilgrims worldwide for solemn open-air masses, fairgrounds and cultural processions honouring the Patron Saint of Goa.', 'fixed', 'https://www.goa-tourism.com/', [('goa', 'north-goa'), ('goa', 'south-goa')], [12]),
        (28, 'Losar (Tibetan New Year)', 'The Tibetan Buddhist New Year celebrated with traditional Cham mask dances at Rumtek and Enchey monasteries, lighting of butter lamps, family feasts of gutuk dumplings and ceremonial prayer flags hoisted atop hills.', 'lunar', 'https://www.sikkimtourism.gov.in/', [('sikkim', 'gangtok'), ('sikkim', 'pakyong')], [2, 3]),
        (29, 'Saga Dawa', 'The most sacred Buddhist festival commemorating the birth, enlightenment and parinirvana of Gautama Buddha. Monks lead grand processions carrying the holy Kangyur scriptures through Gangtok accompanied by conch shells and Tibetan horns.', 'lunar', 'https://www.sikkimtourism.gov.in/', [('sikkim', 'gangtok')], [5, 6]),
        (30, 'Pang Lhabsol', 'A festival unique to Sikkim, honouring Mount Kangchenjunga as the guardian deity of the kingdom. Spectacular warrior dances (Chaam) are performed at Pemayangtse and Tsuklakhang palaces to invoke divine protection and commemorate the historical blood brotherhood treaty between the Lepchas and Bhutias.', 'lunar', 'https://www.sikkimtourism.gov.in/', [('sikkim', 'gyalshing'), ('sikkim', 'gangtok')], [8, 9]),
        (31, 'Losoong / Namsoong', 'The Sikkimese harvest festival and the New Year for the Bhutia and Lepcha communities. Monasteries across Sikkim erupt in sacred black-hat and animal-mask Cham dances, archery competitions, vibrant family feasts, and traditional folk sports.', 'lunar', 'https://www.sikkimtourism.gov.in/', [('sikkim', 'gangtok'), ('sikkim', 'gyalshing')], [12]),
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
