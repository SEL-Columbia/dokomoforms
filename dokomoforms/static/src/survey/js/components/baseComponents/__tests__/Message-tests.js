import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Message', () => {
    var Message;

    beforeEach(function() {
        jest.dontMock('../Message.js');
        Message = require('../Message');
    });

    it('should render a sinlge message', () => {
        var message = TestUtils.renderIntoDocument(
            <Message text='Hello' />
        );

        // Get the rendered element
        var messageNode = ReactDOM.findDOMNode(message);

        // Verify that its text matches Press Me!
        expect(messageNode.textContent).toEqual('Hello');
    });


    it('should add classes associated with the classes property', () => {
        var classes = 'testing';

        var message = TestUtils.renderIntoDocument(
            <Message text='Hello' classes={classes} />
        );

        // makes sure there the type prop has added the class
        TestUtils.findRenderedDOMComponentWithClass(message, 'testing');
    });
});
