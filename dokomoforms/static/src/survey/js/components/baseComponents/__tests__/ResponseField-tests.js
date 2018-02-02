import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';
import PropTypes from 'prop-types';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('ResponseField', () => {
    var ResponseField, callback, setCustomValidity;

    beforeEach(function() {
        jest.dontMock('../ResponseField.js');
        ResponseField = require('../ResponseField');
        callback = jest.genMockFunction();
        setCustomValidity = jest.genMockFunction();
    });

    it('renders a number input if prop type is integer', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='integer' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('number');

        // simulate input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 50
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a number input if prop type is decimal', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='decimal' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('number');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 50
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a datetime-local input if prop type is timestamp', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='timestamp' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('datetime-local');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 1238592847
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a time input if prop type is time', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='time' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 1238592847
                }
            }
        );

        expect(input.getAttribute('type')).toEqual('time');
    });

    it('renders a date input if prop type is date', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='date' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('date');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2013-01-01T00:00:00.000Z'
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders an email input if prop type is email', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='email' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('email');
    });

    it('renders a text input if prop type is not specified', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('text');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'onetwothree'
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a minus if prop showMinus is true', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField showMinus={true} buttonFunction={callback} />
        );

        // check that minus is rendered
        TestUtils.findRenderedDOMComponentWithClass(ResponseFieldInstance, 'question__minus');
    });

    it('calls buttonFunction when minus is clicked', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField showMinus={true} buttonFunction={callback} />
        );

        // click on minus
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(ResponseFieldInstance, 'question__minus')
        );

        // check that the delete method was called (which in turn calls buttonFunction prop)
        expect(callback).toBeCalled();
    });

    it('calls onInput prop via onChange when input changes', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: noop,
                    value: 'a'
                }
            }
        );

        // check that the delete method was called (which in turn calls buttonFunction prop)
        expect(callback).toBeCalled();
    });

    it('validates non-numeric values in integer field', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='integer' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'a'
                }
            }
        );

        //  called once with empty string to clear, then again with invalid message
        expect(setCustomValidity.mock.calls[0][0]).toEqual('');
        expect(setCustomValidity.mock.calls[1][0]).toEqual('Invalid field.');
    });

    it('validates min and max values in integer field', () => {

        var logic = {
            min: 10,
            max: 20
        };

        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='integer' logic={logic} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate correct input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 15
                }
            }
        );

        // should be only called once if validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(1);

        // simulate bad min input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 5
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(3);

        // simulate bad max input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 25
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(5);
    });

    it('validates non-numeric values in decimal field', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='decimal' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'a'
                }
            }
        );

        //  called once with empty string to clear, then again with invalid message
        expect(setCustomValidity.mock.calls[0][0]).toEqual('');
        expect(setCustomValidity.mock.calls[1][0]).toEqual('Invalid field.');
    });

    it('validates min and max values in decimal field', () => {

        var logic = {
            min: 10,
            max: 20
        };

        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='decimal' logic={logic} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate correct input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 15
                }
            }
        );

        // should be only called once if validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(1);

        // simulate bad min input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 5
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(3);

        // simulate bad max input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 25
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(5);
    });

    it('validates non-parseable date values in date field', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='date' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'gibberish'
                }
            }
        );

        //  called once with empty string to clear, then again with invalid message
        expect(setCustomValidity.mock.calls[0][0]).toEqual('');
        expect(setCustomValidity.mock.calls[1][0]).toEqual('Invalid field.');
    });

    it('validates min and max values in date field', () => {

        var logic = {
            min: '2014-01-01',
            max: '2015-01-01'
        };

        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='date' logic={logic} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate correct input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2014-06-01'
                }
            }
        );

        // should be only called once if validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(1);

        // simulate bad min input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2013-01-01'
                }
            }
        );

        // should be called two more times when validation doesn't pass
        expect(setCustomValidity.mock.calls.length).toEqual(3);

        // simulate bad max input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2016-01-01'
                }
            }
        );

        // should be called two more times when validation doesn't pass
        expect(setCustomValidity.mock.calls.length).toEqual(5);
    });

});
