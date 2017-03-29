import React from 'react';
import Card from './baseComponents/Card.js';
import Message from './baseComponents/Message.js';
import ResponseField from './baseComponents/ResponseField.js';

/*
 * Submit page component
 * Renders the appropiate card and buttons for the submit page
 *
 * props:
 *     @language: current survey language
 *     @surveyID: current survey id
 */
export default function(props) {

    function onInput(value, index) {
        if (index === 0) {
            localStorage['submitter_name'] = value;
        } else {
            localStorage['submitter_email'] = value;
        }
    }

    // let self = this;
    const name = localStorage['submitter_name'];
    const email = localStorage['submitter_email'];
    const logged_in = props.loggedIn;
    let message;

    if (logged_in) {
        message = <Message text={'You are logged in as:'} />;
    } else {
        message = <Message text={'Please enter your name and email id:'} />;
    }

    return (
        <span>

            {message}

            <ResponseField
                onInput={onInput}
                type={'text'}
                key={'name'}
                placeholder={"Enumerator Name"}
                index={0}
                // disabled={logged_in}
                initValue={name}
                showMinus={false}
            />

            <ResponseField
                onInput={onInput}
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
};
