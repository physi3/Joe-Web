/* global L */
(() => {
    "use strict";
    const root = document.getElementById("photo-map-page");
    if (!root) return;
    const el = (id) => document.getElementById(id);
    const config = JSON.parse(el("photo-map-config").textContent);
    const form = el("map-filters");
    const sheet = el("map-sheet");
    const mobile = window.matchMedia("(max-width: 800px)");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const state = { view: "all", photographer: "", photos: [], weeks: [], photographers: new Map(), visible: [], selected: null };
    const details = new Map();
    const markers = new Map();
    let map, clusters, journeys, popup, dataRequest, detailRequest, renderVersion = 0;
    let restoring = false;
    const dateFormat = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
    const shortDate = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
    const dateValue = (value) => new Date(`${value}T12:00:00Z`);
    const escape = (value) => String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
    const personFor = (photo) => state.photographers.get(photo.photographer_id) || { name: "Former contributor", colour: "#526b78" };
    const make = (tag, className, text) => {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    };

    function message(text, retry = false) {
        el("map-message").hidden = !text;
        el("map-message-text").textContent = text || "";
        el("map-retry").hidden = !retry;
    }

    async function fetchJSON(url, signal) {
        const response = await fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" }, signal });
        if (!response.ok || !response.headers.get("content-type")?.includes("application/json")) throw new Error("Photographs unavailable. Your session may have expired; reload to sign in.");
        return response.json();
    }

    function setupMap() {
        if (!window.L || !L.markerClusterGroup) {
            el("map-summary").textContent = "Map unavailable";
            message("The map couldn’t load. Check your connection and reload the page.");
            return false;
        }
        map = L.map("photo-map", { worldCopyJump: true, minZoom: 2, maxZoom: 19, preferCanvas: true, zoomAnimation: !reducedMotion, fadeAnimation: !reducedMotion, markerZoomAnimation: !reducedMotion }).setView([25, 0], 2);
        map.attributionControl.setPosition(mobile.matches ? "topright" : "bottomright");
        const key = config.carto_api_key;
        const tileURL = key
            ? `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png?key=${encodeURIComponent(key)}`
            : "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
        const tiles = L.tileLayer(tileURL, {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' + (key ? ' &copy; <a href="https://carto.com/attributions">CARTO</a>' : ""),
            subdomains: "abcd", maxZoom: 20,
        }).addTo(map);
        let tileErrors = 0;
        tiles.on("tileerror", () => {
            if (++tileErrors === 4) el("map-summary").textContent = "Map tiles unavailable. Photo markers and filters are still available.";
        });
        L.control.scale({ imperial: false, maxWidth: 120 }).addTo(map);
        journeys = L.layerGroup().addTo(map);
        clusters = L.markerClusterGroup({
            maxClusterRadius: mobile.matches ? 50 : 58,
            showCoverageOnHover: false, spiderfyOnMaxZoom: true,
            animate: !reducedMotion, removeOutsideVisibleBounds: true,
            iconCreateFunction(cluster) {
                const count = cluster.getAllChildMarkers().reduce((sum, marker) => sum + marker.options.photoCount, 0);
                return L.divIcon({ className: "map-cluster-icon", iconSize: [52, 52], html: `<span class="map-cluster-disc" aria-label="${count} photographs">${count}<small>photos</small></span>` });
            },
        }).addTo(map);
        popup = L.popup({ className: "map-popup", closeButton: false, maxWidth: 276, minWidth: 276, offset: [0, -24], autoPanPadding: [35, 35] });
        map.on("click", closePreview);
        map.on("popupclose", () => { if (!restoring) closePreview(false); });
        map.on("layeradd", (event) => {
            if (state.selected && event.layer === state.selected.marker) event.layer.getElement()?.classList.add("is-selected");
        });
        return true;
    }

    function writeURL() {
        const url = new URL(window.location.href);
        ["view", "photographer", "year", "month", "week", "place"].forEach((key) => url.searchParams.delete(key));
        const values = { view: state.view === "weekly" ? "weekly" : "", photographer: state.photographer, year: el("map-year").value, month: el("map-month").value, week: state.view === "weekly" ? el("map-week").value : "", place: el("map-search").value.trim() };
        Object.entries(values).forEach(([key, value]) => { if (value) url.searchParams.set(key, value); });
        window.history.replaceState(null, "", url);
    }

    function updatePersonButtons() {
        el("map-photographers").querySelectorAll("button").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.person === state.photographer)));
    }

    function populateControls() {
        const people = el("map-photographers");
        people.replaceChildren();
        const addPerson = (id, name, colour) => {
            const button = make("button", "", name);
            button.type = "button";
            button.dataset.person = String(id);
            button.setAttribute("aria-pressed", "false");
            if (colour) {
                const dot = make("span", "map-person-dot");
                dot.style.setProperty("--person-colour", colour);
                dot.setAttribute("aria-hidden", "true");
                button.prepend(dot);
            }
            button.addEventListener("click", () => { state.photographer = String(id); updatePersonButtons(); applyFilters(); });
            people.append(button);
        };
        addPerson("", "All photographers");
        state.photographers.forEach((person) => addPerson(person.id, person.name, person.colour));
        const year = el("map-year");
        year.length = 1;
        [...new Set(state.photos.map((photo) => photo.date.slice(0, 4)))].sort().reverse().forEach((value) => year.add(new Option(value, value)));
        const week = el("map-week");
        week.length = 1;
        state.weeks.forEach((entry) => week.add(new Option(`Week ${entry.number} · ${shortDate.format(dateValue(entry.start))}${entry.published ? "" : " · Draft"}`, String(entry.id))));
        const params = new URLSearchParams(window.location.search);
        state.photographer = state.photographers.has(Number(params.get("photographer"))) ? params.get("photographer") : "";
        year.value = params.get("year") || "";
        el("map-month").value = params.get("month") || "";
        week.value = params.get("week") || "";
        el("map-search").value = (params.get("place") || "").slice(0, 150);
        if (params.get("view") === "weekly") state.view = "weekly";
        if (!week.value && state.weeks.length) week.value = String(state.weeks[0].id);
        updatePersonButtons();
        updateView();
    }

    function updateView() {
        root.querySelectorAll("[data-map-view]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.mapView === state.view)));
        el("map-date-filters").hidden = state.view === "weekly";
        el("map-week-filter").hidden = state.view !== "weekly";
        el("map-journey-note").hidden = state.view !== "weekly";
    }

    // Choose the smallest longitude interval, including archives on both sides
    // of the date line, so initial framing doesn't zoom out to the whole globe.
    function unwrapLongitudes(photos) {
        const longs = [...new Set(photos.map((photo) => (photo.longitude + 360) % 360))].sort((a, b) => a - b);
        let start = longs[0] || 0, largest = -1;
        longs.forEach((value, i) => {
            const next = i === longs.length - 1 ? longs[0] + 360 : longs[i + 1];
            if (next - value > largest) { largest = next - value; start = next % 360; }
        });
        const end = start + 360 - Math.max(0, largest);
        const shift = (start + end) / 2 > 180 ? -360 : 0;
        photos.forEach((photo) => {
            let lng = (photo.longitude + 360) % 360;
            if (lng < start) lng += 360;
            photo.mapLongitude = lng + shift;
        });
    }

    function markerIcon(photos, selectedPhoto = photos[0]) {
        const colours = [...new Set(photos.map((photo) => personFor(photo).colour))];
        const ring = colours.length === 1 ? colours[0] : `conic-gradient(${colours.map((colour, i) => `${colour} ${i / colours.length * 100}% ${(i + 1) / colours.length * 100}%`).join(",")})`;
        return L.divIcon({ className: "map-photo-icon", iconSize: [48, 48], iconAnchor: [24, 24], html: `<span class="map-marker-disc" style="--marker-ring:${escape(ring)}"><img src="${escape(selectedPhoto.thumbnail)}" alt="" loading="lazy" decoding="async">${photos.length > 1 ? `<span class="map-marker-count">${photos.length}</span>` : ""}</span>` });
    }

    function fitPhotos() {
        if (!state.visible.length) return;
        const bounds = L.latLngBounds(state.visible.map((photo) => [photo.latitude, photo.mapLongitude]));
        map.fitBounds(bounds, { padding: mobile.matches ? [45, 45] : [65, 65], maxZoom: 13, animate: false });
    }

    function drawJourneys(week) {
        journeys.clearLayers();
        if (!week) return;
        const byPerson = new Map();
        // Search narrows locations, but must not invent a direct journey between
        // nonconsecutive points. Break the line at every filtered-out photo.
        const visibleIDs = new Set(state.visible.map((photo) => photo.id));
        state.photos.filter((photo) => photo.date >= week.start && photo.date <= week.end).forEach((photo) => {
            if (!byPerson.has(photo.photographer_id)) byPerson.set(photo.photographer_id, []);
            byPerson.get(photo.photographer_id).push(photo);
        });
        byPerson.forEach((photos) => {
            photos.sort((a, b) => a.date.localeCompare(b.date) || a.id - b.id);
            let segment = [];
            const flush = () => {
                if (segment.length > 1) L.polyline(segment, { color: personFor(photos[0]).colour, weight: 2, opacity: .6, dashArray: "4 6", interactive: false }).addTo(journeys);
                segment = [];
            };
            photos.forEach((photo) => {
                if (!visibleIDs.has(photo.id)) { flush(); return; }
                let lng = photo.mapLongitude;
                if (segment.length) {
                    const previous = segment[segment.length - 1][1];
                    while (lng - previous > 180) lng -= 360;
                    while (lng - previous < -180) lng += 360;
                }
                segment.push([photo.latitude, lng]);
            });
            flush();
        });
    }

    async function applyFilters() {
        const version = ++renderVersion;
        closePreview();
        clusters.clearLayers();
        markers.clear();
        const week = state.view === "weekly" ? state.weeks.find((entry) => String(entry.id) === el("map-week").value) : null;
        const query = el("map-search").value.trim().toLocaleLowerCase();
        state.visible = state.photos.filter((photo) => {
            if (state.photographer && String(photo.photographer_id) !== state.photographer) return false;
            if (state.view === "weekly") {
                if (!week || photo.date < week.start || photo.date > week.end) return false;
            } else {
                if (el("map-year").value && !photo.date.startsWith(el("map-year").value)) return false;
                if (el("map-month").value && photo.date.slice(5, 7) !== el("map-month").value) return false;
            }
            return !query || photo.location.toLocaleLowerCase().includes(query);
        });
        unwrapLongitudes(state.visible);
        const locations = new Map();
        state.visible.forEach((photo) => {
            const key = `${photo.latitude.toFixed(6)},${photo.longitude.toFixed(6)}`;
            if (!locations.has(key)) locations.set(key, []);
            locations.get(key).push(photo);
        });
        const count = state.visible.length;
        el("map-summary").textContent = `${count.toLocaleString()} photograph${count === 1 ? "" : "s"} · ${locations.size.toLocaleString()} location${locations.size === 1 ? "" : "s"}${state.view === "weekly" && week ? ` · Week ${week.number}` : ""}`;
        el("map-fit").disabled = !count;
        const link = el("map-dispatch-link");
        link.hidden = !week;
        if (week) link.href = week.url;
        message(count ? "" : state.view === "weekly" && !week ? "No dispatches are available yet. Explore All photos while the next edition is being prepared." : !state.photos.length ? "No geotagged photographs yet. Photos with a location will appear here." : "No photographs match these filters. Try another date, contributor or place.");
        drawJourneys(week);
        writeURL();
        const groups = [...locations.entries()];
        // Yield between batches so a large archive doesn't block touch input.
        for (let i = 0; i < groups.length; i += 250) {
            if (version !== renderVersion) return;
            const batch = groups.slice(i, i + 250).map(([key, photos]) => {
                photos.sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id);
                const photo = photos[0];
                const marker = L.marker([photo.latitude, photo.mapLongitude], { icon: markerIcon(photos), photoCount: photos.length, keyboard: true, title: `${photo.location} · ${photos.length} photograph${photos.length === 1 ? "" : "s"}`, alt: `Explore photographs at ${photo.location}`, riseOnHover: true });
                marker.on("click", () => openPreview(key, photos, marker, 0));
                markers.set(key, marker);
                return marker;
            });
            clusters.addLayers(batch);
            if (i + 250 < groups.length) await new Promise(window.requestAnimationFrame);
        }
        if (version === renderVersion) fitPhotos();
    }

    function closePreview(closePopup = true) {
        detailRequest?.abort();
        if (state.selected) {
            state.selected.marker.getElement()?.classList.remove("is-selected");
            state.selected.marker.setZIndexOffset(0);
        }
        state.selected = null;
        sheet.hidden = true;
        sheet.replaceChildren();
        el("map-stage").classList.remove("has-preview");
        if (closePopup && map) map.closePopup();
    }

    function showCard(card, marker, focus = true) {
        if (mobile.matches) {
            sheet.replaceChildren(card);
            sheet.hidden = false;
            el("map-stage").classList.add("has-preview");
            // Keep the selected point above the sheet without covering it.
            const point = map.latLngToContainerPoint(marker.getLatLng());
            const available = map.getSize().y - sheet.offsetHeight;
            if (point.y > available - 55) map.panBy([0, point.y - available + 75], { animate: !reducedMotion });
        } else {
            popup.setLatLng(marker.getLatLng()).setContent(card).openOn(map);
        }
        if (focus) card.querySelector(".map-card-close")?.focus({ preventScroll: true });
    }

    async function openPreview(key, photos, marker, index, keepFocus = false) {
        closePreview();
        const selection = { key, photos, marker, index };
        state.selected = selection;
        marker.setIcon(markerIcon(photos, photos[index]));
        marker.getElement()?.classList.add("is-selected");
        marker.setZIndexOffset(1000);
        const card = make("article", "map-card");
        card.setAttribute("aria-label", "Photograph preview");
        // Browsing replaces the old card during the button's click handler.
        // Stop that original click before it reaches the map and closes the
        // newly opened preview, even after the old card has been detached.
        card.addEventListener("click", (event) => event.stopPropagation());
        card.addEventListener("keydown", (event) => {
            if (event.key !== "Escape") event.stopPropagation();
        });
        const close = make("button", "map-card-close", "×");
        close.type = "button";
        close.setAttribute("aria-label", "Close photograph preview");
        close.addEventListener("click", () => { closePreview(); marker.getElement()?.focus({ preventScroll: true }); });
        card.append(close, make("p", "map-card-loading", "Opening photograph…"));
        showCard(card, marker, !keepFocus);
        const photo = photos[index];
        detailRequest = new AbortController();
        try {
            const detail = details.get(photo.id) || await fetchJSON(photo.detail_url, detailRequest.signal);
            if (state.selected !== selection) return;
            // Bound the session cache while making location browsing immediate.
            if (details.size >= 100) details.delete(details.keys().next().value);
            details.set(photo.id, detail);
            card.querySelector(".map-card-loading").remove();
            const image = make("img", "map-card-image");
            image.src = detail.thumbnail;
            image.alt = detail.caption || `Photograph at ${detail.location}`;
            image.decoding = "async";
            image.addEventListener("error", () => { image.alt = "Photograph unavailable"; });
            const time = make("time", "map-card-date", dateFormat.format(dateValue(detail.date)));
            time.dateTime = detail.date;
            const heading = make("h2", "", detail.location);
            const person = personFor(photo);
            const byline = make("div", "map-card-person");
            const dot = make("span", "map-person-dot");
            dot.style.setProperty("--person-colour", person.colour);
            dot.setAttribute("aria-hidden", "true");
            byline.append(dot, document.createTextNode(`By ${person.name}`));
            const day = make("a", "map-card-day", "View day →");
            day.href = detail.day_url;
            card.append(image, time, heading, byline);
            if (detail.caption) card.append(make("p", "map-card-caption", detail.caption));
            card.append(day);
            if (photos.length > 1) {
                const browse = make("nav", "map-card-browse");
                browse.setAttribute("aria-label", "Photographs at this location");
                const previous = make("button", "", "←");
                const next = make("button", "", "→");
                previous.type = next.type = "button";
                previous.setAttribute("aria-label", "Previous photograph at this location");
                next.setAttribute("aria-label", "Next photograph at this location");
                previous.addEventListener("click", () => openPreview(key, photos, marker, (index - 1 + photos.length) % photos.length));
                next.addEventListener("click", () => openPreview(key, photos, marker, (index + 1) % photos.length));
                const position = make("span", "", `${index + 1} / ${photos.length} at this location`);
                position.setAttribute("role", "status");
                browse.append(previous, position, next);
                card.append(browse);
            }
            if (!mobile.matches) popup.update();
            else showCard(card, marker, false);
        } catch (error) {
            if (error.name === "AbortError" || state.selected !== selection) return;
            card.querySelector(".map-card-loading")?.remove();
            const notice = make("div", "map-card-error", "This photograph couldn’t be loaded. ");
            const retry = make("button", "", "Try again");
            retry.type = "button";
            retry.addEventListener("click", () => openPreview(key, photos, marker, index));
            notice.append(retry);
            card.append(notice);
            if (!mobile.matches) popup.update();
        }
    }

    async function loadData() {
        dataRequest?.abort();
        dataRequest = new AbortController();
        message("Loading photographs…");
        try {
            const data = await fetchJSON(config.data_url, dataRequest.signal);
            state.photos = data.photos;
            state.weeks = data.weeks;
            state.photographers = new Map(data.photographers.map((person) => [person.id, person]));
            populateControls();
            await applyFilters();
        } catch (error) {
            if (error.name === "AbortError") return;
            el("map-summary").textContent = "Archive unavailable";
            message(error.message || "The archive couldn’t be loaded.", true);
        }
    }

    if (!setupMap()) return;
    form.addEventListener("submit", (event) => event.preventDefault());
    ["map-year", "map-month", "map-week"].forEach((id) => el(id).addEventListener("change", () => applyFilters()));
    let searchTimer;
    el("map-search").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(applyFilters, 180); });
    form.addEventListener("reset", () => {
        clearTimeout(searchTimer);
        state.photographer = "";
        state.view = "all";
        // Wait until the browser has restored native form values.
        setTimeout(() => { updatePersonButtons(); updateView(); applyFilters(); }, 0);
    });
    el("map-filter-toggle").addEventListener("click", () => {
        const expanded = form.classList.toggle("is-expanded");
        el("map-filter-toggle").setAttribute("aria-expanded", String(expanded));
        el("map-filter-toggle").querySelector("span").textContent = expanded ? "−" : "+";
        map.invalidateSize({ pan: false });
    });
    root.querySelectorAll("[data-map-view]").forEach((button) => button.addEventListener("click", () => {
        state.view = button.dataset.mapView;
        if (state.view === "weekly" && !el("map-week").value && state.weeks.length) el("map-week").value = String(state.weeks[0].id);
        if (state.view === "weekly" && mobile.matches) {
            form.classList.add("is-expanded");
            el("map-filter-toggle").setAttribute("aria-expanded", "true");
            el("map-filter-toggle").querySelector("span").textContent = "−";
        }
        updateView();
        applyFilters();
    }));
    el("map-fit").addEventListener("click", () => { closePreview(); fitPhotos(); });
    el("map-retry").addEventListener("click", loadData);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && state.selected) {
            const marker = state.selected.marker;
            closePreview();
            marker.getElement()?.focus({ preventScroll: true });
        }
    });
    mobile.addEventListener("change", () => {
        const selection = state.selected;
        restoring = true;
        map.closePopup();
        restoring = false;
        if (selection) openPreview(selection.key, selection.photos, selection.marker, selection.index, true);
        map.attributionControl.setPosition(mobile.matches ? "topright" : "bottomright");
        map.invalidateSize({ pan: false });
    });
    loadData();
})();
