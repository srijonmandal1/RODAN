$(function () {
  var path = window.location.href;
  $(".nav").each(function () {
    if (this.href === path) {
      $("ul li a").removeClass("active");
      $(this).addClass("active");
    }
  });
  if (path.includes("/login")) {
    $("#login").addClass("active");
  }
});
function closeFlash() {
  $(".alert").alert("close");
}
