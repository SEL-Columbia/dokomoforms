import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Header', () => {
    var Header;

    beforeEach(function() {
        jest.dontMock('../Header.js');
        Header = require('../Header');
    });

    it('does nothing', () => {

    });

});
