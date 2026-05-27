/* md-to-html theme behavior — inline this whole file into <script>. No external deps. */
(function () {
  // 1) theme toggle (respects system preference + persists)
  var root = document.documentElement;
  var btn = document.getElementById('themeBtn');
  var saved = null; try { saved = localStorage.getItem('theme'); } catch (e) {}
  var sysDark = window.matchMedia && window.matchMedia('(prefers-color-scheme:dark)').matches;
  apply(saved || (sysDark ? 'dark' : 'light'));
  function apply(t) { root.setAttribute('data-theme', t); if (btn) btn.textContent = (t === 'dark' ? '☀️' : '🌙'); }
  if (btn) btn.addEventListener('click', function () {
    var t = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    apply(t); try { localStorage.setItem('theme', t); } catch (e) {}
  });

  // 2) scroll reveal
  var els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    els.forEach(function (e) { e.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function (e) { io.observe(e); });
  }

  // 3) TOC scrollspy
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          links.forEach(function (l) { l.classList.remove('active'); l.removeAttribute('aria-current'); });
          var a = map[en.target.id];
          if (a) { a.classList.add('active'); a.setAttribute('aria-current', 'true'); }
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px', threshold: 0 });
    document.querySelectorAll('main section[id]').forEach(function (s) { spy.observe(s); });
  }
})();
