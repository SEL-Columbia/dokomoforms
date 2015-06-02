var jsdom = require('jsdom');
var should = require('should');
global.window = require('./emulate_dom.js');

document = window.document;
raw_survey = null;
L = window.L;
_ = window._;
$ = window.$;
alert = window.alert;
setInterval = function(hey, you) {  } //console.log('pikachu'); }
console = window.console;
Image = window.Image;
navigator = window.navigator;
localStorage = {};

var mah_code = require('../dokomoforms/static/bundle.js');
var getNearbyFacilities = mah_code.getNearbyFacilities
var App = {};
//var Widgets = mah_code.Widgets;


// User interaction, "trigger" tests when submitting offline
describe('Get nearby facilities', function(done) {

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        $.mockjax.clear();
        $(".page_nav__next").off(); //XXX Find out why events are cached
        $(".page_nav__prev").off();
        localStorage.setItem = function(id, data) {
            localStorage[id] = data;
        }

        App.unsynced_facilities = {};
        App.facilities = {};
        navigator.onLine = false;
        done();
    });

    afterEach(function(done) {
        raw_survey = null;
        localStorage = {};
        $(".page_nav__next").off('click'); //XXX Find out why events are cached
        $(".page_nav__prev").off('click');
        $(".message").clearQueue().text("");
        $('.content').empty();
        $.mockjax.clear();
        navigator.onLine = false;
        done();
    });

    it('retrieve facilities',
        function(done) {
            var lat = 40;
            var lng = 70;
            var rad = 200;
            var lim = 100; //all ignored
            var cb = function(facilities) {
                facilities.should.be.ok;
                Object.keys(facilities).length.should.match(68);
                done();
            }
            var url = "http://staging.revisit.global/api/v0/facilities.json";
            $.mockjax({
                  url: url,
                  status: 200,
                  onAfterSuccess: function() { 
                  },
                  onAfterError: function() { 
                      assert(false, "Failed to catch revisit correctly"); 
                  },
                  responseText: {
                        'facilities': require('./fixtures/facilities.json')
                  }
            });
            
            getNearbyFacilities(lat, lng, rad, lim, cb);
            
        });
 });
