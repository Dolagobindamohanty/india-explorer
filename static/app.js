const root = document.querySelector('#app');
const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const shortMonth = n => months[n - 1].slice(0, 3);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fallbackImage = state => state === 'kerala'
  ? 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=900&q=80'
  : state === 'rajasthan'
    ? 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=900&q=80'
    : 'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=80';
const image = (url, state) => url || fallbackImage(state);
let saved;
try { const data = JSON.parse(localStorage.getItem('india-locally-saved') || '[]'); saved = new Set(Array.isArray(data) ? data.filter(x => typeof x === 'string') : []); }
catch { saved = new Set(); }
let routeVersion = 0;
async function api(path) {
  const response = await fetch('/api/' + path);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(typeof error.detail === 'string' ? error.detail : 'We could not load this page. Please try again.');
  }
  return response.json();
}
function updateCount() { document.querySelector('#saved-count').textContent = saved.size; }
updateCount();
function saveButton(p) { return `<button class="save" data-save="${esc(p.slug)}" aria-pressed="${saved.has(p.slug)}" aria-label="Save ${esc(p.name)}">${saved.has(p.slug) ? '♥ Saved' : '♡ Save'}</button>`; }
function placeCard(p) {
  return `<article class="card"><a href="#/place/${esc(p.slug)}" class="art" style="display:block" aria-label="Explore ${esc(p.name)}"><img loading="lazy" src="${esc(image(p.image_url, p.state_slug))}" alt="${esc(p.name)} destination image" onerror="this.onerror=null;this.src='${esc(fallbackImage(p.state_slug))}'"><span class="badge">${p.heritage_id ? 'UNESCO heritage' : esc(p.category)}</span></a><div class="card-body"><div class="meta">${esc(p.district)} · ${esc(p.state)}</div><h3><a href="#/place/${esc(p.slug)}">${esc(p.name)}</a></h3><p>${esc(p.description)}</p><div class="card-bottom"><span>${p.distance_km != null ? `${p.distance_km} km straight-line` : p.best_months.map(shortMonth).join(' · ')}</span>${saveButton(p)}</div></div></article>`;
}
function regionCard(r, kind) {
  const initials = r.name.split(/\s+/).map(word => word[0]).slice(0, 2).join('');
  const cover = r.cover_image_url
    ? `<div class="art"><img src="${esc(r.cover_image_url)}" alt="${esc(r.name)} destination image" loading="lazy" onerror="this.onerror=null;this.parentElement.classList.add('image-missing');this.remove()"></div>`
    : `<div class="directory-art" aria-hidden="true"><strong>${esc(initials)}</strong></div>`;
  return `<a class="card region-card" href="#/state/${esc(r.slug)}">${cover}<div class="card-body"><div class="meta">${kind} · ${r.district_count} districts</div><h3>${esc(r.name)} ↗</h3><p>${esc(r.description)}</p><div class="card-bottom"><span>${r.place_count} detailed places</span><span class="source">Explore</span></div></div></a>`;
}
function cards(items) { return items.length ? `<div class="cards">${items.map(placeCard).join('')}</div>` : '<p class="empty">No places match yet. Try another month or filter. Our pilot directory is still small.</p>'; }
function festivalCards(items) {
  return items.length ? `<div class="cards two">${items.map(f => `<article class="festival"><span class="badge">Typically ${f.months.map(shortMonth).join(' / ')}</span><h3>${esc(f.name)}</h3><p>${esc(f.description)}</p><p>${f.districts.map(d => `<a href="#/district/${esc(d.slug)}">${esc(d.name)}</a>`).join(' · ')}</p><small>${f.occurrences.length ? f.occurrences.map(o => `${esc(o.starts_on)} – ${esc(o.ends_on)}`).join(', ') : 'Annual dates not confirmed in this directory.'}</small><p><a href="${esc(f.source_url)}" target="_blank" rel="noopener noreferrer">Check the tourism authority ↗</a></p></article>`).join('')}</div>` : '<p class="empty">No festivals recorded for this selection yet. This does not mean there are no local celebrations.</p>';
}
function breadcrumb(items) { return `<div class="breadcrumb"><a href="#/">Home</a>${items.map(([label, link]) => ` / ${link ? `<a href="${link}">${esc(label)}</a>` : esc(label)}`).join('')}</div>`; }
async function legacyHome() {
  const [states, places] = await Promise.all([api('states'), api('places')]);
  return `<section class="hero"><div><p class="eyebrow">Many Indias. One place to begin.</p><h1>A little closer to<br>somewhere new.</h1><p>Beyond the famous landmarks, find the places, people and celebrations that make a district feel like nowhere else.</p><div class="buttons"><a class="button" href="#/explore">Plan a trip ↗</a><a class="button secondary" href="#/area">Explore my area</a></div><p style="font-size:11px;margin-top:25px">STARTING SMALL, EXPLORING DEEPLY · ${states.map(s => esc(s.name.toUpperCase())).join(' · ')}</p></div><div class="hero-image" role="img" aria-label="Illustrative Kerala backwater landscape"><div><span class="eyebrow" style="color:#cde5bd">Slow journeys, lasting stories</span><p><strong>The quieter side of India</strong></p><p>Discover a district →</p></div></div></section><section class="section"><div class="section-head"><div><p class="eyebrow">Choose your next chapter</p><h2>${states.length} states. A world of difference.</h2></div><span class="meta">Our pilot destinations</span></div><div class="cards">${states.map(s => `<a class="card" href="#/state/${esc(s.slug)}"><div class="art"><img src="${esc(image(s.cover_image_url, s.slug))}" alt="${esc(s.name)} destination image" loading="lazy" onerror="this.onerror=null;this.src='${esc(fallbackImage(s.slug))}'"></div><div class="card-body"><div class="meta">${s.district_count} pilot districts · ${s.place_count} places</div><h3>${esc(s.name)} ↗</h3><p>${esc(s.description)}</p></div></a>`).join('')}</div></section><div class="band"><div><p class="eyebrow">Travel with the seasons</p><h3>Sometimes the best destination is a celebration.</h3><p>Explore typical festival months and discover places for your travel season.</p></div><a href="#/month/8" class="button">Find your month →</a></div><section class="section"><div class="section-head"><div><p class="eyebrow">Worth a closer look</p><h2>A few places to start.</h2></div><a href="#/explore">See all destinations ↗</a></div>${cards(places.slice(0, 3))}</section>`;
}
async function home() {
  const [states, territories, places] = await Promise.all([api('states'), api('union-territories'), api('places')]);
  const stateCards = states.map(s => regionCard(s, 'State')).join('');
  const territoryCards = territories.map(t => regionCard(t, 'Union territory')).join('');
  return `<section class="hero"><div><p class="eyebrow">Many Indias. One place to begin.</p><h1>A little closer to<br>somewhere new.</h1><p>Beyond the famous landmarks, find the places, people and celebrations that make a district feel like nowhere else.</p><div class="buttons"><a class="button" href="#/explore">Plan a trip ↗</a><a class="button secondary" href="#/area">Explore my area</a></div><p style="font-size:11px;margin-top:25px">28 STATES · 8 UNION TERRITORIES · DISTRICT-LED EXPLORING</p></div><div class="hero-image" role="img" aria-label="Illustrative Kerala backwater landscape"><div><span class="eyebrow" style="color:#cde5bd">Slow journeys, lasting stories</span><p><strong>The quieter side of India</strong></p><p>Discover a district →</p></div></div></section><section class="section"><div class="section-head"><div><p class="eyebrow">Explore the states</p><h2>28 states. A world of difference.</h2></div><span class="meta">${states.length} states in the directory</span></div><div class="cards">${stateCards}</div></section><section class="section"><div class="section-head"><div><p class="eyebrow">Explore separately</p><h2>Union territories.</h2></div><span class="meta">${territories.length} territories in the directory</span></div><div class="cards">${territoryCards}</div></section><div class="band"><div><p class="eyebrow">Travel with the seasons</p><h3>Sometimes the best destination is a celebration.</h3><p>Explore typical festival months and discover places for your travel season.</p></div><a href="#/month/8" class="button">Find your month →</a></div><section class="section"><div class="section-head"><div><p class="eyebrow">Worth a closer look</p><h2>A few places to start.</h2></div><a href="#/explore">See all destinations ↗</a></div>${cards(places.slice(0, 3))}</section>`;
}
async function statePage(slug) {
  const s = await api('states/' + encodeURIComponent(slug));
  const cover = image(s.cover_image_url, s.slug);
  return `${breadcrumb([[s.name]])}<div class="state-hero" style="background-image:linear-gradient(90deg,rgba(25,57,47,.9),rgba(25,57,47,.25)),url('${esc(cover)}')"><div><p class="eyebrow" style="color:#d7e8c7">${s.kind === 'union_territory' ? 'Union territory' : 'State'} guide</p><h1>${esc(s.name)}</h1><p>${esc(s.description)}</p></div></div><h3>All districts in ${esc(s.name)}</h3><div class="districts">${s.districts.map(d => `<a href="#/district/${esc(d.slug)}">${esc(d.name)} ↗</a>`).join('')}</div><p style="font-size:12px;margin-top:14px">${s.districts.length} administrative district entries are listed. Detailed tourist places are added district by district after editorial verification.</p><section class="section"><h2>Places with a story</h2>${cards(s.places)}</section>`;
}
async function districtPage(slug) {
  const d = await api('districts/' + encodeURIComponent(slug));
  return `${breadcrumb([[d.state, '#/state/' + d.state_slug], [d.name]])}<p class="eyebrow">Your local field guide</p><h1>${esc(d.name)}</h1><p class="lead">${esc(d.description)}</p><div class="band"><div><h3>A taste of the district</h3><p>${esc(d.food_notes)}</p></div><a class="source" href="${esc(d.source_url)}" target="_blank" rel="noopener noreferrer">Official information ↗</a></div><section class="section"><h2>Make a day of it</h2>${cards(d.places)}</section><section class="section"><h2>Local celebrations</h2><p>Typical months help with inspiration. Confirm the annual programme before making bookings.</p>${festivalCards(d.festivals)}</section>`;
}
async function placePage(slug) {
  const p = await api('places/' + encodeURIComponent(slug));
  return `${breadcrumb([[p.state,'#/state/'+p.state_slug],[p.district,'#/district/'+p.district_slug],[p.name]])}<p class="eyebrow">${esc(p.category)} · ${esc(p.district)}</p><h1>${esc(p.name)}</h1><div class="detail"><div><p class="lead">${esc(p.description)}</p>${p.heritage_id ? `<p class="badge">UNESCO World Heritage</p><p>Listed property: <a class="source" href="${esc(p.unesco_url)}" target="_blank" rel="noopener noreferrer">${esc(p.heritage_name)} ↗</a></p>` : ''}<h3>How to reach</h3><p>${esc(p.how_to_reach)}</p><h3>Before you go</h3><p>${esc(p.practical_notes)}</p><p class="notice">Pilot editorial entry · ${p.last_verified_at ? 'Last checked: '+esc(p.last_verified_at) : 'Not yet independently verified'}. Confirm access, fees and opening hours with the official source.</p><a class="source" href="${esc(p.source_url)}" target="_blank" rel="noopener noreferrer">Official reference ↗</a></div><aside><h3>A good time to go</h3><p>${p.best_months.map(n => months[n-1]).join(', ')}</p><p style="font-size:12px">Indicative seasonal guidance, not a weather forecast.</p><h3>Find your way</h3><p><a class="source" href="https://www.openstreetmap.org/?mlat=${p.latitude}&mlon=${p.longitude}#map=14/${p.latitude}/${p.longitude}" target="_blank" rel="noopener noreferrer">Open location on map ↗</a></p>${saveButton(p)}</aside></div><section class="section"><h2>A little further along</h2><p>Nearby places sorted by straight-line distance, not road travel time.</p>${cards(p.nearby)}</section>`;
}
async function explorePage(query) {
  const params = new URLSearchParams(query || '');
  const [states, places] = await Promise.all([api('states'), api('places?' + params)]);
  return `${breadcrumb([['Destinations']])}<p class="eyebrow">Follow your curiosity</p><h1>Find your kind of place.</h1><p>Browse our directory by season, state and interest.</p><form id="filters" class="filters"><input name="q" placeholder="Search places or districts" aria-label="Search places" value="${esc(params.get('q') || '')}"><select name="state" aria-label="State"><option value="">All states and UTs</option>${states.map(s => `<option value="${esc(s.slug)}" ${params.get('state') === s.slug ? 'selected' : ''}>${esc(s.name)}</option>`).join('')}</select><select name="month" aria-label="Best travel month"><option value="">Any month</option>${months.map((m,i) => `<option value="${i+1}" ${params.get('month') === String(i+1) ? 'selected' : ''}>${m}</option>`).join('')}</select><select name="category" aria-label="Interest"><option value="">Any interest</option>${['heritage','culture','nature','beach'].map(c => `<option ${params.get('category') === c ? 'selected' : ''}>${c}</option>`).join('')}</select><label><input type="checkbox" name="unesco" value="true" ${params.get('unesco') === 'true' ? 'checked' : ''}>UNESCO only</label><button class="button">Find places</button></form><p>${places.length} detailed places found</p>${cards(places)}`;
}
async function monthPage(value) {
  const month = Number(value);
  if (!Number.isInteger(month) || month < 1 || month > 12) throw new Error('Choose a month from January to December.');
  const [festivals, places] = await Promise.all([api('festivals?month='+month),api('places?month='+month)]);
  return `${breadcrumb([['By month']])}<p class="eyebrow">Let the calendar be your compass</p><h1>India in ${months[month-1]}.</h1><p>Seasonal inspiration and typical festival months from our pilot districts.</p><div class="month-grid">${months.map((m,i) => `<a href="#/month/${i+1}" class="${i+1===month?'active':''}">${m.slice(0,3)}</a>`).join('')}</div><section class="section"><h2>Celebrations to discover</h2><p>These are recurring seasonal windows, not confirmed dates for a specific year.</p>${festivalCards(festivals)}</section><section class="section"><h2>A good season for…</h2>${cards(places)}</section>`;
}
async function legacyAreaPage() {
  const states = await api('states');
  const detail = await Promise.all(states.map(s => api('states/' + s.slug)));
  return `${breadcrumb([['Explore my area']])}<p class="eyebrow">New here? Start close to home.</p><h1>Your next weekend,<br>a little more local.</h1><p class="lead">Choose your district for places, local food and celebrations. No location permission needed.</p>${detail.map(s => `<section class="section"><h2>${esc(s.name)}</h2><div class="cards two">${s.districts.map(d => `<a class="card card-body" href="#/district/${esc(d.slug)}"><h3>${esc(d.name)} ↗</h3><p>${esc(d.description)}</p></a>`).join('')}</div></section>`).join('')}`;
}
async function areaPage() {
  const [states, territories] = await Promise.all([api('states'), api('union-territories')]);
  const group = (items, label) => `<section class="section"><p class="eyebrow">${label}</p><h2>${label === 'States' ? 'Choose a state' : 'Choose a union territory'}</h2><div class="districts">${items.map(r => `<a href="#/state/${esc(r.slug)}">${esc(r.name)} · ${r.district_count} districts ↗</a>`).join('')}</div></section>`;
  return `${breadcrumb([['Explore my area']])}<p class="eyebrow">New here? Start close to home.</p><h1>Your next weekend,<br>a little more local.</h1><p class="lead">Choose your state or union territory, then select a district for places, local food and celebrations. No location permission needed.</p>${group(states, 'States')}${group(territories, 'Union territories')}`;
}
async function route() {
  const version = ++routeVersion;
  const [path, query] = (location.hash.slice(1) || '/').split('?');
  const [, type, slug] = path.split('/');
  root.innerHTML = '<p class="loading" role="status">Finding your next discovery…</p>';
  try {
    let html;
    if (!type) html = await home();
    else if (type === 'state') html = await statePage(slug);
    else if (type === 'district') html = await districtPage(slug);
    else if (type === 'place') html = await placePage(slug);
    else if (type === 'explore') html = await explorePage(query);
    else if (type === 'month') html = await monthPage(slug);
    else if (type === 'area') html = await areaPage();
    else if (type === 'saved') {
      const places = (await api('places')).filter(p => saved.has(p.slug));
      html = `${breadcrumb([['Saved places']])}<p class="eyebrow">For another day</p><h1>Your little collection.</h1><p>Saved on this browser. No account needed.</p>${places.length ? cards(places) : '<p class="empty">Tap Save on a destination to keep it here.</p>'}`;
    } else throw new Error('That page does not exist.');
    if (version !== routeVersion) return;
    root.innerHTML = html;
  } catch (error) {
    if (version !== routeVersion) return;
    root.innerHTML = `<h1>A small detour.</h1><p role="alert">${esc(error.message)}</p><a class="button" href="#/">Back to exploring</a>`;
  }
  window.scrollTo(0,0);
}
root.addEventListener('submit', event => {
  if (event.target.id !== 'filters') return;
  event.preventDefault();
  const params = new URLSearchParams();
  for (const [k,v] of new FormData(event.target)) if (v) params.set(k,v);
  location.hash = '/explore?' + params;
});
root.addEventListener('click', event => {
  const button = event.target.closest('[data-save]');
  if (!button) return;
  const slug = button.dataset.save;
  saved.has(slug) ? saved.delete(slug) : saved.add(slug);
  try { localStorage.setItem('india-locally-saved', JSON.stringify([...saved])); }
  catch { button.textContent = 'Storage unavailable'; return; }
  button.textContent = saved.has(slug) ? '♥ Saved' : '♡ Save';
  button.setAttribute('aria-pressed', saved.has(slug));
  updateCount();
  if (location.hash === '#/saved') route();
});
window.addEventListener('hashchange', route);
route();
