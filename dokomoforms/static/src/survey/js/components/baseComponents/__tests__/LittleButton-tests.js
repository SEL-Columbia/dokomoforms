import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('LittleButton', () => {
    var LittleButton;

    beforeEach(function() {
        jest.dontMock('../LittleButton.js');
        LittleButton = require('../LittleButton');
    });

    it('renders displaying its text property', () => {
        // Render a LittleButton in the document
        var button = TestUtils.renderIntoDocument(
            <LittleButton text='Press Me!' buttonFunction={noop} />
        );

        // Get the rendered element
        var buttonNode = ReactDOM.findDOMNode(button);

        // Verify that its text matches Press Me!
        expect(buttonNode.textContent).toEqual('Press Me!');
    });

    it('calls the buttonFunction property when pressed', () => {
        var callback = jest.genMockFunction();

        // Render a LittleButton in the document
        var button = TestUtils.renderIntoDocument(
            <LittleButton text='Press Me!' buttonFunction={callback} />
        );

        // Simulate click on button
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithTag(button, 'button')
        );

        // Verify that the callback was called once.
        expect(callback.mock.calls.length).toEqual(1);
    });

    it('is disabled when disabled property is set', () => {
        var callback = jest.genMockFunction();

        // Render a LittleButton in the document
        var button = TestUtils.renderIntoDocument(
            <LittleButton text='Press Me!' buttonFunction={callback} disabled={true} />
        );

        // Simulate click on button
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithTag(button, 'button')
        );

        // Verify that the callback was called once.
        expect(callback.mock.calls.length).toEqual(0);
    });

    it('includes an icon if an icon property is set', () => {
        // Render a LittleButton in the document
        var button = TestUtils.renderIntoDocument(
            <LittleButton text='Press Me!' buttonFunction={noop} icon="icon-test" />
        );

        // makes sure there is a span tag (i.e. icon) rendered within the button
        TestUtils.findRenderedDOMComponentWithTag(button, 'span');
    });

});
