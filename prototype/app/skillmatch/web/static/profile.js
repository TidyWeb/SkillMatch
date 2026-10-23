/* SkillMatch profile form. Builds the profile JSON and keeps it in sessionStorage only. */
(function () {
  "use strict";
  var tax = JSON.parse(document.getElementById("taxonomy-data").textContent);
  var personas = JSON.parse(document.getElementById("persona-data").textContent);
  var form = document.getElementById("profile-form");
  var rolesBox = document.getElementById("roles");
  var roleTemplate = document.getElementById("role-template");
  var MAX_ROLES = 4;
  var uid = 0;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function nextId(prefix) { uid += 1; return prefix + "-" + uid; }

  // ---------- postcode: only the outward code leaves the browser ----------
  var OUTWARD = /^([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})?$/;
  function outwardCode(text) {
    var m = OUTWARD.exec((text || "").trim().toUpperCase());
    return m ? m[1] : null;
  }

  // ---------- skills ----------
  function addSkillRow(id, level) {
    if (!tax.skills[id] || $("#skill-" + id)) return;
    var row = document.createElement("div");
    row.className = "skill-row";
    var label = document.createElement("label");
    label.setAttribute("for", "skill-" + id);
    label.textContent = tax.skills[id].label;
    var sel = document.createElement("select");
    sel.id = "skill-" + id;
    sel.setAttribute("data-skill", id);
    [["", "Not ticked"], ["course", "Learned on a course"], ["project", "Used in a project"], ["confident", "Confident"]].forEach(function (o) {
      var opt = document.createElement("option");
      opt.value = o[0]; opt.textContent = o[1];
      sel.appendChild(opt);
    });
    sel.value = level || "project";
    row.appendChild(label);
    row.appendChild(sel);
    document.getElementById("other-skills").appendChild(row);
  }
  document.getElementById("add-skill-btn").addEventListener("click", function () {
    var sel = document.getElementById("add-skill");
    if (sel.value) { addSkillRow(sel.value); sel.value = ""; }
  });

  // ---------- roles and competencies ----------
  function compRow(roleEl, id, evidence, ticked) {
    var box = $("[data-competencies]", roleEl);
    if ($('[data-comp="' + id + '"]', box)) return;
    var c = tax.competencies[id];
    var row = document.createElement("div");
    row.className = "comp";
    row.setAttribute("data-comp", id);
    var cb = document.createElement("input");
    cb.type = "checkbox"; cb.id = nextId("comp");
    cb.checked = !!ticked;
    var lab = document.createElement("label");
    lab.setAttribute("for", cb.id);
    lab.className = "comp-label";
    lab.textContent = c.label.charAt(0).toUpperCase() + c.label.slice(1);
    var head = document.createElement("div");
    head.className = "comp-head";
    head.appendChild(cb); head.appendChild(lab);
    var desc = document.createElement("p");
    desc.className = "hint"; desc.textContent = c.description;
    var evLab = document.createElement("label");
    var ev = document.createElement("input");
    ev.id = nextId("ev"); ev.maxLength = 200; ev.value = evidence || "";
    ev.setAttribute("data-evidence", "");
    evLab.setAttribute("for", ev.id);
    evLab.className = "evidence-label";
    evLab.textContent = "Your evidence, one line (optional)";
    ev.placeholder = "What you did, ideally with a number";
    ev.addEventListener("input", function () { if (ev.value.trim()) cb.checked = true; });
    row.appendChild(head); row.appendChild(desc); row.appendChild(evLab); row.appendChild(ev);
    box.appendChild(row);
  }

  function refreshAddComp(roleEl) {
    var sel = $("[data-field=add-comp]", roleEl);
    var present = $all("[data-comp]", roleEl).map(function (el) { return el.getAttribute("data-comp"); });
    sel.innerHTML = "";
    var first = document.createElement("option");
    first.value = ""; first.textContent = "Choose a competency…";
    sel.appendChild(first);
    Object.keys(tax.competencies).forEach(function (id) {
      if (present.indexOf(id) !== -1) return;
      var o = document.createElement("option");
      o.value = id; o.textContent = tax.competencies[id].label;
      sel.appendChild(o);
    });
  }

  function proposeFor(roleEl, archetypeId) {
    var a = tax.archetypes[archetypeId];
    if (!a) return;
    a.competencies.forEach(function (id) { compRow(roleEl, id, "", false); });
    refreshAddComp(roleEl);
  }

  function renumber() {
    $all(".role", rolesBox).forEach(function (el, i) { $("[data-role-n]", el).textContent = String(i + 1); });
    document.getElementById("add-role").hidden = $all(".role", rolesBox).length >= MAX_ROLES;
  }

  function addRole(data) {
    if ($all(".role", rolesBox).length >= MAX_ROLES) return null;
    var frag = roleTemplate.content.cloneNode(true);
    var roleEl = frag.querySelector(".role");
    $all("[data-for]", roleEl).forEach(function (lab) {
      var field = lab.getAttribute("data-for");
      var input = $("[data-field=" + field + "]", roleEl);
      var id = nextId(field);
      input.id = id; lab.setAttribute("for", id);
    });
    rolesBox.appendChild(roleEl);
    var archSel = $("[data-field=archetype]", roleEl);
    var title = $("[data-field=title]", roleEl);
    var note = $("[data-match-note]", roleEl);
    archSel.addEventListener("change", function () { proposeFor(roleEl, archSel.value); note.textContent = ""; });
    title.addEventListener("change", function () {
      if (archSel.value || !title.value.trim()) return;
      fetch("/api/archetype?title=" + encodeURIComponent(title.value.trim()))
        .then(function (r) { return r.json(); })
        .then(function (hit) {
          if (hit && hit.id && !archSel.value) {
            archSel.value = hit.id;
            proposeFor(roleEl, hit.id);
            note.textContent = "We matched “" + title.value.trim() + "” to " + hit.label + ". Change it if that's wrong.";
          } else if (!archSel.value) {
            note.textContent = "We couldn't match that title. Choose the closest kind of role.";
          }
        })
        .catch(function () { /* offline: the user can still choose */ });
    });
    $("[data-add-comp]", roleEl).addEventListener("click", function () {
      var sel = $("[data-field=add-comp]", roleEl);
      if (sel.value) { compRow(roleEl, sel.value, "", true); refreshAddComp(roleEl); }
    });
    $("[data-remove-role]", roleEl).addEventListener("click", function () {
      roleEl.remove();
      if (!$all(".role", rolesBox).length) addRole();
      renumber();
    });
    if (data) {
      title.value = data.title || "";
      archSel.value = data.archetype || "";
      $("[data-field=seniority]", roleEl).value = data.seniority || "individual";
      $("[data-field=years]", roleEl).value = data.years != null ? data.years : "";
      var comps = data.competencies || {};
      Object.keys(comps).forEach(function (id) { if (tax.competencies[id]) compRow(roleEl, id, comps[id], true); });
      if (data.archetype) proposeFor(roleEl, data.archetype);
    }
    refreshAddComp(roleEl);
    renumber();
    return roleEl;
  }
  document.getElementById("add-role").addEventListener("click", function () {
    var el = addRole();
    if (el) $("[data-field=title]", el).focus();
  });

  // ---------- collect and fill ----------
  function collect() {
    var skills = {};
    $all("[data-skill]").forEach(function (sel) { if (sel.value) skills[sel.getAttribute("data-skill")] = sel.value; });
    var roles = $all(".role", rolesBox).map(function (el) {
      var comps = {};
      $all("[data-comp]", el).forEach(function (row) {
        var cb = $("input[type=checkbox]", row);
        if (cb.checked) comps[row.getAttribute("data-comp")] = $("[data-evidence]", row).value.trim();
      });
      return {
        title: $("[data-field=title]", el).value.trim(),
        archetype: $("[data-field=archetype]", el).value,
        seniority: $("[data-field=seniority]", el).value,
        years: $("[data-field=years]", el).value,
        competencies: comps
      };
    }).filter(function (r) { return r.title || r.archetype; });
    var travel = $("input[name=travel]:checked");
    return {
      postcode: outwardCode($("#postcode").value) || "",
      travel: travel ? travel.value : "",
      max_miles: $("#max_miles").value,
      include_remote: $("#include_remote").checked,
      max_office_days: $("#max_office_days").value,
      skills: skills,
      roles: roles,
      qualifications: { ci_diploma: $("#ci_diploma").checked, degree: $("#degree").value, other: $("#other_quals").value.trim() },
      data_years: $("#data_years").value || 0,
      min_salary: $("#min_salary").value
    };
  }

  function fill(p) {
    $("#postcode").value = p.postcode || "";
    $all("input[name=travel]").forEach(function (r) { r.checked = r.value === p.travel; });
    $("#max_miles").value = p.max_miles || "";
    $("#include_remote").checked = p.include_remote !== false;
    $("#max_office_days").value = p.max_office_days != null ? String(Math.round(p.max_office_days)) : "5";
    var skills = p.skills || {};
    $all("[data-skill]").forEach(function (sel) {
      var id = sel.getAttribute("data-skill");
      sel.value = skills[id] || "";
    });
    document.getElementById("other-skills").innerHTML = "";
    Object.keys(skills).forEach(function (id) { if (!$("#skill-" + id)) addSkillRow(id, skills[id]); });
    rolesBox.innerHTML = "";
    (p.roles || []).forEach(function (r) { addRole(r); });
    if (!(p.roles || []).length) addRole();
    var q = p.qualifications || {};
    $("#ci_diploma").checked = q.ci_diploma !== false;
    $("#degree").value = q.degree || "none";
    $("#other_quals").value = q.other || "";
    $("#data_years").value = p.data_years != null ? p.data_years : 0;
    $("#min_salary").value = p.min_salary || "";
  }

  // ---------- events ----------
  $all("[data-persona]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var p = personas[btn.getAttribute("data-persona")];
      if (!p) return;
      fill(p);
      window.SkillMatch.setProfile(collect());
      document.getElementById("demo-status").innerHTML =
        "Loaded “" + btn.textContent + "”. Scroll down to review it, or <a href=\"/results\">see their matches</a>.";
    });
  });

  form.addEventListener("submit", function (evt) {
    evt.preventDefault();
    var raw = $("#postcode").value.trim();
    var err = $("#postcode-error");
    if (raw && !outwardCode(raw)) {
      err.textContent = "That doesn't look like a UK postcode. Try something like B91 or WV1 1SH.";
      $("#postcode").focus();
      return;
    }
    err.textContent = "";
    if (!window.SkillMatch.setProfile(collect())) {
      $("#form-status").textContent = "Your browser blocked session storage, so we can't keep your profile for the results page.";
      return;
    }
    window.location.href = "/results";
  });

  document.getElementById("clear-profile").addEventListener("click", function () {
    window.SkillMatch.clearProfile();
    form.reset();
    document.getElementById("other-skills").innerHTML = "";
    rolesBox.innerHTML = "";
    addRole();
    $("#form-status").textContent = "Profile cleared from this tab.";
  });

  // ---------- start ----------
  var saved = window.SkillMatch.getProfile();
  if (saved) {
    try { fill(JSON.parse(saved)); } catch (e) { addRole(); }
  } else {
    addRole();
  }
})();
