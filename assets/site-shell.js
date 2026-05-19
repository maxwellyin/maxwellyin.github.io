(() => {
  const page = document.body.dataset.page || "";

  const navItems = [
    { href: "/", label: "Home", page: "home" },
    { href: "/projects", label: "Projects", page: "projects" },
    { href: "/field-notes/", label: "Notes", page: "field-notes" },
    { href: "/resume", label: "Resume", page: "resume" },
    { href: "/contact", label: "Contact", page: "contact" },
  ];

  const renderLinks = (items) =>
    items
      .map((item) => {
        const className = item.page === page ? ' class="active"' : "";
        const extra = item.external ? ' target="_blank" rel="noopener"' : "";
        return `<a${className} href="${item.href}"${extra}>${item.label}</a>`;
      })
      .join("");

  const navContainer = document.querySelector('[data-site-shell="subpage-nav"]');
  if (navContainer) {
    const links = renderLinks(navItems);
    navContainer.innerHTML = `
      <a class="brand" href="/">Maxwell J. Yin</a>
      <button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false">
        <span class="hamburger"></span>
      </button>
      <div class="nav-links">${links}</div>
    `;

    const toggleBtn = navContainer.querySelector('.menu-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const isOpen = navContainer.classList.toggle('nav-open');
        toggleBtn.setAttribute('aria-expanded', isOpen);
      });
    }
  }

  const homeNavContainer = document.querySelector('[data-site-shell="home-nav"]');
  if (homeNavContainer) {
    homeNavContainer.innerHTML = renderLinks(navItems.filter((item) => item.page !== "home"));
  }

  const footerContainer = document.querySelector('[data-site-shell="footer"]');
  if (footerContainer) {
    footerContainer.innerHTML = '© Maxwell J. Yin · <a id="fun-stuff" href="/games/snake/">Fun stuff 👀</a>';
  }
})();
