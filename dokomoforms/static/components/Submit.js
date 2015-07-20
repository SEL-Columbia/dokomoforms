var React = require('react');
var Card = require('./baseComponents/Card.js');

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
