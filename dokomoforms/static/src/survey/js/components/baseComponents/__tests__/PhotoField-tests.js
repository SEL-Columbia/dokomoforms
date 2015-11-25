import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('PhotoField', () => {
    var PhotoField, PhotoPreview;

    beforeEach(function() {
        jest.dontMock('../PhotoField.js');
        PhotoField = require('../PhotoField');
        jest.dontMock('../PhotoPreview.js');
        PhotoPreview = require('../PhotoPreview');
    });

    it('calls showPreview on thumbnail click', () => {

        // Hackity hack hack hack
        // https://github.com/facebook/jest/issues/207
        PhotoField.prototype.__reactAutoBindMap.showPreview = jest.genMockFunction();

        var Photo = TestUtils.renderIntoDocument(
            <PhotoField />
        );

        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(Photo, 'photo_container')
        );

        expect(PhotoField.prototype.__reactAutoBindMap.showPreview).toBeCalled();
    });

    it('renders image tag when initValue passed', () => {

        var Photo = TestUtils.renderIntoDocument(
            <PhotoField initValue='nothing.jpg' />
        );

        TestUtils.findRenderedDOMComponentWithTag(Photo, 'img');

    });

    it('renders PhotoPreview on thumbnail click', () => {

        var Photo = TestUtils.renderIntoDocument(
            <PhotoField />
        );

        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(Photo, 'photo_container')
        );

        TestUtils.findRenderedComponentWithType(Photo, PhotoPreview);
    });



    it('hides PhotoPreview on thumbnail click', () => {

        // render photo field instance
        var Photo = TestUtils.renderIntoDocument(
            <PhotoField />
        );

        // click thumbnail
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(Photo, 'photo_container')
        );

        // get reference to rendered PhotoPreview instance
        var PhotoPreviewInstance = TestUtils.findRenderedComponentWithType(Photo, PhotoPreview);

        // click close button on preview
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(PhotoPreviewInstance, 'btn-photo-close')
        );

        // check that there are no longer any rendered PhotoPreview instances
        var PhotoPreviewInstances = TestUtils.scryRenderedComponentsWithType(Photo, PhotoPreview);

        expect(PhotoPreviewInstances.length).toEqual(0);
    });

    it('calls onDelete when delete button pressed in preview', () => {

        var callback = jest.genMockFunction();

        // render photo field instance
        var Photo = TestUtils.renderIntoDocument(
            <PhotoField buttonFunction={callback} />
        );

        // click thumbnail
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(Photo, 'photo_container')
        );

        // get reference to rendered PhotoPreview instance
        var PhotoPreviewInstance = TestUtils.findRenderedComponentWithType(Photo, PhotoPreview);

        // click close button on preview
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(PhotoPreviewInstance, 'btn-photo-delete')
        );

        // check that the delete method was called (which in turn calls buttonFunction prop)
        expect(callback).toBeCalled();
    });

});
