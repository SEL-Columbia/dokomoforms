var React = require('react');
var Select = require('./baseComponents/Select.js');

/*
 * Multiple choice question component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 *     @disabled: boolean for disabling all inputs
 */
module.exports = React.createClass({
    getInitialState: function() {
        return { 
        }
    },

    render: function() {
        var self = this;
        var choices = this.props.question.choices.map(function(choice) {
            return { 
                'value': choice.choice_id, 
                'text': choice.choice_text[self.props.language] 
            }
        });

        return (<Select 
                    choices={choices}
                    withOther={this.props.question.allow_other}
                    multiSelect={this.props.question.allow_multiple}
                />)
    }
});
