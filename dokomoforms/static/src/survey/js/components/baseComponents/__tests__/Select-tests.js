import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Select', () => {
    var Select, ResponseField, callback;

    beforeEach(function() {
        jest.dontMock('../Select.js');
        jest.dontMock('../ResponseField.js');
        Select = require('../Select');
        ResponseField = require('../ResponseField');
        callback = jest.genMockFunction();
    });

    it('renders a single select dropdown', () => {
        var choices = [{
            value: 0,
            text: 'Zero'
        }];

        var SelectInstance = TestUtils.renderIntoDocument(
            <Select choices={choices} multiSelect={false} />
        );

        var select = TestUtils.findRenderedDOMComponentWithTag(SelectInstance, 'select');

        expect(select.getAttribute('multiple')).toBeNull();

        var options = TestUtils.scryRenderedDOMComponentsWithTag(SelectInstance, 'option');

        // expect two, as placeholder is added to top
        expect(options.length).toEqual(2);
    });

    it('renders a multi select dropdown', () => {
        var choices = [{
            value: 0,
            text: 'Zero'
        }];

        var SelectInstance = TestUtils.renderIntoDocument(
            <Select choices={choices} multiSelect={true} />
        );

        var select = TestUtils.findRenderedDOMComponentWithTag(SelectInstance, 'select');

        expect(select.getAttribute('multiple')).toBeDefined();
    });

    it('renders other option', () => {
        var choices = [{
            value: 0,
            text: 'Zero'
        }];

        var SelectInstance = TestUtils.renderIntoDocument(
            <Select choices={choices} multiSelect={false} withOther={true} />
        );

        var options = TestUtils.scryRenderedDOMComponentsWithTag(SelectInstance, 'option');
        // expect two, as placeholder is added to top
        expect(options.length).toEqual(3);
    });

    it('renders other field when other option selected', () => {
        var choices = [{
            value: 0,
            text: 'Zero'
        }];

        var SelectInstance = TestUtils.renderIntoDocument(
            <Select choices={choices} multiSelect={false} withOther={true} />
        );

        var options = TestUtils.scryRenderedDOMComponentsWithTag(SelectInstance, 'option');
        var select = TestUtils.findRenderedDOMComponentWithTag(SelectInstance, 'select');

        TestUtils.Simulate.change(
            select,
            {
                target: {
                    selectedOptions: [
                        options[2]
                    ]
                }
            }
        );

        // make sure the response field is rendered
        var ResponseFieldInstance = TestUtils.findRenderedComponentWithType(SelectInstance, ResponseField);
    });

    it('calls onSelect prop when changed', () => {
        var choices = [{
            value: 0,
            text: 'Zero'
        }];

        var SelectInstance = TestUtils.renderIntoDocument(
            <Select choices={choices} multiSelect={false} onSelect={callback} />
        );

        var options = TestUtils.scryRenderedDOMComponentsWithTag(SelectInstance, 'option');
        var select = TestUtils.findRenderedDOMComponentWithTag(SelectInstance, 'select');

        TestUtils.Simulate.change(
            select,
            {
                target: {
                    selectedOptions: [
                        options[1]
                    ]
                }
            }
        );

        expect(callback).toBeCalled();

    });

    it('renders with default value from initSelect', () => {
        var choices = [{
            value: 0,
            text: 'Zero'
        }];

        var SelectInstance = TestUtils.renderIntoDocument(
            <Select choices={choices} multiSelect={false} initSelect={[0]} />
        );

        var select = TestUtils.findRenderedDOMComponentWithTag(SelectInstance, 'select');

        expect(select.value).toEqual('0');
    });
});
