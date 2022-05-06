/*
  A module for DELPHI's Epidata API.
   https://github.com/cmu-delphi/delphi-epidata
   Notes:
   - If running in node.js (or using browserify), there are no external
     dependencies. Otherwise, a global jQuery object named `$` must be available.
  */
"use strict";
(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    // AMD. Register as an anonymous module.
    define(["exports", root.fetch, "jQuery"], factory);
  } else if (
    typeof exports === "object" &&
    typeof exports.nodeName !== "string"
  ) {
    // CommonJS
    factory(exports, require("cross-fetch").fetch);
  } else {
    // Browser globals
    factory(root, root.fetch, root.jQuery || root.$);
  }
})(this, function (exports, fetchImpl, jQuery) {
  const BASE_URL = "https://delphi.cmu.edu/epidata/";
  const client_version = "0.3.18";

  // Helper function to cast values and/or ranges to strings
  function _listitem(value) {
    if (value == null) {
      return null;
    }
    if (
      value != null &&
      value.hasOwnProperty("from") &&
      value.hasOwnProperty("to")
    ) {
      return "" + value["from"] + "-" + value["to"];
    }
    return "" + value;
  }

  function _list(values) {
    if (values == null) {
      return null;
    }
    if (!Array.isArray(values)) {
      values = [values];
    }
    return values.map((d) => _listitem(d)).join(",");
  }

  /**
   * @param {string} baseURL
   * @param {string} endpoint
   * @param {Record<string, unknown>} params
   * @returns
   */
  function _requestImpl(baseURL, endpoint, params) {
    const isCompatibility = baseURL.endsWith(".php");
    const requestUrl = isCompatibility ? baseURL : baseURL + endpoint + "/";
    const url = new URL(requestUrl);

    const cleanParams = {};
    if (isCompatibility) {
      cleanParams.endpoint = endpoint;
      url.searchParams.set("endpoint", endpoint);
    }
    Object.keys(params).forEach((key) => {
      const v = params[key];
      if (v != null) {
        cleanParams[key] = v;
        url.searchParams.set(key, v);
      }
    });
    const usePOST = url.href.length > 2048;
    if (jQuery && jQuery.ajax) {
      return $.ajax({
        url: requestUrl,
        dataType: "json",
        method: usePOST ? "POST" : "GET",
        data: cleanParams,
      });
    }
    if (usePOST) {
      return fetchImpl(requestUrl, {
        method: "POST",
        body: url.searchParams,
      }).then((r) => r.json());
    }
    return fetchImpl(url).then((r) => r.json());
  }

  function requireAll(obj) {
    const keys = Object.keys(obj);
    if (keys.some((k) => obj[k] == null)) {
      throw new Error(
        keys.map((k) => "`" + k + "`").join(",") + " are all required"
      );
    }
  }

  function issuesOrLag(issues, lag) {
    if (issues != null && lag != null) {
      throw new Error("`issues` and `lag` are mutually exclusive");
    }
  }

  function range(from, to) {
    return { from, to };
  }

  ////#region begin of views

  function createEpidataAsync(baseUrl) {
    const _request = (endpoint, params) =>
      _requestImpl(baseUrl || BASE_URL, endpoint, params);

    return {
      BASE_URL: baseUrl || BASE_URL,
      withURL: createEpidataAsync,
      range,
      client_version,
      version: () => {
        return _request('version', {}).then((r) => Object.assign(r, {client_version}));
      },
      /**
       * Fetch AFHSB data (point data, no min/max)
       */
      afhsb: (auth, locations, epiweeks, flu_types) => {
        requireAll({ auth, locations, epiweeks, flu_types });
        const params = {
          auth,
          locations: _list(locations),
          epiweeks: _list(epiweeks),
          flu_types: _list(flu_types),
        };
        return _request("afhsb", params);
      },
      /**
       * Fetch CDC page hits
       */
      cdc: (auth, epiweeks, locations) => {
        requireAll({ auth, locations, epiweeks });
        const params = {
          auth,
          epiweeks: _list(epiweeks),
          locations: _list(locations),
        };
        return _request("cdc", params);
      },
      /**
       * Fetch COVID hospitalization data for specific facilities
       */
      covid_hosp_facility: (
        hospital_pks,
        collection_weeks,
        publication_dates
      ) => {
        requireAll({ hospital_pks, collection_weeks });
        const params = {
          hospital_pks: _list(hospital_pks),
          collection_weeks: _list(collection_weeks),
          publication_dates: _list(publication_dates),
        };
        return _request("covid_hosp_facility", params);
      },

      /**
       * Lookup COVID hospitalization facility identifiers
       */
      covid_hosp_facility_lookup: (state, ccn, city, zip, fips_code) => {
        const params = {};
        if (state != null) {
          params.state = state;
        } else if (ccn != null) {
          params.ccn = ccn;
        } else if (city != null) {
          params.city = city;
        } else if (zip != null) {
          params.zip = zip;
        } else if (fips_code != null) {
          params.fips_code = fips_code;
        } else {
          throw new Error(
            "one of `state`, `ccn`, `city`, `zip`, or `fips_code` is required"
          );
        }
        return _request("covid_hosp_facility", params);
      },
      /**
       * Fetch COVID hospitalization data
       */
      covid_hosp: (states, dates, issues) => {
        requireAll({ states, dates });
        const params = {
          states: _list(states),
          dates: _list(dates),
          issues: _list(issues),
        };
        return _request("covid_hosp_state_timeseries", params);
      },
      /**
       * Fetch COVID hospitalization data
       */
      covid_hosp_state_timeseries: (states, dates, issues) => {
        requireAll({ states, dates });
        const params = {
          states: _list(states),
          dates: _list(dates),
          issues: _list(issues),
        };
        return _request("covid_hosp_state_timeseries", params);
      },
      /**
       * Fetch Delphi's COVID-19 Surveillance Streams metadata
       */
      covidcast_meta: () => {
        return _request("covidcast_meta", {});
      },
      /**
       * Fetch Delphi's COVID-19 Surveillance Streams
       */
      covidcast_nowcast: (
        data_source,
        signals,
        time_type,
        geo_type,
        time_values,
        geo_value,
        as_of,
        issues,
        lag,
        format
      ) => {
        requireAll({
          data_source,
          signals,
          time_type,
          geo_type,
          time_values,
          geo_value,
        });
        issuesOrLag(issues, lag);

        const params = {
          data_source,
          signals,
          time_type,
          geo_type,
          time_values: _list(time_values),
          as_of,
          issues: _list(issues),
          format,
        };
        if (Array.isArray(geo_value)) {
          params.geo_values = geo_value.join(",");
        } else {
          params.geo_value = geo_value;
        }
        return _request("covidcast_nowcast", params);
      },
      /**
       * Fetch Delphi's COVID-19 Surveillance Streams
       */
      covidcast: (
        data_source,
        signals,
        time_type,
        geo_type,
        time_values,
        geo_value,
        as_of,
        issues,
        lag,
        format
      ) => {
        requireAll({
          data_source,
          signals,
          time_type,
          geo_type,
          time_values,
          geo_value,
        });
        issuesOrLag(issues, lag);

        const params = {
          data_source,
          signals,
          time_type,
          geo_type,
          time_values: _list(time_values),
          as_of,
          issues: _list(issues),
          format,
        };
        if (Array.isArray(geo_value)) {
          params.geo_values = geo_value.join(",");
        } else {
          params.geo_value = geo_value;
        }
        return _request("covidcast", params);
      },
      /**
       * Fetch FluView data
       */
      fluview: (regions, epiweeks, issues, lag, auth) => {
        requireAll({ regions, epiweeks });
        issuesOrLag(issues, lag);
        const params = {
          regions: _list(regions),
          epiweeks: _list(epiweeks),
          issues: _list(issues),
          lag,
          auth,
        };
        return _request("fluview", params);
      },
      /**
       * Fetch FluView clinical data
       */
      fluview_clinical: (regions, epiweeks, issues, lag) => {
        requireAll({ regions, epiweeks });
        issuesOrLag(issues, lag);
        const params = {
          regions: _list(regions),
          epiweeks: _list(epiweeks),
          issues: _list(issues),
          lag,
        };
        return _request("fluview_clinical", params);
      },
      /**
       * Fetch FluView metadata
       */
      fluview_meta: () => {
        return _request("fluview_meta", {});
      },
      /**
       * Fetch FluSurv data
       */
      flusurv: (locations, epiweeks, issues, lag) => {
        requireAll({ locations, epiweeks });
        issuesOrLag(issues, lag);
        const params = {
          locations: _list(locations),
          epiweeks: _list(epiweeks),
          issues: _list(issues),
          lag,
        };
        return _request("flusurv", params);
      },
      /**
       * Fetch Google Flu Trends data
       */
      gft: (locations, epiweeks) => {
        requireAll({ locations, epiweeks });
        const params = {
          locations: _list(locations),
          epiweeks: _list(epiweeks),
        };
        return _request("gft", params);
      },
      /**
       * Fetch Google Health Trends data
       */
      ght: (auth, locations, epiweeks, query) => {
        requireAll({ auth, locations, epiweeks, query });
        const params = {
          auth,
          locations: _list(locations),
          epiweeks: _list(epiweeks),
          query,
        };
        return _request("ght", params);
      },
      /**
       * ?
       */
      kcdc_ili: (regions, epiweeks, issues, lag) => {
        requireAll({ regions, epiweeks });
        const params = {
          regions: _list(regions),
          epiweeks: _list(epiweeks),
          issues: _list(issues),
          lag,
        };
        return _request("kcdc_ili", params);
      },
      /**
       * Fetch AFHSB metadata
       */
      meta_afhsb: (auth) => {
        requireAll({ auth });
        const params = {
          auth,
        };
        return _request("meta_afhsb", params);
      },
      /**
       * Fetch NoroSTAT metadata
       */
      meta_norostat: (auth) => {
        if (auth == null) {
          throw new Error("`auth` is required");
        }
        const params = {
          auth,
        };
        return _request("meta_norostat", params);
      },
      /**
       * Fetch API metadata
       */
      meta: () => {
        return _request({
          endpoint: "meta",
        });
      },
      /**
       * Fetch NIDSS dengue data
       */
      nidss_dengue: (locations, epiweeks) => {
        requireAll({ locations, regions });
        const params = {
          locations: _list(locations),
          epiweeks: _list(epiweeks),
        };
        return _request("nidss_dengue", params);
      },
      /**
       * Fetch NIDSS flu data
       */
      nidss_flu: (regions, epiweeks, issues, lag) => {
        requireAll({ epiweeks, regions });
        issuesOrLag(issues, lag);
        const params = {
          regions: _list(regions),
          epiweeks: _list(epiweeks),
          issues: _list(issues),
          lag,
        };
        return _request("nidss_flu", params);
      },
      /**
       * Fetch NoroSTAT data (point data, no min/max)
       */
      norostat: (auth, location, epiweeks) => {
        requireAll({ auth, locations, epiweeks });
        const params = {
          auth,
          location,
          epiweeks: _list(epiweeks),
        };
        return _request("norostat", params);
      },
      /**
       * Fetch Delphi's ILI nowcast
       */
      nowcast: (locations, epiweeks) => {
        requireAll({ locations, epiweeks });
        const params = {
          locations: _list(locations),
          epiweeks: _list(epiweeks),
        };
        return _request("nowcast", params);
      },
      /**
       * Fetch Quidel data
       */
      paho_denque: (regions, epiweeks, issues, lag) => {
        requireAll({ regions, epiweeks });
        const params = {
          epiweeks: _list(epiweeks),
          regions: _list(regions),
          issues: _list(issues),
          lag,
        };
        return _request("paho_denque", params);
      },
      /**
       * Fetch Quidel data
       */
      quidel: (auth, epiweeks, locations) => {
        requireAll({ auth, locations, epiweeks });
        const params = {
          auth,
          epiweeks: _list(epiweeks),
          locations: _list(locations),
        };
        return _request("quidel", params);
      },
      /**
       * Fetch Delphi's forecast
       */
      delphi: (system, epiweek) => {
        requireAll({ system, epiweek });
        const params = {
          system,
          epiweek,
        };
        return _request("delphi", params);
      },

      /**
       * Fetch Delphi's digital surveillance sensors
       */
      sensors: (auth, names, locations, epiweeks) => {
        requireAll({ auth, names, locations, epiweeks });
        const params = {
          auth,
          names: _list(names),
          locations: _list(locations),
          epiweeks: _list(epiweeks),
        };
        return _request("sensors", params);
      },
      /**
       * Twitter data
       */
      twitter: (auth, locations, dates, epiweeks) => {
        requireAll({ auth, locations });
        if ((dates != null) !== (epiweeks != null)) {
          throw new Error("one of `dates` and `epiweeks` are required");
        }
        const params = {
          auth,
          locations: _list(locations),
          dates: _list(dates),
          epiweeks: _list(epiweeks),
        };
        return _request("twitter", params);
      },
      /**
       * Wikipedia data
       */
      wiki: (articles, dates, epiweeks, language) => {
        requireAll({ articles });
        if ((dates != null) !== (epiweeks != null)) {
          throw new Error("one of `dates` and `epiweeks` are required");
        }
        const params = {
          articles: _list(articles),
          dates: _list(dates),
          epiweeks: _list(epiweeks),
          language,
        };
        return _request("wiki", params);
      },
    };
  }
  exports.EpidataAsync = createEpidataAsync();

  function createEpidata(baseUrl) {
    const api = createEpidataAsync(baseUrl);
    const r = {
      BASE_URL: api.BASE_URL,
      withURL: createEpidata,
      range,
      client_version,
      version: () => {
        return _request('version', {}).then((r) => Object.assign(r, { client_version }));
      },
    };
    const knownKeys = Object.keys(r);
    Object.keys(api).forEach((key) => {
      if (knownKeys.indexOf(key) >= 0) {
        // known key ignore
        return;
      }
      r[key] = function (callback) {
        const args = Array.from(arguments).slice(1);
        if (callback == null) {
          throw new Error("callback is missing");
        }
        const r = api[key].apply(this, args);
        r.then((data) => {
          if (data && data.result != null) {
            callback(data.result, data.message, data.epidata);
          } else {
            return callback(0, "unknown error", null);
          }
        });
        return r;
      };
    });
    return r;
  }
  exports.Epidata = createEpidata();
  ////#endregion
});
