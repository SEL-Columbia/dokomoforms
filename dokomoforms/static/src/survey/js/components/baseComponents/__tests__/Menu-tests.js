import 'raf/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-dom/test-utils';

// jest.autoMockOff();

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('Menu', () => {
    var Menu;

    beforeEach(function() {
        jest.dontMock('../Menu.js');
        Menu = require('../Menu');
    });

    it('does nothing', () => {

    });

    // it('renders log out/in and revisit reload only when online', () => {

    // });

    // it('renders log out when user is logged in', () => {

    // });

    // it('renders log in when user is not logged in', () => {

    // });

    // it('calls logout function when logout is pressed', () => {

    // });

    // it('calls login function when login is pressed', () => {

    // });

});
