import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('location', () => {
    var location;

    beforeEach(function() {
        jest.dontMock('../location.js');
        location = require('../location');
    });

    it('does nothing', () => {

    });

});
