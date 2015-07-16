var React = require('react');

var ResponseField = require('./components/baseComponents/ResponseField.js');
var ResponseFields = require('./components/baseComponents/ResponseFields.js');
var BigButton = require('./components/baseComponents/BigButton.js');
var LittleButton = require('./components/baseComponents/LittleButton.js');
var DontKnow = require('./components/baseComponents/DontKnow.js');

var Title = require('./components/baseComponents/Title.js');
var Card = require('./components/baseComponents/Card.js');
var Select = require('./components/baseComponents/Select.js');
var FacilityRadios = require('./components/baseComponents/FacilityRadios.js');
var Message = require('./components/baseComponents/Message.js');

var Header = require('./components/baseComponents/Header.js');
var Footer = require('./components/baseComponents/Footer.js');

var Question = require('./components/Question.js'); 

var Application = React.createClass({
    getInitialState: function() {
        return { 
            showDontKnow: false,
            nextQuestion: 0,
            states : {
                SPLASH : 1,
                QUESTION : 2,
                SUBMIT : 3,
            },
            state: 1,
        }
    },

    onNextButton: function() {
        var questions = this.props.survey.nodes;
        var nextQuestion = this.state.nextQuestion + 1;
        var nextState = this.state.state;
        var numQuestions = this.props.survey.nodes.length;
        var showDontKnow = false;

        if (nextQuestion > 0 && nextQuestion < numQuestions) { 
            nextState = this.state.states.QUESTION;
            showDontKnow = questions[nextQuestion].allow_dont_know
        }

        if (nextQuestion == numQuestions) {
            nextState = this.state.states.SUBMIT
        }

        if (nextQuestion > numQuestions) {
            nextQuestion = 0
            nextState = this.state.states.SPLASH
        }


        this.setState({
            nextQuestion: nextQuestion,
            showDontKnow: showDontKnow,
            state: nextState
        })

    },

    onPrevButton: function() {
        var questions = this.props.survey.nodes;
        var nextQuestion = this.state.nextQuestion - 1;
        var nextState = this.state.state;
        var numQuestions = this.props.survey.nodes.length;
        var showDontKnow = false;
        
        if (nextQuestion < numQuestions && nextQuestion > 0) {
            nextState = this.state.states.QUESTION;
            showDontKnow = questions[nextQuestion].allow_dont_know
        }

        if (nextQuestion <= 0) { 
            nextState = this.state.states.SPLASH;
            nextQuestion = 0;
        }

        this.setState({
            nextQuestion: nextQuestion,
            showDontKnow: showDontKnow,
            state: nextState
        })

    },

    getContent: function() {
        var questions = this.props.survey.nodes;
        var nextQuestion = this.state.nextQuestion;
        var state = this.state.state;
        if (state === this.state.states.QUESTION) {
            return (
                   <Question key={nextQuestion} allowMultiple={questions[nextQuestion].allow_multiple} 
                            questionType={questions[nextQuestion].type_constraint}
                   />
               )
        } else if (state === this.state.states.SUBMIT) {
            return (
                    <Card messages={["hey", "how you doing", 
                        ["i ", <b>love</b>, " toast"]]} type={"message-error"}/>
                   )
        } else {
            return (
                    <Card messages={["i guess you do", 
                        [<b>love</b>], "toast"]} type={"message-primary"}/>
                   )
        }
    },

    getTitle: function() {
        var questions = this.props.survey.nodes;
        var survey = this.props.survey;
        var nextQuestion = this.state.nextQuestion;
        var state = this.state.state;

        if (state === this.state.states.QUESTION) {
            return questions[nextQuestion].title[survey.default_language] 
        } else if (state === this.state.states.SUBMIT) {
            return "Ready to Save?"
        } else {
            return survey.title[survey.default_language] 
        }
    },

    getMessage: function() {
        var questions = this.props.survey.nodes;
        var survey = this.props.survey;
        var nextQuestion = this.state.nextQuestion;
        var state = this.state.state;

        if (state === this.state.states.QUESTION) {
            return questions[nextQuestion].hint[survey.default_language] 
        } else if (state === this.state.states.SUBMIT) {
            return "If youre satisfied with the answers to all the questions, you can save the survey now."
        } else {
            return "version " + survey.version + " | last updated " + survey.last_updated_time;
        }
    },

    getButtonText: function() {
        var state = this.state.state;
        if (state === this.state.states.QUESTION) {
            return "Next Question";
        } else if (state === this.state.states.SUBMIT) {
            return "Save Survey"
        } else {
            return "Begin a New Survey"
        }
    },

    render: function() {
        var contentClasses = "content";
        var state = this.state.state;
        var nextQuestion = this.state.nextQuestion;
        var questions = this.props.survey.nodes;

        if (state === this.state.states.QUESTION && this.state.showDontKnow) 
            contentClasses += " content-shrunk";

        return (
                <div id="wrapper">
                    <Header buttonFunction={this.onPrevButton} 
                        number={nextQuestion}
                        total={questions.length}
                        splash={state === this.state.states.SPLASH}/>
                    <div className={contentClasses}>
                        <Title title={this.getTitle()} message={this.getMessage()} />
                        {this.getContent()}
                    </div>
                    <Footer 
                        showDontKnow={state === this.state.states.QUESTION 
                            && this.state.showDontKnow} 
                        buttonFunction={this.onNextButton}
                        buttonType={state === this.state.states.QUESTION 
                            ? 'btn-primary': 'btn-positive'}
                        buttonText={this.getButtonText()}
                     />

                </div>
               )
    }
});

init = function(survey) {
    React.render(
            <Application survey={survey}/>,
            document.body
    );
};
