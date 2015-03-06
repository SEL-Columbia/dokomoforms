var jsdom = require('jsdom');
var should = require('should');
var assert = require('assert');
global.window = require('./emulate_dom.js');

document = window.document;
raw_survey = null;
L = window.L;
_ = window._;
$ = window.$;
alert = function(msg) { console.log(msg, 'poop') };
navigator = window.navigator;
setInterval = function(hey, you) {  } //console.log('pikachu'); }
console = window.console;
Image = window.Image;
location = {};
localStorage = {};
require('../dokomoforms/static/persona.js');

describe('Persona login tests', function(done) {
    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        localStorage = {};
        location = {};
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
            $.mockjax({
                  url: "",
                  onAfterSuccess: function() { 
                  },
                  onAfterError: function() { 
                      assert(false, "Failed to handle xsrf request"); 
                  },
                  responseText: {
                      status: "success",
                      msg: "A text response from the server"
                  }
            });

            $.mockjax({
                  url: "/user/login/persona",
                  type: 'post',
                  onAfterSuccess: function() { 
                      localStorage.email.should.match('test_email');
                      done();
                  },
                  onAfterError: function() { 
                      assert(false, "Failed to handle xsrf request"); 
                  },
                  status: 200,
                  responseText: { email: 'test_email' }
            });

            $('#login').click();
    });

});
