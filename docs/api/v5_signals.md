---
title: Delphi V5 Sources and Signals
parent: Delphi V5 API
nav_order: 3
has_children: true
---

# Delphi V5 Sources and Signals

> **The legacy V4 API is being phased out.** See the [V4 to V5 Migration Guide](v5_migration.md) for guidance on migrating existing queries.
{: .warning }

## V5 Sources

Sources available in V5, and the legacy V4 source each one replaces. A V4 source not listed here has not migrated and remains V4-only. The table entries are filled real-time using [`/epidata/v5/metadata/`](v5_meta.md).

| Source | V4 Equivalent | Geographies | Extra Key Columns |
| :--- | :--- | :--- | :--- |
| [`nssp`](v5-signals/nssp.md) | [`nssp`](covidcast-signals/nssp.md) | census_division, census_region, county, hhs, hrr, hsa_nci, msa, nation, state | — |
| [`nhsn`](v5-signals/nhsn.md) | [`nhsn`](covidcast-signals/nhsn.md) | census_division, census_region, hhs, nation, state | — |
| [`pophive`](v5-signals/epic-cosmos.md) | New in V5 | hhs, nation, state | `age_group` |
| [`nwss`](v5-signals/nwss.md) | New in V5 | sewershed | `nwss_source`, `sample_index` |
| [`claims_outpatient`](v5-signals/claims_outpatient.md) | [`doctor-visits`](covidcast-signals/doctor-visits.md) | census_division, census_region, county, hhs, hrr, msa, nation, state | — |
| [`claims_inpatient`](v5-signals/claims_inpatient.md) | [`hospital-admissions`](covidcast-signals/hospital-admissions.md) | census_division, census_region, county, hhs, hrr, msa, nation, state | — |
| [`va_respiratory`](v5-signals/va_respiratory.md) | New in V5 | census_division, census_region, hhs, msa, nation, state, va_facility | — |
| `sleepcycle` | Not yet verified | census_division, census_region, county, hhs, hrr, msa, nation, state | — |
{: #v5-sources-table}

<span id="v5-sources-table-status">V5 sources available as of August 25, 2026.</span>

**Not yet verified** means this page's maintainers have not yet confirmed whether the source is genuinely new in V5 or a renamed V4 source.

<!--
  DEVELOPER INSTRUCTIONS FOR UPDATING THIS PAGE:

  1. Static fallback table (above) — shown when the metadata fetch fails:
     - Add the source row with its V4 equivalent, geographies, and extra keys.
     - Use markdown .md links here; jekyll-relative-links rewrites them to .html at build time.
     - Update the static date in the status span.

  2. Dynamic JavaScript config (below) — patches the table from the live metadata endpoint.
     Paths here are NOT processed by jekyll-relative-links (they are injected client-side),
     so they MUST be written as .html:
     - New V5 doc page (docs/api/v5-signals/<source>.md)? Add '<source>': 'v5-signals/<source>.html' to V5_DOCS.
     - A V5 source with the SAME name as a V4 source is auto-detected as that source. Only
       add to V5_RENAMED_FROM_V4 when the name CHANGED between V4 and V5.
     - Confirmed to have no V4 predecessor? Add it to CONFIRMED_NEW_IN_V5.
     - Anything else renders as "Not yet verified" — that is deliberate. Do not guess.
-->

<script>
(function () {
  // V4 source name -> its V4 documentation page.
  var V4_DOCS = {
    'nssp': 'covidcast-signals/nssp.html',
    'nhsn': 'covidcast-signals/nhsn.html',
    'doctor-visits': 'covidcast-signals/doctor-visits.html',
    'hospital-admissions': 'covidcast-signals/hospital-admissions.html',
    'fluview': 'fluview.html',
    'fluview_clinical': 'fluview_clinical.html',
    'flusurv': 'flusurv.html',
    'quidel': 'quidel.html'
  };

  // Only for sources RENAMED between V4 and V5. Identical names resolve via V4_DOCS.
  var V5_RENAMED_FROM_V4 = {
    'claims_outpatient': 'doctor-visits',
    'claims_inpatient': 'hospital-admissions'
  };

  // Sources confirmed to have no V4 predecessor. Everything unlisted stays "Not yet verified".
  var CONFIRMED_NEW_IN_V5 = ['pophive', 'nwss', 'va_respiratory', 'sleepcycle'];

  // V5 source name -> its V5 documentation page.
  var V5_DOCS = {
    'nssp': 'v5-signals/nssp.html',
    'nhsn': 'v5-signals/nhsn.html',
    'pophive': 'v5-signals/epic-cosmos.html',
    'nwss': 'v5-signals/nwss.html',
    'claims_outpatient': 'v5-signals/claims_outpatient.html',
    'claims_inpatient': 'v5-signals/claims_inpatient.html',
    'va_respiratory': 'v5-signals/va_respiratory.html'
  };

  var code = function (s) { return '<code>' + s + '</code>'; };
  var link = function (href, label) { return href ? '<a href="' + href + '">' + label + '</a>' : label; };

  // Resolution order: explicit rename -> identical name -> confirmed new -> unverified.
  var v4Equivalent = function (v5Name) {
    var v4Name = V5_RENAMED_FROM_V4[v5Name] || (V4_DOCS[v5Name] ? v5Name : null);
    if (v4Name) return link(V4_DOCS[v4Name], code(v4Name));
    if (CONFIRMED_NEW_IN_V5.indexOf(v5Name) !== -1) return 'New in V5';
    return '<em>Not yet verified</em>';
  };

  fetch('https://delphi.cmu.edu/epidata/v5/metadata/')
    .then(function (r) { return r.json(); })
    .then(function (meta) {
      var live = Object.keys(meta).filter(function (s) {
        var info = meta[s];
        return info && Array.isArray(info.signals) && info.signals.length > 0;
      });

      var formatDate = function (d) { return d ? d.slice(0, 10) : '—'; };
      var formatRange = function (range) {
        return (range && range.first && range.latest)
          ? formatDate(range.first) + ' – ' + formatDate(range.latest)
          : '—';
      };

      // The live table carries extra metadata columns the static fallback cannot fill.
      document.querySelector('#v5-sources-table thead tr').innerHTML =
        '<th>Source</th><th>V4 Equivalent</th><th>Geographies</th><th>Extra Key Columns</th><th>Signals</th><th>Report Time Range</th><th>Reference Time Range</th>';

      var sourceRows = live.map(function (s) {
        var info = meta[s] || {};
        var geos = (info.geo_types || []).join(', ') || '—';
        var extraKeys = (info.extra_key_columns || []).map(code).join(', ') || '—';
        return '<tr>'
          + '<td>' + link(V5_DOCS[s], code(s)) + '</td>'
          + '<td>' + v4Equivalent(s) + '</td>'
          + '<td>' + geos + '</td>'
          + '<td>' + extraKeys + '</td>'
          + '<td>' + (info.signals ? info.signals.length : '—') + '</td>'
          + '<td>' + formatRange(info.report_time_range) + '</td>'
          + '<td>' + formatRange(info.reference_time_range) + '</td>'
          + '</tr>';
      });

      document.querySelector('#v5-sources-table tbody').innerHTML = sourceRows.join('');
      document.querySelector('#v5-sources-table-status').textContent =
        'This table\'s entries are updated in realtime.';
    })
    .catch(function () { /* Preserve static fallback table and message if fetch fails */ });
})();
</script>
