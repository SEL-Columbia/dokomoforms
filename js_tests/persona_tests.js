var jsdom = require('jsdom');
var should = require('should');

global.window = require('./emulate_dom.js');

document = window.document;
raw_survey = null;
L = window.L;
_ = window._;
$ = window.$;
alert = function(msg) { console.log(msg) };
navigator = window.navigator;
setInterval = function(hey, you) {  } //console.log('pikachu'); }
console = window.console;
Image = window.Image;
localStorage = {};


describe('Persona login tests', function(done) {
    var server;
    before(function(done) {
        require('../static/persona.js');
        done();
    });

    beforeEach(function(done) {
        localStorage = {};
        localStorage.setItem = function(id, data) {
            localStorage[id] = data;
        }

        done();
    });

    afterEach(function(done) {
        done();
    });
    
    after(function(done) {
        done();
    });

    it('should login in specified user',
        function(done) {
            //XXX: Need to prevent server from posting to persona url or provide valid auth somehow
            $('#login').click();
            console.log(localStorage.email);
            done();
    });

});
