/**
 * @global {jest}
 */
const fetchM = require('cross-fetch');
const {Epidata, EpidataAsync} = require('..');

jest.mock('cross-fetch');

beforeEach(() => {
    fetchM.fetch.mockClear();
});

function mockReturn(res) {
    fetchM.fetch.mockResolvedValue({
        json: () => Promise.resolve(res)
    });
}

describe('fluview', () => {
    const api = new EpidataAsync();
    const apiCallbacks = new Epidata();

    describe('basic', () => {
        const res = { message: 'm', result: 1, epidata: [] };
        it('async', async () => {
            mockReturn(res);
            const r = await api.fluview('a', 4);
            expect(r).toEqual(res);
            expect(fetchM.fetch).toMatchSnapshot();
        });
        it('sync', (done) => {
            mockReturn(res);
            apiCallbacks.fluview((result, message, epidata) => {
                expect({result, message, epidata}).toEqual(res);
                expect(fetchM.fetch).toMatchSnapshot();
                done();
            }, 'a', 4);
        });
    });
    it('wrong params', () => {
        expect(() => api.fluview()).toThrow("`regions`,`epiweeks` are all required");
        expect(() => api.fluview('a')).toThrow("`regions`,`epiweeks` are all required");
        expect(() => api.fluview(null)).toThrow("`regions`,`epiweeks` are all required");
        expect(() => api.fluview('a', 4, 4, 3)).toThrow("`issues` and `lag` are mutually exclusive")
    });
});

describe('alternative API endpoints', () => {
    const res = { message: 'm', result: 1, epidata: [] };
    it('php', async () => {
        mockReturn(res);
        const api = new EpidataAsync('http://test.com/api.php');
        const r = await api.fluview('a', 4);
        expect(r).toEqual(res);
        expect(fetchM.fetch).toHaveBeenCalledTimes(1);
        expect(fetchM.fetch.mock.calls[0][0].toString()).toEqual('http://test.com/api.php?endpoint=fluview&regions=a&epiweeks=4');
        expect(fetchM.fetch).toMatchSnapshot();
    });
    it('new', async () => {
        mockReturn(res);
        const api = new EpidataAsync('http://test.com/');
        const r = await api.fluview('a', 4);
        expect(r).toEqual(res);
        expect(fetchM.fetch).toHaveBeenCalledTimes(1);
        expect(fetchM.fetch.mock.calls[0][0].toString()).toEqual('http://test.com/fluview/?regions=a&epiweeks=4');
        expect(fetchM.fetch).toMatchSnapshot();
    });
});

