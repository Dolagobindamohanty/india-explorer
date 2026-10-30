const root = document.querySelector('#app');
const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const categories = [
  ['heritage', '🏛', 'Heritage'], ['beach', '🏖', 'Beaches'], ['nature', '🌿', 'Nature'],
  ['spiritual', '🙏', 'Spiritual'], ['culture', '🎨', 'Culture']
];
const shortMonth = n => months[n - 1].slice(0, 3);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fallbackImage = state => state ? `/assets/states/${state}.jpg` : '/assets/state-cover.svg';
const image = (url, state) => url || fallbackImage(state);
const readList = key => { try { const data = JSON.parse(localStorage.getItem(key) || '[]'); return Array.isArray(data) ? data.filter(x => typeof x === 'string') : []; } catch { return []; } };
let saved = new Set(readList('india-locally-saved'));
let recent = readList('india-locally-recent');
let routeVersion = 0;

function updateCount() { const count = document.querySelector('#saved-count'); if (count) count.textContent = saved.size; }
function saveRecent(slug) {
  recent = [slug, ...recent.filter(item => item !== slug)].slice(0, 5);
  try { localStorage.setItem('india-locally-recent', JSON.stringify(recent)); } catch { /* optional enhancement */ }
}
function categoryLabel(value) { return categories.find(item => item[0] === value)?.[2] || value || 'Destination'; }
function saveButton(p) { return `<button class="save" data-save="${esc(p.slug)}" aria-pressed="${saved.has(p.slug)}" aria-label="Save ${esc(p.name)}">${saved.has(p.slug) ? '♥ Saved' : '♡ Save'}</button>`; }
function placeCard(p) {
  let badge = categoryLabel(p.category);
  if (p.heritage_designation === 'world_heritage_site') badge = 'UNESCO World Heritage';
  else if (p.heritage_designation === 'component_site') badge = 'UNESCO Component';
  else if (p.heritage_designation === 'tentative_list') badge = 'UNESCO Tentative List';
  const placeArtwork = p.image_url || `/assets/places/${p.slug}.jpg`;
  const timing = p.distance_km != null ? `${p.distance_km} km straight-line` : p.best_months.length ? `Best in ${p.best_months.map(shortMonth).join(' · ')}` : 'Seasonal details pending';
  const feeBadge = p.entry_fee ? `<span class="badge fee-badge">🎟 ${esc(p.entry_fee)}</span>` : '';
  const sectorDisplay = p.address ? `📍 ${esc(p.address)}` : `${esc(p.district)} · ${esc(p.state)}`;
  return `<article class="card place-card" data-category="${esc(p.category)}"><a href="/place/${esc(p.slug)}" class="art" aria-label="Explore ${esc(p.name)}"><img loading="lazy" src="${esc(placeArtwork)}" alt="${esc(p.name)} destination photo" onerror="this.onerror=null;this.src='/assets/places/${esc(p.slug)}.jpg'"><span class="badge">${esc(badge)}</span>${feeBadge}</a><div class="card-body"><div class="meta">${sectorDisplay}</div><h3><a href="/place/${esc(p.slug)}">${esc(p.name)}</a></h3><p>${esc(p.description)}</p><div class="card-bottom"><span>${timing}</span>${saveButton(p)}</div></div></article>`;
}
function regionCard(r, kind) {
  const initials = r.name.split(/\s+/).map(word => word[0]).slice(0, 2).join('');
  const cover = r.cover_image_url
    ? `<div class="art"><img src="${esc(r.cover_image_url)}" alt="${esc(r.name)} destination image" loading="lazy" onerror="this.onerror=null;this.parentElement.classList.add('image-missing');this.remove()"></div>`
    : `<div class="directory-art" aria-hidden="true"><strong>${esc(initials)}</strong></div>`;
  return `<a class="card region-card" href="/state/${esc(r.slug)}">${cover}<div class="card-body"><div class="meta">${kind} · ${r.district_count} districts</div><h3>${esc(r.name)} <span class="arrow">↗</span></h3><p>${esc(r.description)}</p><div class="card-bottom"><span>${r.place_count} detailed places</span><span class="source">Explore</span></div></div></a>`;
}
function cards(items) { return items.length ? `<div class="cards">${items.map(placeCard).join('')}</div>` : '<p class="empty">No places match yet. Try another month or filter. Our pilot directory is still small.</p>'; }
function skeletonCards(count = 3) { return `<div class="cards skeleton-cards">${Array.from({length: count}, () => '<div class="skeleton-card"><div class="skeleton skeleton-image"></div><div class="skeleton skeleton-line"></div><div class="skeleton skeleton-line short"></div></div>').join('')}</div>`; }
function categoryChips() { return categories.map(([value, icon, label]) => `<a class="category-chip" href="/explore?category=${value}"><span>${icon}</span>${label}</a>`).join(''); }
function festivalCards(items) {
  return items.length ? `<div class="cards two">${items.map(f => {
    const locations = (f.districts || []).map(d => `<span class="festival-location">📍 <strong>${esc(d.state || '')}</strong>: <a href="/district/${esc(d.slug)}">${esc(d.name)}</a></span>`).join(' ');
    const sourceLink = f.source_url ? `<a class="source" href="${esc(f.source_url)}" target="_blank" rel="noopener noreferrer">Official tourism reference ↗</a>` : '';
    const monthsStr = (f.months || []).map(shortMonth).join(' / ');
    return `<article class="card festival-card"><div class="card-body"><div class="meta">${locations || '<span class="festival-location">📍 Pan-India</span>'}</div><h3>${esc(f.name)}</h3><p>${esc(f.description)}</p><div class="card-bottom"><span>🗓 Typically in ${esc(monthsStr)}</span>${sourceLink}</div></div></article>`;
  }).join('')}</div>` : '<p class="empty">No festivals recorded for this selection yet.</p>';
}
function breadcrumb(items) { return `<div class="breadcrumb"><a href="/">Home</a>${items.map(([label, link]) => ` / ${link ? `<a href="${link}">${esc(label)}</a>` : esc(label)}`).join('')}</div>`; }
function homeSearch() { return `<form id="home-search" class="hero-search"><span aria-hidden="true">⌕</span><input name="q" placeholder="Search destinations, states or districts…" aria-label="Search destinations"><button type="submit">Search</button></form>`; }

