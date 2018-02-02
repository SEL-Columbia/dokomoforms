import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('auth', () => {
    var auth;

    beforeEach(function() {
        jest.dontMock('../auth.js');
        auth = require('../auth');
    });

    it('does nothing', () => {

    });

});
