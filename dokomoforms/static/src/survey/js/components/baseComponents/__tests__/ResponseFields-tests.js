import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';
import PropTypes from 'prop-types';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('ResponseFields', () => {
    var ResponseFields, ResponseField;

    beforeEach(function() {
        jest.dontMock('../ResponseFields.js');
        jest.dontMock('../ResponseField.js');
        ResponseFields = require('../ResponseFields');
        ResponseField = require('../ResponseField');
    });

    it('renders multiple ResponseField components based on childCount prop', () => {
        var ResponseFieldsInstance = TestUtils.renderIntoDocument(
            <ResponseFields childCount='5' onInput={noop} buttonFunction={noop} type='date'/>
        );

        var ResponseFieldInstances = TestUtils.scryRenderedComponentsWithType(ResponseFieldsInstance, ResponseField);

        expect(ResponseFieldInstances.length).toEqual(5);
    });
});
