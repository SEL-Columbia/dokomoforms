import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';

jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/BigButton.js');
jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/LittleButton.js');
jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/Card.js');
jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/Message.js');
jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/Title.js');
jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/DontKnow.js');
jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview.js');
jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoField.js');
// jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/Menu.js');

const BigButton = require('../../dokomoforms/static/src/survey/js/components/baseComponents/BigButton');
const LittleButton = require('../../dokomoforms/static/src/survey/js/components/baseComponents/LittleButton');
const Card = require('../../dokomoforms/static/src/survey/js/components/baseComponents/Card');
const Message = require('../../dokomoforms/static/src/survey/js/components/baseComponents/Message');
const Title = require('../../dokomoforms/static/src/survey/js/components/baseComponents/Title');
const DontKnow = require('../../dokomoforms/static/src/survey/js/components/baseComponents/DontKnow');
const PhotoPreview = require('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview');
const PhotoField = require('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoField');
// const Menu = require('../../dokomoforms/static/src/survey/js/components/baseComponents/Menu');

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('BigButton', () => {

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

describe('LittleButton', () => {

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

describe('Card', () => {

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

describe('Message', () => {

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

describe('Title', () => {

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


describe('DontKnow', () => {

    it('calls the checkBoxFunction property when pressed', () => {
        var callback = jest.genMockFunction();

        // Render a DontKnow in the document
        var dontKnow = TestUtils.renderIntoDocument(
            <DontKnow checkBoxFunction={callback} />
        );

        // Simulate click on button
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithTag(dontKnow, 'input')
        );

        // Verify that the callback was called once.
        expect(callback.mock.calls.length).toEqual(1);
    });

    it('is not checked by default', () => {
        // Render a DontKnow in the document
        var dontKnow = TestUtils.renderIntoDocument(
            <DontKnow checkBoxFunction={noop} />
        );

        // Get the rendered element
        var dontKnowNode = TestUtils.findRenderedDOMComponentWithTag(dontKnow, 'input');

        expect(dontKnowNode.defaultChecked).toEqual(false);
    });

    it('is checked by default when checked property is present', () => {
        // Render a DontKnow in the document
        var dontKnow = TestUtils.renderIntoDocument(
            <DontKnow checkBoxFunction={noop} checked={true} />
        );

        // Get the rendered element
        var dontKnowNode = TestUtils.findRenderedDOMComponentWithTag(dontKnow, 'input');

        expect(dontKnowNode.defaultChecked).toEqual(true);
    });
});

describe('PhotoPreview', () => {

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

describe('PhotoField', () => {
    var sr;

    beforeEach(function() {
        sr = TestUtils.createRenderer();
    });

    it('does not show preview by default', () => {

        // Render a DontKnow in the document
        sr.render(
            <PhotoField />
        );

        var result = sr.getRenderOutput();

        expect(result.type).toBe('span');

        console.log(result.props.children[1]);
        // expect(result.props.children).toEqual([

        // ]);
        // expect(preview.length).toEqual(0);
    });

    it('preview shown when showPreview prop is true', () => {

        // Render a DontKnow in the document
        var photo = TestUtils.renderIntoDocument(
            <PhotoField />
        );

        var preview = TestUtils.scryRenderedComponentsWithType(photo, 'PhotoPreview');

        expect(preview.length).toEqual(0);

        photo.setState({
            showPreview: true
        });

        jest.runAllTicks();

        TestUtils.findRenderedComponentWithType(photo, 'PhotoPreview');
    });
});

// describe('Menu', () => {
//     var survey = {
//             languages: ['English', 'French']
//         },
//         surveyId = 0,
//         db;
//     beforeEach(function() {
//         // Set up some mocked out file info before each test
//         db = require('pouchdb');
//     });

//     it('renders log out/in and revisit reload only when online', () => {
//         navigator.onLine = false;

//         var menu = TestUtils.renderIntoDocument(
//             <Menu
//                 language='English'
//                 survey={survey}
//                 surveyID={surveyId}
//                 db={db}
//                 loggedIn={false}
//                 hasFacilities={false}
//             />
//         );

//         var loginBtn = TestUtils.scryRenderedDOMComponentsWithClass(menu, 'menu_login');
//         var logoutBtn = TestUtils.scryRenderedDOMComponentsWithClass(menu, 'menu_logout');

//         expect(loginBtn.length).toEqual(0);
//         expect(logoutBtn.length).toEqual(0);

//     });

//     it('renders log out when user is logged in', () => {

//     });

//     it('renders log in when user is not logged in', () => {

//     });

//     it('calls logout function when logout is pressed', () => {

//     });

//     it('calls login function when login is pressed', () => {

//     });

// });
