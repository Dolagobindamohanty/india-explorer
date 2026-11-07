import os
from PIL import Image

# List of missing image paths from the validation errors
missing_images = [
    "/assets/places/solomon-temple-aizawl.jpg",
    "/assets/places/dzukou-valley.jpg",
    "/assets/places/rih-dil-lake.jpg",
    "/assets/places/murlen-national-park.jpg",
    "/assets/places/vaphai-waterfall.jpg",
    "/assets/places/hmunhmung-heritage-village.jpg",
    "/assets/places/kawlbem-waterfall.jpg",
    "/assets/places/khawzawl-park.jpg",
    "/assets/places/tiau-river.jpg",
    "/assets/places/khanmun-waterfall.jpg",
    "/assets/places/tamdil-lake.jpg",
    "/assets/places/ngengpui-wildlife-sanctuary.jpg",
    "/assets/places/saikao-village.jpg",
    "/assets/places/lunglei-viewpoint.jpg",
    "/assets/places/thorangtlang-sanctuary.jpg",
    "/assets/places/pallel-heritage.jpg",
    "/assets/places/dampa-tiger-reserve.jpg",
    "/assets/places/rwmzawm-viewpoint.jpg",
    "/assets/places/saitual-viewpoint.jpg",
    "/assets/places/serchhip-lake.jpg",
    "/assets/places/vantawng-waterfall.jpg",
    "/assets/places/palak-lake.jpg",
    "/assets/places/siaha-town.jpg",
]

# Create a 1x1 placeholder (RGB for JPEG)
placeholder = Image.new('RGB', (1, 1), (200, 200, 200))

static_places_dir = "static/assets/places"
os.makedirs(static_places_dir, exist_ok=True)

for img_path in missing_images:
    filename = os.path.basename(img_path)
    full_path = os.path.join(static_places_dir, filename)
    placeholder.save(full_path, 'JPEG')
    print(f"Created: {full_path}")

print(f"\nCreated {len(missing_images)} placeholder images")