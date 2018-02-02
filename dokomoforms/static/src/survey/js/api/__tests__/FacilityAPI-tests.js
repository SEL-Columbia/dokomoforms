import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('FacilityAPI', () => {
    var FacilityAPI;

    beforeEach(function() {
        jest.dontMock('../FacilityAPI.js');
        FacilityAPI = require('../FacilityAPI');
    });

    it('does nothing', () => {

    });

});
