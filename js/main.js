/* ============================================================
   MAIN.JS — Filip Čaniga Website
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Sticky header ──────────────────────────────────────── */
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', function () {
      header.classList.toggle('scrolled', window.scrollY > 30);
    });
  }

  /* ── Hamburger / mobile nav ─────────────────────────────── */
  const hamburger = document.querySelector('.hamburger');
  const mobileNav = document.querySelector('.mobile-nav');
  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', function () {
      hamburger.classList.toggle('open');
      mobileNav.classList.toggle('open');
      document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
    });
  }

  /* ── Desktop dropdown on click (touch friendly) ─────────── */
  document.querySelectorAll('.nav-item.has-sub').forEach(function (item) {
    const link = item.querySelector('.nav-link');
    if (!link) return;
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.nav-item.has-sub').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item.has-sub')) {
      document.querySelectorAll('.nav-item.has-sub').forEach(i => i.classList.remove('open'));
    }
  });

  /* ── Generic carousel factory ───────────────────────────── */
  function initCarousel(wrapSelector, trackSelector, itemSelector, visibleCount) {
    const wrap = document.querySelector(wrapSelector);
    if (!wrap) return;
    const track = wrap.querySelector(trackSelector);
    if (!track) return;
    const items = track.querySelectorAll(itemSelector);
    if (!items.length) return;

    let current = 0;
    const total = items.length;
    const max = Math.max(0, total - visibleCount);

    function slide() {
      const itemWidth = items[0].offsetWidth + parseInt(getComputedStyle(track).gap || 0);
      track.style.transform = `translateX(-${current * itemWidth}px)`;
    }

    const prevBtn = wrap.querySelector('.carousel-btn--prev');
    const nextBtn = wrap.querySelector('.carousel-btn--next');

    if (prevBtn) prevBtn.addEventListener('click', function () {
      current = current > 0 ? current - 1 : max;
      slide();
    });

    if (nextBtn) nextBtn.addEventListener('click', function () {
      current = current < max ? current + 1 : 0;
      slide();
    });

    window.addEventListener('resize', slide);
  }

  initCarousel('.celebrity-carousel', '.carousel-track', '.celebrity-card', 6);
  initCarousel('.testimonial-carousel', '.testimonials-track', '.testimonial-card', 3);

  /* ── Accordion ───────────────────────────────────────────── */
  document.querySelectorAll('.accordion-trigger').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const body = this.nextElementSibling;
      const isOpen = this.classList.contains('open');

      // Close all in same parent
      const parent = this.closest('.accordion-wrap') || document;
      parent.querySelectorAll('.accordion-trigger').forEach(b => {
        b.classList.remove('open');
        const nb = b.nextElementSibling;
        if (nb) nb.classList.remove('open');
      });

      if (!isOpen) {
        this.classList.add('open');
        if (body) body.classList.add('open');
      }
    });
  });

  /* ── FAQ accordion ───────────────────────────────────────── */
  document.querySelectorAll('.faq-question').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const answer = this.nextElementSibling;
      const isOpen = this.classList.contains('open');

      document.querySelectorAll('.faq-question').forEach(b => {
        b.classList.remove('open');
        const nb = b.nextElementSibling;
        if (nb) nb.classList.remove('open');
      });

      if (!isOpen) {
        this.classList.add('open');
        if (answer) answer.classList.add('open');
      }
    });
  });

  /* ── Cookie banner ───────────────────────────────────────── */
  const cookieBanner = document.querySelector('.cookie-banner');
  if (cookieBanner) {
    if (!localStorage.getItem('fc_cookies_accepted')) {
      setTimeout(function () {
        cookieBanner.classList.remove('hidden');
      }, 800);
    } else {
      cookieBanner.remove();
    }

    document.querySelectorAll('.cookie-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        localStorage.setItem('fc_cookies_accepted', '1');
        cookieBanner.classList.add('hidden');
        setTimeout(() => cookieBanner.remove(), 500);
      });
    });
  }

  /* ── Scroll fade-in animations ──────────────────────────── */
  const fadeEls = document.querySelectorAll('.fade-up');
  if (fadeEls.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    fadeEls.forEach(function (el) { observer.observe(el); });
  } else {
    fadeEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ── Contact form — Formspree AJAX submission ────────────── */
  const contactForm = document.querySelector('.contact-form form');
  if (contactForm) {
    contactForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = contactForm.querySelector('[type="submit"]');
      const originalText = btn ? btn.textContent : '';

      // Highlight empty required fields
      let valid = true;
      contactForm.querySelectorAll('[required]').forEach(function (input) {
        const empty = input.type === 'checkbox' ? !input.checked : !input.value.trim();
        input.style.borderColor = empty ? '#e74c3c' : '';
        if (empty) valid = false;
      });
      if (!valid) return;

      if (btn) { btn.textContent = 'Odosielam…'; btn.disabled = true; }

      try {
        const res = await fetch(contactForm.action, {
          method: 'POST',
          body: new FormData(contactForm),
          headers: { Accept: 'application/json' }
        });

        if (res.ok) {
          if (btn) {
            btn.textContent = '✓ Správa odoslaná';
            btn.style.background = '#2ecc71';
            btn.style.borderColor = '#2ecc71';
          }
          contactForm.reset();
        } else {
          throw new Error('server error');
        }
      } catch (_) {
        if (btn) { btn.textContent = originalText; btn.disabled = false; }
        alert('Nastala chyba. Skúste neskôr alebo nás kontaktujte telefonicky.');
      }
    });
  }

});
