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
})();
