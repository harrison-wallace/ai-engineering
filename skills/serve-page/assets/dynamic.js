// Dynamic page behaviour for serve-page pages. Paste this whole file into one inline <script>
// at the end of <body>. No fetch, no storage, no external code. Without JS every panel shows.
//
// Markup it drives:
//   Tabs     <nav class="tabs"><a href="#infra">Infra</a>...</nav>  <section class="panel" id="infra">
//   Layers   <input type="checkbox" data-layer="planned" checked>    any element with class="planned"
//   Choices  <input type="radio" name="mode" data-choose="mode" value="prod">  sets body[data-mode]
//   Links    <g data-id="db">  ...  <div data-links="db api">         click a [data-links] element
//            (or an svg [data-id]) to highlight every [data-id] it names; click again to clear
//   Stepper  <div class="stepper"><div class="step">..</div>...<button data-step="-1">..
//            an optional <button data-play> plays the frames (data-delay on .stepper, in ms)
(function () {
  var d = document;
  d.documentElement.classList.add("js");

  // Start the SVG animations (a flow step's packet, begin="indefinite") in what just came into
  // view. CSS animations restart by themselves when an element is shown again.
  function replay(el) {
    el.querySelectorAll("animateMotion").forEach(function (a) { if (a.beginElement) a.beginElement(); });
  }

  replay(d);  // a page with no tabs or steppers still starts its packets; show() and go() restart them

  // Tabs, driven by the URL hash so a tab can be linked.
  var panels = [].slice.call(d.querySelectorAll("section.panel"));
  function show() {
    if (!panels.length) return;
    var id = location.hash.slice(1);
    var open = panels.filter(function (p) {  // a tab that a choice hides by CSS cannot be shown
      var a = d.querySelector('.tabs a[href="#' + p.id + '"]');
      return !a || getComputedStyle(a).display !== "none";
    });
    if (!open.length) open = panels;
    if (!open.some(function (p) { return p.id === id; })) id = open[0].id;
    panels.forEach(function (p) { p.hidden = p.id !== id; if (p.id === id) replay(p); });
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

  // Choices: a radio with data-choose="mode" sets <body data-mode="<value>">, for the page's CSS.
  d.querySelectorAll("input[data-choose]").forEach(function (r) {
    function set() {
      if (!r.checked) return;
      d.body.setAttribute("data-" + r.dataset.choose, r.value);
      show();
    }
    r.addEventListener("change", set);
    set();  // a reload can restore a checked radio
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
    var ids = (src.dataset.links || src.dataset.id || "").split(/\s+/).filter(Boolean);
    if (!ids.length) return;  // nothing linked: leave the page as it is
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
      replay(steps[i]);
      if (count) count.textContent = (i + 1) + " / " + steps.length;
    }
    var play = st.querySelector("[data-play]"), timer = null;
    function stop() {
      clearInterval(timer); timer = null;
      if (play) play.textContent = "Play";
    }
    st.querySelectorAll("[data-step]").forEach(function (b) {
      b.addEventListener("click", function () { stop(); go(i + Number(b.dataset.step)); });
    });
    if (play) play.addEventListener("click", function () {
      if (timer) { stop(); return; }
      if (i === steps.length - 1) go(0);
      play.textContent = "Pause";
      timer = setInterval(function () {
        if (i === steps.length - 1) stop(); else go(i + 1);
      }, Number(st.dataset.delay) || 2500);
    });
    go(0);
  });
})();
