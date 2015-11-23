import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';

// a noop function useful for passing into components that require it.
var noop = () => {};

describe('BigButton', () => {
    var BigButton;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/BigButton.js');
        BigButton = require('../../dokomoforms/static/src/survey/js/components/baseComponents/BigButton');
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

describe('LittleButton', () => {
    var LittleButton;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/LittleButton.js');
        LittleButton = require('../../dokomoforms/static/src/survey/js/components/baseComponents/LittleButton');
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

describe('Card', () => {
    var Card;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/Card.js');
        Card = require('../../dokomoforms/static/src/survey/js/components/baseComponents/Card');
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

describe('Message', () => {
    var Message;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/Message.js');
        Message = require('../../dokomoforms/static/src/survey/js/components/baseComponents/Message');
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

describe('Title', () => {
    var Title;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/Title.js');
        Title = require('../../dokomoforms/static/src/survey/js/components/baseComponents/Title');
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


describe('DontKnow', () => {
    var DontKnow;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/DontKnow.js');
        DontKnow = require('../../dokomoforms/static/src/survey/js/components/baseComponents/DontKnow');
    });

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
    var PhotoPreview;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview.js');
        PhotoPreview = require('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview');
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

describe('PhotoField', () => {
    var PhotoField;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoField.js');
        PhotoField = require('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoField');
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

        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview.js');
        var PhotoPreview = require('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview');

        var Photo = TestUtils.renderIntoDocument(
            <PhotoField />
        );

        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(Photo, 'photo_container')
        );

        TestUtils.findRenderedComponentWithType(Photo, PhotoPreview);
    });



    it('hides PhotoPreview on thumbnail click', () => {

        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview.js');
        var PhotoPreview = require('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview');

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

        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview.js');
        var PhotoPreview = require('../../dokomoforms/static/src/survey/js/components/baseComponents/PhotoPreview');

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

describe('ResponseField', () => {
    var ResponseField, callback, setCustomValidity;

    beforeEach(function() {
        jest.dontMock('../../dokomoforms/static/src/survey/js/components/baseComponents/ResponseField.js');
        ResponseField = require('../../dokomoforms/static/src/survey/js/components/baseComponents/ResponseField');
        callback = jest.genMockFunction();
        setCustomValidity = jest.genMockFunction();
    });

    it('renders a number input if prop type is integer', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='integer' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('number');

        // simulate input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 50
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a number input if prop type is decimal', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='decimal' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('number');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 50
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a datetime-local input if prop type is timestamp', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='timestamp' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('datetime-local');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 1238592847
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a time input if prop type is time', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='time' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 1238592847
                }
            }
        );

        expect(input.getAttribute('type')).toEqual('time');
    });

    it('renders a date input if prop type is date', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='date' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('date');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2013-01-01T00:00:00.000Z'
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders an email input if prop type is email', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='email' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('email');
    });

    it('renders a text input if prop type is not specified', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField type='' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        expect(input.getAttribute('type')).toEqual('text');

        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'onetwothree'
                }
            }
        );

        expect(setCustomValidity).toBeCalled();
    });

    it('renders a minus if prop showMinus is true', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField showMinus={true} buttonFunction={callback} />
        );

        // check that minus is rendered
        TestUtils.findRenderedDOMComponentWithClass(ResponseFieldInstance, 'question__minus');
    });

    it('calls buttonFunction when minus is clicked', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField showMinus={true} buttonFunction={callback} />
        );

        // click on minus
        TestUtils.Simulate.click(
            TestUtils.findRenderedDOMComponentWithClass(ResponseFieldInstance, 'question__minus')
        );

        // check that the delete method was called (which in turn calls buttonFunction prop)
        expect(callback).toBeCalled();
    });

    it('calls onInput prop via onChange when input changes', () => {
        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: noop,
                    value: 'a'
                }
            }
        );

        // check that the delete method was called (which in turn calls buttonFunction prop)
        expect(callback).toBeCalled();
    });

    it('validates non-numeric values in integer field', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='integer' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'a'
                }
            }
        );

        //  called once with empty string to clear, then again with invalid message
        expect(setCustomValidity.mock.calls[0][0]).toEqual('');
        expect(setCustomValidity.mock.calls[1][0]).toEqual('Invalid field.');
    });

    it('validates min and max values in integer field', () => {

        var logic = {
            min: 10,
            max: 20
        };

        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='integer' logic={logic} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate correct input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 15
                }
            }
        );

        // should be only called once if validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(1);

        // simulate bad min input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 5
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(3);

        // simulate bad max input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 25
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(5);
    });

    it('validates non-numeric values in decimal field', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='decimal' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'a'
                }
            }
        );

        //  called once with empty string to clear, then again with invalid message
        expect(setCustomValidity.mock.calls[0][0]).toEqual('');
        expect(setCustomValidity.mock.calls[1][0]).toEqual('Invalid field.');
    });

    it('validates min and max values in decimal field', () => {

        var logic = {
            min: 10,
            max: 20
        };

        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='decimal' logic={logic} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate correct input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 15
                }
            }
        );

        // should be only called once if validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(1);

        // simulate bad min input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 5
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(3);

        // simulate bad max input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 25
                }
            }
        );

        // should be called two more times when validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(5);
    });

    it('validates non-parseable date values in date field', () => {


        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='date' />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate changing input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: 'gibberish'
                }
            }
        );

        //  called once with empty string to clear, then again with invalid message
        expect(setCustomValidity.mock.calls[0][0]).toEqual('');
        expect(setCustomValidity.mock.calls[1][0]).toEqual('Invalid field.');
    });

    it('validates min and max values in date field', () => {

        var logic = {
            min: '2014-01-01T00:00:00.000Z',
            max: '2015-01-01T00:00:00.000Z'
        };

        var ResponseFieldInstance = TestUtils.renderIntoDocument(
            <ResponseField onInput={callback} type='decimal' logic={logic} />
        );

        var input = TestUtils.findRenderedDOMComponentWithTag(ResponseFieldInstance, 'input');

        // simulate correct input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2014-06-01T00:00:00.000Z'
                }
            }
        );

        // should be only called once if validation passes
        expect(setCustomValidity.mock.calls.length).toEqual(1);

        // simulate bad min input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2013-01-01T00:00:00.000Z'
                }
            }
        );

        // should be called two more times when validation doesn't pass
        expect(setCustomValidity.mock.calls.length).toEqual(3);

        // simulate bad max input
        TestUtils.Simulate.change(
            input,
            {
                target: {
                    setCustomValidity: setCustomValidity,
                    value: '2016-01-01T00:00:00.000Z'
                }
            }
        );

        // should be called two more times when validation doesn't pass
        expect(setCustomValidity.mock.calls.length).toEqual(5);
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
