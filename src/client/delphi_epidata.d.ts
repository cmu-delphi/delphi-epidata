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

        fluview(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number, auth?: string): Promise<EpiDataResponse>;
        fluview_meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        fluview_clinical(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        flusurv(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        gft(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        ght(callback: EpiDataCallback, auth: string, locations: StringParam, epiweeks: EpiRangeParam, query: string): Promise<EpiDataResponse>;
        cdc(callback: EpiDataCallback, auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        quidel(callback: EpiDataCallback, auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        norostat(callback: EpiDataCallback, auth: string, location: string, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        meta_norostat(callback: EpiDataCallback, auth: string): Promise<EpiDataResponse>;
        afhsb(callback: EpiDataCallback, auth: string, locations: StringParam, epiweeks: EpiRangeParam, flu_types: StringParam): Promise<EpiDataResponse>;
        meta_afhsb(callback: EpiDataCallback, auth: string): Promise<EpiDataResponse>;
        nidss_flu(callback: EpiDataCallback, regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        nidss_dengue(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        delphi(callback: EpiDataCallback, system: string, epiweek: string | number): Promise<EpiDataResponse>;
        sensors(callback: EpiDataCallback, auth: string, names: StringParam, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        nowcast(callback: EpiDataCallback, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        covidcast(callback: EpiDataCallback, data_source: string, signals: string, time_type: 'day' | 'week', geo_type: string, time_values: EpiRangeParam, as_of?: number, issues?: EpiRangeParam, format?: 'json' | 'tree' | 'classic' | 'csv'): Promise<EpiDataResponse>;
        covidcast_meta(callback: EpiDataCallback): Promise<EpiDataResponse>;
        covid_hosp(callback: EpiDataCallback, states: StringParam, dates: EpiRangeParam, issues: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_facility(callback: EpiDataCallback, hospital_pks: StringParam, collection_weeks: EpiRangeParam, publication_dates: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_facility_lookup(callback: EpiDataCallback, state?: string, ccn?: string, city?: string, zip?: string, fips_code?: string): Promise<EpiDataResponse>;
    }

    export const Epidata: EpidataFunctions;

    export interface EpidataAsyncFunctions {
        readonly BASE_URL: string;
        range(this: void, from: string | number, to: string | number): EpiRange;
        withURL(this: void, baseUrl?: string): EpidataAsyncFunctions;

        fluview(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number, auth?: string): Promise<EpiDataResponse>;
        fluview_meta(): Promise<EpiDataResponse>;
        fluview_clinical(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        flusurv(locations: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        gft(locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        ght(auth: string, locations: StringParam, epiweeks: EpiRangeParam, query: string): Promise<EpiDataResponse>;
        cdc(auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        quidel(auth: string, epiweeks: EpiRangeParam, locations: StringParam): Promise<EpiDataResponse>;
        norostat(auth: string, location: string, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        meta_norostat(auth: string): Promise<EpiDataResponse>;
        afhsb(auth: string, locations: StringParam, epiweeks: EpiRangeParam, flu_types: StringParam): Promise<EpiDataResponse>;
        meta_afhsb(auth: string): Promise<EpiDataResponse>;
        nidss_flu(regions: StringParam, epiweeks: EpiRangeParam, issues?: EpiRangeParam, lag?: number): Promise<EpiDataResponse>;
        nidss_dengue(locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        delphi(system: string, epiweek: string | number): Promise<EpiDataResponse>;
        sensors(auth: string, names: StringParam, locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        nowcast(locations: StringParam, epiweeks: EpiRangeParam): Promise<EpiDataResponse>;
        meta(): Promise<EpiDataResponse>;
        covidcast(data_source: string, signals: string, time_type: 'day' | 'week', geo_type: string, time_values: EpiRangeParam, as_of?: number, issues?: EpiRangeParam, format?: 'json' | 'tree' | 'classic' | 'csv'): Promise<EpiDataResponse>;
        covidcast_meta(): Promise<EpiDataResponse>;
        covid_hosp(states: StringParam, dates: EpiRangeParam, issues: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_facility(hospital_pks: StringParam, collection_weeks: EpiRangeParam, publication_dates: EpiRangeParam): Promise<EpiDataResponse>;
        covid_hosp_facility_lookup(state?: string, ccn?: string, city?: string, zip?: string, fips_code?: string): Promise<EpiDataResponse>;
    }

    export const EpidataAsync: EpidataAsyncFunctions;
}
