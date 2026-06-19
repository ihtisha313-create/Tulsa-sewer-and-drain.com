/* Tulsa Sewer & Drain — Main JS */
(function(){
  'use strict';
  document.addEventListener('DOMContentLoaded', function(){

    /* ===================================================
       MOBILE MENU — Slide-in drawer with overlay
    =================================================== */
    var toggle = document.querySelector('.mobile-toggle');
    var nav    = document.querySelector('.main-nav');

    /* Upgrade the toggle button from ☰ text to animated spans */
    if (toggle) {
      toggle.innerHTML = '<span></span><span></span><span></span>';
      toggle.setAttribute('aria-label', 'Open navigation menu');
      toggle.setAttribute('aria-expanded', 'false');
    }

    /* Inject overlay element */
    var overlay = document.createElement('div');
    overlay.className = 'nav-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    document.body.appendChild(overlay);

    /* Inject a sticky header inside the drawer */
    if (nav) {
      var navHeader = document.createElement('div');
      navHeader.className = 'main-nav-header';
      navHeader.setAttribute('aria-hidden', 'true');
      navHeader.innerHTML =
        '<span>Menu</span>' +
        '<button class="main-nav-close" aria-label="Close navigation menu" tabindex="-1">&#x2715;</button>';
      nav.insertBefore(navHeader, nav.firstChild);

      var closeBtn = navHeader.querySelector('.main-nav-close');
      if (closeBtn) {
        closeBtn.addEventListener('click', closeMenu);
      }
    }

    /* Wrap dropdowns for mobile accordion */
    document.querySelectorAll('.nav-dropdown').forEach(function(li){
      var topLink = li.querySelector(':scope > a');
      if (topLink) {
        /* On mobile the top link toggles the sub-menu instead of navigating */
        topLink.addEventListener('click', function(e){
          if (window.innerWidth <= 768) {
            e.preventDefault();
            var isOpen = li.classList.contains('mob-open');
            /* Close all others */
            document.querySelectorAll('.nav-dropdown.mob-open').forEach(function(el){
              el.classList.remove('mob-open');
            });
            if (!isOpen) li.classList.add('mob-open');
          }
        });
      }
    });

    function openMenu(){
      if (!nav) return;
      nav.classList.add('open');
      overlay.classList.add('active');
      toggle && toggle.classList.add('is-open');
      toggle && toggle.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    }

    function closeMenu(){
      if (!nav) return;
      nav.classList.remove('open');
      overlay.classList.remove('active');
      toggle && toggle.classList.remove('is-open');
      toggle && toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      /* Close all mobile accordions */
      document.querySelectorAll('.nav-dropdown.mob-open').forEach(function(el){
        el.classList.remove('mob-open');
      });
    }

    if (toggle && nav) {
      toggle.addEventListener('click', function(e){
        e.stopPropagation();
        nav.classList.contains('open') ? closeMenu() : openMenu();
      });
    }

    /* Clicking the overlay closes the drawer */
    overlay.addEventListener('click', closeMenu);

    /* Close when a leaf nav link is tapped (but not dropdown parent on mobile) */
    if (nav) {
      nav.querySelectorAll('a').forEach(function(a){
        a.addEventListener('click', function(){
          /* Only close if it's not a parent dropdown toggle on mobile */
          var parentLi = a.closest('.nav-dropdown');
          if (parentLi && a === parentLi.querySelector(':scope > a') && window.innerWidth <= 768) {
            return; /* handled by accordion logic above */
          }
          closeMenu();
        });
      });
    }

    /* ESC closes drawer */
    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape') closeMenu();
    });

    /* Re-enable scrolling on resize */
    window.addEventListener('resize', function(){
      if (window.innerWidth > 768) {
        document.body.style.overflow = '';
        overlay.classList.remove('active');
        nav && nav.classList.remove('open');
      }
    });


    /* ===================================================
       FAQ ACCORDION
    =================================================== */
    document.querySelectorAll('.faq-question').forEach(function(q){
      /* Upgrade inner content to use the new toggle icon markup */
      var text = q.textContent.replace(/[+×]/g, '').trim();
      q.innerHTML = '<span>' + text + '</span><span class="faq-toggle-icon" aria-hidden="true">+</span>';
      q.setAttribute('aria-expanded', 'false');

      q.addEventListener('click', function(){
        var item   = q.closest('.faq-item');
        var isOpen = item.classList.contains('open');

        /* Close any open items first */
        document.querySelectorAll('.faq-item.open').forEach(function(i){
          i.classList.remove('open');
          var btn = i.querySelector('.faq-question');
          if (btn) btn.setAttribute('aria-expanded', 'false');
        });

        if (!isOpen) {
          item.classList.add('open');
          q.setAttribute('aria-expanded', 'true');
        }
      });
    });


    /* ===================================================
       ACTIVE NAV LINK
    =================================================== */
    var path = window.location.pathname.replace(/index\.html$/, '').replace(/\/$/, '');
    document.querySelectorAll('.main-nav a').forEach(function(a){
      var href = (a.getAttribute('href') || '')
                   .replace(/index\.html$/, '').replace(/\/$/, '');
      if (href === path || (path === '' && href === '')) {
        a.classList.add('active');
      }
    });


    /* ===================================================
       QUOTE FORM — GA4 Tracking
    =================================================== */
    document.querySelectorAll('form.quote-card').forEach(function(form){
      form.addEventListener('submit', function(){
        if (typeof gtag === 'function') {
          var svc = (form.querySelector('[name="service"]') || {}).value || 'unknown';
          gtag('event', 'quote_form_submit', {
            event_category: 'lead',
            event_label: svc,
            page_location: window.location.href
          });
        }
      });
    });


    /* ===================================================
       CLICK-TO-CALL — GA4 Tracking
    =================================================== */
    document.querySelectorAll('a[href^="tel:"]').forEach(function(a){
      a.addEventListener('click', function(){
        if (typeof gtag === 'function') {
          gtag('event', 'click_to_call', {
            event_category: 'engagement',
            event_label: a.getAttribute('href').replace('tel:', ''),
            page_location: window.location.href
          });
        }
      });
    });


    /* ===================================================
       SMOOTH SCROLL — anchor links with sticky header offset
    =================================================== */
    document.querySelectorAll('a[href^="#"]').forEach(function(a){
      a.addEventListener('click', function(e){
        var id = a.getAttribute('href');
        if (id === '#') return;
        var target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          var headerH = parseInt(
            getComputedStyle(document.documentElement).getPropertyValue('--header-height')
          ) || 70;
          var top = target.getBoundingClientRect().top + window.pageYOffset - headerH - 16;
          window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
        }
      });
    });


    /* ===================================================
       SCROLL-REVEAL — subtle fade-up for cards
    =================================================== */
    if ('IntersectionObserver' in window) {
      var revealEls = document.querySelectorAll(
        '.service-card, .review-card, .reason-card, .trust-item, .stat-num'
      );
      var revealStyle = document.createElement('style');
      revealStyle.textContent =
        '.reveal-pending{opacity:0;transform:translateY(18px);transition:opacity .45s ease,transform .45s ease;}' +
        '.reveal-done{opacity:1;transform:none;}';
      document.head.appendChild(revealStyle);

      revealEls.forEach(function(el){
        el.classList.add('reveal-pending');
      });

      var obs = new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
          if (entry.isIntersecting) {
            entry.target.classList.remove('reveal-pending');
            entry.target.classList.add('reveal-done');
            obs.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

      revealEls.forEach(function(el){ obs.observe(el); });
    }

  }); /* end DOMContentLoaded */


  /* ===================================================
     WebMCP — expose business tools to AI agents
  =================================================== */
  if (navigator.modelContext && navigator.modelContext.provideContext) {
    navigator.modelContext.provideContext({
      tools: [
        {
          name: "get_contact_info",
          description: "Returns the business phone number, hours of operation, and quote form URL for Tulsa Sewer & Drain.",
          inputSchema: { type: "object", properties: {} },
          execute: function(){
            return {
              business: "Tulsa Sewer & Drain",
              phone: "(918) 992-4725",
              tel: "+19189924725",
              hours: "24/7 — 365 days a year",
              emergency_response: "60-minute arrival goal",
              quote_form: window.location.origin + "/contact/",
              license: "Licensed & Insured Oklahoma Plumbers"
            };
          }
        },
        {
          name: "list_services",
          description: "Returns all sewer and drain plumbing services offered by Tulsa Sewer & Drain with their page URLs.",
          inputSchema: { type: "object", properties: {} },
          execute: function(){
            return {
              services: [
                { name: "Drain Cleaning",          url: window.location.origin + "/drain-cleaning/",                  price_range: "$100–$300"    },
                { name: "Sewer Line Repair",        url: window.location.origin + "/sewer-line-repair/"                                           },
                { name: "Hydro Jetting",            url: window.location.origin + "/hydro-jetting/",                  price_range: "$350–$600"    },
                { name: "Trenchless Sewer Repair",  url: window.location.origin + "/trenchless-sewer-repair-tulsa/",  price_range: "$1,500–$5,000+" },
                { name: "Sewer Camera Inspection",  url: window.location.origin + "/sewer-camera-inspection/",        price_range: "$150–$300"    },
                { name: "Emergency Plumber 24/7",   url: window.location.origin + "/emergency-plumber-tulsa/",        price_range: "$150–$250 + repairs" }
              ]
            };
          }
        },
        {
          name: "check_service_area",
          description: "Check whether a given city is in the Tulsa Sewer & Drain service area.",
          inputSchema: {
            type: "object",
            required: ["city"],
            properties: { city: { type: "string", description: "City name to check." } }
          },
          execute: function(args){
            var areas = {
              "tulsa":        "/plumbers-tulsa/",
              "broken arrow": "/broken-arrow-plumber/",
              "owasso":       "/owasso-plumber/",
              "bixby":        "/bixby-plumber/",
              "jenks":        "/jenks-plumber/",
              "catoosa":      "/catoosa-plumber/",
              "sand springs": "/sand-springs-plumber/",
              "glenpool":     "/glenpool-plumber/",
              "sapulpa":      "/sapulpa-plumber/",
              "kellyville":   "/kellyville-plumber/"
            };
            var key  = ((args && args.city) || '').toLowerCase().trim();
            var path = areas[key];
            if (path) return { served: true, city: args.city, url: window.location.origin + path };
            return {
              served: "unknown",
              message: "Call (918) 992-4725 to confirm service to " + args.city + ". We cover the full Tulsa metro.",
              service_areas_url: window.location.origin + "/service-areas/"
            };
          }
        },
        {
          name: "get_pricing",
          description: "Returns typical pricing ranges for common plumbing services offered by Tulsa Sewer & Drain.",
          inputSchema: { type: "object", properties: {} },
          execute: function(){
            return {
              note: "All jobs quoted flat-rate upfront before work begins. Prices vary by access, line length, and conditions.",
              pricing: [
                { service: "Drain Cleaning",           typical: "$100–$300"       },
                { service: "Sewer Camera Inspection",  typical: "$150–$300"       },
                { service: "Hydro Jetting",            typical: "$350–$600"       },
                { service: "Trenchless Sewer Repair",  typical: "$1,500–$5,000+"  },
                { service: "Emergency Service Call",   typical: "$150–$250 + repairs" }
              ]
            };
          }
        }
      ]
    });
  }

})();
