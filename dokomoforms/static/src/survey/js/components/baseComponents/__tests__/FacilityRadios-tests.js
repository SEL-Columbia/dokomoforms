import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {},
    facilities = [{
        'name': 'water point',
        'coordinates': [6.456968, 12.91716],
        '_version': 0,
        'properties': {
            'sector': 'water',
            'type': 'type unavailable',
            'grid_power': null,
            'improved_water_supply': null,
            'improved_sanitation': null,
            'visits': 0,
            'photoUrls': []
        },
        'identifiers': [],
        'updatedAt': '2014-12-04T21:54:37.177Z',
        'createdAt': '2014-12-04T21:54:37.177Z',
        'active': true,
        'href': 'http://staging.revisit.global/api/v0/facilities/5480d81d2ecfcf69084425f3.json',
        'uuid': '5480d81d2ecfcf69084425f3'
    }, {
        'name': 'water point',
        'coordinates': [6.459725, 12.91686],
        '_version': 0,
        'properties': {
            'sector': 'water',
            'type': 'type unavailable',
            'grid_power': null,
            'improved_water_supply': null,
            'improved_sanitation': null,
            'visits': 0,
            'photoUrls': []
        },
        'identifiers': [],
        'updatedAt': '2014-12-04T21:54:37.177Z',
        'createdAt': '2014-12-04T21:54:37.177Z',
        'active': true,
        'href': 'http://staging.revisit.global/api/v0/facilities/5480d81d2ecfcf69084425b0.json',
        'uuid': '5480d81d2ecfcf69084425b0',
        'distance': 100
    }, {
        'name': 'water point',
        'coordinates': [6.454339, 12.92059],
        '_version': 0,
        'properties': {
            'sector': 'water',
            'type': 'type unavailable',
            'grid_power': null,
            'improved_water_supply': null,
            'improved_sanitation': null,
            'visits': 0,
            'photoUrls': []
        },
        'identifiers': [],
        'updatedAt': '2014-12-04T21:54:37.177Z',
        'createdAt': '2014-12-04T21:54:37.177Z',
        'active': true,
        'href': 'http://staging.revisit.global/api/v0/facilities/5480d81d2ecfcf69084425ff.json',
        'uuid': '5480d81d2ecfcf69084425ff'
    }, {
        'name': 'water point',
        'coordinates': [6.456571, 12.92105],
        '_version': 0,
        'properties': {
            'sector': 'water',
            'type': 'type unavailable',
            'grid_power': null,
            'improved_water_supply': null,
            'improved_sanitation': null,
            'visits': 0,
            'photoUrls': []
        },
        'identifiers': [],
        'updatedAt': '2014-12-04T21:54:37.177Z',
        'createdAt': '2014-12-04T21:54:37.177Z',
        'active': true,
        'href': 'http://staging.revisit.global/api/v0/facilities/5480d81d2ecfcf690844261a.json',
        'uuid': '5480d81d2ecfcf690844261a'
    }, {
        'name': 'water point',
        'coordinates': [6.458883, 12.92059],
        '_version': 0,
        'properties': {
            'sector': 'water',
            'type': 'type unavailable',
            'grid_power': null,
            'improved_water_supply': null,
            'improved_sanitation': null,
            'visits': 0,
            'photoUrls': []
        },
        'identifiers': [],
        'updatedAt': '2014-12-04T21:54:37.177Z',
        'createdAt': '2014-12-04T21:54:37.177Z',
        'active': true,
        'href': 'http://staging.revisit.global/api/v0/facilities/5480d81d2ecfcf6908442625.json',
        'uuid': '5480d81d2ecfcf6908442625'
    }, {
        'name': 'water point',
        'coordinates': [6.459097, 12.92074],
        '_version': 0,
        'properties': {
            'sector': 'water',
            'type': 'type unavailable',
            'grid_power': null,
            'improved_water_supply': null,
            'improved_sanitation': null,
            'visits': 0,
            'photoUrls': []
        },
        'identifiers': [],
        'updatedAt': '2014-12-04T21:54:37.177Z',
        'createdAt': '2014-12-04T21:54:37.177Z',
        'active': true,
        'href': 'http://staging.revisit.global/api/v0/facilities/5480d81d2ecfcf6908442607.json',
        'uuid': '5480d81d2ecfcf6908442607'
    }];

describe('FacilityRadios', () => {
    var FacilityRadios, callback;

    beforeEach(function() {
        jest.dontMock('../FacilityRadios.js');
        FacilityRadios = require('../FacilityRadios');
        callback = jest.genMockFunction();
    });

    it('renders no facilities message if no facilities passed', () => {
        var FacilityRadiosInstance = TestUtils.renderIntoDocument(
            <FacilityRadios facilities={[]} />
        );

        var message = TestUtils.findRenderedDOMComponentWithClass(FacilityRadiosInstance, 'content-padded');

        expect(message.textContent).toEqual('No nearby facilities located.');
    });

    it('renders facilities list', () => {
        var len = facilities.length;

        var FacilityRadiosInstance = TestUtils.renderIntoDocument(
            <FacilityRadios facilities={facilities} />
        );

        var facs = TestUtils.scryRenderedDOMComponentsWithClass(FacilityRadiosInstance, 'question__radio');

        expect(facs.length).toEqual(len);
    });

    it('calls selectFunction prop on facility click', () => {
        var FacilityRadiosInstance = TestUtils.renderIntoDocument(
            <FacilityRadios facilities={facilities} selectFunction={callback} />
        );

        var facs = TestUtils.scryRenderedDOMComponentsWithTag(FacilityRadiosInstance, 'input');


        TestUtils.Simulate.click(facs[0]);

        expect(callback).toBeCalled();
    });

    it('selects a facility when facility radio clicked', () => {
        var FacilityRadiosInstance = TestUtils.renderIntoDocument(
            <FacilityRadios facilities={facilities} selectFunction={callback} />
        );

        var facs = TestUtils.scryRenderedDOMComponentsWithTag(FacilityRadiosInstance, 'input');

        expect(facs[0].getAttribute('checked')).toBeNull();

        TestUtils.Simulate.click(facs[0], {
            target: facs[0]
        });

        facs = TestUtils.scryRenderedDOMComponentsWithTag(FacilityRadiosInstance, 'input');

        expect(facs[0].getAttribute('checked')).toBeDefined();

        TestUtils.Simulate.click(facs[0], {
            target: facs[0]
        });

        expect(facs[0].getAttribute('checked')).toBeNull();
    });

});
