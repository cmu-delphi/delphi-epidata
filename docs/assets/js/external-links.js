// Open external links in a new tab by default, so readers don't lose their place in the docs.
document.addEventListener('DOMContentLoaded', () => {
    const openInNewTab = link => {
        link.target = '_blank';
        link.rel = 'noopener';
    };

    document.querySelectorAll('#main-content a[href]').forEach(link => {
        if (link.hostname && link.hostname !== window.location.hostname) {
            openInNewTab(link);
        }
    });

    // Callout banners (.note/.warning/.important/.tip/.caution) send readers off the page they're
    // reading; open those links in a new tab too, except plain in-page anchors.
    const calloutSelector = ['note', 'warning', 'important', 'tip', 'caution']
        .map(cls => `#main-content .${cls} a[href]`)
        .join(', ');
    document.querySelectorAll(calloutSelector).forEach(link => {
        if (!(link.getAttribute('href') || '').startsWith('#')) {
            openInNewTab(link);
        }
    });
});
