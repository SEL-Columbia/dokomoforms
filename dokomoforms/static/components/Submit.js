var React = require('react');
var Card = require('./baseComponents/Card.js');

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

    render: function() {
        return (
                <Card messages={["hey", "how you doing", 
                    ["i ", <b>love</b>, " toast"]]} type={"message-error"}/>
               )
    }
});
