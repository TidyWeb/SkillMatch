/* Builds the simplified profile JSON and keeps it in sessionStorage only. */
(function () {
  "use strict";
  var taxNode = document.getElementById("taxonomy-data");
  var form = document.getElementById("profile-form");
  if (!taxNode || !form) return;
  var tax = JSON.parse(taxNode.textContent);
  var skillsBox = document.getElementById("selected-skills");
  var areasBox = document.getElementById("selected-areas");
  function $(selector, root) { return (root || document).querySelector(selector); }
  function $all(selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); }
  var OUTWARD = /^([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})?$/;
  function outwardCode(text) { var m = OUTWARD.exec((text || "").trim().toUpperCase()); return m ? m[1] : ""; }

  function skillChip(id, level) {
    if (!tax.skills[id] || $('[data-skill-chip="' + id + '"]', skillsBox)) return;
    var template = document.getElementById("selected-item-template");
    var chip = template.content.firstElementChild.cloneNode(true); chip.dataset.skillChip = id;
    chip.querySelector("[data-item-label]").textContent = tax.skills[id].label;
    var levelSelect = chip.querySelector("[data-skill-level]");
    levelSelect.dataset.skillLevel = id;
    levelSelect.setAttribute("aria-label", "Your experience level with " + tax.skills[id].label);
    levelSelect.value = level || "";
    var remove = chip.querySelector("[data-remove-item]");
    remove.setAttribute("aria-label", "Remove " + tax.skills[id].label);
    remove.addEventListener("click", function () { chip.remove(); refreshSkillOptions(); });
    skillsBox.appendChild(chip); refreshSkillOptions();
  }
  function refreshSkillOptions() {
    var select = document.getElementById("add-skill");
    var selected = $all("[data-skill-chip]", skillsBox).map(function (el) { return el.dataset.skillChip; });
    $all("option", select).forEach(function (option) { if (option.value) option.hidden = selected.indexOf(option.value) !== -1; });
  }
  document.getElementById("add-skill").addEventListener("change", function (event) {
    if (event.target.value) skillChip(event.target.value);
    event.target.value = "";
  });

  function makeArea(id, selectedSkills) {
    var area = (tax.areas || []).find(function (item) { return item.id === id; });
    if (!area || $('[data-area="' + id + '"]', areasBox) || $all("[data-area]", areasBox).length >= 5) return;
    var section = document.createElement("fieldset"); section.className = "area-item"; section.dataset.area = id;
    var legend = document.createElement("legend"); legend.textContent = area.label; section.appendChild(legend);
    var remove = document.createElement("button"); remove.type = "button"; remove.className = "button-quiet"; remove.textContent = "Remove area";
    remove.addEventListener("click", function () { section.remove(); refreshAreaOptions(); }); section.appendChild(remove);
    var skillIds = area.competencies || area.skills || [];
    skillIds.forEach(function (skillId) {
      var comp = (tax.competencies || {})[skillId]; if (!comp) return;
      var row = document.createElement("label"); row.className = "choice area-skill";
      var checkbox = document.createElement("input"); checkbox.type = "checkbox"; checkbox.value = skillId; checkbox.checked = selectedSkills === undefined || selectedSkills.indexOf(skillId) >= 0;
      row.append(checkbox, document.createTextNode(comp.label)); section.appendChild(row);
    });
    areasBox.appendChild(section); refreshAreaOptions();
  }
  function refreshAreaOptions() {
    var select = document.getElementById("add-area");
    var selected = $all("[data-area]", areasBox).map(function (el) { return el.dataset.area; });
    $all("option", select).forEach(function (option) { if (option.value) option.hidden = selected.indexOf(option.value) !== -1; });
    select.disabled = selected.length >= 5;
  }
  document.getElementById("add-area").addEventListener("change", function (event) {
    if (event.target.value) makeArea(event.target.value);
    event.target.value = "";
  });
  function collect() {
    var travel = $("#travel").value;
    return {
      postcode: outwardCode($("#postcode").value), travel: travel,
      max_miles: $("#max_miles").value, include_remote: $("#include_remote").checked,
      max_office_days: $("#max_office_days").value,
      skills: $all("[data-skill-chip]", skillsBox).map(function (el) { return el.dataset.skillChip; }),
      skill_levels: $all("[data-skill-level]").reduce(function (levels, select) {
        if (select.value) levels[select.dataset.skillLevel] = select.value;
        return levels;
      }, {}),
      areas: $all("[data-area]", areasBox).map(function (el) {
        return { id: el.dataset.area, skills: $all("input[type=checkbox]:checked", el).map(function (cb) { return cb.value; }) };
      }),
      highest_qualification: Number($("#highest_qualification").value)
    };
  }
  function fill(profile) {
    if (!profile || typeof profile !== "object" || !Array.isArray(profile.skills) || !Array.isArray(profile.areas) || !Number.isFinite(Number(profile.highest_qualification))) return false;
    $("#postcode").value = profile.postcode || ""; $("#travel").value = profile.travel || "";
    $("#max_miles").value = profile.max_miles || ""; $("#include_remote").checked = profile.include_remote !== false;
    $("#max_office_days").value = profile.max_office_days != null ? String(profile.max_office_days) : "5";
    skillsBox.replaceChildren();
    profile.skills.forEach(function (id) {
      skillChip(id, profile.skill_levels && profile.skill_levels[id]);
    });
    $all("[data-skill-level]").forEach(function (select) {
      if (profile.skill_levels && typeof profile.skill_levels === "object") {
        select.value = Object.prototype.hasOwnProperty.call(profile.skill_levels, select.dataset.skillLevel)
          ? profile.skill_levels[select.dataset.skillLevel]
          : "";
      } else if (tax.skills[select.dataset.skillLevel] && tax.skills[select.dataset.skillLevel].course) {
        select.value = "course";
      }
    });
    areasBox.replaceChildren(); profile.areas.slice(0, 5).forEach(function (area) { if (area && area.id) makeArea(area.id, Array.isArray(area.skills) ? area.skills : []); });
    $("#highest_qualification").value = String(profile.highest_qualification);
    return true;
  }
  function clearForm() {
    form.reset(); skillsBox.replaceChildren(); areasBox.replaceChildren(); refreshSkillOptions(); refreshAreaOptions();
    $("#max_office_days").value = "5"; $("#include_remote").checked = true;
  }
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var raw = $("#postcode").value.trim();
    if (raw && !outwardCode(raw)) { $("#postcode-error").textContent = "Enter a UK postcode, such as B91 or WV1 1SH."; $("#postcode").focus(); return; }
    $("#postcode-error").textContent = "";
    if (!window.SkillMatch.setProfile(collect())) { $("#form-status").textContent = "Your browser blocked session storage, so we cannot keep this profile for the results page."; return; }
    window.location.href = "/results";
  });
  document.getElementById("clear-profile").addEventListener("click", function () {
    window.SkillMatch.clearProfile(); clearForm(); $("#form-status").textContent = "Profile cleared from this tab.";
  });
  var saved = window.SkillMatch.getProfile();
  if (saved) { try { if (!fill(JSON.parse(saved))) window.SkillMatch.clearProfile(); } catch (error) { window.SkillMatch.clearProfile(); } }
})();
