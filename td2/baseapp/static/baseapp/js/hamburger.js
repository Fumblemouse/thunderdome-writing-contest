document.getElementById('hamburger-nav').classList.add("js")
document.getElementById('hamburger-button').classList.add("js")

var toggle = document.querySelector('#hamburger-button');
var menu = document.querySelector('#hamburger-nav');

toggle.addEventListener('click', function(){
  if (menu.classList.contains('is-active')) {
    this.setAttribute('aria-expanded', 'false');
    menu.classList.remove('is-active');
    menu.classList.add('is-not-active');
  } else {
    menu.classList.add('is-active');
    menu.classList.remove('is-not-active');
    this.setAttribute('aria-expanded', 'true');
  }
});