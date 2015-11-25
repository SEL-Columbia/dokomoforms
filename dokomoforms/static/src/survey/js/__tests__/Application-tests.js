import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Application', () => {
    var Application;

    beforeEach(function() {
        jest.dontMock('../Application.js');
        Application = require('../Application');
    });

    it('does nothing', () => {

    });

});
