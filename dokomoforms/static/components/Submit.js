var React = require('react');
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
module.exports = React.createClass({
    getInitialState: function() {
        return { 
        }
    },

    onInput: function(value, index) {
        if (index === 0) {
            localStorage['submitter_name'] = value;
        } else {
            localStorage['submitter_email'] = value;
        }

    },

    render: function() {
        var self = this;
        return (
                <span>
                
                <Message text={'Enter your name and email id'} />
                <ResponseField 
                    onInput={self.onInput}
                    type={'text'}
                    key={'name'} 
                    placeholder={"Enumerator Name"}
                    index={0} 
                    initValue={localStorage['submitter_name']} 
                    showMinus={false}
                />

                <ResponseField 
                    onInput={self.onInput}
                    type={'email'}
                    key={'email'} 
                    placeholder={"Enumerator Email"}
                    index={1} 
                    initValue={localStorage['submitter_email']} 
                    showMinus={false}
                />

                <Card messages={["Saved surveys must be uploaded when you next have network connectivity."]} 
                    type={"message-primary"}/>

                </span>
               )
    }
});
