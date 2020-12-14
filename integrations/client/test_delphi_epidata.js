const Epidata = require('../../src/client/delphi_epidata').Epidata;

function cb(r, msg, data) {
    console.log(r, msg, data);
}
Epidata.covidcast(cb, 'fb-survey', Array(1).fill('raw_cli').join(','), 'day', 'state', '2020-12-01', 'ca');
Epidata.covidcast(cb, 'fb-survey', Array(1000).fill('raw_cli').join(','), 'day', 'state', '2020-12-01', 'ca');