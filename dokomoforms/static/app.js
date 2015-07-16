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
        console.log("heyt");
        var nextQuestion = this.state.nextQuestion + 1;
        var nextState = this.state.state;
        var numQuestions = this.props.survey.nodes.length;

        if (nextQuestion > 0)  
            nextState = this.state.states.QUESTION;

        if (nextQuestion >= numQuestions) {
            nextQuestion = numQuestions
            nextState = this.state.states.SUBMIT
        }

        this.setState({
            nextQuestion: nextQuestion,
            state: nextState
        })

    },

    onPrevButton: function() {
        console.log("heyt");
        var nextQuestion = this.state.nextQuestion - 1;
        var nextState = this.state.state;
        var numQuestions = this.props.survey.nodes.length;
        
        if (nextQuestion < numQuestions)
            nextState = this.state.states.QUESTION;

        if (nextQuestion <= 0) { 
            nextState = this.state.states.SPLASH;
            nextQuestion = 0;
        }


        this.setState({
            nextQuestion: nextQuestion,
            state: nextState
        })

    },

    getContent: function(question) {
        var state = this.state.state;
        if (state === this.state.states.QUESTION) {
           return (
                   <Question allowMultiple={question.allow_multiple} 
                            questionType={question.type_constraint}
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

    render: function() {
        var contentClasses = "content";
        var questions = this.props.survey.nodes;
        var state = this.state.state;
        var nextQuestion = this.state.nextQuestion;

        if (state === this.state.states.QUESTION && this.state.showDontKnow) 
            contentClasses += " content-shrunk";

        return (
                <div id="wrapper">
                    <Header buttonFunction={this.onPrevButton} 
                        splash={state === this.state.states.SPLASH}/>
                    <div className={contentClasses}>
                        <Title />
                        {this.getContent(questions[nextQuestion])}
                    </div>
                    <Footer showDontKnow={
                        state == this.state.states.QUESTION && this.state.showDontKnow
                    } buttonFunction={this.onNextButton}/>

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
