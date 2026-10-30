/* SkillMatch: shared helpers. The profile lives in sessionStorage only (cleared when the tab
   closes) and is sent with each results/detail request. Nothing is stored on the server. */
(function () {
  "use strict";
  var KEY = "skillmatch.profile";

  function getProfile() {
    try { return sessionStorage.getItem(KEY) || ""; } catch (e) { return ""; }
  }
  function setProfile(obj) {
    try { sessionStorage.setItem(KEY, JSON.stringify(obj)); return true; } catch (e) { return false; }
  }
  function clearProfile() {
    try { sessionStorage.removeItem(KEY); } catch (e) { /* ignore */ }
  }
  function hasProfile() { return getProfile() !== ""; }

  window.SkillMatch = { getProfile: getProfile, setProfile: setProfile, clearProfile: clearProfile, hasProfile: hasProfile };

  // Send the profile with every HTMX request that asks for it.
  document.addEventListener("htmx:configRequest", function (evt) {
    if (evt.detail.elt.closest("[data-send-profile]")) {
      evt.detail.headers["X-SkillMatch-Profile"] = getProfile();
      evt.detail.parameters.profile = getProfile();
    }
  });

  // Reveal or copy a job brief when the Tailor my CV page is unavailable.
  document.addEventListener("click", function (evt) {
    var toggle = evt.target.closest("[data-brief-toggle]");
    if (toggle) {
      var panel = document.getElementById(toggle.dataset.briefToggle);
      if (panel) {
        panel.hidden = !panel.hidden;
        toggle.textContent = panel.hidden ? "Tailor my CV" : "Hide job brief";
      }
      return;
    }
    var button = evt.target.closest("[data-copy-brief]");
    if (!button) return;
    var field = document.getElementById(button.dataset.copyBrief);
    if (!field) return;
    field.focus(); field.select();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(field.value).then(function () { button.textContent = "Copied"; }).catch(function () { document.execCommand("copy"); });
    } else { document.execCommand("copy"); }
  });

  // Show the profile-only parts of a page when a profile exists.
  document.addEventListener("DOMContentLoaded", function () {
    var has = hasProfile();
    document.querySelectorAll("[data-if-profile]").forEach(function (el) { el.hidden = !has; });
    document.querySelectorAll("[data-if-no-profile]").forEach(function (el) { el.hidden = has; });
    document.dispatchEvent(new CustomEvent("skillmatch:profile-checked", { detail: { hasProfile: has } }));
  });
})();
