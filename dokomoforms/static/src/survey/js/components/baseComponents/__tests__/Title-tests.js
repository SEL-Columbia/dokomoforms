import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Title', () => {
    var Title;

    beforeEach(function() {
        jest.dontMock('../Title.js');
        Title = require('../Title');
    });

    it('should render a title with a message', () => {
        var title = TestUtils.renderIntoDocument(
            <Title title='Hello' message='Hola' />
        );

        var titleNode = TestUtils.findRenderedDOMComponentWithTag(title, 'h3');
        var messageNode = TestUtils.findRenderedDOMComponentWithTag(title, 'p');

        // Verify that its text matches Press Me!
        expect(titleNode.textContent).toEqual('Hello');
        expect(messageNode.textContent).toEqual('Hola');
    });
});
