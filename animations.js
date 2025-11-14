document.addEventListener("DOMContentLoaded", () => {
  const elements = document.querySelectorAll(".content-card, .feature-card");
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-in");
        observer.unobserve(entry.target);
      }
    });
  });

  elements.forEach(el => observer.observe(el));
});
