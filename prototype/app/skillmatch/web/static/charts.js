/* Insights charts and maps use the named design tokens; charts have table twins. */
(function () {
  "use strict";
  var css = getComputedStyle(document.documentElement);
  function token(name) {
    var value = css.getPropertyValue(name).trim();
    if (!value) throw new Error("Missing required style token " + name);
    return value;
  }
  var ACCENT = token("--accent");
  var INK = token("--ink");
  var INK_SOFT = token("--ink-soft");
  var RULE = token("--rule");
  var SURFACE = token("--paper-raised");
  var TRANSPARENT = token("--transparent");
  var ESSENTIAL_DEMAND = token("--chart-essential-demand");
  var COURSE_COVERAGE = token("--chart-course-coverage");
  var TIER = {
    not_yet: token("--tier-not-yet"),
    stretch: token("--tier-stretch"),
    good: token("--tier-good"),
    strong: token("--tier-strong")
  };
  var TIER_LABEL = { strong: "Strong fit", good: "Good fit", stretch: "Stretch", not_yet: "Not yet" };
  var TIER_RADIUS = { strong: 8, good: 7, stretch: 6, not_yet: 6 };

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
    if (horizontal) {
      // Give every row room for its longest wrapped label so labels never overlap.
      var lines = labels.reduce(function (m, l) { return Math.max(m, Array.isArray(l) ? l.length : 1); }, 1);
      var rowPx = Math.max(30, lines * 15 + 10);
      el.parentNode.style.height = (48 + rows.length * rowPx) + "px";
    }
    new Chart(el, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{ data: rows.map(function (r) { return r.n; }), backgroundColor: ACCENT, borderRadius: 4, borderSkipped: "start", maxBarThickness: 14 }]
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

  function essentialSkills(rows) {
    var el = document.getElementById("chart-essential-skills");
    if (!el || !window.Chart || !rows || !rows.length) return;
    Chart.defaults.font.family = css.getPropertyValue("--sans");
    Chart.defaults.color = INK_SOFT;
    new Chart(el, {
      type: "radar",
      data: {
        labels: rows.map(function (row) { return row.label; }),
        datasets: [
          {
            label: "Essential skill demand share",
            data: rows.map(function (row) { return row.share; }),
            borderColor: ESSENTIAL_DEMAND,
            backgroundColor: TRANSPARENT,
            pointBackgroundColor: ESSENTIAL_DEMAND,
            borderWidth: 2
          },
          {
            label: "Course coverage overlap",
            data: rows.map(function (row) { return row.course_share; }),
            borderColor: COURSE_COVERAGE,
            backgroundColor: TRANSPARENT,
            pointBackgroundColor: COURSE_COVERAGE,
            borderWidth: 2
          }
        ]
      },
      options: {
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                return " " + context.dataset.label + ": " + context.parsed.r.toFixed(2) + "%";
              }
            }
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            ticks: {
              color: INK_SOFT,
              callback: function (value) { return value + "%"; }
            },
            grid: { color: RULE },
            angleLines: { color: RULE },
            pointLabels: { color: INK, font: { size: 10 } }
          }
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
    // Draw weaker fits first so the strongest sit on top.
    var order = ["not_yet", "stretch", "good", "strong"];
    points.slice().sort(function (a, b) { return order.indexOf(a.tier) - order.indexOf(b.tier); }).forEach(function (p) {
      var colour = byTier ? TIER[p.tier] : ACCENT;
      var markerOutline = byTier && (p.tier === "stretch" || p.tier === "not_yet") ? INK : SURFACE;
      L.circleMarker([p.lat, p.lon], {
        radius: byTier ? TIER_RADIUS[p.tier] : 6, color: markerOutline, weight: 2, fillColor: colour, fillOpacity: 0.95
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
    essentialSkills(d.essential_skill_chart);
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
        L.circleMarker(d.home, { radius: 9, color: INK, weight: 3, fillColor: SURFACE, fillOpacity: 1 })
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
