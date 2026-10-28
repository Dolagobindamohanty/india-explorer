const root = document.querySelector('#app');
const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const categories = [
  ['heritage', '🏛', 'Heritage'], ['beach', '🏖', 'Beaches'], ['nature', '🌿', 'Nature'],
  ['spiritual', '🙏', 'Spiritual'], ['culture', '🎨', 'Culture']
];
const shortMonth = n => months[n - 1].slice(0, 3);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fallbackImage = state => state === 'kerala'
  ? 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=900&q=80'
  : state === 'rajasthan'
    ? 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=900&q=80'
    : 'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=80';
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
  const badge = p.heritage_id ? 'UNESCO heritage' : categoryLabel(p.category);
  const placeArtwork = p.image_url || `/assets/places/${p.slug}.jpg`;
  return `<article class="card place-card"><a href="/place/${esc(p.slug)}" class="art" aria-label="Explore ${esc(p.name)}"><img loading="lazy" src="${esc(placeArtwork)}" alt="${esc(p.name)} destination photo" onerror="this.onerror=null;this.src='/assets/places/${esc(p.slug)}.jpg'"><strong class="art-title">${esc(p.name)}</strong><span class="badge">${esc(badge)}</span></a><div class="card-body"><div class="meta">${esc(p.district)} · ${esc(p.state)}</div><h3><a href="/place/${esc(p.slug)}">${esc(p.name)}</a></h3><p>${esc(p.description)}</p><div class="card-bottom"><span>${p.distance_km != null ? `${p.distance_km} km straight-line` : p.best_months.map(shortMonth).join(' · ')}</span>${saveButton(p)}</div></div></article>`;
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
  return items.length ? `<div class="cards two">${items.map(f => `<article class="festival"><span class="badge">Typically ${f.months.map(shortMonth).join(' / ')}</span><h3>${esc(f.name)}</h3><p>${esc(f.description)}</p><p>${f.districts.map(d => `<a href="/district/${esc(d.slug)}">${esc(d.name)}</a>`).join(' · ')}</p><small>${f.occurrences.length ? f.occurrences.map(o => `${esc(o.starts_on)} – ${esc(o.ends_on)}`).join(', ') : 'Annual dates not confirmed in this directory.'}</small><p><a href="${esc(f.source_url)}" target="_blank" rel="noopener noreferrer">Check the tourism authority ↗</a></p></article>`).join('')}</div>` : '<p class="empty">No festivals recorded for this selection yet. This does not mean there are no local celebrations.</p>';
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

