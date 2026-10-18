/* Curated Weekly Dispatch editor.
   Client-side editing is immediate; persistence requires entry.save_url.
   Server contract: POST { member_order: [integer IDs], layout: "layout-01" }.
*/
(() => {
  "use strict";

  const page = document.getElementById("weekly-dispatch");
  const toggle = page?.querySelector(".weekly-edit-toggle");
  if (!page || !toggle) return;

  const layouts = JSON.parse(
    document.getElementById("weekly-layouts-data").textContent
  );

  const layoutClasses = Object.keys(layouts);
  const days = [...page.querySelectorAll(".weekly-day")];
  const saved = new WeakMap();
  let draggedCard = null;
  let savingCount = 0;

  const cardsFor = (day) => [...day.querySelectorAll(".weekly-contributor")];
  const currentOrder = (day) => cardsFor(day).map((card) => card.dataset.memberId);
  const currentLayout = (day) => day.querySelector(".weekly-layout-select")?.value || day.dataset.layout;

  function snapshot(day) {
    return { order: currentOrder(day), layout: currentLayout(day) };
  }

  function isDirty(day) {
    const initial = saved.get(day);
    return initial && (initial.layout !== currentLayout(day) ||
      initial.order.join(",") !== currentOrder(day).join(","));
  }

  function setStatus(day, message = "", kind = "") {
    const status = day.querySelector(".weekly-save-status");
    if (!status) return;
    status.textContent = message;
    status.classList.toggle("is-error", kind === "error");
    status.classList.toggle("is-success", kind === "success");
  }

  function refreshButtons(day) {
    const dirty = Boolean(isDirty(day));
    day.classList.toggle("is-dirty", dirty);
    const undo = day.querySelector(".weekly-reset-day");
    const save = day.querySelector(".weekly-save-day");
    const busy = day.dataset.saving === "true";
    if (undo) undo.disabled = !dirty || busy;
    if (save) save.disabled = !dirty || busy || !day.dataset.saveUrl;
    const cards = cardsFor(day);
    cards.forEach((card, i) => {
      const up = card.querySelector(".weekly-move-up");
      const down = card.querySelector(".weekly-move-down");
      if (up) up.disabled = i === 0 || busy;
      if (down) down.disabled = i === cards.length - 1 || busy;
      card.draggable = page.classList.contains("is-editing") && !busy;
    });
  }

  // Reordering DOM nodes preserves their images, captions, and event listeners.
  function syncPhotos(day) {
    const gallery = day.querySelector(".weekly-gallery");
    if (!gallery) return;
    const figures = new Map([...gallery.querySelectorAll(".weekly-photo")]
      .map((figure) => [figure.dataset.memberId, figure]));
    currentOrder(day).forEach((memberId) => {
      const figure = figures.get(memberId);
      if (figure) gallery.appendChild(figure);
    });
  }

  function afterChange(day) {
    syncPhotos(day);
    setStatus(day, !day.dataset.saveUrl ? "Preview only — add entry.save_url to enable saving." : "");
    refreshButtons(day);
  }

  function applyLayout(day, layout) {
    if (!layoutClasses.includes(layout)) return;
    day.classList.remove(...layoutClasses);
    day.classList.add(layout);
    day.dataset.layout = layout;
    const description = day.querySelector(".weekly-layout-description");
    if (description) description.textContent = layouts[layout].description;
    const select = day.querySelector(".weekly-layout-select");
    if (select && select.value !== layout) select.value = layout;
  }

  function restore(day) {
    const initial = saved.get(day);
    if (!initial) return;
    const list = day.querySelector(".weekly-contributors");
    const byId = new Map(cardsFor(day).map((card) => [card.dataset.memberId, card]));
    initial.order.forEach((memberId) => {
      const card = byId.get(memberId);
      if (card) list.appendChild(card);
    });
    applyLayout(day, initial.layout);
    afterChange(day);
  }

  function setEditing(editing) {
    page.classList.toggle("is-editing", editing);
    toggle.setAttribute("aria-pressed", String(editing));
    toggle.textContent = editing ? "Finish editing" : "Enable editing";
    days.forEach((day) => {
      refreshButtons(day);
      if (editing && !day.dataset.saveUrl) {
        setStatus(day, "Preview only — add entry.save_url to enable saving.");
      }
    });
  }

  async function saveDay(day) {
    if (!isDirty(day) || !day.dataset.saveUrl || day.dataset.saving === "true") return;
    if (!day.dataset.entryId) {
      setStatus(day, "Cannot save: this day has no entry.id.", "error");
      return;
    }

    const csrfInput = day.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrf = csrfInput?.value;
    if (!csrf) {
      setStatus(day, "Cannot save: CSRF token is missing.", "error");
      return;
    }

    const payload = {
      member_order: currentOrder(day).map((id) => Number(id)),
      layout: currentLayout(day)
    };
    if (payload.member_order.some((id) => !Number.isSafeInteger(id))) {
      setStatus(day, "Cannot save: invalid member ID.", "error");
      return;
    }

    day.dataset.saving = "true";
    savingCount += 1;
    refreshButtons(day);
    setStatus(day, "Saving…");

    try {
      const response = await fetch(day.dataset.saveUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          "X-CSRFToken": csrf
        },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        let detail = "";
        try {
          const error = await response.json();
          detail = error.error || error.detail || "";
        } catch (_) { /* A non-JSON error page is also possible. */ }
        throw new Error(detail || `Server returned ${response.status}.`);
      }
      saved.set(day, snapshot(day));
      setStatus(day, "Saved.", "success");
    } catch (error) {
      setStatus(day, `Save failed: ${error.message}`, "error");
    } finally {
      delete day.dataset.saving;
      savingCount -= 1;
      refreshButtons(day);
    }
  }

  // Capture the server-rendered order and chosen composition as the baseline.
  days.forEach((day) => {
    const select = day.querySelector(".weekly-layout-select");
    if (!select) return;
    const layout = layoutClasses.includes(day.dataset.layout) ? day.dataset.layout : "layout-01";
    applyLayout(day, layout);
    saved.set(day, snapshot(day));

    select.addEventListener("change", () => {
      if (!page.classList.contains("is-editing")) return;
      applyLayout(day, select.value);
      afterChange(day);
    });

    day.querySelector(".weekly-reset-day")?.addEventListener("click", () => {
      restore(day);
      setStatus(day, "Reverted to the last saved version.");
    });
    day.querySelector(".weekly-save-day")?.addEventListener("click", () => saveDay(day));

    const list = day.querySelector(".weekly-contributors");
    list?.addEventListener("click", (event) => {
      if (!page.classList.contains("is-editing") || day.dataset.saving === "true") return;
      const button = event.target.closest(".weekly-move-up, .weekly-move-down");
      if (!button) return;
      const card = button.closest(".weekly-contributor");
      if (button.classList.contains("weekly-move-up") && card.previousElementSibling) {
        list.insertBefore(card, card.previousElementSibling);
      } else if (button.classList.contains("weekly-move-down") && card.nextElementSibling) {
        list.insertBefore(card.nextElementSibling, card);
      }
      afterChange(day);
      button.focus();
    });

    list?.addEventListener("dragstart", (event) => {
      if (!page.classList.contains("is-editing") || day.dataset.saving === "true") {
        event.preventDefault();
        return;
      }
      const card = event.target.closest(".weekly-contributor");
      if (!card) return;
      draggedCard = card;
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", card.dataset.memberId);
      card.classList.add("is-dragging");
    });

    list?.addEventListener("dragover", (event) => {
      if (!draggedCard || draggedCard.parentElement !== list) return;
      const target = event.target.closest(".weekly-contributor");
      if (!target || target === draggedCard) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
      const before = event.clientY < target.getBoundingClientRect().top + target.offsetHeight / 2;
      list.querySelectorAll(".weekly-contributor").forEach((card) =>
        card.classList.remove("is-drop-before", "is-drop-after"));
      target.classList.add(before ? "is-drop-before" : "is-drop-after");
    });

    list?.addEventListener("drop", (event) => {
      if (!draggedCard || draggedCard.parentElement !== list) return;
      event.preventDefault();
      const target = event.target.closest(".weekly-contributor");
      if (target && target !== draggedCard) {
        const before = event.clientY < target.getBoundingClientRect().top + target.offsetHeight / 2;
        list.insertBefore(draggedCard, before ? target : target.nextSibling);
        afterChange(day);
      }
      list.querySelectorAll(".weekly-contributor").forEach((card) =>
        card.classList.remove("is-drop-before", "is-drop-after"));
    });

    list?.addEventListener("dragend", () => {
      if (draggedCard) draggedCard.classList.remove("is-dragging");
      draggedCard = null;
      list.querySelectorAll(".weekly-contributor").forEach((card) =>
        card.classList.remove("is-drop-before", "is-drop-after"));
    });
  });

  toggle.addEventListener("click", () => {
    const editing = page.classList.contains("is-editing");
    if (savingCount) return;
    if (editing && days.some(isDirty)) {
      if (!window.confirm("Discard your unsaved changes and finish editing?")) return;
      days.filter(isDirty).forEach(restore);
    }
    setEditing(!editing);
  });

  // Warn about accidental navigation while the user has uncommitted changes.
  window.addEventListener("beforeunload", (event) => {
    if (!days.some(isDirty)) return;
    event.preventDefault();
    event.returnValue = "";
  });

  setEditing(false);
})();
