(() => {
	const header = document.querySelector("#site-header");
	const toggle = document.querySelector(".nav-toggle");
	const nav = document.querySelector("#main-nav");
	const navLinks = [...document.querySelectorAll(".main-nav a[href^='#']")];
	const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

	const closeMenu = () => {
		nav?.classList.remove("open");
		toggle?.setAttribute("aria-expanded", "false");
		toggle?.setAttribute("aria-label", "فتح القائمة");
		document.body.classList.remove("menu-open");
	};

	toggle?.addEventListener("click", () => {
		const opening = !nav.classList.contains("open");
		nav.classList.toggle("open", opening);
		toggle.setAttribute("aria-expanded", String(opening));
		toggle.setAttribute("aria-label", opening ? "إغلاق القائمة" : "فتح القائمة");
		document.body.classList.toggle("menu-open", opening);
	});

	navLinks.forEach((link) => link.addEventListener("click", closeMenu));
	document.addEventListener("keydown", (event) => {
		if (event.key === "Escape") closeMenu();
	});

	let headerIsCompact = false;
	let headerFrame = 0;
	const syncHeader = () => {
		headerFrame = 0;
		const nextState = headerIsCompact ? window.scrollY > 28 : window.scrollY > 72;
		if (nextState === headerIsCompact) return;
		headerIsCompact = nextState;
		header?.classList.toggle("scrolled", headerIsCompact);
	};
	const requestHeaderSync = () => {
		if (headerFrame) return;
		headerFrame = window.requestAnimationFrame(syncHeader);
	};
	syncHeader();
	window.addEventListener("scroll", requestHeaderSync, { passive: true });

	const sections = navLinks
		.map((link) => document.querySelector(link.getAttribute("href")))
		.filter(Boolean);

	if ("IntersectionObserver" in window) {
		const sectionObserver = new IntersectionObserver((entries) => {
			entries.forEach((entry) => {
				if (!entry.isIntersecting) return;
				navLinks.forEach((link) => {
					link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`);
				});
			});
		}, { rootMargin: "-25% 0px -65% 0px" });
		sections.forEach((section) => sectionObserver.observe(section));

		if (!reducedMotion) {
			const revealObserver = new IntersectionObserver((entries, observer) => {
				entries.forEach((entry) => {
					if (!entry.isIntersecting) return;
					entry.target.classList.add("is-visible");
					observer.unobserve(entry.target);
				});
			}, { threshold: .12, rootMargin: "0px 0px -45px" });
			document.querySelectorAll(".reveal").forEach((element, index) => {
				element.style.transitionDelay = `${Math.min(index % 4, 3) * 70}ms`;
				revealObserver.observe(element);
			});
		}
	}

	if (reducedMotion || !("IntersectionObserver" in window)) {
		document.querySelectorAll(".reveal").forEach((element) => element.classList.add("is-visible"));
	}

	document.querySelector("#year").textContent = new Date().getFullYear().toLocaleString("en-US", { useGrouping: false });
})();
