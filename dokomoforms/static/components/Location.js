var React = require('react');

var ResponseField = require('./baseComponents/ResponseField.js');
var ResponseFields = require('./baseComponents/ResponseFields.js');
var LittleButton = require('./baseComponents/LittleButton.js');

/*
 * Location question component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 */
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

    render: function() {
        return (
                <span>
                <LittleButton buttonFunction={this.addNewInput}
                    iconClass={'icon-star'}
                    text={'find my location'} />
                <ResponseFields buttonFunction={this.removeInput}
                    type={this.props.questionType}
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
