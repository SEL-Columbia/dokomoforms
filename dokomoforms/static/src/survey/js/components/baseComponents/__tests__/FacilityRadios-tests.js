import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('FacilityRadios', () => {
    var FacilityRadios;

    beforeEach(function() {
        jest.dontMock('../FacilityRadios.js');
        FacilityRadios = require('../FacilityRadios');
    });

    it('does nothing', () => {

    });

});
