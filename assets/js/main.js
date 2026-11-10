/* Pathfinders College & Career Advisors | site behaviour (no dependencies) */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");

  /* Header shadow on scroll + mobile sticky CTA */
  var header = document.querySelector(".site-header");
  var mobileCta = document.querySelector(".mobile-cta");
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("is-scrolled", y > 8);
    if (mobileCta) mobileCta.classList.toggle("is-visible", y > 640);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Mobile navigation */
  var nav = document.getElementById("main-nav");
  var toggle = document.querySelector(".nav-toggle");
  var closeBtn = document.querySelector(".nav-close");
  var backdrop = document.querySelector(".nav-backdrop");
  function setNav(open) {
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    if (backdrop) backdrop.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
    doc.classList.toggle("nav-open", open);
    if (open) { var first = nav.querySelector("a"); if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 320); }
    else { toggle.focus({ preventScroll: true }); }
  }
  if (toggle) toggle.addEventListener("click", function () { setNav(!nav.classList.contains("is-open")); });
  if (closeBtn) closeBtn.addEventListener("click", function () { setNav(false); });
  if (backdrop) backdrop.addEventListener("click", function () { setNav(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav && nav.classList.contains("is-open")) setNav(false);
  });

  /* Workshops: hide sessions that have already started, flag the next one */
  var now = Date.now();
  var events = Array.prototype.slice.call(document.querySelectorAll("[data-event-start]"));
  var upcoming = events.filter(function (el) {
    var t = Date.parse(el.getAttribute("data-event-start"));
    var past = !isNaN(t) && t < now;
    if (past) el.hidden = true;
    return !past;
  });
  document.querySelectorAll(".event-list").forEach(function (list) {
    var visible = list.querySelectorAll(".event:not([hidden])");
    if (visible.length) {
      visible[0].classList.add("is-next");
      var lbl = visible[0].querySelector(".next-label");
      if (lbl) lbl.hidden = false;
    }
    var empty = list.parentNode.querySelector(".events-empty");
    if (empty) empty.classList.toggle("is-visible", visible.length === 0);
  });
  var announce = document.querySelector("[data-announce]");
  if (announce) {
    var nextAnnounce = Array.prototype.slice.call(document.querySelectorAll("[data-announce-item]")).filter(function (el) {
      var t = Date.parse(el.getAttribute("data-announce-item"));
      return isNaN(t) || t >= now;
    })[0];
    if (nextAnnounce) { announce.innerHTML = nextAnnounce.innerHTML; }
    else { announce.innerHTML = 'Free virtual workshops for families. <a href="' + announce.getAttribute("data-fallback") + '">See upcoming dates</a>'; }
  }

  /* Knowledge base: topic filters + keyword search (combined) */
  var chips = document.querySelectorAll(".chip[data-filter]");
  var posts = document.querySelectorAll("[data-cats]");
  var kbForm = document.querySelector("[data-kb-search]");
  var kbInput = kbForm ? kbForm.querySelector("input") : null;
  var kbClear = kbForm ? kbForm.querySelector(".kb-clear") : null;
  var kbEmpty = document.querySelector(".kb-empty");
  var activeCat = "all";
  // Words parents use -> words the articles use
  var SYN = {
    freshman: ["freshman", "freshmen", "9th", "ninth"], sophomore: ["sophomore", "10th", "tenth"],
    junior: ["junior", "11th", "eleventh"], senior: ["senior", "12th", "twelfth"],
    test: ["sat", "act", "psat", "test"], sat: ["sat", "psat"], act: ["act"],
    aid: ["aid", "fafsa", "css profile", "scholarship"], money: ["cost", "aid", "scholarship", "loan", "529", "price"],
    loan: ["loan", "borrow", "debt"], debt: ["debt", "loan"], cost: ["cost", "price", "tuition"],
    career: ["career"], major: ["major"], ai: ["ai"], trade: ["trade school", "vocational", "apprentice"]
  };
  function terms(q) {
    return q.toLowerCase().replace(/[^a-z0-9\s-]/g, " ").split(/\s+/).filter(function (w) { return w.length > 1; })
      .map(function (w) {
        var forms = [w, w.replace(/ies$/, "y"), w.replace(/s$/, ""), w.replace(/es$/, "")];
        for (var i = 0; i < forms.length; i++) { if (SYN[forms[i]]) return SYN[forms[i]]; }
        return [w.length > 3 ? w.replace(/s$/, "") : w];
      });
  }
  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  function matches(hay, groups) {
    return groups.every(function (alts) {
      return alts.some(function (a) {
        // short terms (AI, ACT, SAT, 529) must be whole words; longer ones match word starts
        var re = new RegExp("(^|[^a-z0-9])" + esc(a) + (a.length <= 3 ? "($|[^a-z0-9])" : ""));
        return re.test(hay);
      });
    });
  }
  function applyKb() {
    var groups = kbInput && kbInput.value.trim() ? terms(kbInput.value) : [];
    var n = 0;
    posts.forEach(function (p) {
      var cats = p.getAttribute("data-cats").split("|");
      var inCat = activeCat === "all" || cats.indexOf(activeCat) !== -1;
      var hay = (p.getAttribute("data-search") || p.textContent).toLowerCase();
      var show = inCat && (!groups.length || matches(hay, groups));
      p.hidden = !show;
      if (show) n++;
    });
    var count = document.querySelector("[data-post-count]");
    if (count) count.textContent = n + (n === 1 ? " article" : " articles");
    if (kbEmpty) kbEmpty.hidden = n !== 0;
    if (kbClear) kbClear.hidden = !(kbInput && kbInput.value);
  }
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      activeCat = chip.getAttribute("data-filter");
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      applyKb();
    });
  });
  if (kbForm) {
    kbForm.addEventListener("submit", function (e) { e.preventDefault(); applyKb(); });
    kbInput.addEventListener("input", applyKb);
    kbClear.addEventListener("click", function () { kbInput.value = ""; applyKb(); kbInput.focus(); });
    var q0 = new URLSearchParams(location.search).get("q");
    if (q0) { kbInput.value = q0; applyKb(); }
  }

  /* Long reviews: read more */
  document.querySelectorAll(".review .clamp").forEach(function (p) {
    if (p.scrollHeight - p.clientHeight < 8) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "read-more";
    btn.textContent = "Read full review";
    btn.setAttribute("aria-expanded", "false");
    btn.addEventListener("click", function () {
      var card = p.closest(".review");
      var open = card.classList.toggle("is-expanded");
      btn.textContent = open ? "Show less" : "Read full review";
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    p.parentNode.appendChild(btn);
  });

  /* Forms: validate, then hand off. Set data-endpoint on a form to post it to your CRM. */
  document.querySelectorAll("form[data-pf-form]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll("[required]").forEach(function (f) {
        var valid = f.type === "checkbox" ? f.checked : f.value.trim() !== "" && (f.type !== "email" || /.+@.+\..+/.test(f.value));
        f.setAttribute("aria-invalid", valid ? "false" : "true");
        if (!valid && ok) { f.focus(); ok = false; }
      });
      if (!ok) {
        if (status) { status.textContent = "Please complete the highlighted fields."; status.classList.add("is-visible"); }
        return;
      }
      var hp = form.querySelector(".hp input");
      if (hp && hp.value) return;
      var endpoint = form.getAttribute("data-endpoint");
      var done = function (msg) {
        if (status) { status.textContent = msg; status.classList.add("is-visible"); }
        form.querySelectorAll("input:not([type=checkbox]), textarea, select").forEach(function (f) { if (!f.closest(".hp")) f.value = ""; });
      };
      if (endpoint) {
        fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
          .then(function (r) { done(r.ok ? form.getAttribute("data-success") : "Something went wrong. Please try again or book a call."); })
          .catch(function () { done("Something went wrong. Please try again or book a call."); });
      } else {
        done(form.getAttribute("data-success") + " (Review build: this form is not connected yet.)");
      }
    });
  });

  /* Reveal on scroll */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* Footer year */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
