// Dynamic page behaviour for serve-page pages. Paste this whole file into one inline <script>
// at the end of <body>. No fetch, no storage, no external code. Without JS every panel shows.
//
// Markup it drives:
//   Tabs     <nav class="tabs"><a href="#infra">Infra</a>...</nav>  <section class="panel" id="infra">
//   Layers   <input type="checkbox" data-layer="planned" checked>    any element with class="planned"
//   Links    <g data-id="db">  ...  <div data-links="db api">         click a [data-links] element
//            (or an svg [data-id]) to highlight every [data-id] it names; click again to clear
//   Stepper  <div class="stepper"><div class="step">..</div>...<button data-step="-1">..
(function () {
  var d = document;
  d.documentElement.classList.add("js");

  // Tabs, driven by the URL hash so a tab can be linked.
  var panels = [].slice.call(d.querySelectorAll("section.panel"));
  function show() {
    if (!panels.length) return;
    var id = location.hash.slice(1);
    if (!panels.some(function (p) { return p.id === id; })) id = panels[0].id;
    panels.forEach(function (p) { p.hidden = p.id !== id; });
    d.querySelectorAll(".tabs a").forEach(function (a) {
      a.setAttribute("aria-current", a.getAttribute("href") === "#" + id ? "page" : "false");
    });
  }
  window.addEventListener("hashchange", show);
  show();

  // Layer toggles: hide every element that carries the layer's class.
  d.querySelectorAll("input[data-layer]").forEach(function (box) {
    box.addEventListener("change", function () {
      d.body.classList.toggle("hide-" + box.dataset.layer, !box.checked);
    });
  });

  // Click to highlight related parts.
  var active = null;
  function clear() {
    d.querySelectorAll(".hl").forEach(function (e) { e.classList.remove("hl"); });
    d.body.classList.remove("focus");
    active = null;
  }
  d.addEventListener("click", function (ev) {
    var src = ev.target.closest("[data-links], svg [data-id]");
    if (!src) return;
    if (active === src) { clear(); return; }
    clear();
    var ids = (src.dataset.links || src.dataset.id).split(/\s+/);
    ids.forEach(function (id) {
      d.querySelectorAll('[data-id="' + id + '"], [data-links~="' + id + '"]')
        .forEach(function (e) { e.classList.add("hl"); });
    });
    src.classList.add("hl");
    d.body.classList.add("focus");
    active = src;
  });

  // Steppers: one frame at a time, with previous and next buttons and a counter.
  d.querySelectorAll(".stepper").forEach(function (st) {
    var steps = [].slice.call(st.querySelectorAll(".step"));
    var count = st.querySelector(".count");
    var i = 0;
    function go(n) {
      i = Math.max(0, Math.min(steps.length - 1, n));
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      if (count) count.textContent = (i + 1) + " / " + steps.length;
    }
    st.querySelectorAll("[data-step]").forEach(function (b) {
      b.addEventListener("click", function () { go(i + Number(b.dataset.step)); });
    });
    go(0);
  });
})();
