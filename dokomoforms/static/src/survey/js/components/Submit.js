var React = require('react'),
    createReactClass = require('create-react-class');
var Card = require('./baseComponents/Card.js');
var Message = require('./baseComponents/Message.js');
var ResponseField = require('./baseComponents/ResponseField.js');

/*
 * Submit page component
 * Renders the appropiate card and buttons for the submit page
 *
 * props:
 *     @language: current survey language
 *     @surveyID: current survey id
 */
module.exports = createReactClass({

    onInput: function(value, index) {
        if (index === 0) {
            localStorage['submitter_name'] = value;
        } else {
            localStorage['submitter_email'] = value;
        }

    },

    render: function() {
        var self = this,
            name = localStorage['submitter_name'],
            email = localStorage['submitter_email'],
            logged_in = this.props.loggedIn,
            message;

        if (logged_in) {
            message = <Message text={'You are logged in as:'} />;
        } else {
            message = <Message text={'Please enter your name and email id:'} />;
        }

        return (
            <span>

                {message}

                <ResponseField
                    onInput={self.onInput}
                    type={'text'}
                    key={'name'}
                    placeholder={"Enumerator Name"}
                    index={0}
                    // disabled={logged_in}
                    initValue={name}
                    showMinus={false}
                />

                <ResponseField
                    onInput={self.onInput}
                    type={'email'}
                    key={'email'}
                    placeholder={"Enumerator Email"}
                    index={1}
                    // disabled={logged_in}
                    initValue={email}
                    showMinus={false}
                />

                <Card messages={['Saved surveys must be uploaded when you next have network connectivity.']}
                    type={'message-primary'}/>

            </span>
       );
    }
});
