(() => {
  const page = document.body.dataset.page || "";

  const navItems = [
    { href: "/", label: "Home", page: "home" },
    { href: "/projects", label: "Projects", page: "projects" },
    { href: "https://github.com/maxwellyin", label: "GitHub", external: true },
    { href: "https://www.linkedin.com/in/mjyin/", label: "LinkedIn", external: true },
    { href: "/resume", label: "Resume", page: "resume" },
  ];

  const navContainer = document.querySelector('[data-site-shell="subpage-nav"]');
  if (navContainer) {
    const links = navItems
      .map((item) => {
        const className = item.page === page ? ' class="active"' : "";
        const extra = item.external ? ' target="_blank" rel="noopener"' : "";
        return `<a${className} href="${item.href}"${extra}>${item.label}</a>`;
      })
      .join("");

    navContainer.innerHTML = `
      <a class="brand" href="/">Maxwell J. Yin</a>
      <div class="nav-links">${links}</div>
    `;
  }

  const footerContainer = document.querySelector('[data-site-shell="footer"]');
  if (footerContainer) {
    footerContainer.innerHTML = '© Maxwell J. Yin · <a id="fun-stuff" href="/games/snake/">Fun stuff 👀</a>';
  }
})();