async function api(path) {
  const response = await fetch('/api/' + path);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'We could not load this page. Please try again.');
  }
  return response.json();
}

const HERO_SLIDES = [
  { img: '/assets/places/konark-sun-temple.jpg', sub: 'Puri, Odisha', title: 'Konark Sun Temple' },
  { img: '/assets/states/uttar-pradesh.jpg', sub: 'Agra, Uttar Pradesh', title: 'Taj Mahal' },
  { img: '/assets/places/aguada-fort.jpg', sub: 'North Goa', title: 'Fort Aguada & Lighthouse' },
  { img: '/assets/states/punjab.jpg', sub: 'Amritsar, Punjab', title: 'Harmandir Sahib (Golden Temple)' },
  { img: '/assets/places/alappuzha-backwaters.jpg', sub: 'Alappuzha, Kerala', title: 'Backwaters of Kerala' },
  { img: '/assets/states/rajasthan.jpg', sub: 'Jaipur, Rajasthan', title: 'Hawa Mahal (Pink City)' },
  { img: '/assets/states/maharashtra.jpg', sub: 'Mumbai, Maharashtra', title: 'Gateway of India' },
  { img: '/assets/states/west-bengal.jpg', sub: 'Kolkata, West Bengal', title: 'Victoria Memorial' },
  { img: '/assets/places/puri-jagannath-temple.jpg', sub: 'Puri, Odisha', title: 'Shree Jagannath Temple' },
  { img: '/assets/states/jammu-and-kashmir.jpg', sub: 'Srinagar, Jammu & Kashmir', title: 'Dal Lake Shikaras' },
  { img: '/assets/places/palolem-beach.jpg', sub: 'Canacona, South Goa', title: 'Palolem Beach' },
  { img: '/assets/states/ladakh.jpg', sub: 'Ladakh', title: 'Thiksey Monastery' },
];

function heroSlidesHtml() {
  const slidesHtml = HERO_SLIDES.map((s, i) => `<div class="hero-slide ${i === 0 ? 'active' : ''}" style="background-image:linear-gradient(180deg,rgba(20,38,32,0.15) 0%,rgba(20,38,32,0.85) 100%),url('${s.img}')" data-caption-sub="${esc(s.sub)}" data-caption-title="${esc(s.title)}"></div>`).join('');
  const dotsHtml = HERO_SLIDES.map((s, i) => `<span class="hero-dot ${i === 0 ? 'active' : ''}" data-slide-index="${i}" role="button" aria-label="Slide ${i+1}: ${esc(s.title)}"></span>`).join('');
  return `<div class="hero-art" id="hero-slideshow" role="region" aria-label="Featured destinations slideshow"><div class="hero-slides">${slidesHtml}</div><div class="hero-art-caption"><span id="hero-art-sub">${esc(HERO_SLIDES[0].sub)}</span><strong id="hero-art-title">${esc(HERO_SLIDES[0].title)}</strong><div class="hero-dots" aria-label="Slideshow navigation">${dotsHtml}</div></div></div>`;
}

function initHeroSlideshow() {
  const container = document.querySelector('#hero-slideshow');
  if (!container) return;
  const slides = container.querySelectorAll('.hero-slide');
  if (slides.length <= 1) return;
  const subEl = container.querySelector('#hero-art-sub');
  const titleEl = container.querySelector('#hero-art-title');
  const dots = container.querySelectorAll('.hero-dot');
  let current = 0;
  let timer = null;

  function update(index) {
    current = index;
    slides.forEach((s, i) => s.classList.toggle('active', i === current));
    dots.forEach((d, i) => d.classList.toggle('active', i === current));
    const activeSlide = slides[current];
    if (subEl && activeSlide.dataset.captionSub) subEl.textContent = activeSlide.dataset.captionSub;
    if (titleEl && activeSlide.dataset.captionTitle) titleEl.textContent = activeSlide.dataset.captionTitle;
  }

  function next() {
    update((current + 1) % slides.length);
  }

  function startTimer() {
    if (timer) clearInterval(timer);
    timer = setInterval(next, 3600);
  }

  dots.forEach(dot => {
    dot.addEventListener('click', e => {
      e.preventDefault();
      const idx = Number(dot.dataset.slideIndex);
      if (!isNaN(idx)) {
        update(idx);
        startTimer();
      }
    });
  });

  container.addEventListener('mouseenter', () => { if (timer) clearInterval(timer); });
  container.addEventListener('mouseleave', () => startTimer());
  startTimer();
}

async function home() {
  const [states, territories, places] = await Promise.all([api('states'), api('union-territories'), api('places')]);
  const trending = places.slice(0, 6);
  const recentPlaces = recent.length ? recent.map(slug => places.find(place => place.slug === slug)).filter(Boolean) : [];
  const featuredStates = states.filter(s => ['odisha', 'rajasthan', 'kerala', 'goa', 'himachal-pradesh', 'tamil-nadu'].includes(s.slug)).slice(0, 6);
  return `<section class="hero hero-search-first"><div class="hero-copy"><p class="eyebrow">Your next Indian story starts here</p><h1>Explore<br><span>Incredible India.</span></h1><p class="hero-lead">Discover states, cities, monuments and culture—one curious search at a time.</p>${homeSearch()}<p class="search-hint">Try “Odisha”, “Kerala”, “heritage”, or “beaches”</p></div>${heroSlidesHtml()}</section><section class="popular-section"><div class="section-head"><div><p class="eyebrow">Start with a feeling</p><h2>What are you looking for?</h2></div></div><div class="category-chips">${categoryChips()}</div></section><section class="section"><div class="section-head"><div><p class="eyebrow">A curated starting point</p><h2>Featured destinations</h2></div><a href="/explore">View all <span class="arrow">↗</span></a></div>${cards(trending)}</section>${recentPlaces.length ? `<section class="section recent-section"><div class="section-head"><div><p class="eyebrow">Pick up where you left off</p><h2>Continue exploring</h2></div></div>${cards(recentPlaces)}</section>` : ''}<section class="section"><div class="section-head"><div><p class="eyebrow">Explore by region</p><h2>Featured States</h2><p>A glimpse into India’s diverse states. Explore them district by district.</p></div><a class="button secondary" href="/area">View all ${states.length} states & ${territories.length} UTs ↗</a></div><div class="cards">${featuredStates.map(s => regionCard(s, 'State')).join('')}</div><div style="margin-top:28px;text-align:center;"><a class="button" href="/area">Explore All ${states.length} States & ${territories.length} Union Territories ↗</a></div></section>`;
}
function categoryFilterHtml(placesList) {
  if (placesList.length < 4) return '';
  const cats = [...new Set(placesList.map(p => p.category).filter(Boolean))].sort();
  const catLabels = { heritage: '🏛 Heritage & Monuments', nature: '🌿 Nature & Gardens', culture: '🎨 Culture & City', spiritual: '🙏 Spiritual', beach: '🏖 Beaches' };
  const pills = [`<button type="button" class="cat-pill active" data-filter="all">All (${placesList.length})</button>`];
  cats.forEach(c => {
    const cnt = placesList.filter(p => p.category === c).length;
    pills.push(`<button type="button" class="cat-pill" data-filter="${c}">${catLabels[c] || c} (${cnt})</button>`);
  });
  return `<div class="category-filter-strip" id="category-filter-strip">${pills.join('')}</div>`;
}

