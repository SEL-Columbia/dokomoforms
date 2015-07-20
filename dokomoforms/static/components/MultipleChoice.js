var React = require('react');
var Select = require('./baseComponents/Select.js');

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
