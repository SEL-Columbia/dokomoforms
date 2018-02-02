import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Question', () => {
    var Question;

    beforeEach(function() {
        jest.dontMock('../Question.js');
        Question = require('../Question');
    });

    it('does nothing', () => {

    });

});
