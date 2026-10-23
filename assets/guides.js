/* SkillMatch team guides: small-screen Contents menu. */
(function () {
  var bar = document.querySelector(".sidebar"), toggle = document.querySelector(".menu-toggle");
  if (!bar || !toggle) return;
  toggle.addEventListener("click", function () {
    var open = bar.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
