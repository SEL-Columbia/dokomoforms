var React = require('react');

var ResponseField = require('./baseComponents/ResponseField.js');
var ResponseFields = require('./baseComponents/ResponseFields.js');
var LittleButton = require('./baseComponents/LittleButton.js');

module.exports = React.createClass({
    getInitialState: function() {
        return { 
            questionCount: 1
        }
    },

    addNewInput: function() {
        this.setState({
            questionCount: this.state.questionCount + 1
        })
    },

    removeInput: function() {
        if (!(this.state.questionCount > 1))
            return;

        this.setState({
            questionCount: this.state.questionCount - 1
        })
    },

    onInput: function(element, value) {
        console.log("Got input", element, value);
    },

    render: function() {
        return (
                <span>
                <ResponseFields buttonFunction={this.removeInput}
                    type={this.props.questionType}
                    onInput={this.onInput}
                    childCount={this.state.questionCount} />

                {this.props.question.allow_multiple
                    ? <LittleButton buttonFunction={this.addNewInput}
                        text={'add another answer'} />
                    : null 
                }
                </span>
               )
    }
});
