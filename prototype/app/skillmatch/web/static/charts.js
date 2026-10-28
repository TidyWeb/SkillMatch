/* Insights charts (Chart.js) and maps (Leaflet + OpenStreetMap tiles).
   One series per chart, so one colour: the site accent. Thin bars with rounded ends,
   hairline grid, hover tooltips; every chart also has a table view in the page. */
(function () {
  "use strict";
  var css = getComputedStyle(document.documentElement);
  var ACCENT = css.getPropertyValue("--accent").trim();
  var INK = css.getPropertyValue("--ink").trim();
  var INK_SOFT = css.getPropertyValue("--ink-soft").trim();
  var RULE = css.getPropertyValue("--rule").trim();
  var SURFACE = css.getPropertyValue("--paper-raised").trim();
  var TRANSPARENT = css.getPropertyValue("--transparent").trim();
  // Ordinal ramp for match, light -> dark; validated (one hue, monotone lightness, light end >= 2:1).
  var TIER = { not_yet: css.getPropertyValue("--tier-not-yet").trim(), stretch: css.getPropertyValue("--tier-stretch").trim(), good: css.getPropertyValue("--tier-good").trim(), strong: css.getPropertyValue("--tier-strong").trim() };
  function numberToken(name) { return Number(css.getPropertyValue(name).trim()); }
  var TIER_RADIUS = { strong: numberToken("--map-radius-strong"), good: numberToken("--map-radius-good"), stretch: numberToken("--map-radius-stretch"), not_yet: numberToken("--map-radius-not-yet") };

  function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }
  // Long category names wrap onto two lines instead of being clipped at the chart edge.
  function wrap(s, width) {
    s = cap(s);
    if (s.length <= width) return s;
    var words = s.split(" "), lines = [""];
    words.forEach(function (w) {
      var last = lines[lines.length - 1];
      if ((last + " " + w).trim().length > width && last) lines.push(w); else lines[lines.length - 1] = (last + " " + w).trim();
    });
    return lines;
  }

  function bar(id, rows, horizontal) {
    var el = document.getElementById(id);
    if (!el || !window.Chart || !rows || !rows.length) return;
    Chart.defaults.font.family = css.getPropertyValue("--sans");
    Chart.defaults.color = INK_SOFT;
    var narrow = el.parentNode.clientWidth < 420;
    var labels = rows.map(function (r) { return horizontal ? wrap(r.label, narrow ? 17 : 24) : cap(r.label); });
    el.parentNode.classList.remove("chart-box--small", "chart-box--medium", "chart-box--large");
    if (horizontal) {
      Array.from(el.parentNode.classList).filter(function (name) { return name.indexOf("chart-rows-") === 0; }).forEach(function (name) { el.parentNode.classList.remove(name); });
      var bucket = Math.min(60, Math.max(5, Math.ceil(rows.length / 5) * 5));
      el.parentNode.classList.add("chart-rows-" + bucket);
    }
    new Chart(el, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{ data: rows.map(function (r) { return r.n; }), backgroundColor: ACCENT, borderRadius: numberToken("--chart-radius"), borderSkipped: "start", maxBarThickness: 14 }]
      },
      options: {
        indexAxis: horizontal ? "y" : "x",
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: function (c) { return " " + c.parsed[horizontal ? "x" : "y"] + " adverts"; } } }
        },
        scales: {
          x: { grid: { color: horizontal ? RULE : TRANSPARENT }, border: { color: RULE }, ticks: { color: horizontal ? INK_SOFT : INK, precision: 0, autoSkip: horizontal }, beginAtZero: true },
          y: { grid: { color: horizontal ? TRANSPARENT : RULE }, border: { color: RULE }, ticks: { color: horizontal ? INK : INK_SOFT, precision: 0, autoSkip: !horizontal }, beginAtZero: true }
        }
      }
    });
  }

  function baseMap(id) {
    var el = document.getElementById(id);
    if (!el || !window.L || el.dataset.ready) return null;
    el.dataset.ready = "1";
    var map = L.map(el, { scrollWheelZoom: false }).setView([52.48, -1.95], 8);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    return map;
  }

  function popup(p) {
    var a = document.createElement("div");
    var link = document.createElement("a");
    link.href = "/job/" + encodeURIComponent(p.id).replace(/%3A/g, ":");
    link.textContent = p.title;
    a.appendChild(link);
    var meta = document.createElement("div");
    meta.textContent = (p.employer ? p.employer : "") + (p.label ? " · " + p.label : "") + (p.approx ? " · area only" : "");
    a.appendChild(meta);
    return a;
  }

  function plot(map, points, byTier) {
    var bounds = [];
    // Draw weaker matches first so the strongest sit on top.
    var order = ["not_yet", "stretch", "good", "strong"];
    points.slice().sort(function (a, b) { return order.indexOf(a.tier) - order.indexOf(b.tier); }).forEach(function (p) {
      var colour = byTier ? TIER[p.tier] : ACCENT;
      L.circleMarker([p.lat, p.lon], {
        radius: byTier ? TIER_RADIUS[p.tier] : numberToken("--map-radius-default"), color: SURFACE, weight: 2, fillColor: colour, fillOpacity: 0.95
      }).bindPopup(popup(p)).addTo(map);
      bounds.push([p.lat, p.lon]);
    });
    if (bounds.length) map.fitBounds(bounds, { padding: [24, 24], maxZoom: 11 });
  }

  function general() {
    var node = document.getElementById("insights-data");
    if (!node) return;
    var d = JSON.parse(node.textContent);
    bar("chart-comp", d.competencies, true);
    bar("chart-skills", d.skills, true);
    bar("chart-salary", d.salary.bands, true);
    bar("chart-senior", d.senior_words, true);
    bar("chart-arr", d.arrangement, true);
    var showAll = function () {
      var host = document.getElementById("map-all");
      if (!host || host.closest("[hidden]")) return;
      var map = baseMap("map-all");
      if (map) plot(map, d.points, false);
    };
    showAll();
    document.addEventListener("skillmatch:profile-checked", showAll);
  }

  function personal() {
    var node = document.getElementById("insights-personal");
    if (!node || node.dataset.done) return;
    node.dataset.done = "1";
    var d = JSON.parse(node.textContent);
    var map = baseMap("map-you");
    if (map) {
      plot(map, d.points, true);
      if (d.home) {
        L.circleMarker(d.home, { radius: numberToken("--map-radius-home"), color: INK, weight: 3, fillColor: SURFACE, fillOpacity: 1 })
          .bindPopup("Your area (" + (d.outcode || "") + ")").addTo(map);
      }
    }
    bar("chart-mine", d.my_competencies, true);
    bar("chart-distance", d.distance_bands, true);
  }

  function start() { general(); personal(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
  document.addEventListener("htmx:afterSettle", personal);
})();
