/* Tulsa Sewer & Drain — Main JS */
(function(){
  'use strict';
  // Mobile menu toggle
  document.addEventListener('DOMContentLoaded',function(){
    var toggle = document.querySelector('.mobile-toggle');
    var nav = document.querySelector('.main-nav');
    if(toggle && nav){
      toggle.addEventListener('click',function(){
        nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', nav.classList.contains('open'));
      });
    }
    // FAQ accordion
    var faqs = document.querySelectorAll('.faq-question');
    faqs.forEach(function(q){
      q.addEventListener('click',function(){
        var item = q.parentElement;
        item.classList.toggle('open');
      });
    });
    // Highlight current nav link
    var path = window.location.pathname.replace(/index\.html$/,'').replace(/\/$/,'');
    var links = document.querySelectorAll('.main-nav a');
    links.forEach(function(a){
      var href = a.getAttribute('href').replace(/index\.html$/,'').replace(/\/$/,'');
      if(href === path || (path === '' && href === '')) a.classList.add('active');
    });
  });
})();
