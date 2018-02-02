import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Submit', () => {
    var Submit;

    beforeEach(function() {
        jest.dontMock('../Submit.js');
        Submit = require('../Submit');
    });

    it('does nothing', () => {

    });

});
