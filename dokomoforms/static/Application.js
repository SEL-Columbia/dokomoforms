var React = require('react');
var $ = require('jquery');
var PouchDB  = require('pouchdb');
PouchDB.plugin(require('pouchdb-upsert'));

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

var Header = require('./components/Header.js');
var Footer = require('./components/Footer.js');
var Question = require('./components/Question.js'); 
var Note = require('./components/Note.js'); 

var MultipleChoice = require('./components/MultipleChoice.js'); 
var Photo = require('./components/Photo.js'); 
var Location = require('./components/Location.js'); 
var Facility = require('./components/Facility.js'); 
var Submit = require('./components/Submit.js'); 
var Splash = require('./components/Splash.js'); 

var PhotoAPI = require('./PhotoAPI.js');
var FacilityTree = require('./Facilities.js');

/* 
 * Create Single Page App with three main components
 * Header, Content, Footer
 */
var Application = React.createClass({
    getInitialState: function() {
        var trees = {};
        window.trees = trees;
        var nyc = {lat: 40.80690, lng:-73.96536}
        window.nyc = nyc;
        
        var surveyDB = new PouchDB(this.props.survey.id, {
                    'auto_compation': true,
        });

        this.props.survey.nodes.forEach(function(node) {
            if (node.type_constraint === 'facility') {
                console.log(node.logic);
                console.log(node);
                trees[node.id] = new FacilityTree(
                        parseFloat(node.logic.nlat), 
                        parseFloat(node.logic.wlng), 
                        parseFloat(node.logic.slat), 
                        parseFloat(node.logic.elng),
                        surveyDB);
            }
        });

        window.surveyDB = surveyDB;

        return { 
            showDontKnow: false,
            showDontKnowBox: false,
            nextQuestion: -1,
            states : {
                SPLASH : 1,
                QUESTION : 2,
                SUBMIT : 3,
            },
            state: 1,
            trees: trees,
            db: surveyDB
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
        var showDontKnowBox = false;

        if (nextQuestion > -1 && nextQuestion < numQuestions) { 
            nextState = this.state.states.QUESTION;
            showDontKnow = questions[nextQuestion].allow_dont_know
        }

        if (nextQuestion == numQuestions) {
            nextState = this.state.states.SUBMIT
        }

        if (nextQuestion > numQuestions) {
            nextQuestion = -1
            nextState = this.state.states.SPLASH
            this.onSave();
        }

        if (this.state.states.QUESTION === nextState && showDontKnow) {
            var questionID = questions[nextQuestion].id;
            var response = this.refs.footer.getAnswer(questionID);
            console.log("Footer response:", response);
            showDontKnowBox = Boolean(response);
        }

        this.setState({
            nextQuestion: nextQuestion,
            showDontKnow: showDontKnow,
            showDontKnowBox: showDontKnowBox,
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
        var showDontKnowBox = false;
        
        if (nextQuestion < numQuestions && nextQuestion > 0) {
            nextState = this.state.states.QUESTION;
            showDontKnow = questions[nextQuestion].allow_dont_know
        }

        if (nextQuestion <= -1) { 
            nextState = this.state.states.SPLASH;
            nextQuestion = -1;
        }

        if (this.state.states.QUESTION === nextState && showDontKnow) {
            var questionID = questions[nextQuestion].id;
            var response = this.refs.footer.getAnswer(questionID);
            console.log("Footer response:", response);
            showDontKnowBox = Boolean(response);
        }

        this.setState({
            nextQuestion: nextQuestion,
            showDontKnow: showDontKnow,
            showDontKnowBox: showDontKnowBox,
            state: nextState
        })

    },

    /*
     * Save active survey into unsynced array 
     */
    onSave: function() {
        var survey = JSON.parse(localStorage[this.props.survey.id] || '{}');
        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.survey.id] || [];
        // Get array of unsynced photo id's for given survey
        var unsynced_photos = JSON.parse(localStorage['unsynced_photos'] || '[]');

        // Build new submission
        var answers = []; 
        var self = this;
        this.props.survey.nodes.forEach(function(question) {
            var responses = survey[question.id] || [];
            responses.forEach(function(response) {

                if (question.type_constraint === 'photo') {
                   unsynced_photos.push({
                       'surveyID': self.props.survey.id,
                       'photoID': response.response,
                       'questionID': question.id
                   });
                }

                answers.push({
                    survey_node_id: question.id,
                    response: response,
                    type_constraint: question.type_constraint
                });
            });

        });

        // Don't record it if there are no answers, will mess up splash 
        if (answers.length === 0) {
            return;
        }

        var submission = {
            submitter_name: localStorage['submitter_name'] || "anon",
            submitter_email: localStorage['submitter_email'] || "anon@anon.org",
            submission_type: "unauthenticated", //XXX 
            survey_id: this.props.survey.id,
            answers: answers,
            save_time: new Date().toISOString(),
            submission_time: "" // For comparisions during submit ajax callback
        }

        console.log("Submission", submission);

        // Record new submission into array
        unsynced_submissions.push(submission);
        unsynced_surveys[this.props.survey.id] = unsynced_submissions;
        localStorage['unsynced'] = JSON.stringify(unsynced_surveys);

        // Store photos 
        localStorage['unsynced_photos'] = JSON.stringify(unsynced_photos);

        // Wipe active survey
        localStorage[this.props.survey.id] = JSON.stringify({});

        // Wipe location info
        localStorage['location'] = JSON.stringify({});
    },

    /*
     * Loop through unsynced submissions for active survey and POST
     * Only modifies localStorage on success
     */
    onSubmit: function() {
        function getCookie(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        }
        
        var self = this;

        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.survey.id] || [];
        // Get all unsynced photos.
        var unsynced_photos = JSON.parse(localStorage['unsynced_photos'] || '[]');

        unsynced_submissions.forEach(function(survey) {
            // Update submit time
            survey.submission_time = new Date().toISOString();
            $.ajax({
                url: '/api/v0/surveys/'+survey.survey_id+'/submit',
                type: 'POST',
                contentType: 'application/json',
                processData: false,
                data: JSON.stringify(survey),
                headers: {
                    "X-XSRFToken": getCookie("_xsrf")
                },
                dataType: 'json',
                success: function(survey, anything, hey) {
                    console.log("success", anything, hey);
                    // Get all unsynced surveys
                    var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
                    // Get array of unsynced submissions to this survey
                    var unsynced_submissions = unsynced_surveys[survey.survey_id] || [];

                    // Find unsynced_submission
                    var idx = -1;
                    unsynced_submissions.forEach(function(usurvey, i) {
                        if (Date(usurvey.save_time) === Date(survey.save_time)) {
                            idx = i;
                            return false;
                        }
                        return true;
                    });

                    // Not sure what happened, do not update localStorage
                    if (idx === -1) 
                        return;

                    console.log(idx, unsynced_submissions.length);
                    unsynced_submissions.splice(idx, 1);

                    unsynced_surveys[survey.survey_id] = unsynced_submissions;
                    localStorage['unsynced'] = JSON.stringify(unsynced_surveys);

                    // Update splash page if still on it
                    if (self.state.state === self.state.states.SPLASH)
                        self.refs.splash.update();
                },

                error: function(err) {
                    console.log("Failed to post survey", err, survey);
                }
            });

            console.log('synced submission:', survey);
            console.log('survey', '/api/v0/surveys/'+survey.survey_id+'/submit');
        });

        unsynced_photos.forEach(function(photo, idx) {
            if (photo.surveyID === self.props.survey.id) {
                PhotoAPI.getBase64(self.state.db, photo.photoID, function(err, base64){
                    $.ajax({
                        url: '/api/v0/photos',
                        type: 'POST',
                        contentType: 'application/json',
                        processData: false,
                        data: JSON.stringify({
                            'id' : photo.photoID,
                            'mime_type': 'image/png',
                            'image': base64
                        }),
                        headers: {
                            "X-XSRFToken": getCookie("_xsrf")
                        },
                        dataType: 'json',
                        success: function(photo) {
                            console.log("Photo success:", photo);
                            var unsynced_photos = JSON.parse(localStorage['unsynced_photos'] || '[]');

                            // Find photo
                            var idx = -1;
                            unsynced_photos.forEach(function(uphoto, i) {
                                if (uphoto.photoID === photo.id) {
                                    idx = i;
                                    PhotoAPI.removePhoto(self.state.db, uphoto.photoID, function(err, result) {
                                        if (err) {
                                            console.log("Couldnt remove from db:", err);
                                            return;
                                        }

                                        console.log("Removed:", result);
                                    });
                                    return false;
                                }
                                return true;
                            });

                            // What??
                            if (idx === -1)
                                return;

                            console.log(idx, unsynced_photos.length);
                            unsynced_photos.splice(idx, 1);

                            localStorage['unsynced_photos'] = JSON.stringify(unsynced_photos);
                        },

                        error: function(err) {
                            console.log("Failed to post photo:", err, photo);
                        }
                    });
                });
            }
        });
    },


    /*
     * Respond to don't know checkbox event, this is listend to by Application
     * due to app needing to resize for the increased height of the don't know
     * region
     */
    onCheckButton: function() {
        this.setState({
            showDontKnowBox: this.state.showDontKnowBox ? false: true,
            showDontKnow: this.state.showDontKnow,
            state: this.state.state,
            nextQuestion: this.state.nextQuestion,
        });

        // Force questions to update
        if (this.state.state = this.state.states.QUESTION)
            this.refs.question.update();

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
                                ref="question"
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                       )
                case 'photo':
                    return (
                            <Photo
                                ref="question"
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                                db={this.state.db}
                           />
                       )

                case 'location':
                    return (
                            <Location
                                ref="question"
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                       )
                case 'facility':
                    return (
                            <Facility
                                ref="question"
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                                db={this.state.db}
                                tree={this.state.trees[questions[nextQuestion].id]}
                           />
                       )
                case 'note':
                    return (
                            <Note
                                ref="question"
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                       )
                default:
                    return (
                            <Question 
                                ref="question"
                                key={nextQuestion} 
                                question={questions[nextQuestion]} 
                                questionType={questionType}
                                language={survey.default_language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                       )
            }
        } else if (state === this.state.states.SUBMIT) {
            return (
                    <Submit
                        ref="submit"
                        surveyID={survey.id}
                        language={survey.default_language}
                    />
                   )
        } else {
            return (
                    <Splash 
                        ref="splash"
                        surveyID={survey.id}
                        surveyTitle={survey.title}
                        language={survey.default_language}
                        buttonFunction={this.onSubmit}
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
        var surveyID = this.props.survey.id;
        var questionID = questions[nextQuestion] && questions[nextQuestion].id 
            || this.state.state;


        // Alter the height of content based on DontKnow state
        if (this.state.showDontKnow) 
            contentClasses += " content-shrunk";

        if (this.state.showDontKnowBox) 
            contentClasses += " content-shrunk content-super-shrunk";

        return (
                <div id="wrapper">
                    <Header 
                        ref="header"
                        buttonFunction={this.onPrevButton} 
                        number={nextQuestion + 1}
                        total={questions.length + 1}
                        db={this.state.db}
                        surveyID={surveyID}
                        splash={state === this.state.states.SPLASH}/>
                    <div 
                        className={contentClasses}>
                        <Title title={this.getTitle()} message={this.getMessage()} />
                        {this.getContent()}
                    </div>
                    <Footer 
                        ref="footer"
                        showDontKnow={this.state.showDontKnow} 
                        showDontKnowBox={this.state.showDontKnowBox} 
                        buttonFunction={this.onNextButton}
                        checkBoxFunction={this.onCheckButton}
                        buttonType={state === this.state.states.QUESTION 
                            ? 'btn-primary': 'btn-positive'}
                        buttonText={this.getButtonText()}
                        questionID={questionID}
                        surveyID={surveyID}
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
