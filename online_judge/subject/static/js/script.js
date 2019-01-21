
$(document).ready(function(){
  $('.carousel').carousel();
  //$('.carousel').duration(200);
  setInterval(function(){
    $('.carousel').carousel('next');
  }, 2000);
	$(".button-collapse").sideNav();
});
