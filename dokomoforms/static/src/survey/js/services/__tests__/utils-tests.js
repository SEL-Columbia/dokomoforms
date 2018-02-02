import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('utils', () => {
    var utils;

    beforeEach(function() {
        jest.dontMock('../utils.js');
        utils = require('../utils');
    });

    it('does nothing', () => {

    });

});
