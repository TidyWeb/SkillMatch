(() => {
  'use strict';

  const configs = {
    excel: {
      src: 'assets/maps/excel_map.svg',
      label: 'Excel at a glance, with a learning order and a worked example'
    },
    sql: {
      src: 'assets/maps/sql_map.svg',
      label: 'SQL at a glance, with a learning order and an example query'
    }
  };

  const dialog = document.querySelector('#sm-map-dialog');
  const dialogTitle = document.querySelector('#sm-map-dialog-title');
  const closeButton = dialog?.querySelector('[data-map-close]');
  const zoomInButton = dialog?.querySelector('[data-map-zoom-in]');
  const zoomOutButton = dialog?.querySelector('[data-map-zoom-out]');
  const resetButton = dialog?.querySelector('[data-map-reset]');
  const viewport = dialog?.querySelector('[data-map-viewport]');
  const stage = dialog?.querySelector('[data-map-stage]');
  const zoomStatus = dialog?.querySelector('[data-map-zoom-status]');

  if (!dialog || !dialogTitle || !closeButton || !viewport || !stage || typeof dialog.showModal !== 'function') return;

  let activeTrigger = null;
  let cloneNumber = 0;
  let transform = { x: 0, y: 0, scale: 1 };
  const pointers = new Map();
  let gesture = null;

  function prefixIds(svg, prefix) {
    const idMap = new Map();
    const idElements = [svg, ...svg.querySelectorAll('[id]')].filter(element => element.hasAttribute('id'));

    for (const element of idElements) {
      const oldId = element.getAttribute('id');
      const newId = `${prefix}-${oldId}`;
      idMap.set(oldId, newId);
      element.setAttribute('id', newId);
    }

    const rewriteUrlReferences = value => value.replace(/url\(\s*(["']?)#([^\s)'" ]+)\1\s*\)/g, (match, quote, id) => {
      return idMap.has(id) ? `url(${quote}#${idMap.get(id)}${quote})` : match;
    });

    for (const element of [svg, ...svg.querySelectorAll('*')]) {
      for (const attribute of [...element.attributes]) {
        const name = attribute.name.toLowerCase();
        if ((name === 'href' || name === 'xlink:href') && attribute.value.startsWith('#')) {
          const oldId = attribute.value.slice(1);
          if (idMap.has(oldId)) element.setAttribute(attribute.name, `#${idMap.get(oldId)}`);
        } else if (name === 'aria-labelledby' || name === 'aria-describedby') {
          element.setAttribute(attribute.name, attribute.value.split(/\s+/).map(id => idMap.get(id) || id).join(' '));
        } else {
          element.setAttribute(attribute.name, rewriteUrlReferences(attribute.value));
        }
      }

      if (element.localName === 'style') element.textContent = rewriteUrlReferences(element.textContent);
    }
    return svg;
  }

  async function loadMap(key, config) {
    const trigger = document.querySelector(`[data-map-trigger="${key}"]`);
    if (!trigger) return;

    const loading = trigger.querySelector('[data-map-loading]');
    const fallback = trigger.querySelector('[data-map-fallback]');

    try {
      const response = await fetch(config.src, { cache: 'no-cache' });
      if (!response.ok) throw new Error(`Map request returned ${response.status}`);
      const source = await response.text();
      const parsed = new DOMParser().parseFromString(source, 'image/svg+xml');
      const sourceSvg = parsed.documentElement;
      if (sourceSvg.localName !== 'svg' || parsed.querySelector('parsererror')) throw new Error('Map SVG could not be parsed');

      const svg = prefixIds(document.importNode(sourceSvg, true), `sm-${key}`);
      svg.setAttribute('width', '100%');
      svg.setAttribute('height', 'auto');
      svg.setAttribute('focusable', 'false');
      svg.classList.add('sm-map-svg');
      trigger.dataset.mapStatus = 'inline';
      trigger.dataset.mapTitle = sourceSvg.querySelector('title')?.textContent.trim() || config.label;
      loading?.remove();
      if (fallback) fallback.hidden = true;
      trigger.insertBefore(svg, fallback || null);
    } catch {
      trigger.dataset.mapStatus = 'fallback';
      trigger.dataset.mapTitle = config.label;
      if (loading) loading.hidden = true;
      if (fallback) fallback.hidden = false;
    }
  }

  function applyTransform() {
    stage.style.transform = `translate3d(${transform.x}px, ${transform.y}px, 0) scale(${transform.scale})`;
    if (zoomStatus) zoomStatus.textContent = `Map zoom ${Math.round(transform.scale * 100)} percent`;
  }

  function zoomAt(clientX, clientY, factor) {
    const rect = viewport.getBoundingClientRect();
    const pointX = clientX - rect.left - rect.width / 2;
    const pointY = clientY - rect.top - rect.height / 2;
    const nextScale = Math.min(12, Math.max(0.5, transform.scale * factor));
    transform.x = pointX - ((pointX - transform.x) / transform.scale) * nextScale;
    transform.y = pointY - ((pointY - transform.y) / transform.scale) * nextScale;
    transform.scale = nextScale;
    applyTransform();
  }

  function zoomFromCentre(factor) {
    const rect = viewport.getBoundingClientRect();
    zoomAt(rect.left + rect.width / 2, rect.top + rect.height / 2, factor);
  }

  function resetView() {
    transform = { x: 0, y: 0, scale: 1 };
    applyTransform();
  }

  function openMap(trigger, key) {
    activeTrigger = trigger;
    const originalSvg = trigger.querySelector(':scope > svg');
    const originalImage = trigger.querySelector(':scope > img[data-map-fallback]');
    stage.replaceChildren();

    if (originalSvg) {
      const clone = prefixIds(originalSvg.cloneNode(true), `sm-lightbox-${key}-${++cloneNumber}`);
      clone.setAttribute('width', '100%');
      clone.setAttribute('height', '100%');
      clone.setAttribute('focusable', 'false');
      stage.append(clone);
    } else if (originalImage) {
      const image = document.createElement('img');
      image.src = originalImage.src;
      image.alt = originalImage.alt;
      stage.append(image);
    }

    dialogTitle.textContent = trigger.dataset.mapTitle || `${key.toUpperCase()} learning map`;
    resetView();
    dialog.showModal();
    document.documentElement.classList.add('sm-map-dialog-open');
    closeButton.focus();
  }

  function closeMap() {
    if (dialog.open) dialog.close();
  }

  for (const [key, config] of Object.entries(configs)) {
    const trigger = document.querySelector(`[data-map-trigger="${key}"]`);
    trigger?.addEventListener('click', () => openMap(trigger, key));
    loadMap(key, config);
  }

  closeButton.addEventListener('click', closeMap);
  zoomInButton?.addEventListener('click', () => zoomFromCentre(1.25));
  zoomOutButton?.addEventListener('click', () => zoomFromCentre(0.8));
  resetButton?.addEventListener('click', resetView);

  dialog.addEventListener('cancel', event => {
    event.preventDefault();
    closeMap();
  });

  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('sm-map-dialog-open');
    pointers.clear();
    gesture = null;
    if (activeTrigger?.isConnected) activeTrigger.focus({ preventScroll: true });
    activeTrigger = null;
  });

  dialog.addEventListener('keydown', event => {
    if (event.key === 'Tab') {
      const focusable = [...dialog.querySelectorAll('button:not([disabled]), [tabindex="0"]')].filter(element => !element.hidden);
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
      return;
    }

    if (event.key === '+' || event.key === '=') {
      event.preventDefault();
      zoomFromCentre(1.25);
    } else if (event.key === '-' || event.key === '_') {
      event.preventDefault();
      zoomFromCentre(0.8);
    } else if (event.key.startsWith('Arrow')) {
      event.preventDefault();
      const step = event.shiftKey ? 100 : 48;
      if (event.key === 'ArrowLeft') transform.x += step;
      if (event.key === 'ArrowRight') transform.x -= step;
      if (event.key === 'ArrowUp') transform.y += step;
      if (event.key === 'ArrowDown') transform.y -= step;
      applyTransform();
    }
  });

  viewport.addEventListener('wheel', event => {
    event.preventDefault();
    zoomAt(event.clientX, event.clientY, Math.exp(-event.deltaY * 0.001));
  }, { passive: false });

  function distanceBetween(first, second) {
    return Math.hypot(first.x - second.x, first.y - second.y);
  }

  function centreBetween(first, second) {
    return { x: (first.x + second.x) / 2, y: (first.y + second.y) / 2 };
  }

  function updateGesture() {
    const points = [...pointers.values()];
    if (points.length === 1) {
      gesture = { type: 'pan', last: points[0] };
    } else if (points.length >= 2) {
      gesture = {
        type: 'pinch',
        lastDistance: Math.max(0.01, distanceBetween(points[0], points[1])),
        lastCentre: centreBetween(points[0], points[1])
      };
    } else {
      gesture = null;
    }
  }

  viewport.addEventListener('pointerdown', event => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    event.preventDefault();
    try { viewport.setPointerCapture(event.pointerId); } catch {}
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    updateGesture();
    viewport.classList.add('is-dragging');
  });

  viewport.addEventListener('pointermove', event => {
    if (!pointers.has(event.pointerId)) return;
    event.preventDefault();
    const previous = pointers.get(event.pointerId);
    const current = { x: event.clientX, y: event.clientY };
    pointers.set(event.pointerId, current);

    if (pointers.size === 1 && gesture?.type === 'pan') {
      transform.x += current.x - previous.x;
      transform.y += current.y - previous.y;
      gesture.last = current;
      applyTransform();
    } else if (pointers.size >= 2 && gesture?.type === 'pinch') {
      const points = [...pointers.values()];
      const nextCentre = centreBetween(points[0], points[1]);
      const nextDistance = Math.max(0.01, distanceBetween(points[0], points[1]));
      zoomAt(gesture.lastCentre.x, gesture.lastCentre.y, nextDistance / gesture.lastDistance);
      transform.x += nextCentre.x - gesture.lastCentre.x;
      transform.y += nextCentre.y - gesture.lastCentre.y;
      gesture.lastCentre = nextCentre;
      gesture.lastDistance = nextDistance;
      applyTransform();
    }
  });

  function endPointer(event) {
    pointers.delete(event.pointerId);
    if (pointers.size === 0) viewport.classList.remove('is-dragging');
    updateGesture();
  }

  viewport.addEventListener('pointerup', endPointer);
  viewport.addEventListener('pointercancel', endPointer);
  viewport.addEventListener('lostpointercapture', endPointer);
})();