function initCategoryFilterStrip() {
  const strip = document.getElementById('category-filter-strip');
  if (!strip) return;
  const pills = strip.querySelectorAll('.cat-pill');
  const cardElements = document.querySelectorAll('.card.place-card');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const filter = pill.dataset.filter;
      cardElements.forEach(c => {
        const cat = c.dataset.category;
        c.style.display = (filter === 'all' || cat === filter) ? '' : 'none';
      });
    });
  });
}

async function statePage(slug) {
  const s = await api('states/' + encodeURIComponent(slug));
  const cover = image(s.cover_image_url, s.slug);
  return `${breadcrumb([['States', '/area'], [s.name]])}<div class="state-hero" style="background-image:linear-gradient(180deg,rgba(15,28,24,0.08) 0%,rgba(15,28,24,0.65) 60%,rgba(15,28,24,0.92) 100%),url('${esc(cover)}')"><button type="button" class="hero-photo-toggle" aria-label="Toggle photo view" title="View unobstructed photo">👁 View Photo</button><div class="state-hero-card"><span class="hero-badge-pill">${esc(s.kind === 'union_territory' ? 'Union territory' : 'State')} Guide</span><h1>${esc(s.name)}</h1><p>${esc(s.description)}</p><div class="hero-stats-strip"><span>🏛 <strong>${s.districts.length}</strong> districts</span><span>📍 <strong>${s.places.length}</strong> curated attractions</span><a href="${esc(cover)}" target="_blank" rel="noopener noreferrer" class="hero-cta-btn" title="View landmark photo">🖼 Fullscreen Photo ↗</a></div></div></div><div class="section-head"><div><p class="eyebrow">Administrative directory</p><h2>All districts in ${esc(s.name)}</h2></div><span class="meta">${s.districts.length} district entries</span></div><div class="districts">${s.districts.map(d => `<a href="/district/${esc(d.slug)}">${esc(d.name)} <span>↗</span></a>`).join('')}</div><section class="section" id="destinations"><div class="section-head"><div><p class="eyebrow">Curated field guide</p><h2>Places with a story</h2></div><span class="meta">${s.places.length} attractions</span></div>${categoryFilterHtml(s.places)}${cards(s.places)}</section>`;
}
async function districtPage(slug) {
  const d = await api('districts/' + encodeURIComponent(slug));
  const cover = fallbackImage(d.state_slug);
  return `${breadcrumb([[d.state, '/state/' + d.state_slug], [d.name]])}<div class="state-hero district-hero" style="background-image:linear-gradient(180deg,rgba(15,28,24,0.08) 0%,rgba(15,28,24,0.65) 60%,rgba(15,28,24,0.92) 100%),url('${esc(cover)}')"><button type="button" class="hero-photo-toggle" aria-label="Toggle photo view" title="View unobstructed photo">👁 View Photo</button><div class="state-hero-card"><span class="hero-badge-pill">${esc(d.state)} · District Field Guide</span><h1>${esc(d.name)}</h1><p>${esc(d.description)}</p><div class="hero-stats-strip"><span>📍 <strong>${d.places.length}</strong> detailed attractions</span><span>🎉 <strong>${d.festivals.length}</strong> festivals</span><a href="${esc(cover)}" target="_blank" rel="noopener noreferrer" class="hero-cta-btn" title="View landmark photo">🖼 Fullscreen Photo ↗</a></div></div></div><div class="band"><div><h3>A taste of the district</h3><p>${esc(d.food_notes)}</p></div><a class="source" href="${esc(d.source_url)}" target="_blank" rel="noopener noreferrer">Official information ↗</a></div><section class="section" id="destinations"><div class="section-head"><div><p class="eyebrow">Curated attractions</p><h2>Make a day of it</h2></div><span class="meta">${d.places.length} attractions in ${esc(d.name)}</span></div>${categoryFilterHtml(d.places)}${cards(d.places)}</section><section class="section"><h2>Local celebrations</h2><p>Typical months help with inspiration. Confirm the annual programme before making bookings.</p>${festivalCards(d.festivals)}</section>`;
}
async function placePage(slug) {
  const p = await api('places/' + encodeURIComponent(slug));
  saveRecent(p.slug);
  const monthPills = months.map((m, idx) => {
    const isBest = (p.best_months || []).includes(idx + 1);
    return `<span class="season-pill ${isBest ? 'pill-best' : 'pill-off'}" title="${m}: ${isBest ? 'Peak season' : 'Low/Monsoon'}">${m.slice(0, 3)}</span>`;
  }).join('');
  const catTips = {
    heritage: 'Wear comfortable walking shoes with grip. A licensed monument guide helps unearth historical details.',
    beach: 'Swim only in designated lifeguard-patrolled zones. High-SPF sunscreen and light cottons recommended.',
    spiritual: 'Modest attire covering shoulders and knees is strictly required. Remove footwear and deposit electronics outside.',
    nature: 'Eco-sensitive sanctuary. Carry reusable water bottles, insect repellent, and avoid plastic litter.',
    culture: 'Support local artisan cooperatives and ask for permission before photographing people or private residences.'
  };
  const tip = catTips[p.category] || 'Check weather updates and confirm entry schedules with official tourism authorities.';

  let unescoBox = '';
  if (p.heritage_designation === 'world_heritage_site') {
    unescoBox = `<div class="unesco-detail-box"><span class="badge">UNESCO World Heritage Site</span><p>Officially inscribed World Heritage property: <a class="source" href="${esc(p.unesco_url)}" target="_blank" rel="noopener noreferrer">${esc(p.heritage_name)} ↗</a></p></div>`;
  } else if (p.heritage_designation === 'component_site') {
    unescoBox = `<div class="unesco-detail-box"><span class="badge">UNESCO Component Site</span><p>Component of serial World Heritage property: <a class="source" href="${esc(p.unesco_url)}" target="_blank" rel="noopener noreferrer">${esc(p.heritage_name)} ↗</a></p></div>`;
  } else if (p.heritage_designation === 'tentative_list') {
    unescoBox = `<div class="unesco-detail-box"><span class="badge">UNESCO Tentative List</span><p>Nominated on UNESCO’s Tentative List: <a class="source" href="${esc(p.unesco_url)}" target="_blank" rel="noopener noreferrer">${esc(p.heritage_name)} ↗</a></p></div>`;
  }

  const feeBox = p.entry_fee ? `<div class="aside-box"><h3>Official Entry Fee</h3><p class="entry-fee-highlight">🎟 <strong>${esc(p.entry_fee)}</strong></p></div>` : '';
  const addrBox = p.address ? `<div class="aside-box"><h3>Location / Address</h3><p>📍 ${esc(p.address)}</p></div>` : '';
  const imgUrl = p.image_url || fallbackImage(p.state_slug);
  const placeHero = `<div class="state-hero place-hero-banner" style="background-image:linear-gradient(180deg,rgba(15,28,24,0.06) 0%,rgba(15,28,24,0.55) 60%,rgba(15,28,24,0.92) 100%),url('${esc(imgUrl)}')"><button type="button" class="hero-photo-toggle" aria-label="Toggle photo view" title="View unobstructed photo">👁 View Photo</button><div class="state-hero-card place-hero-card"><span class="hero-badge-pill">${esc(categoryLabel(p.category))} · ${esc(p.district)} · ${esc(p.state)}</span><h1>${esc(p.name)}</h1><div class="hero-stats-strip"><span>📍 ${esc(p.address || p.district + ', ' + p.state)}</span>${p.entry_fee ? `<span>🎟 <strong>${esc(p.entry_fee)}</strong></span>` : ''}<a href="${esc(imgUrl)}" target="_blank" rel="noopener noreferrer" class="hero-cta-btn" title="View full resolution photo">🖼 Fullscreen Photo ↗</a></div></div></div>`;

  return `${breadcrumb([[p.state,'/state/'+p.state_slug],[p.district,'/district/'+p.district_slug],[p.name]])}${placeHero}<div class="detail"><div><p class="lead">${esc(p.description)}</p>${unescoBox}<h3>How to reach</h3><p>${esc(p.how_to_reach)}</p><h3>Before you go & practical notes</h3><p>${esc(p.practical_notes)}</p><div class="travel-tip-card"><strong>💡 Traveler’s Protocol:</strong> ${esc(tip)}</div><p class="notice">Pilot editorial entry · ${p.last_verified_at ? 'Last checked: '+esc(p.last_verified_at) : 'Not yet independently verified'}. Confirm access, fees and opening hours with the official source.</p><a class="source" href="${esc(p.source_url)}" target="_blank" rel="noopener noreferrer">Official reference ↗</a></div><aside>${feeBox}${addrBox}<div class="aside-box"><h3>Best time to visit</h3><p>Typical peak months: <strong>${p.best_months.map(n => months[n-1]).join(', ')}</strong></p><div class="season-pill-strip">${monthPills}</div><div class="season-legend"><span class="legend-dot best"></span> Peak Season <span class="legend-dot off"></span> Low/Monsoon</div></div><div class="aside-box"><h3>Coordinates</h3><p><a class="source" href="https://www.openstreetmap.org/?mlat=${p.latitude}&mlon=${p.longitude}#map=14/${p.latitude}/${p.longitude}" target="_blank" rel="noopener noreferrer">Open on OpenStreetMap ↗</a></p>${saveButton(p)}</div></aside></div><section class="section"><h2>A little further along</h2><p>Nearby places sorted by straight-line distance, not road travel time.</p>${cards(p.nearby)}</section>`;
}
async function explorePage(query) {
  const params = new URLSearchParams(query || '');
  const [states, places] = await Promise.all([api('states'), api('places?' + params)]);
  const placesJson = JSON.stringify(places.map(p => ({
    slug: p.slug,
    name: p.name,
    category: p.category,
    lat: p.latitude,
    lon: p.longitude,
    image_url: p.image_url || fallbackImage(p.state_slug),
    district: p.district,
    state: p.state
  })));
  return `${breadcrumb([['Destinations']])}<p class="eyebrow">Follow your curiosity</p><h1>Find your kind of place.</h1><p>Browse our directory by season, state and interest.</p><form id="filters" class="filters"><div class="filter-search"><span>⌕</span><input name="q" placeholder="Search places or districts" aria-label="Search places" value="${esc(params.get('q') || '')}"></div><select name="state" aria-label="State"><option value="">All states and UTs</option>${states.map(s => `<option value="${esc(s.slug)}" ${params.get('state') === s.slug ? 'selected' : ''}>${esc(s.name)}</option>`).join('')}</select><select name="month" aria-label="Best travel month"><option value="">Any month</option>${months.map((m,i) => `<option value="${i+1}" ${params.get('month') === String(i+1) ? 'selected' : ''}>${m}</option>`).join('')}</select><select name="category" aria-label="Interest"><option value="">Any interest</option>${categories.map(([value,, label]) => `<option value="${value}" ${params.get('category') === value ? 'selected' : ''}>${label}</option>`).join('')}</select><label class="check"><input type="checkbox" name="unesco" value="true" ${params.get('unesco') === 'true' ? 'checked' : ''}> UNESCO only</label><button class="button">Find places</button></form><div class="explore-toolbar"><p><strong>${places.length}</strong> detailed places found</p><div class="view-toggles"><button type="button" class="view-toggle active" id="view-grid-btn">⊞ Grid View</button><button type="button" class="view-toggle" id="view-map-btn">🗺 Interactive Map</button></div></div><div id="explore-map-container" class="explore-map-wrap" style="display:none;"><div id="explore-leaflet-map" class="explore-leaflet-map" data-places="${esc(placesJson)}"></div></div><div id="explore-grid-container">${cards(places)}</div>`;
}

