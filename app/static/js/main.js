/* Fly Happy International Travels — core front-end behaviour */
document.addEventListener("DOMContentLoaded", function () {
  // ---------------- Loading screen (once per browser session) ----------------
  var loader = document.getElementById("loading-screen");
  if (loader) {
    if (sessionStorage.getItem("flyhappy_loaded")) {
      loader.classList.add("hide");
      loader.style.display = "none";
    } else {
      window.addEventListener("load", function () {
        setTimeout(function () {
          loader.classList.add("hide");
          sessionStorage.setItem("flyhappy_loaded", "1");
          setTimeout(function () { loader.style.display = "none"; }, 700);
        }, 3000);
      });
    }
  }

  // ---------------- AOS ----------------
  if (window.AOS) {
    AOS.init({ duration: 800, once: true, offset: 80 });
  }

  // ---------------- Navbar scroll shadow ----------------
  var navbar = document.getElementById("siteNavbar");
  function onScroll() {
    if (!navbar) return;
    if (window.scrollY > 30) navbar.classList.add("scrolled");
    else navbar.classList.remove("scrolled");

    var backToTop = document.getElementById("back-to-top");
    if (backToTop) {
      if (window.scrollY > 400) backToTop.classList.add("show");
      else backToTop.classList.remove("show");
    }
  }
  window.addEventListener("scroll", onScroll);
  onScroll();

  var backToTop = document.getElementById("back-to-top");
  if (backToTop) {
    backToTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // ---------------- Animated statistics counters ----------------
  var counters = document.querySelectorAll(".stat-number[data-count]");
  if (counters.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { observer.observe(c); });
  }

  function animateCounter(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    var duration = 1800;
    var startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      var value = Math.floor(progress * target);
      el.textContent = value.toLocaleString() + suffix;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString() + suffix;
    }
    requestAnimationFrame(step);
  }

  // ---------------- Booking form: trip type toggle ----------------
  var tripTypeInputs = document.querySelectorAll('input[name="trip_type"]');
  var returnDateWrap = document.getElementById("return-date-wrap");
  function toggleReturnDate() {
    var selected = document.querySelector('input[name="trip_type"]:checked');
    if (!selected || !returnDateWrap) return;
    if (selected.value === "round_trip") {
      returnDateWrap.classList.remove("d-none");
      returnDateWrap.querySelector("input").setAttribute("required", "required");
    } else {
      returnDateWrap.classList.add("d-none");
      returnDateWrap.querySelector("input").removeAttribute("required");
    }
  }
  if (tripTypeInputs.length) {
    tripTypeInputs.forEach(function (input) { input.addEventListener("change", toggleReturnDate); });
    toggleReturnDate();
  }

  // ---------------- Booking form: live price estimate ----------------
  var priceForm = document.getElementById("booking-form");
  if (priceForm) {
    var basePrice = parseFloat(priceForm.getAttribute("data-base-price") || "0");
    var estimateEl = document.getElementById("price-estimate");
    function recalc() {
      var adults = parseInt(priceForm.querySelector('[name="adults"]').value || "0", 10);
      var children = parseInt(priceForm.querySelector('[name="children"]').value || "0", 10);
      var infants = parseInt(priceForm.querySelector('[name="infants"]').value || "0", 10);
      var seatClass = priceForm.querySelector('[name="seat_class"]').value;
      var tripType = document.querySelector('input[name="trip_type"]:checked');
      var multiplier = seatClass === "Business" ? 1.6 : seatClass === "First" ? 2.2 : 1.0;
      var tripMultiplier = (tripType && tripType.value === "round_trip") ? 1.85 : 1.0;
      var total = basePrice * multiplier * tripMultiplier * (adults + children + infants * 0.25);
      if (estimateEl) estimateEl.textContent = "PKR " + Math.round(total).toLocaleString();
    }
    ["adults", "children", "infants", "seat_class"].forEach(function (name) {
      var field = priceForm.querySelector('[name="' + name + '"]');
      if (field) field.addEventListener("input", recalc);
    });
    tripTypeInputs.forEach(function (input) { input.addEventListener("change", recalc); });
    recalc();
  }

  // ---------------- Generic search/filter form auto-submit ----------------
  document.querySelectorAll(".auto-filter").forEach(function (el) {
    el.addEventListener("change", function () { el.closest("form").submit(); });
  });

  // ---------------- Print buttons ----------------
  document.querySelectorAll(".btn-print").forEach(function (btn) {
    btn.addEventListener("click", function () { window.print(); });
  });
});
