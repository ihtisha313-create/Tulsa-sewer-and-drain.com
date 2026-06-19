/* Tulsa Sewer & Drain — Main JS */
(function(){
  'use strict';
  document.addEventListener('DOMContentLoaded',function(){

    /* ===== Mobile Menu ===== */
    var toggle = document.querySelector('.mobile-toggle');
    var nav    = document.querySelector('.main-nav');

    function openMenu(){
      nav.classList.add('open');
      toggle.classList.add('is-open');
      toggle.setAttribute('aria-expanded','true');
      toggle.textContent = '✕';
      document.body.style.overflow = 'hidden';
    }
    function closeMenu(){
      nav.classList.remove('open');
      toggle.classList.remove('is-open');
      toggle.setAttribute('aria-expanded','false');
      toggle.textContent = '☰';
      document.body.style.overflow = '';
    }

    if(toggle && nav){
      toggle.addEventListener('click',function(e){
        e.stopPropagation();
        nav.classList.contains('open') ? closeMenu() : openMenu();
      });

      // Close when clicking the dark overlay (outside the ul)
      nav.addEventListener('click',function(e){
        if(e.target === nav) closeMenu();
      });

      // Close when a nav link is tapped
      var navLinks = nav.querySelectorAll('a');
      navLinks.forEach(function(a){
        a.addEventListener('click', closeMenu);
      });

      // Close on Escape key
      document.addEventListener('keydown',function(e){
        if(e.key === 'Escape' && nav.classList.contains('open')) closeMenu();
      });
    }

    /* ===== FAQ Accordion ===== */
    var faqs = document.querySelectorAll('.faq-question');
    faqs.forEach(function(q){
      q.addEventListener('click',function(){
        var item = q.parentElement;
        var isOpen = item.classList.contains('open');
        // Close all open items first
        document.querySelectorAll('.faq-item.open').forEach(function(i){
          i.classList.remove('open');
        });
        // Open clicked one if it was closed
        if(!isOpen) item.classList.add('open');
      });
    });

    /* ===== Active nav link ===== */
    var path = window.location.pathname.replace(/index\.html$/,'').replace(/\/$/,'');
    var links = document.querySelectorAll('.main-nav a');
    links.forEach(function(a){
      var href = a.getAttribute('href').replace(/index\.html$/,'').replace(/\/$/,'');
      if(href === path || (path === '' && href === '')) a.classList.add('active');
    });

    /* ===== Quote Form Submission GA4 Tracking ===== */
    document.querySelectorAll('form.quote-card').forEach(function(form){
      form.addEventListener('submit', function(){
        if(typeof gtag === 'function'){
          var service = (form.querySelector('[name="service"]') || {}).value || 'unknown';
          gtag('event', 'quote_form_submit', {
            event_category: 'lead',
            event_label: service,
            page_location: window.location.href
          });
        }
      });
    });

    /* ===== Click-to-Call GA4 Tracking ===== */
    document.querySelectorAll('a[href^="tel:"]').forEach(function(a){
      a.addEventListener('click', function(){
        if(typeof gtag === 'function'){
          gtag('event', 'click_to_call', {
            event_category: 'engagement',
            event_label: a.getAttribute('href').replace('tel:',''),
            page_location: window.location.href
          });
        }
      });
    });

    /* ===== Smooth scroll for anchor links with sticky header offset ===== */
    document.querySelectorAll('a[href^="#"]').forEach(function(a){
      a.addEventListener('click',function(e){
        var target = document.querySelector(a.getAttribute('href'));
        if(target){
          e.preventDefault();
          var offset = 80;
          var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
          window.scrollTo({ top: top, behavior: 'smooth' });
        }
      });
    });

  });

  /* ===== WebMCP — expose business tools to AI agents ===== */
  if (navigator.modelContext && navigator.modelContext.provideContext) {
    navigator.modelContext.provideContext({
      tools: [
        {
          name: "get_contact_info",
          description: "Returns the business phone number, hours of operation, and quote form URL for Tulsa Sewer & Drain.",
          inputSchema: { type: "object", properties: {} },
          execute: function() {
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
          execute: function() {
            return {
              services: [
                { name: "Drain Cleaning", url: window.location.origin + "/drain-cleaning/", price_range: "$100–$300" },
                { name: "Sewer Line Repair", url: window.location.origin + "/sewer-line-repair/" },
                { name: "Hydro Jetting", url: window.location.origin + "/hydro-jetting/", price_range: "$350–$600" },
                { name: "Trenchless Sewer Repair", url: window.location.origin + "/trenchless-sewer-repair-tulsa/", price_range: "$1,500–$5,000+" },
                { name: "Sewer Camera Inspection", url: window.location.origin + "/sewer-camera-inspection/", price_range: "$150–$300" },
                { name: "Emergency Plumber 24/7", url: window.location.origin + "/emergency-plumber-tulsa/", price_range: "$150–$250 + repairs" }
              ]
            };
          }
        },
        {
          name: "check_service_area",
          description: "Check whether a given city is in the Tulsa Sewer & Drain service area and return the relevant city page URL.",
          inputSchema: {
            type: "object",
            required: ["city"],
            properties: {
              city: { type: "string", description: "City name to check, e.g. 'Broken Arrow' or 'Sand Springs'" }
            }
          },
          execute: function(args) {
            var areas = {
              "tulsa":         "/plumbers-tulsa/",
              "broken arrow":  "/broken-arrow-plumber/",
              "owasso":        "/owasso-plumber/",
              "bixby":         "/bixby-plumber/",
              "jenks":         "/jenks-plumber/",
              "catoosa":       "/catoosa-plumber/",
              "sand springs":  "/sand-springs-plumber/",
              "glenpool":      "/glenpool-plumber/",
              "sapulpa":       "/sapulpa-plumber/",
              "kellyville":    "/kellyville-plumber/"
            };
            var key = (args.city || '').toLowerCase().trim();
            var path = areas[key];
            if (path) {
              return { served: true, city: args.city, url: window.location.origin + path };
            }
            var tulsa_metro = ["tulsa", "broken arrow", "owasso", "bixby", "jenks", "catoosa",
                               "sand springs", "glenpool", "sapulpa", "kellyville"];
            return {
              served: "unknown",
              message: "Call (918) 992-4725 to confirm service to " + args.city + ". We cover the full Tulsa metro.",
              known_areas: tulsa_metro,
              service_areas_url: window.location.origin + "/service-areas/"
            };
          }
        },
        {
          name: "get_pricing",
          description: "Returns typical pricing ranges for common plumbing services offered by Tulsa Sewer & Drain.",
          inputSchema: { type: "object", properties: {} },
          execute: function() {
            return {
              note: "All jobs quoted flat-rate upfront before work begins. Prices vary by access, line length, and conditions.",
              pricing: [
                { service: "Drain Cleaning",            typical: "$100–$300" },
                { service: "Sewer Camera Inspection",   typical: "$150–$300" },
                { service: "Hydro Jetting",             typical: "$350–$600" },
                { service: "Trenchless Sewer Repair",   typical: "$1,500–$5,000+" },
                { service: "Emergency Service Call",    typical: "$150–$250 + repairs" }
              ]
            };
          }
        }
      ]
    });
  }

})();
