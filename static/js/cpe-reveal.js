/* Apparition au scroll - applique .is-visible aux .cpe-reveal */
(function () {
    'use strict';

    const init = () => {
        const targets = document.querySelectorAll('.cpe-reveal');
        if (!targets.length) return;

        if (!('IntersectionObserver' in window)) {
            targets.forEach(el => el.classList.add('is-visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const delay = parseInt(entry.target.dataset.cpeDelay || '0', 10);
                    setTimeout(() => entry.target.classList.add('is-visible'), delay);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        targets.forEach(el => observer.observe(el));
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
