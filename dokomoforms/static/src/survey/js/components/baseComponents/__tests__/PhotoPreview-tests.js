import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('PhotoPreview', () => {
    var PhotoPreview;

    beforeEach(function() {
        jest.dontMock('../PhotoPreview.js');
        PhotoPreview = require('../PhotoPreview');
    });

    it('calls onClose property when close button is pressed', () => {
        var callback = jest.genMockFunction();

        // Render a DontKnow in the document
        var preview = TestUtils.renderIntoDocument(
            <PhotoPreview onClose={callback} onDelete={noop} />
        );

        // Simulate click on button
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(preview, 'btn-photo-close')
        );

        // Verify that the callback was called once.
        expect(callback.mock.calls.length).toEqual(1);
    });

    it('calls onDelete property when close button is pressed', () => {
        var callback = jest.genMockFunction();

        // Render a DontKnow in the document
        var preview = TestUtils.renderIntoDocument(
            <PhotoPreview onClose={noop} onDelete={callback} />
        );

        // Simulate click on button
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(preview, 'btn-photo-delete')
        );

        // Verify that the callback was called once.
        expect(callback.mock.calls.length).toEqual(1);
    });
});