async function circuitsPage() {
  const circuits = await api('circuits');
  return `${breadcrumb([['Curated travel circuits']])}<p class="eyebrow">Themed journeys</p><h1>Curated travel trails.</h1><p class="lead">Follow hand-crafted routes connecting iconic landmarks, sacred heritage, clifftop sea bastions, and high Himalayan valleys across India.</p><div class="cards two">${circuits.map(c => `
    <article class="card circuit-card">
      <a href="/circuit/${esc(c.slug)}" class="art">
        <img src="${esc(c.cover_image_url)}" alt="${esc(c.name)} trail photo" loading="lazy">
        <span class="badge">🧭 ${esc(c.duration)}</span>
      </a>
      <div class="card-body">
        <div class="meta">Trail · ${c.stops.length} curated stops · ${esc(c.best_season)}</div>
        <h3><a href="/circuit/${esc(c.slug)}">${esc(c.name)} <span class="arrow">↗</span></a></h3>
        <p>${esc(c.description)}</p>
        <div class="circuit-route-preview"><strong>Stops:</strong> ${c.stops.slice(0, 3).map(s => esc(s.name)).join(' → ')}${c.stops.length > 3 ? ` and ${c.stops.length - 3} more` : ''}</div>
        <div class="card-bottom">
          <span>🗓 Best: ${esc(c.best_season)}</span>
          <a class="button secondary compact" href="/circuit/${esc(c.slug)}">Explore trail ↗</a>
        </div>
      </div>
    </article>
  `).join('')}</div>`;
}

