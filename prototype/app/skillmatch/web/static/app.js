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
      evt.detail.parameters.profile = getProfile();
    }
  });

  // Show the profile-only parts of a page when a profile exists.
  document.addEventListener("DOMContentLoaded", function () {
    var has = hasProfile();
    document.querySelectorAll("[data-if-profile]").forEach(function (el) { el.hidden = !has; });
    document.querySelectorAll("[data-if-no-profile]").forEach(function (el) { el.hidden = has; });
    document.dispatchEvent(new CustomEvent("skillmatch:profile-checked", { detail: { hasProfile: has } }));
  });
})();
