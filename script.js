

// Smooth scroll for nav links
document.querySelectorAll('nav a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});


// Show 'Back to Top' button
let topBtn = document.getElementById("topBtn");
window.onscroll = function() {
  if (document.body.scrollTop > 270 || document.documentElement.scrollTop > 270) {
    topBtn.style.display = "block";
  } else {
    topBtn.style.display = "none";
  }
};
topBtn.onclick = function() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};