async function circuitPage(slug) {
  const c = await api('circuits/' + encodeURIComponent(slug));
  return `${breadcrumb([['Travel trails', '/circuits'], [c.name]])}
    <div class="state-hero" style="background-image:linear-gradient(90deg,rgba(30,58,95,.92),rgba(30,58,95,.28)),url('${esc(c.cover_image_url)}')">
      <div>
        <p class="eyebrow">Curated Trail · ${esc(c.duration)}</p>
        <h1>${esc(c.name)}</h1>
        <p>${esc(c.tagline)}</p>
      </div>
    </div>
    <div class="circuit-detail-header">
      <div class="circuit-meta-pill"><strong>Duration:</strong> ${esc(c.duration)}</div>
      <div class="circuit-meta-pill"><strong>Best season:</strong> ${esc(c.best_season)}</div>
      <div class="circuit-meta-pill"><strong>Stops:</strong> ${c.stops.length} destinations</div>
    </div>
    <p class="lead">${esc(c.description)}</p>
    <section class="section">
      <h2>Itinerary & stops</h2>
      <div class="circuit-timeline">
        ${c.stops.map(s => `
          <div class="timeline-stop">
            <div class="stop-badge">Stop ${s.stop_order}</div>
            <div class="stop-content">
              <h3><a href="/place/${esc(s.slug)}">${esc(s.name)} ↗</a></h3>
              <div class="meta">${esc(s.district)} · ${esc(s.state)} · ${esc(s.category.toUpperCase())}</div>
              <p>${esc(s.description)}</p>
              <div class="stop-note">💡 <strong>Trail note:</strong> ${esc(s.notes)}</div>
            </div>
          </div>
        `).join('')}
      </div>
    </section>
    <section class="section">
      <h2>Destinations on this trail</h2>
      ${cards(c.stops)}
    </section>`;
}

function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c);
}

