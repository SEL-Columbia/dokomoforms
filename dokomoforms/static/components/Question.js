var React = require('react');

var ResponseField = require('./baseComponents/ResponseField.js');
var LittleButton = require('./baseComponents/LittleButton.js');

module.exports = React.createClass({
    getInitialState: function() {
        var answers = localStorage[this.props.question.id] || '[{}]';
        answers = JSON.parse(answers);
        console.log("Answer length is:", answers.length, answers);

        return { 
            questionCount: answers.length,
        }
    },

    addNewInput: function() {
        var answers = localStorage[this.props.question.id] || '[{}]';
        answers = JSON.parse(answers);

        if (answers.length == this.state.questionCount) {
          this.setState({
              questionCount: this.state.questionCount + 1
          })
        }
    },

    removeInput: function(index) {
        console.log("Remove", index);

        if (!(this.state.questionCount > 1))
            return;

        var answers = localStorage[this.props.question.id] || '[]';
        answers = JSON.parse(answers);
        answers.splice(index, 1);
        localStorage[this.props.question.id] = JSON.stringify(answers);

        this.setState({
            questionCount: this.state.questionCount - 1
        })

        this.forceUpdate();
    },

    onInput: function(index, value) {
        console.log("Hey", index, value);
        var answers = localStorage[this.props.question.id] || '[]';
        answers = JSON.parse(answers);
        answers[index] = {
            'response': value, 
            'response_type': this.props.questionType
        };

        localStorage[this.props.question.id] = JSON.stringify(answers);

    },

    getAnswer: function(index) {
        console.log("In:", index);
        var answers = localStorage[this.props.question.id] || '[]';
        answers = JSON.parse(answers);
        console.log(answers, index);
        return answers[index] && answers[index].response || null;
    },

    render: function() {
        var children = Array.apply(null, {length: this.state.questionCount})
        var self = this;
        return (
                <span>
                {children.map(function(child, idx) {
                    return (
                            <ResponseField 
                                buttonFunction={self.removeInput}
                                onInput={self.onInput}
                                type={self.props.questionType}
                                key={Math.random()} 
                                index={idx} 
                                initValue={self.getAnswer(idx)} 
                                showMinus={self.state.questionCount > 1}
                            />
                           )
                })}
                {this.props.question.allow_multiple
                    ? <LittleButton buttonFunction={this.addNewInput}
                        text={'add another answer'} />
                    : null 
                }
                </span>
               )
    }
});
