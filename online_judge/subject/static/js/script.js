
$(document).ready(function(){
  $('.carousel').carousel();
  //$('.carousel').duration(200);
  setInterval(function(){
    $('.carousel').carousel('next');
  }, 2000);
	$(".button-collapse").sideNav();
});


document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.dropdown-trigger');
    var instances = M.Dropdown.init(elems, options);
  });