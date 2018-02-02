import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('MultipleChoice', () => {
    var MultipleChoice;

    beforeEach(function() {
        jest.dontMock('../MultipleChoice.js');
        MultipleChoice = require('../MultipleChoice');
    });

    it('does nothing', () => {

    });

});
