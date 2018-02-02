import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Facility', () => {
    var Facility;

    beforeEach(function() {
        jest.dontMock('../Facility.js');
        Facility = require('../Facility');
    });

    it('does nothing', () => {

    });

});
