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
var MultipleChoice = require('./components/MultipleChoice.js'); 
var Location = require('./components/Location.js'); 
var Facility = require('./components/Facility.js'); 
var Submit = require('./components/Submit.js'); 
var Splash = require('./components/Splash.js'); 

/* 
 * Create Single Page App with three main components
 * Header, Content, Footer
 */
var Application = React.createClass({
    getInitialState: function() {
        return { 
            showDontKnow: false,
            showDontKnowBox: false,
            nextQuestion: 0,
            states : {
                SPLASH : 1,
                QUESTION : 2,
                SUBMIT : 3,
            },
            state: 1,
        }
    },

    /*
     * Load next question, updates state of the Application
     * if next question is not found to either SPLASH/SUBMIT
     */
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
            showDontKnowBox: false,
            state: nextState
        })

    },

    /*
     * Load prev question, updates state of the Application
     * if prev question is not found to SPLASH
     */
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
            showDontKnowBox: false,
            state: nextState
        })

    },

    /*
     * Save active survey into unsynced array 
     */
    onSave: function() {
    },


    /*
     * Respond to don't know checkbox event, this is listend to by Application
     * due to app needing to resize for the increased height of the don't know
     * region
     */
    onCheckButton: function() {
        this.setState({
            showDontKnowBox: this.state.showDontKnowBox ? false: true,
        });
    },

    /*
     * Load the appropiate question based on the nextQuestion state
     * Loads splash or submit content if state is either SPLASH/SUBMIT 
     */
    getContent: function() {
        var questions = this.props.survey.nodes;
        var nextQuestion = this.state.nextQuestion;
        var state = this.state.state;
        var survey = this.props.survey;

        if (state === this.state.states.QUESTION) {
            var questionType = questions[nextQuestion].type_constraint;
            switch(questionType) {
                case 'multiple_choice':
                    return (
                            <MultipleChoice 
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                           />
                       )

                case 'location':
                    return (
                            <Location
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                           />
                       )
                case 'facility':
                    return (
                            <Facility
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                           />
                       )
                default:
                    return (
                            <Question 
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                           />
                       )
            }
        } else if (state === this.state.states.SUBMIT) {
            return (
                    <Submit
                        surveyID={survey.id}
                        language={survey.default_language}
                    />
                   )
        } else {
            return (
                    <Splash 
                        surveyID={survey.id}
                        language={survey.default_language}
                    />
                   )
        }
    },

    /*
     * Load the appropiate title based on the nextQuestion and state
     */
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

    /*
     * Load the appropiate 'hint' based on the nextQuestion and state
     */
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

    /*
     * Load the appropiate text in the Footer's button based on state
     */
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
        var questionID = questions[nextQuestion] && questions[nextQuestion].id 
            || this.state.state;


        // Alter the height of content based on DontKnow state
        if (this.state.showDontKnow) 
            contentClasses += " content-shrunk";

        if (this.state.showDontKnowBox) 
            contentClasses += " content-shrunk content-super-shrunk";

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
                        showDontKnow={this.state.showDontKnow} 
                        showDontKnowBox={this.state.showDontKnowBox} 
                        buttonFunction={this.onNextButton}
                        checkBoxFunction={this.onCheckButton}
                        buttonType={state === this.state.states.QUESTION 
                            ? 'btn-primary': 'btn-positive'}
                        buttonText={this.getButtonText()}
                        questionID={questionID}
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
