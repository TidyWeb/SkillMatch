/* Loads request-scoped skill data and draws its chart without storing the profile server-side. */
(function () {
  "use strict";
  var status = document.getElementById("skill-page-status");
  if (!status) return;

  var loading = document.getElementById("skill-page-loading");
  var noProfile = document.getElementById("skill-page-no-profile");
  var errorPanel = document.getElementById("skill-page-error");
  var errorMessage = document.getElementById("skill-page-error-message");
  var results = document.getElementById("skill-page-results");
  var chartRoot = document.getElementById("skill-level-chart-scroll");
  var summaryRoot = document.getElementById("skill-summary");
  var vacancyRoot = document.getElementById("skill-vacancy-list");
  var SVG_NS = "http://www.w3.org/2000/svg";

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function svgElement(tag, attributes, text) {
    var node = document.createElementNS(SVG_NS, tag);
    Object.keys(attributes || {}).forEach(function (name) {
      node.setAttribute(name, attributes[name]);
    });
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function renderChart(rows) {
    chartRoot.replaceChildren();
    var empty = document.getElementById("skill-chart-empty");
    if (!rows.length) {
      empty.hidden = false;
      return;
    }
    empty.hidden = true;

    var rowHeight = 46;
    var chart = svgElement("svg", {
      "class": "skill-level-chart",
      "viewBox": "0 0 1000 " + (70 + rows.length * rowHeight),
      "role": "img",
      "aria-labelledby": "skill-chart-title skill-chart-description"
    });
    chart.appendChild(svgElement("title", { id: "skill-chart-title" }, "Your skill levels and essential vacancy requirements"));
    chart.appendChild(svgElement(
      "desc",
      { id: "skill-chart-description" },
      "Skills are ordered by essential vacancy count. Bars show your selected level from one for not ticked to four for confident. The dotted line shows relative essential vacancy counts."
    ));

    var tickLabels = { 1: "Not ticked", 2: "Learned", 3: "Project", 4: "Confident" };
    var plotBottom = 52 + rows.length * rowHeight;
    for (var tick = 1; tick <= 4; tick += 1) {
      var tickX = 365 + tick * 145;
      chart.appendChild(svgElement("line", {
        "class": "skill-chart-gridline", x1: tickX, y1: 50, x2: tickX, y2: plotBottom
      }));
      chart.appendChild(svgElement("text", {
        "class": "skill-chart-axis", x: tickX, y: 43, "text-anchor": "middle"
      }, tickLabels[tick]));
    }
    chart.appendChild(svgElement("text", {
      "class": "skill-chart-axis-title", x: 655, y: 14, "text-anchor": "middle"
    }, "Your skill level / essential vacancy demand"));

    var points = [];
    rows.forEach(function (row, index) {
      var y = 70 + index * rowHeight;
      var score = Math.max(1, Math.min(4, Number(row.score) || 1));
      var demand = Math.max(1, Math.min(4, Number(row.demand_score) || 1));
      var courseStatus = row.course_covered === true
        ? "On course"
        : row.course_covered === false ? "Not on course" : "Course coverage unknown";
      var barColor = /^#[0-9a-f]{6}$/i.test(row.bar_color) ? row.bar_color : "#D8D2C4";

      chart.appendChild(svgElement("text", {
        "class": "skill-chart-name", x: 12, y: y - 3
      }, (index + 1) + ". " + row.skill));
      chart.appendChild(svgElement("text", {
        "class": "skill-chart-detail", x: 12, y: y + 13
      }, row.profile_level + " · " + courseStatus + " · " + row.count + " essential vacancies"));
      chart.appendChild(svgElement("rect", {
        "class": "skill-chart-bar", x: 365, y: y - 9, width: score * 145, height: 18, rx: 2, fill: barColor
      }));
      points.push((365 + demand * 145) + "," + y);
    });
    if (rows.length > 1) {
      chart.appendChild(svgElement("polyline", {
        "class": "skill-chart-demand-line", points: points.join(" ")
      }));
    }
    rows.forEach(function (row, index) {
      var demand = Math.max(1, Math.min(4, Number(row.demand_score) || 1));
      chart.appendChild(svgElement("circle", {
        "class": "skill-chart-demand-point",
        cx: 365 + demand * 145,
        cy: 70 + index * rowHeight,
        r: 4
      }));
    });
    chartRoot.appendChild(chart);
  }

  function renderGroups(groups) {
    summaryRoot.replaceChildren();
    groups.forEach(function (group) {
      var section = element("section", "skill-summary-group panel");
      var heading = element("h3", "", group.label + " ");
      var count = element("span", "count", String(group.skills.length));
      heading.appendChild(count);
      section.appendChild(heading);
      if (group.skills.length) {
        var list = element("ul", "skill-summary-list");
        group.skills.forEach(function (skill) {
          list.appendChild(element("li", "", skill));
        });
        section.appendChild(list);
      } else {
        section.appendChild(element("p", "hint", "No skills in this group."));
      }
      summaryRoot.appendChild(section);
    });
  }

  function renderVacancyRows(comparison) {
    vacancyRoot.replaceChildren();
    var empty = document.getElementById("skill-vacancy-empty");
    if (!comparison.skills.length) {
      empty.hidden = false;
      return;
    }
    empty.hidden = true;
    comparison.skills.forEach(function (row) {
      var item = element("div", "skill-comparison-row");
      item.appendChild(element("p", "skill-comparison-sentence", row.sentence));
      var progress = element("progress");
      progress.max = comparison.max_count || 1;
      progress.value = row.count;
      progress.setAttribute("aria-label", row.sentence);
      item.appendChild(progress);
      var statusLine = element("div", "skill-comparison-status");
      var coverage = row.course_covered === true ? "Yes" : row.course_covered === false ? "No" : "Unknown";
      statusLine.appendChild(element("span", "skill-status", "Course covered: " + coverage));
      statusLine.appendChild(element(
        "span",
        "skill-status",
        "Profile: " + (row.profile_level || "Not ticked")
      ));
      statusLine.appendChild(element("span", "skill-status", "Essential: " + row.essential_count));
      item.appendChild(statusLine);
      vacancyRoot.appendChild(item);
    });
  }

  function showError(message) {
    loading.hidden = true;
    noProfile.hidden = true;
    errorPanel.hidden = false;
    errorMessage.textContent = message;
  }

  var profile = window.SkillMatch && window.SkillMatch.getProfile();
  if (!profile) {
    loading.hidden = true;
    noProfile.hidden = false;
    return;
  }

  fetch("/api/profile/skills", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
    body: new URLSearchParams({ profile: profile }),
    cache: "no-store"
  }).then(function (response) {
    return response.json().then(function (data) {
      if (!response.ok) throw new Error(data.error || "Could not load your skill data.");
      return data;
    });
  }).then(function (data) {
    renderChart(data.comparison.chart || []);
    renderGroups(data.groups || []);
    renderVacancyRows(data.comparison);
    loading.hidden = true;
    status.hidden = true;
    results.hidden = false;
  }).catch(function (error) {
    showError(error.message || "Could not load your skill data.");
  });
})();