function generateItineraryHtml(userPlaces) {
  const remaining = [...userPlaces];
  const ordered = [remaining.shift()];
  while (remaining.length > 0) {
    const current = ordered[ordered.length - 1];
    let nearestIdx = 0;
    let nearestDist = Infinity;
    remaining.forEach((p, idx) => {
      const d = haversineKm(current.latitude, current.longitude, p.latitude, p.longitude);
      if (d < nearestDist) {
        nearestDist = d;
        nearestIdx = idx;
      }
    });
    ordered.push(remaining.splice(nearestIdx, 1)[0]);
  }

  const days = [];
  for (let i = 0; i < ordered.length; i += 2) {
    days.push(ordered.slice(i, i + 2));
  }

  let shareText = `*My India Travel Itinerary*\nGenerated with India Explorer (https://india-explorer-hazel.vercel.app/saved)\n\n`;
  days.forEach((dayPlaces, dayIdx) => {
    shareText += `*Day ${dayIdx + 1}:*\n`;
    dayPlaces.forEach(p => {
      shareText += `• ${p.name} (${p.district}, ${p.state})\n`;
    });
    shareText += `\n`;
  });
  const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`;

  return `
    <div class="itinerary-card">
      <div class="itinerary-header">
        <div>
          <span class="eyebrow">Smart Route Planner</span>
          <h2>Your Custom ${days.length}-Day Route</h2>
          <p>${ordered.length} destinations sequenced by geographical proximity.</p>
        </div>
        <div class="itinerary-actions">
          <a class="button" href="${waUrl}" target="_blank" rel="noopener noreferrer">💬 Share to WhatsApp</a>
          <button class="button secondary" type="button" onclick="window.print()">🖨 Print / PDF</button>
        </div>
      </div>
      <div class="itinerary-days">
        ${days.map((dayPlaces, dIdx) => `
          <div class="itinerary-day-block">
            <div class="day-badge">Day ${dIdx + 1}</div>
            <div class="day-places">
              ${dayPlaces.map((p, pIdx) => {
                let distNote = '';
                if (pIdx > 0) {
                  const prev = dayPlaces[pIdx - 1];
                  const dist = haversineKm(prev.latitude, prev.longitude, p.latitude, p.longitude);
                  distNote = `<span class="leg-distance">🚗 ~${dist} km from previous stop</span>`;
                }
                return `
                  <div class="itinerary-stop">
                    <img src="${p.image_url || fallbackImage(p.state_slug)}" alt="${p.name}" class="stop-thumb">
                    <div>
                      <strong><a href="/place/${p.slug}">${p.name} ↗</a></strong>
                      <div class="meta">${p.district} · ${p.state} · ${p.category}</div>
                      <p>${p.description}</p>
                      ${distNote}
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

async function savedPage() {
  const allPlaces = await api('places');
  const userPlaces = allPlaces.filter(p => saved.has(p.slug));
  const itineraryHtml = userPlaces.length >= 2 ? generateItineraryHtml(userPlaces) : '';
  return `${breadcrumb([['Saved places']])}<p class="eyebrow">Trip planning & favorites</p><h1>Your saved collection.</h1><p class="lead">Save destinations across India as you explore. Turn your collection into a day-by-day smart travel itinerary, calculate road distances, and share directly to WhatsApp.</p>${itineraryHtml}<div class="section"><div class="section-head"><div><p class="eyebrow">All saved destinations</p><h2>Saved places (${userPlaces.length})</h2></div></div>${userPlaces.length ? cards(userPlaces) : '<p class="empty">Tap Save on any destination card to keep it here and build your itinerary.</p>'}</div>`;
}
async function festivalsPage(selectedMonth) {
  const monthNum = selectedMonth ? Number(selectedMonth) : null;
  const url = (monthNum && monthNum >= 1 && monthNum <= 12) ? 'festivals?month=' + monthNum : 'festivals';
  const festList = await api(url);
  const activeTitle = (monthNum && monthNum >= 1 && monthNum <= 12) ? `Festivals in ${months[monthNum - 1]}` : 'Festivals Across India';
  const activeHeading = (monthNum && monthNum >= 1 && monthNum <= 12) ? `Festivals in ${months[monthNum - 1]}.` : 'Celebrations across India.';
  const tabs = `<nav class="month-selector-tabs" aria-label="Filter festivals by month"><a href="/festivals" class="month-tab ${!monthNum ? 'active' : ''}">All Months</a>${months.map((m, i) => `<a href="/festivals?month=${i + 1}" class="month-tab ${monthNum === (i + 1) ? 'active' : ''}">${m.slice(0, 3)}</a>`).join('')}</nav>`;
  const notice = '<p class="notice">Festival months represent recurring seasonal windows. Always verify exact dates, venues and schedules with official state tourism authorities.</p>';
  return `${breadcrumb([['Festival calendar']])}<p class="eyebrow">${activeTitle}</p><h1>${activeHeading}</h1><p class="lead">Select a month to explore vibrant traditional festivals, fairs and celebrations across Indian states and districts.</p>${tabs}${notice}<p><strong>${festList.length}</strong> celebrations found across India</p>${festivalCards(festList)}`;
}

async function monthPage(value) {
  return festivalsPage(value);
}
async function areaPage() {
  const [states, territories] = await Promise.all([api('states'), api('union-territories')]);
  const group = (items, label) => `<section class="section"><p class="eyebrow">${label}</p><h2>${label === 'States' ? 'Choose a state' : 'Choose a union territory'}</h2><div class="cards">${items.map(r => regionCard(r, label === 'States' ? 'State' : 'Union territory')).join('')}</div></section>`;
  return `${breadcrumb([['Explore by region']])}<p class="eyebrow">Start close to home</p><h1>Every corner has a story.</h1><p class="lead">Choose a state or union territory, then select a district for places, local food and celebrations.</p><div class="state-search-box"><span>⌕</span><input type="text" id="state-filter-input" placeholder="Quick find a state or territory (e.g. Odisha, Sikkim, Goa)..." aria-label="Filter states"></div><div id="states-group-wrap">${group(states, 'States')}${group(territories, 'Union territories')}</div>`;
}
function aboutPage() { return `${breadcrumb([['About']])}<p class="eyebrow">Built for curious travellers</p><h1>Travel deeper,<br>one district at a time.</h1><p class="lead">India Explorer helps you move beyond a checklist of famous landmarks. Find the local context, heritage, celebrations and practical starting points that make a destination memorable.</p><div class="about-grid"><div><h3>Explore with context</h3><p>Browse India’s states and union territories, then follow the directory into districts and detailed places.</p></div><div><h3>Save your ideas</h3><p>Favorites and recently viewed places stay on this device, so planning feels personal without an account.</p></div><div><h3>Travel responsibly</h3><p>Tourism details and festival dates can change. Use the linked official sources to confirm plans before you go.</p></div></div>`; }

let exploreMapInstance = null;

function initExploreMap() {
  const container = document.getElementById('explore-leaflet-map');
  const mapWrap = document.getElementById('explore-map-container');
  const gridWrap = document.getElementById('explore-grid-container');
  const gridBtn = document.getElementById('view-grid-btn');
  const mapBtn = document.getElementById('view-map-btn');

  if (!container || !window.L) return;

  const placesDataRaw = container.dataset.places;
  let placesList = [];
  try {
    placesList = JSON.parse(placesDataRaw || '[]');
  } catch (e) {
    placesList = [];
  }

  function setupMap() {
    if (exploreMapInstance) {
      exploreMapInstance.remove();
      exploreMapInstance = null;
    }
    exploreMapInstance = L.map('explore-leaflet-map').setView([22.5, 82.0], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© OpenStreetMap contributors'
    }).addTo(exploreMapInstance);

    const bounds = [];
    placesList.forEach(p => {
      if (p.lat && p.lon) {
        bounds.push([p.lat, p.lon]);
        const marker = L.circleMarker([p.lat, p.lon], {
          radius: 8,
          fillColor: '#d46a3b',
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.95
        }).addTo(exploreMapInstance);

        const popupContent = `
          <div class="map-popup-card">
            <img src="${p.image_url}" alt="${p.name}">
            <div class="map-popup-body">
              <span class="badge">${p.category.toUpperCase()}</span>
              <h4>${p.name}</h4>
              <p>${p.district}, ${p.state}</p>
              <a href="/place/${p.slug}">View destination ↗</a>
            </div>
          </div>
        `;
        marker.bindPopup(popupContent);
      }
    });

    if (bounds.length > 0) {
      exploreMapInstance.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
    }
  }

  if (gridBtn && mapBtn) {
    gridBtn.onclick = () => {
      gridBtn.classList.add('active');
      mapBtn.classList.remove('active');
      if (gridWrap) gridWrap.style.display = 'block';
      if (mapWrap) mapWrap.style.display = 'none';
    };

    mapBtn.onclick = () => {
      mapBtn.classList.add('active');
      gridBtn.classList.remove('active');
      if (gridWrap) gridWrap.style.display = 'none';
      if (mapWrap) mapWrap.style.display = 'block';
      setupMap();
      setTimeout(() => {
        if (exploreMapInstance) exploreMapInstance.invalidateSize();
      }, 150);
    };
  }
}

function initAreaFilter() {
  const input = document.getElementById('state-filter-input');
  if (!input) return;
  input.oninput = () => {
    const term = input.value.trim().toLowerCase();
    const cards = document.querySelectorAll('#states-group-wrap .region-card');
    cards.forEach(card => {
      const title = card.querySelector('h3') ? card.querySelector('h3').textContent.toLowerCase() : '';
      card.style.display = title.includes(term) ? '' : 'none';
    });
  };
}

async function route() {
  const version = ++routeVersion;
  const rawRoute = location.hash.slice(1) || (location.pathname + location.search) || '/';
  const [path, query] = rawRoute.split('?');
  const [, type, slug] = path.split('/');
  root.innerHTML = `<section class="loading-shell" aria-live="polite"><div class="skeleton skeleton-kicker"></div><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-copy"></div>${skeletonCards(3)}<p class="loading-message">Connecting to the travel database…</p></section>`;
  try {
    let html;
    if (!type) html = await home();
    else if (type === 'state') html = await statePage(slug);
    else if (type === 'district') html = await districtPage(slug);
    else if (type === 'place') html = await placePage(slug);
    else if (type === 'explore') html = await explorePage(query);
    else if (type === 'circuits') html = await circuitsPage();
    else if (type === 'circuit') html = await circuitPage(slug);
    else if (type === 'festivals') {
      const params = new URLSearchParams(query || '');
      html = await festivalsPage(params.get('month'));
    }
    else if (type === 'month') html = await monthPage(slug);
    else if (type === 'area') html = await areaPage();
    else if (type === 'about') html = aboutPage();
    else if (type === 'saved') html = await savedPage();
    else throw new Error('That page does not exist.');
    if (version !== routeVersion) return;
    root.innerHTML = html;
    if (!type) initHeroSlideshow();
    if (type === 'explore') initExploreMap();
    if (type === 'area') initAreaFilter();
    if (type === 'state' || type === 'district') initCategoryFilterStrip();
  } catch (error) {
    if (version !== routeVersion) return;
    root.innerHTML = `<div class="error-state"><h1>A small detour.</h1><p role="alert">${esc(error.message)}</p><a class="button" href="/">Back to exploring</a></div>`;
  }
  window.scrollTo(0,0);
}

// Spotlight Search Controller
let cachedPlaces = null;
let cachedStates = null;
let cachedFestivals = null;

async function loadSpotlightData() {
  if (cachedPlaces) return;
  try {
    const [p, s, f] = await Promise.all([
      api('places'),
      api('states'),
      api('festivals')
    ]);
    cachedPlaces = p;
    cachedStates = s;
    cachedFestivals = f;
  } catch (err) {
    console.error('Failed to preload spotlight data', err);
  }
}

function openSpotlight(initialQuery = '') {
  const overlay = document.getElementById('spotlight-overlay');
  const input = document.getElementById('spotlight-input');
  if (!overlay || !input) return;
  overlay.style.display = 'flex';
  overlay.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  loadSpotlightData();
  if (initialQuery) {
    input.value = initialQuery;
    renderSpotlightResults(initialQuery);
  } else {
    input.value = '';
    setTimeout(() => input.focus(), 50);
    renderSpotlightResults('');
  }
}

function closeSpotlight() {
  const overlay = document.getElementById('spotlight-overlay');
  if (!overlay) return;
  overlay.style.display = 'none';
  overlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

function renderSpotlightResults(query) {
  const container = document.getElementById('spotlight-results');
  if (!container) return;
  const q = query.trim().toLowerCase();

  if (!q) {
    const totalPlaces = (cachedPlaces && cachedPlaces.length) ? cachedPlaces.length : 227;
    container.innerHTML = `<div class="spotlight-hint">Type to instantly search across ${totalPlaces} destinations, 807 districts, 36 regions, and festivals...</div>`;
    return;
  }

  const matchedPlaces = (cachedPlaces || []).filter(p =>
    p.name.toLowerCase().includes(q) ||
    p.district.toLowerCase().includes(q) ||
    p.state.toLowerCase().includes(q) ||
    p.category.toLowerCase().includes(q)
  ).slice(0, 8);

  const matchedStates = (cachedStates || []).filter(s =>
    s.name.toLowerCase().includes(q) ||
    s.description.toLowerCase().includes(q)
  ).slice(0, 4);

  const matchedFestivals = (cachedFestivals || []).filter(f =>
    f.name.toLowerCase().includes(q) ||
    f.description.toLowerCase().includes(q)
  ).slice(0, 4);

  let html = '';

  if (matchedPlaces.length > 0) {
    html += `<div class="spotlight-group-title">Destinations (${matchedPlaces.length})</div>`;
    html += matchedPlaces.map(p => `
      <a href="/place/${esc(p.slug)}" class="spotlight-item" onclick="closeSpotlight()">
        <img src="${esc(p.image_url || fallbackImage(p.state_slug))}" alt="${esc(p.name)}" class="spotlight-thumb">
        <div class="spotlight-info">
          <div class="spotlight-name">${esc(p.name)} <span class="spotlight-cat-tag">${esc(p.category)}</span></div>
          <div class="spotlight-sub">${esc(p.district)}, ${esc(p.state)} ${p.entry_fee ? `· 🎟 ${esc(p.entry_fee)}` : ''}</div>
        </div>
        <span class="spotlight-arrow">↗</span>
      </a>
    `).join('');
  }

  if (matchedStates.length > 0) {
    html += `<div class="spotlight-group-title">States & Territories (${matchedStates.length})</div>`;
    html += matchedStates.map(s => `
      <a href="/state/${esc(s.slug)}" class="spotlight-item" onclick="closeSpotlight()">
        <div class="spotlight-avatar">🏛</div>
        <div class="spotlight-info">
          <div class="spotlight-name">${esc(s.name)} <span class="spotlight-cat-tag">${esc(s.kind === 'union_territory' ? 'UT' : 'State')}</span></div>
          <div class="spotlight-sub">${s.district_count} districts · ${esc(s.description.slice(0, 75))}...</div>
        </div>
        <span class="spotlight-arrow">↗</span>
      </a>
    `).join('');
  }

  if (matchedFestivals.length > 0) {
    html += `<div class="spotlight-group-title">Festivals (${matchedFestivals.length})</div>`;
    html += matchedFestivals.map(f => `
      <a href="/festivals" class="spotlight-item" onclick="closeSpotlight()">
        <div class="spotlight-avatar">🎉</div>
        <div class="spotlight-info">
          <div class="spotlight-name">${esc(f.name)}</div>
          <div class="spotlight-sub">${esc(f.description.slice(0, 80))}...</div>
        </div>
        <span class="spotlight-arrow">↗</span>
      </a>
    `).join('');
  }

  if (!html) {
    container.innerHTML = `<div class="spotlight-no-results">No destinations, states, or festivals found matching "<strong>${esc(query)}</strong>". Try searching for "Taj Mahal", "Chandigarh", "Puri", or "Monastery".</div>`;
  } else {
    container.innerHTML = html;
  }
}

// Spotlight Keyboard & Click Events
document.addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    openSpotlight();
  } else if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
    e.preventDefault();
    openSpotlight();
  } else if (e.key === 'Escape') {
    closeSpotlight();
  }
});