async function home() {
  const [states, territories, places] = await Promise.all([api('states'), api('union-territories'), api('places')]);
  const trending = places.slice(0, 5);
  const recentPlaces = recent.length ? recent.map(slug => places.find(place => place.slug === slug)).filter(Boolean) : [];
  return `<section class="hero hero-search-first"><div class="hero-copy"><p class="eyebrow">Your next Indian story starts here</p><h1>Explore<br><span>Incredible India.</span></h1><p class="hero-lead">Discover states, cities, monuments and culture—one curious search at a time.</p>${homeSearch()}<p class="search-hint">Try “Kerala”, “heritage”, or “beaches”</p></div><div class="hero-art" role="img" aria-label="Indian landscape collage"><div class="hero-art-caption"><span>Many places. One beautiful beginning.</span><strong>Go a little further.</strong></div></div></section><section class="popular-section"><div class="section-head"><div><p class="eyebrow">Start with a feeling</p><h2>What are you looking for?</h2></div></div><div class="category-chips">${categoryChips()}</div></section><section class="section"><div class="section-head"><div><p class="eyebrow">Keep exploring</p><h2>Trending destinations</h2></div><a href="/explore">View all <span class="arrow">↗</span></a></div>${cards(trending)}</section>${recentPlaces.length ? `<section class="section recent-section"><div class="section-head"><div><p class="eyebrow">Pick up where you left off</p><h2>Continue exploring</h2></div></div>${cards(recentPlaces)}</section>` : ''}<section class="section directory-preview"><div class="section-head"><div><p class="eyebrow">The full directory</p><h2>Every corner has a story.</h2><p>Browse all ${states.length} states and ${territories.length} union territories, then go district by district.</p></div><a class="button secondary" href="/area">Browse the map of places</a></div><div class="mini-stats"><div><strong>${states.length}</strong><span>States</span></div><div><strong>${territories.length}</strong><span>Union territories</span></div><div><strong>809</strong><span>District entries</span></div><div><strong>${places.length}</strong><span>Detailed places</span></div></div></section>`;
}
async function statePage(slug) {
  const s = await api('states/' + encodeURIComponent(slug));
  const cover = image(s.cover_image_url, s.slug);
  return `${breadcrumb([[s.name]])}<div class="state-hero" style="background-image:linear-gradient(90deg,rgba(30,58,95,.92),rgba(30,58,95,.28)),url('${esc(cover)}')"><div><p class="eyebrow">${s.kind === 'union_territory' ? 'Union territory' : 'State'} guide</p><h1>${esc(s.name)}</h1><p>${esc(s.description)}</p></div></div><div class="section-head"><div><p class="eyebrow">Administrative directory</p><h2>All districts in ${esc(s.name)}</h2></div><span class="meta">${s.districts.length} district entries</span></div><div class="districts">${s.districts.map(d => `<a href="/district/${esc(d.slug)}">${esc(d.name)} <span>↗</span></a>`).join('')}</div><p class="directory-note">Detailed tourist places are added district by district after editorial verification.</p><section class="section"><div class="section-head"><h2>Places with a story</h2></div>${cards(s.places)}</section>`;
}
async function districtPage(slug) {
  const d = await api('districts/' + encodeURIComponent(slug));
  return `${breadcrumb([[d.state, '/state/' + d.state_slug], [d.name]])}<p class="eyebrow">Your local field guide</p><h1>${esc(d.name)}</h1><p class="lead">${esc(d.description)}</p><div class="band"><div><h3>A taste of the district</h3><p>${esc(d.food_notes)}</p></div><a class="source" href="${esc(d.source_url)}" target="_blank" rel="noopener noreferrer">Official information ↗</a></div><section class="section"><h2>Make a day of it</h2>${cards(d.places)}</section><section class="section"><h2>Local celebrations</h2><p>Typical months help with inspiration. Confirm the annual programme before making bookings.</p>${festivalCards(d.festivals)}</section>`;
}
async function placePage(slug) {
  const p = await api('places/' + encodeURIComponent(slug));
  saveRecent(p.slug);
  return `${breadcrumb([[p.state,'/state/'+p.state_slug],[p.district,'/district/'+p.district_slug],[p.name]])}<p class="eyebrow">${esc(categoryLabel(p.category))} · ${esc(p.district)}</p><h1>${esc(p.name)}</h1><div class="detail"><div><p class="lead">${esc(p.description)}</p>${p.heritage_id ? `<p class="badge">UNESCO World Heritage</p><p>Listed property: <a class="source" href="${esc(p.unesco_url)}" target="_blank" rel="noopener noreferrer">${esc(p.heritage_name)} ↗</a></p>` : ''}<h3>How to reach</h3><p>${esc(p.how_to_reach)}</p><h3>Before you go</h3><p>${esc(p.practical_notes)}</p><p class="notice">Pilot editorial entry · ${p.last_verified_at ? 'Last checked: '+esc(p.last_verified_at) : 'Not yet independently verified'}. Confirm access, fees and opening hours with the official source.</p><a class="source" href="${esc(p.source_url)}" target="_blank" rel="noopener noreferrer">Official reference ↗</a></div><aside><h3>A good time to go</h3><p>${p.best_months.map(n => months[n-1]).join(', ')}</p><p class="fine-print">Indicative seasonal guidance, not a weather forecast.</p><h3>Find your way</h3><p><a class="source" href="https://www.openstreetmap.org/?mlat=${p.latitude}&mlon=${p.longitude}#map=14/${p.latitude}/${p.longitude}" target="_blank" rel="noopener noreferrer">Open location on map ↗</a></p>${saveButton(p)}</aside></div><section class="section"><h2>A little further along</h2><p>Nearby places sorted by straight-line distance, not road travel time.</p>${cards(p.nearby)}</section>`;
}
async function explorePage(query) {
  const params = new URLSearchParams(query || '');
  const [states, places] = await Promise.all([api('states'), api('places?' + params)]);
  return `${breadcrumb([['Destinations']])}<p class="eyebrow">Follow your curiosity</p><h1>Find your kind of place.</h1><p>Browse our directory by season, state and interest.</p><form id="filters" class="filters"><div class="filter-search"><span>⌕</span><input name="q" placeholder="Search places or districts" aria-label="Search places" value="${esc(params.get('q') || '')}"></div><select name="state" aria-label="State"><option value="">All states and UTs</option>${states.map(s => `<option value="${esc(s.slug)}" ${params.get('state') === s.slug ? 'selected' : ''}>${esc(s.name)}</option>`).join('')}</select><select name="month" aria-label="Best travel month"><option value="">Any month</option>${months.map((m,i) => `<option value="${i+1}" ${params.get('month') === String(i+1) ? 'selected' : ''}>${m}</option>`).join('')}</select><select name="category" aria-label="Interest"><option value="">Any interest</option>${categories.map(([value,, label]) => `<option value="${value}" ${params.get('category') === value ? 'selected' : ''}>${label}</option>`).join('')}</select><label class="check"><input type="checkbox" name="unesco" value="true" ${params.get('unesco') === 'true' ? 'checked' : ''}> UNESCO only</label><button class="button">Find places</button></form><div class="results-heading"><p>${places.length} detailed places found</p><div class="category-chips compact">${categoryChips()}</div></div>${cards(places)}`;
}
async function monthPage(value) {
  const month = Number(value);
  if (!Number.isInteger(month) || month < 1 || month > 12) throw new Error('Choose a month from January to December.');
  const [festivals, places] = await Promise.all([api('festivals?month='+month),api('places?month='+month)]);
  return `${breadcrumb([['By month']])}<p class="eyebrow">Let the calendar be your compass</p><h1>India in ${months[month-1]}.</h1><p>Seasonal inspiration and typical festival months from our pilot districts.</p><div class="month-grid">${months.map((m,i) => `<a href="/month/${i+1}" class="${i+1===month?'active':''}">${m.slice(0,3)}</a>`).join('')}</div><section class="section"><h2>Celebrations to discover</h2><p>These are recurring seasonal windows, not confirmed dates for a specific year.</p>${festivalCards(festivals)}</section><section class="section"><h2>A good season for…</h2>${cards(places)}</section>`;
}
async function areaPage() {
  const [states, territories] = await Promise.all([api('states'), api('union-territories')]);
  const group = (items, label) => `<section class="section"><p class="eyebrow">${label}</p><h2>${label === 'States' ? 'Choose a state' : 'Choose a union territory'}</h2><div class="districts">${items.map(r => `<a href="/state/${esc(r.slug)}">${esc(r.name)} · ${r.district_count} districts ↗</a>`).join('')}</div></section>`;
  return `${breadcrumb([['Explore by region']])}<p class="eyebrow">Start close to home</p><h1>Every corner has a story.</h1><p class="lead">Choose a state or union territory, then select a district for places, local food and celebrations.</p>${group(states, 'States')}${group(territories, 'Union territories')}`;
}
function aboutPage() { return `${breadcrumb([['About']])}<p class="eyebrow">Built for curious travellers</p><h1>Travel deeper,<br>one district at a time.</h1><p class="lead">India Explorer helps you move beyond a checklist of famous landmarks. Find the local context, heritage, celebrations and practical starting points that make a destination memorable.</p><div class="about-grid"><div><h3>Explore with context</h3><p>Browse India’s states and union territories, then follow the directory into districts and detailed places.</p></div><div><h3>Save your ideas</h3><p>Favorites and recently viewed places stay on this device, so planning feels personal without an account.</p></div><div><h3>Travel responsibly</h3><p>Tourism details and festival dates can change. Use the linked official sources to confirm plans before you go.</p></div></div>`; }

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
    else if (type === 'month') html = await monthPage(slug);
    else if (type === 'area') html = await areaPage();
    else if (type === 'about') html = aboutPage();
    else if (type === 'saved') { const places = (await api('places')).filter(p => saved.has(p.slug)); html = `${breadcrumb([['Saved places']])}<p class="eyebrow">For another day</p><h1>Your little collection.</h1><p>Saved on this browser. No account needed.</p>${places.length ? cards(places) : '<p class="empty">Tap Save on a destination to keep it here.</p>'}`; }
    else throw new Error('That page does not exist.');
    if (version !== routeVersion) return;
    root.innerHTML = html;
  } catch (error) {
    if (version !== routeVersion) return;
    root.innerHTML = `<div class="error-state"><h1>A small detour.</h1><p role="alert">${esc(error.message)}</p><a class="button" href="/">Back to exploring</a></div>`;
  }
  window.scrollTo(0,0);
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
window.addEventListener('hashchange', route);
route();
