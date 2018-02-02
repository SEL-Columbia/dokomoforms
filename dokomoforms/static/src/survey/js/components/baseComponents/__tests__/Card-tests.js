import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Card', () => {
    var Card;

    beforeEach(function() {
        jest.dontMock('../Card.js');
        Card = require('../Card');
    });

    it('should render a sinlge message', () => {
        var message = ['hello'];

        var card = TestUtils.renderIntoDocument(
            <Card messages={message} />
        );

        // makes sure there is a single span tag (i.e. message)
        TestUtils.findRenderedDOMComponentWithTag(card, 'span');
    });

    it('should render multiple messages', () => {
        var messages = ['hello', 'hi', 'hola'];

        var card = TestUtils.renderIntoDocument(
            <Card messages={messages} />
        );

        // makes sure there is a single span tag (i.e. message)
        var spans = TestUtils.scryRenderedDOMComponentsWithTag(card, 'span');

        expect(spans.length).toEqual(3);
    });

    it('should add a class associated with a type property', () => {
        var message = ['hello'];

        var card = TestUtils.renderIntoDocument(
            <Card messages={message} type='message-secondary' />
        );

        // makes sure there the type prop has added the class
        TestUtils.findRenderedDOMComponentWithClass(card, 'message-secondary');
    });
});