document.addEventListener('click', e => {
  const spotlightBtn = e.target.closest('#spotlight-btn');
  if (spotlightBtn) {
    e.preventDefault();
    openSpotlight();
    return;
  }
  const closeBtn = e.target.closest('#spotlight-close');
  if (closeBtn) {
    closeSpotlight();
    return;
  }
  const tagBtn = e.target.closest('.spotlight-tag');
  if (tagBtn) {
    const q = tagBtn.dataset.q;
    const input = document.getElementById('spotlight-input');
    if (input) {
      input.value = q;
      renderSpotlightResults(q);
    }
    return;
  }
  const overlay = document.getElementById('spotlight-overlay');
  if (e.target === overlay) {
    closeSpotlight();
    return;
  }

  // Hero Photo View Toggle
  const photoToggle = e.target.closest('.hero-photo-toggle');
  if (photoToggle) {
    const hero = photoToggle.closest('.state-hero');
    if (hero) {
      const card = hero.querySelector('.state-hero-card');
      if (card) {
        const isCollapsed = card.classList.toggle('card-collapsed');
        photoToggle.textContent = isCollapsed ? '✕ Show Guide' : '👁 View Photo';
        photoToggle.classList.toggle('active', isCollapsed);
      }
    }
  }
});

const spotlightInput = document.getElementById('spotlight-input');
if (spotlightInput) {
  spotlightInput.addEventListener('input', e => {
    renderSpotlightResults(e.target.value);
  });
}

