declare module 'delphi_epidata' {
    interface EpiRange {
        from: number;
        to: number;
    }
    export type StringParam = string | readonly string[];
    export type EpiRangeParam = string | number | EpiRange | readonly (string | number | EpiRange)[];

    export interface EpiDataResponse {
        status: number;
        message: string;
        epidata?: Record<string, unknown>[];
    }
    export type EpiDataCallback = (result: number, message: string, epidata: EpiDataResponse['epidata']) => void;

    export interface EpidataFunctions {
        readonly BASE_URL: string;
        range(this: void, from: string | number, to: string | number): EpiRange;
        withURL(this: void, baseUrl?: string): EpidataFunctions;
        client_version: string;
        version(): Promise<{version: string, client_version: string}>;

        cdc(callback: EpiDataCallback, auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        covid_hosp_facility(callback: EpiDataCallback, hospital_pks: StringParam, collection_weeks: EpiRangeParam, publication_dates: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_facility_lookup(callback: EpiDataCallback, state?: string, ccn?: string, city?: string, zip?: string, fips_code?: string): Promise<EpiDataResponse>;
        // alias to covid_hosp_state_timeseries
        covid_hosp(callback: EpiDataCallback, states: StringParam, dates: EpiRangeParam, issues: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_state_timeseries(callback: EpiDataCallback, states: StringParam, dates: EpiRangeParam, issues: EpiRangeParam): Promise<EpiDataResponse>;
        covidcast_meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        covidcast_nowcast(callback: EpiDataCallback, data_source: string, signals: string, time_type: 'day' | 'week', geo_type: string, time_values: EpiRangeParam, as_of?: number, issues?: EpiRangeParam, format?: 'json' | 'tree' | 'classic' | 'csv'): Promise<EpiDataResponse>;
        covidcast(callback: EpiDataCallback, data_source: string, signals: string, time_type: 'day' | 'week', geo_type: string, time_values: EpiRangeParam, as_of?: number, issues?: EpiRangeParam, format?: 'json' | 'tree' | 'classic' | 'csv'): Promise<EpiDataResponse>;
        fluview(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number, auth?: string): Promise<EpiDataResponse>;
        fluview_clinical(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        fluview_meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        flusurv(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        gft(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        ght(callback: EpiDataCallback, auth: string, locations: StringParam, epiweeks: EpiRangeParam, query: string): Promise<EpiDataResponse>;
        kcdc_ili(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        meta_afhsb(callback: EpiDataCallback, auth: string): Promise<EpiDataResponse>;
        meta_norostat(callback: EpiDataCallback, auth: string): Promise<EpiDataResponse>;
        meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        nidss_dengue(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        nidss_flu(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        norostat(callback: EpiDataCallback, auth: string, location: string, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        nowcast(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        paho_dengue(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        quidel(callback: EpiDataCallback, auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        delphi(callback: EpiDataCallback, system: string, epiweek: string | number): Promise<EpiDataResponse>;
        sensors(callback: EpiDataCallback, auth: string, names: StringParam, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        twitter(callback: EpiDataCallback, auth: string, locations: StringParam, dates?: EpiRangeParam, epiweeks?: EpiRangeParam): Promise<EpiDataResponse>;
        wiki(callback: EpiDataCallback, articles: StringParam, dates?: EpiRangeParam,  epiweeks: EpiRangeParam, language?: string = 'en'): Promise<EpiDataResponse>;
    }

    export const Epidata: EpidataFunctions;

    export interface EpidataAsyncFunctions {
        readonly BASE_URL: string;
        range(this: void, from: string | number, to: string | number): EpiRange;
        withURL(this: void, baseUrl?: string): EpidataAsyncFunctions;
        client_version: string;
        version(): Promise<{ version: string, client_version: string }>;

        cdc(auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        covid_hosp_facility(hospital_pks: StringParam, collection_weeks: EpiRangeParam, publication_dates: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_facility_lookup(state?: string, ccn?: string, city?: string, zip?: string, fips_code?: string): Promise<EpiDataResponse>;
        // alias to covid_hosp_state_timeseries
        covid_hosp(states: StringParam, dates: EpiRangeParam, issues: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_state_timeseries(states: StringParam, dates: EpiRangeParam, issues: EpiRangeParam): Promise<EpiDataResponse>;
        covidcast_meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        covidcast_nowcast(data_source: string, signals: string, time_type: 'day' | 'week', geo_type: string, time_values: EpiRangeParam, as_of?: number, issues?: EpiRangeParam, format?: 'json' | 'tree' | 'classic' | 'csv'): Promise<EpiDataResponse>;
        covidcast(data_source: string, signals: string, time_type: 'day' | 'week', geo_type: string, time_values: EpiRangeParam, as_of?: number, issues?: EpiRangeParam, format?: 'json' | 'tree' | 'classic' | 'csv'): Promise<EpiDataResponse>;
        fluview(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number, auth?: string): Promise<EpiDataResponse>;
        fluview_clinical(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        fluview_meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        flusurv(locations: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        gft(locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        ght(auth: string, locations: StringParam, epiweeks: EpiRangeParam, query: string): Promise<EpiDataResponse>;
        kcdc_ili(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        meta_afhsb(auth: string): Promise<EpiDataResponse>;
        meta_norostat(auth: string): Promise<EpiDataResponse>;
        meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        nidss_dengue(locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        nidss_flu(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        norostat(auth: string, location: string, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        nowcast(locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        paho_dengue(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        quidel(auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        delphi(system: string, epiweek: string | number): Promise<EpiDataResponse>;
        sensors(auth: string, names: StringParam, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        twitter(auth: string, locations: StringParam, dates?: EpiRangeParam, epiweeks?: EpiRangeParam): Promise<EpiDataResponse>;
        wiki(articles: StringParam, dates?: EpiRangeParam, epiweeks: EpiRangeParam, language?: string = 'en'): Promise<EpiDataResponse>;
    }

    export const EpidataAsync: EpidataAsyncFunctions;
}
