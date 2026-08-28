// Open external links in a new tab by default, so readers don't lose their place in the docs.
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('#main-content a[href]').forEach(link => {
        if (link.hostname && link.hostname !== window.location.hostname) {
            link.target = '_blank';
            link.rel = 'noopener';
        }
    });
});
