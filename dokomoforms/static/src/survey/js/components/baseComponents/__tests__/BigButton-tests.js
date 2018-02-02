import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('BigButton', () => {
    var BigButton;

    beforeEach(function() {
        jest.dontMock('../BigButton.js');
        BigButton = require('../BigButton');
    });

    it('renders displaying its text property', () => {
        // Render a BigButton in the document
        var button = TestUtils.renderIntoDocument(
            <BigButton text='Press Me!' buttonFunction={noop} />
        );

        // Get the rendered element
        var buttonNode = ReactDOM.findDOMNode(button);

        // Verify that its text matches Press Me!
        expect(buttonNode.textContent).toEqual('Press Me!');
    });

    it('calls the buttonFunction property when pressed', () => {
        var callback = jest.genMockFunction();

        // Render a BigButton in the document
        var button = TestUtils.renderIntoDocument(
            <BigButton text='Press Me!' buttonFunction={callback} />
        );

        // Simulate click on button
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithTag(button, 'button')
        );

        // Verify that the callback was called once.
        expect(callback.mock.calls.length).toEqual(1);
    });

    it('should add a class associated with a type property', () => {
        // Render a BigButton in the document
        var button = TestUtils.renderIntoDocument(
            <BigButton text='Press Me!' buttonFunction={noop} type='btn-testing' />
        );

        // makes sure the type property has added the class
        TestUtils.findRenderedDOMComponentWithClass(button, 'btn-testing');
    });

});
