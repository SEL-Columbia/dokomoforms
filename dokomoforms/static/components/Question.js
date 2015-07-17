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

    render: function() {
        return (
                <span>
                <ResponseFields buttonFunction={this.removeInput}
                    type={this.props.questionType}
                    childCount={this.state.questionCount} />

                <div className="content-padded">
                    {this.props.question.allowMultiple
                        ? <LittleButton buttonFunction={this.addNewInput}
                            text={'add another answer'} />
                        : null 
                    }
                </div>
                </span>
               )
    }
});
