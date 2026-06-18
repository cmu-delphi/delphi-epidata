// Populates "latest data availability" table cells on source pages by
// querying the public /metadata endpoint client-side, since this is a static site
// and can't bake live values in at build time.
const METADATA_ENDPOINT = 'https://delphi.cmu.edu/epidata/v5/metadata/?source=nwss';

function formatTimestamp(value) {
    return value ? value.slice(0, 10) : 'unknown';
}

function getField(data, path) {
    return path.split('.').reduce((value, key) => (value == null ? value : value[key]), data);
}

async function populateSourceMetadata(source, fields) {
    const url = `${METADATA_ENDPOINT}?source=${encodeURIComponent(source)}`;
    let sourceData;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        sourceData = (await response.json())[source];
    } catch (err) {
        console.error(`Failed to load metadata for source "${source}":`, err);
        fields.forEach((field) => {
            field.textContent = 'unavailable';
        });
        return;
    }

    fields.forEach((field) => {
        field.textContent = formatTimestamp(getField(sourceData, field.dataset.field));
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const fieldsBySource = new Map();
    document.querySelectorAll('.source-metadata-field[data-source][data-field]').forEach((field) => {
        const source = field.dataset.source;
        if (!fieldsBySource.has(source)) {
            fieldsBySource.set(source, []);
        }
        fieldsBySource.get(source).push(field);
    });

    fieldsBySource.forEach((fields, source) => populateSourceMetadata(source, fields));
});
