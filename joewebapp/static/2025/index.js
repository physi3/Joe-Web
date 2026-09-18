window.onscroll = function() { scrollFunction() };
var logoSection = document.getElementById("logo-section");
var logo = document.getElementById("logo");
var scrolledPast = false;

function scrollFunction() {
    var top = logoSection.getBoundingClientRect().top;
    if (top <= 0 || (scrolledPast && top < 100)) {
        scrolledPast = true;
        logo.style.setProperty("--logo-size", "6em");
        logo.style.padding = "1em";

    } else {
        scrolledPast = false;
        logo.style.setProperty("--logo-size", "20em");
        logo.style.padding = "4em";
    }
}