function submitSearch(form) { const params = new URLSearchParams(); for (const [key, value] of new FormData(form)) if (value) params.set(key, value); location.hash = '/explore' + (params.toString() ? `?${params}` : ''); }
document.addEventListener('submit', event => { if (event.target.id === 'filters' || event.target.id === 'home-search' || event.target.id === 'nav-search') { event.preventDefault(); submitSearch(event.target); } });
root.addEventListener('click', event => {
  const button = event.target.closest('[data-save]');
  if (button) { const slug = button.dataset.save; saved.has(slug) ? saved.delete(slug) : saved.add(slug); try { localStorage.setItem('india-locally-saved', JSON.stringify([...saved])); } catch { button.textContent = 'Storage unavailable'; return; } button.textContent = saved.has(slug) ? '♥ Saved' : '♡ Save'; button.setAttribute('aria-pressed', saved.has(slug)); updateCount(); if (location.hash === '#/saved') route(); }
});
document.querySelector('#theme-toggle').addEventListener('click', () => { const dark = document.body.dataset.theme !== 'dark'; document.body.dataset.theme = dark ? 'dark' : 'light'; localStorage.setItem('india-locally-theme', dark ? 'dark' : 'light'); document.querySelector('#theme-toggle').innerHTML = dark ? '☀ <span>Light</span>' : '☾ <span>Dark</span>'; });
document.querySelector('#menu-toggle').addEventListener('click', () => { const nav = document.querySelector('#nav-links'); const open = nav.classList.toggle('open'); document.querySelector('#menu-toggle').setAttribute('aria-expanded', open); });
document.querySelector('#nav-links').addEventListener('click', event => { if (event.target.closest('a')) document.querySelector('#nav-links').classList.remove('open'); });
document.body.dataset.theme = localStorage.getItem('india-locally-theme') || 'light';
if (document.body.dataset.theme === 'dark') document.querySelector('#theme-toggle').innerHTML = '☀ <span>Light</span>';
updateCount();
initHeroSlideshow();
initExploreMap();
initAreaFilter();
initCategoryFilterStrip();
if (document.body.dataset.serverRendered !== 'true') {
  window.addEventListener('hashchange', route);
  route();
}
