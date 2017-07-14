// vendor
import $ from 'jquery';
import React from 'react';
import moment from 'moment';
import PouchDB from 'pouchdb';
import ps from '../../common/js/pubsub';
import cookies from '../../common/js/cookies';
import uuid from 'node-uuid';

// pouch plugin
// PouchDB.plugin(require('pouchdb-upsert'));

// components
import Title from './components/baseComponents/Title';
import Header from './components/Header';
import Footer from './components/Footer';
import Question from './components/Question';
import Note from './components/Note';
import MultipleChoice from './components/MultipleChoice';
import Photo from './components/Photo';
import Location from './components/Location';
import Facility from './components/Facility';
import Submit from './components/Submit';
import Splash from './components/Splash';
import Loading from './components/Loading';

    // api services
import PhotoAPI from './api/PhotoAPI';
import FacilityTree from './api/FacilityAPI';

/*
 * Create Single Page App with three main components
 * Header, Content, Footer
 */

var utils = function(){
    var counter = 0;
    counter++;
    return "_" + counter.toString();
}

class Application extends React.Component {

    constructor(props){
        super(props);

        this.buildTrees = this.buildTrees.bind(this);
        this.onSurveyStart = this.onSurveyStart.bind(this);
        this.onNextButton = this.onNextButton.bind(this);
        this.onPrevButton = this.onPrevButton.bind(this);
        this.inBucket = this.inBucket.bind(this);
        this.cloneNode = this.cloneNode.bind(this);
        this.onSave = this.onSave.bind(this);
        this.onSubmit = this.onSubmit.bind(this);
        this.onCheckButton = this.onCheckButton.bind(this);
        this.getContent = this.getContent.bind(this);
        this.getTitle = this.getTitle.bind(this);
        this.getMessage = this.getMessage.bind(this);
        this.getButtonText = this.getButtonText.bind(this);

        this.state = {
            showDontKnow: false,
            showDontKnowBox: false,
            head: null,
            question: null,
            headStack: [], //XXX Stack of linked list heads
            states: {
                LOADING: 0,
                SPLASH: 1,
                QUESTION: 2,
                SUBMIT: 3
            },
            language: null,
            state: 0,
            trees: {},
            loggedIn: null,
            hasFacilities: null,
            db: null
        }
    }

    // getInitialState: function() {
    //     // Set up db for photos and facility tree
    //     // var trees = {};
    //     // var surveyDB = new PouchDB(this.props.survey.id, {
    //     //     'auto_compaction': true
    //     // });

    //     // loading state, unless there are no facility nodes
    //     // var init_state = 0;

    //     // window.surveyDB = surveyDB;

    //     // Build initial linked list
    //     var questions = this.props.survey.nodes;
    //     // var first_question = null;
    //     questions.forEach(function(node, idx) {
    //         var question = node;
    //         question.id = question.id;
    //         question.prev = null;
    //         question.next = null;
    //         if (idx > 0) {
    //             question.prev = questions[idx - 1];
    //         }

    //         if (idx < questions.length - 1) {
    //             question.next = questions[idx + 1];
    //         }

    //         if (idx === 0) {
    //             first_question = question;
    //         }

    //     });

    //     this.questions = questions;

    //     // // Recursively construct trees
    //     // var has_facility_node = this.buildTrees(questions, trees);

    //     // if (!has_facility_node) {
    //     //     init_state = 1;
    //     // }

    //     // set default lang -- use user pref stored in localStorage,
    //     // falling back to survey default if the user pref is not available
    //     // for this survey
    //     var language = this.props.survey.default_language;
    //     if (localStorage['default_language']
    //         && this.props.survey.languages.indexOf(localStorage['default_language']) !== -1) {
    //         language = localStorage['default_language'];
    //     }

    //     // user stuff
    //     var logged_in = window.CURRENT_USER !== undefined;
    //     if (logged_in) {
    //         localStorage['submitter_name'] = window.CURRENT_USER.name;
    //         localStorage['submitter_email'] = window.CURRENT_USER.email;
    //     }

    //     // return {
    //     //     showDontKnow: false,
    //     //     showDontKnowBox: false,
    //     //     head: first_question,
    //     //     question: null,
    //     //     headStack: [], //XXX Stack of linked list heads
    //     //     states: {
    //     //         LOADING: 0,
    //     //         SPLASH: 1,
    //     //         QUESTION: 2,
    //     //         SUBMIT: 3
    //     //     },
    //     //     language: language,
    //     //     state: init_state,
    //     //     trees: trees,
    //     //     loggedIn: logged_in,
    //     //     hasFacilities: null,
    //     //     db: surveyDB
    //     // };
    // },

    componentWillMount() {
        // Set up db for photos and facility tree
        // var trees = {};

        var self = this;

        var surveyDB = new PouchDB(this.props.survey.id, {
            'auto_compaction': true
        });

        window.surveyDB = surveyDB;


        // Build initial linked list
        var questions = self.props.survey.nodes;
        var first_question = null;
        questions.forEach(function(node, idx) {
            var question = node;
            question.id = question.id;
            question.prev = null;
            question.next = null;
            if (idx > 0) {
                question.prev = questions[idx - 1];
            }

            if (idx < questions.length - 1) {
                question.next = questions[idx + 1];
            }

            if (idx === 0) {
                first_question = question;
            }

        });

        self.questions = questions;

        var language = self.props.survey.default_language;
        if (localStorage['default_language']
            && self.props.survey.languages.indexOf(localStorage['default_language']) !== -1) {
            language = localStorage['default_language'];
        }

        // user stuff
        var logged_in = window.CURRENT_USER !== undefined;
        if (logged_in) {
            localStorage['submitter_name'] = window.CURRENT_USER.name;
            localStorage['submitter_email'] = window.CURRENT_USER.email;
        }

        // /////////

        // ps.subscribe('loading:progress', function() {
        //     // unused as of this moment, since we can't know the content-length
        //     // due to gzipping.
        // });

        console.log('right before')

        ps.subscribe('loading:complete', function() {
            console.log('LOADING COMPLETE');
        });

        // ps.subscribe('settings:language_changed', function(e, lang) {
        //     self.setState({
        //         language: lang
        //     }, function(){
        //         localStorage['default_language'] = lang;
        //         console.log('lang state', self.state)
        //     });
        // });

        // // handle revisit:reload_facilities event by flushing existing facilities
        // // and refreshing page.
        // ps.subscribe('revisit:reload_facilities', function() {
        //     localStorage.removeItem('facilities');
        //     window.location.reload();
        // });

        self.setState({
            state: 1,
            head: first_question,
            language: language,
            loggedIn: logged_in,
            db: surveyDB
        }, function(){
            console.log('state set', this.footer)
        })
    }

    componentDidMount() {
        // Recursively construct trees
        var has_facility_node = this.buildTrees(this.questions, this.state.trees);
        var state = has_facility_node ? 0 : 1;

        if (!has_facility_node) {
            this.setState({
                state: 1
            });
        } else {
            this.setState({
                hasFacilities: true
            });
        }

        console.log('did mount', this.state)


    }

    /*
     * Create Facility Tree object at node id for every facility tree question
     * Recurse into subnodes if found
     *
     * @questions: all nodes at current sub level
     * @trees: dictionary of question ids and facility trees
     *
     * NOTE: facility trees update exact same location in pouchdb (based on bounds of coordinates)
     * i.e: Multiple trees with same bounds do not increase memory usage (network usage does increase though)
     */
    buildTrees(questions, trees) {
        var self = this;
        var has_facility_node = false;
        var questions = questions || [];

        questions.forEach(function(node) {
            if (node.type_constraint === 'facility') {
                has_facility_node = true;
                trees[node.id] = new FacilityTree(
                    parseFloat(node.logic.nlat),
                    parseFloat(node.logic.wlng),
                    parseFloat(node.logic.slat),
                    parseFloat(node.logic.elng),
                    window.surveyDB,
                    node.id
                );
            }

            if (node.sub_surveys) {
                node.sub_surveys.forEach(function(subs) {
                    has_facility_node = self.buildTrees(subs.nodes, trees);
                });
            }
        });

        return has_facility_node;
    }

    /**
     * Sets the start time on the survey, to be saved with submission.
     */
    onSurveyStart() {
        console.log('onSurveyStart -- setting start_time');
        var surveyID = this.props.survey.id;
        var survey = JSON.parse(localStorage[surveyID] || '{}');
        survey.start_time = new Date().toISOString();
        localStorage[surveyID] = JSON.stringify(survey);
    }

    /*
     * Load next question, updates state of the Application
     * if next question is not found move to either SPLASH/SUBMIT
     *
     * Deals with branching, required and setting up dontknow footer state
     * Uses refs! (Could be removed)
     */
    onNextButton() {
        console.log('next button')
        let self = this;
        let surveyID = this.props.survey.id;
        let currentState = this.state.state;
        let currentQuestion = this.state.question;

        // Set up next state
        let nextQuestion = null;
        let showDontKnow = false;
        let showDontKnowBox = false;
        let state = this.state.states.SPLASH;
        let head = this.state.head;
        let headStack = this.state.headStack;

        let questionID;

        console.log('Current Question', this.state);

        switch (currentState) {
            case this.state.states.LOADING:
                console.log('states dot loading')
                nextQuestion = null;
                showDontKnow = false;
                showDontKnowBox = false;
                state = this.state.states.LOADING;
                //XXX Fire Modal for submitting here
                this.onSave();

                // Reset Survey Linked List
                head = this.state.headStack[0] || head;
                console.log('head', head)
                console.log('headstack', this.state.headStack)
                while (head.prev) {
                    head = head.prev;
                }
                console.log('moved past')
                headStack = [];
                break;
            // On Submit page and next was pressed
            case this.state.states.SUBMIT:
                nextQuestion = null;
                showDontKnow = false;
                showDontKnowBox = false;
                state = this.state.states.SPLASH;
                //XXX Fire Modal for submitting here
                this.onSave();

                // Reset Survey Linked List
                head = this.state.headStack[0] || head;
                while (head.prev) {
                    head = head.prev;
                }
                headStack = [];
                break;

            // On Splash page and next was pressed
            case this.state.states.SPLASH:

            console.log('state splash');

                nextQuestion = this.state.head;
                showDontKnow = nextQuestion.allow_dont_know || false;
                showDontKnowBox = false;
                state = this.state.states.QUESTION;

                this.onSurveyStart();

                questionID = nextQuestion.id;
                if (showDontKnow) {
                    var response = this.footer.getAnswer(questionID);
                    console.log('Footer response:', response);
                    showDontKnowBox = Boolean(response);
                }

                break;

            case this.state.states.QUESTION:
                // Look into active answers, check if any filled out if question is REQUIRED
                var required = currentQuestion.required || false,
                    survey,
                    answers;

                if (required) {
                    questionID = currentQuestion.id;
                    survey = JSON.parse(localStorage[surveyID] || '{}');
                    answers = (survey[questionID] || []).filter(function(response) {
                        return (response && response.response !== null);
                    });

                    if (!answers.length) {
                        alert('Valid response is required.');
                        return;
                    }
                }

                // Get answer
                questionID = currentQuestion.id;
                survey = JSON.parse(localStorage[surveyID] || '{}');
                answers = (survey[questionID] || []).filter(function(response) {
                    return (response && response.response !== null);
                });

                console.log('answers 1', answers)

                // XXX Confirm response type is answer (instead of dont-know/other)
                var answer = answers.length && answers[0].response || null;
                var sub_surveys = currentQuestion.sub_surveys;

                // If has subsurveys then it can branch
                if (sub_surveys) {
                    console.log('Subsurveys:', currentQuestion.id, currentQuestion, sub_surveys);
                    console.log('Answer:', answer);


                    /////////
                    var answerResponse;
                    if (currentQuestion.type_constraint=="integer") {
                        answerResponse = answers[0].response;
                    } else if (currentQuestion.type_constraint=="text" ||
                        currentQuestion.type_constraint=="multiple_choice") {
                        console.log('text answer', answers.length)
                        answerResponse = answers.length;

                    } else {
                        answerResponse = 1;
                    }

                    var text_answers = answers;
                    /////////

                    // Check which subsurvey this answer buckets into
                    var BREAK = false;
                    // get the original length of the sub-survey before repeats are added
                    
                    sub_surveys.forEach(function(sub) {
                        // get the original sub node length before repetitions are added
                        if (!sub.original_length) sub.original_length = sub.nodes.length;

                        console.log('original', sub.original_length)

                        if (BREAK) {
                            return;
                        }
                        console.log('Bucket:', sub.buckets, 'Type:', currentQuestion.type_constraint);

                        // Append all subsurveys to clone of current question, update head, update headStack if in bucket
                        var inBee = self.inBucket(sub.buckets, currentQuestion.type_constraint, answer);

                        console.log('inbee', inBee)
                        

                        // a repeatable question wont have buckets
                        if ((!sub.buckets.length) || inBee) {
                            // Clone current element
                            var clone = self.cloneNode(currentQuestion);
                            var temp = clone.next;

                        ////////////

                            var original_length = sub.original_length;

                            console.log('original again', original_length)

                            var ids = {};

                            // list is the list of reptitions. It's appended on to the original nodes list later
                            var list = [];

                            var currentResponse = answerResponse*original_length;
                            let repetitions = 0;

                            // check if the answer(s) to the question require reptitions
                            // OR if the answer(s) to the question have been changed and require added repetitions
                            if (currentResponse==sub.nodes.length) {
                                console.log('the same', currentResponse, sub.nodes.length);
                            } else {
                                console.log('not equal', currentResponse, original_length, sub.nodes.length)
                                repetitions = ((currentResponse-sub.nodes.length)/original_length)
                                console.log(repetitions)
                            }

                            
                            if (repetitions!=0) {
                                var copiedNode,
                                    augmentedId
                                ;
                                if (repetitions>0) {
                                    for (var e = 0; e < repetitions; e++) {
                                        for (var p = 0; p < original_length; p++) {
                                            copiedNode = Object.assign({}, sub.nodes[p]);
                                            console.log('copiednode', sub.nodes[p])
                                            augmentedId = utils();
                                            // temporariy append the ID. it needs to be unique for each question
                                            console.log('augmented', augmentedId)
                                            copiedNode.id = copiedNode.id + augmentedId;
                                            console.log('list', list)
                                            list.push(copiedNode)

                                        }
                                    }

                                    sub.nodes = sub.nodes.concat(list);
                                    list = [];

                                    console.log('length', sub.nodes.length)
                                    sub.nodes.forEach(function(node){
                                        console.log('after', node.id)
                                    })

                                    console.log('copied list length', list.length);
                                    console.log('node length', sub.nodes.length)


                                } else if (repetitions<0) {
                                    // this may happen if the enumerator goes back
                                    // and changes the initial answer to the question
                                    let removed = repetitions * original_length;
                                    sub.nodes.splice(removed)
                                    console.log('removed', removed, repetitions)
                                    console.log('sub.nodes', sub.nodes)
                                }

                            }


                            console.log('subnodes', sub.nodes)

                            // let j = 0;
                            // let k = 1;
                            // let m = 1;
                            // if (currentQuestion.type_constraint=="integer") {
                            //     sub.nodes.forEach(function(node){
                            //         node.answerText = m.toString();
                            //         m++;
                            //     });
                            // } else {

                            //     sub.nodes.forEach(function(node, i){
                            //         // if (k > original_length) {
                            //         //     j++;
                            //         //     if (j > original_length) return;
                            //         //     k = 1;
                            //         // }
                            //         // console.log('j', j, original_length)
                            //         // if (text_answers[j]) {
                            //         //     node.answerText = text_answers[j].response;
                            //         // }
                            //         // console.log(node.answerText);
                            //         // k++;
                            //         // console.log('k', k)
                            //         console.log('function', node.id, i)
                            //         node.answerText = text_answers[i].response;
                            //     })

                            // }

                            // link sub nodes
                            // TODO: Deal with repeatable flag here!
                            // XXX: When adding repeat questions make sure to augment the question.id in a repeatable and unique way
                            // XXX: QuestionIDs are used to distinguish/remember questions everywhere, do not reuse IDs!
                            for (var i = 0; i < sub.nodes.length; i++) {
                                if (i === 0) {
                                    clone.next = sub.nodes[i];
                                    sub.nodes[i].prev = clone;
                                } else {
                                    sub.nodes[i].prev = sub.nodes[i - 1];
                                }

                                if (i === sub.nodes.length - 1) {
                                    sub.nodes[i].next = temp;
                                    if (temp)
                                        temp.prev = sub.nodes[i];
                                } else {
                                    sub.nodes[i].next = sub.nodes[i + 1];
                                }
                            }


                            // Always add branchable questions previous state into headStack
                            // This is how we can revert alterations to a branched question
                            headStack.push(currentQuestion);

                            // Find the head
                            var newHead = clone;
                            while (newHead.prev) {
                                newHead = newHead.prev;
                            }
                            head = newHead;

                            // Set current question to CLONE always
                            currentQuestion = clone;

                            BREAK = true; // break
                        }
                    })

                }

                nextQuestion = currentQuestion.next;
                state = this.state.states.QUESTION;

                // Set the state to SUBMIT when reach the end of questions
                if (nextQuestion === null) {
                    nextQuestion = currentQuestion; //Keep track of tail
                    showDontKnow = false;
                    showDontKnowBox = false;
                    state = this.state.states.SUBMIT;
                    break;
                }

                // Moving into a valid question
                showDontKnow = nextQuestion.allow_dont_know || false;
                showDontKnowBox = false;
                questionID = nextQuestion.id;

                if (showDontKnow) {
                    response = this.footer.getAnswer(questionID);
                    console.log('Footer response:', response);
                    showDontKnowBox = Boolean(response);
                }

                break;

        }

        this.setState({
            question: nextQuestion,
            showDontKnow: showDontKnow,
            showDontKnowBox: showDontKnowBox,
            head: head,
            headStack: headStack,
            state: state
        });

        return;

    }

    /*
     * Load prev question, updates state of the Application
     * if prev question is not found to SPLASH
     */
    onPrevButton() {
        var currentState = this.state.state;
        var currentQuestion = this.state.question;

        // Set up next state
        var nextQuestion = null;
        var showDontKnow = false;
        var showDontKnowBox = false;
        var state = this.state.states.SPLASH;
        var head = this.state.head;
        var headStack = this.state.headStack,
            sub_surveys,
            newHead,
            questionID,
            response;

        switch (currentState) {
            // On Submit page and prev was pressed
            case this.state.states.SUBMIT:
                nextQuestion = currentQuestion; // Tail was saved in current question

                // Branching ONLY happens when moving BACK into branchable question
                // Rare but can happen on question that either leads to submit or more questions
                sub_surveys = nextQuestion.sub_surveys;
                if (sub_surveys && headStack.length) {
                    // If he's in the branched stack, pop em off
                    if (headStack[headStack.length - 1].id === nextQuestion.id) {
                        console.log('RESETING', nextQuestion.id, headStack.length);
                        // Reset the nextQuestion to previously unbranched state
                        nextQuestion = headStack.pop();
                        console.log('RESET', nextQuestion.id, headStack.length);
                        // Find the head
                        newHead = nextQuestion;
                        while (newHead.prev) {
                            newHead = newHead.prev;
                        }
                        head = newHead;
                    }
                }


                showDontKnow = currentQuestion.allow_dont_know || false;
                showDontKnowBox = false;
                state = this.state.states.QUESTION;

                questionID = currentQuestion.id;
                if (showDontKnow) {
                    response = this.footer.getAnswer(questionID);
                    console.log('Footer response:', response);
                    showDontKnowBox = Boolean(response);
                }
                break;

                // On Splash page and prev was pressed (IMPOSSIBLE)
            case this.state.states.SPLASH:
                nextQuestion = null;
                showDontKnowBox = false;
                showDontKnow = false;
                state = this.state.states.SPLASH;
                break;

            case this.state.states.QUESTION:
                nextQuestion = currentQuestion.prev;
                state = this.state.states.QUESTION;

                // Set the state to SUBMIT when reach the end of questions
                if (nextQuestion === null) {
                    nextQuestion = currentQuestion;
                    showDontKnow = false;
                    showDontKnowBox = false;
                    state = this.state.states.SPLASH;
                    break;
                }

                // Branching ONLY happens when moving BACK into branchable question
                // ALWAYS undo branched state to maintain survey consitency
                sub_surveys = nextQuestion.sub_surveys;
                if (sub_surveys && headStack.length) {
                    // If he's in the branched stack, pop em off
                    if (headStack[headStack.length - 1].id === nextQuestion.id) {
                        console.log('RESETING', nextQuestion.id, headStack.length);
                        // Reset the nextQuestion to previously unbranched state
                        nextQuestion = headStack.pop();
                        console.log('RESET', nextQuestion.id, headStack.length);
                        // Find the head
                        newHead = nextQuestion;
                        while (newHead.prev) {
                            newHead = newHead.prev;
                        }
                        head = newHead;
                    }
                }


                // Moving into a valid question
                showDontKnow = nextQuestion.allow_dont_know || false;
                showDontKnowBox = false;
                questionID = nextQuestion.id;

                if (showDontKnow) {
                    response = this.footer.getAnswer(questionID);
                    console.log('Footer response:', response);
                    showDontKnowBox = Boolean(response);
                }

                break;

        }

        this.setState({
            question: nextQuestion,
            showDontKnow: showDontKnow,
            showDontKnowBox: showDontKnowBox,
            head: head,
            headStack: headStack,
            state: state
        });

        return;

    }

    /*
     * Check if response is in bucket
     *
     * @buckets: Array of buckets (can be ranges in [num,num) form or 'qid' for mc
     * @type: type of bucket
     * @resposne: answer to check if in bucket
     */
    inBucket(buckets, type, response) {
        var leftLim,
            rightLim,
            inBee,
            BREAK;

        if (response === null)
            return false;

        switch (type) {
            case 'integer':
            case 'decimal':
                inBee = 1; // Innocent untill proven guilty
                // Split bucket into four sections, confirm that value in range, otherwise set inBee to false
                BREAK = false;
                buckets.forEach(function(bucket) {
                    if (BREAK) {
                        return;
                    }
                    inBee = 1;
                    var left = bucket.split(',')[0];
                    var right = bucket.split(',')[1];
                    if (left[0] === '[') {
                        leftLim = parseFloat(left.split('[')[1]);
                        console.log('Inclusive Left', leftLim);
                        if (!isNaN(leftLim)) // Infinity doesnt need to be checked
                            inBee &= (response >= leftLim);
                    } else if (left[0] === '(') {
                        leftLim = parseFloat(left.split('(')[1]);
                        console.log('Exclusive Left', leftLim);
                        if (!isNaN(leftLim)) // Infinity doesnt need to be checked
                            inBee &= (response > leftLim);
                    } else {
                        inBee = 0;
                    }

                    if (right[right.length - 1] === ']') {
                        rightLim = parseFloat(right.split(']')[0]);
                        console.log('Inclusive Right', rightLim);
                        if (!isNaN(rightLim)) // Infinity doesnt need to be checked
                            inBee &= (response <= rightLim);
                    } else if (right[right.length - 1] === ')') {
                        rightLim = parseFloat(right.split(')')[0]);
                        console.log('Exclusive Right', rightLim);
                        if (!isNaN(rightLim)) // Infinity doesnt need to be checked
                            inBee &= (response < rightLim);
                    } else {
                        inBee = 0; // unknown
                    }

                    console.log('Bucket:', bucket, response, inBee);
                    if (inBee) {
                        BREAK = true; //break
                    }

                });

                return inBee;

            case 'timestamp': // TODO: We need moment.js for this to work properly
            case 'date':
                inBee = 1; // Innocent untill proven guilty
                response = new Date(response); // Convert to date object for comparisons
                BREAK = false;
                buckets.forEach(function(bucket) {
                    inBee = 1;
                    if (BREAK) {
                        return;
                    }
                    var left = bucket.split(',')[0];
                    var right = bucket.split(',')[1];
                    if (left[0] === '[') {
                        console.log('Inclusive Left');
                        leftLim = new Date(left.split('[')[1].replace(/\s/, 'T'));
                        if (!isNaN(leftLim)) // Infinity doesnt need to be checked
                            inBee &= (response >= leftLim);
                    } else if (left[0] === '(') {
                        console.log('Exclusive Left');
                        leftLim = new Date(left.split('(')[1].replace(/\s/, 'T'));
                        if (!isNaN(leftLim)) // Infinity doesnt need to be checked
                            inBee &= (response > leftLim);
                    } else {
                        inBee = 0;
                    }

                    if (right[right.length - 1] === ']') {
                        console.log('Inclusive Right');
                        rightLim = new Date(right.split(']')[0].replace(/\s/, 'T'));
                        if (!isNaN(rightLim)) // Infinity doesnt need to be checked
                            inBee &= (response <= rightLim);
                    } else if (right[right.length - 1] === ')') {
                        console.log('Exclusive Right');
                        rightLim = new Date(right.split(')')[0].replace(/\s/, 'T'));
                        if (!isNaN(rightLim)) // Infinity doesnt need to be checked
                            inBee &= (response < rightLim);
                    } else {
                        inBee = 0; // unknown
                    }

                    console.log('Bucket:', bucket, response, inBee);
                    if (inBee) {
                        BREAK = true; //break
                    }

                    return true;
                });

                return inBee;
            case 'multiple_choice':
                inBee = 0;
                buckets.forEach(function(bucket) {
                    inBee |= (bucket === response);
                    console.log('Bucket:', bucket, response, inBee);
                });
                return inBee;
            default:
                return false;

        }
    }

    /*
     * Clone linked list node, arrays don't need to be cloned, only next/prev ptrs
     * @node: Current node to clone
     * @ids: Dictionay reference of currently cloned nodes, prevents recursion going on forever
     */
    cloneNode(node, ids) {
        var self = this;
        var clone = {
            next: null,
            prev: null
        };

        ids = ids || {};

        Object.keys(node).forEach(function(key) {
            if (key !== 'next' && key !== 'prev') {
                clone[key] = node[key];
            }
        });

        // Mutable so next/prev pointers will be visible to all nodes that reference this dictionary
        ids[node.id] = clone;

        if (node.next) {
            var next = ids[node.next.id];
            clone.next = next || self.cloneNode(node.next, ids);
        }

        if (node.prev) {
            var prev = ids[node.prev.id];
            clone.prev = prev || self.cloneNode(node.prev, ids);
        }

        return clone;
    }

    /*
     * Save active survey into unsynced array
     */
    onSave() {
        var survey = JSON.parse(localStorage[this.props.survey.id] || '{}');
        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.survey.id] || [];
        // Get array of unsynced photo id's
        var unsynced_photos = JSON.parse(localStorage['unsynced_photos'] || '[]');
        // Get array of unsynced facilities
        var unsynced_facilities = JSON.parse(localStorage['unsynced_facilities'] || '[]');

        // Build new submission
        var answers = [];
        var self = this;

        // Copy active questions into simple list;
        var questions = [];
        var head = this.state.head;
        while (head) {
            questions.push(head);
            head = head.next;
        }

        questions.forEach(function(question) {
            var responses = survey[question.id] || [];
            responses.forEach(function(response) {
                // Ignore empty responses
                if (!response || response.response === null) {
                    return true; // continue;
                }

                // Photos need to synced independently from survey
                if (question.type_constraint === 'photo') {
                    unsynced_photos.push({
                        'surveyID': self.props.survey.id,
                        'photoID': response.response,
                        'questionID': question.id
                    });
                }

                // New facilities need to be stored seperatly from survey
                if (question.type_constraint === 'facility') {
                    if (response.metadata && response.metadata.is_new) {
                        console.log('Facility:', response);

                        // if self.state.trees.[question.id] exists, the compressed data from Revisit
                        // was successfully downloaded initially
                        var in_tree = false;
                        var tree = self.state.trees[question.id];
                        if (tree && tree.root) {
                            self.state.trees[question.id]
                                .addFacility(response.response.lat, response.response.lng, response.response);
                            in_tree = true;
                        } else {
                            console.log('Question ' + question.id + '\'s tree does not have a facility root node.');
                        }

                        unsynced_facilities.push({
                            'surveyID': self.props.survey.id,
                            'facilityData': response.response,
                            'questionID': question.id,
                            'in_tree': in_tree
                        });
                    }
                }

                if (question.id.length > 36) question.id = question.id.substring(question.id, question.id.indexOf('_'));

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
            submitter_name: localStorage['submitter_name'] || 'anon',
            submitter_email: localStorage['submitter_email'] || 'anon@anon.org',
            survey_id: this.props.survey.id,
            answers: answers,
            start_time: survey.start_time || null,
            save_time: new Date().toISOString(),
            submission_time: '' // For comparisions during submit ajax callback
        };

        console.log('Submission', submission);

        // Record new submission into array
        unsynced_submissions.push(submission);
        unsynced_surveys[this.props.survey.id] = unsynced_submissions;
        localStorage['unsynced'] = JSON.stringify(unsynced_surveys);

        // Store photos
        localStorage['unsynced_photos'] = JSON.stringify(unsynced_photos);

        // Store facilities
        localStorage['unsynced_facilities'] = JSON.stringify(unsynced_facilities);

        // Wipe active survey
        localStorage[this.props.survey.id] = JSON.stringify({});

        // Wipe location info
        localStorage['location'] = JSON.stringify({});

    }

    /*
     * Loop through unsynced submissions for active survey and POST
     * Only modifies localStorage on success
     */
    onSubmit() {
        var self = this;

        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.survey.id] || [];
        // Get all unsynced photos.
        var unsynced_photos = JSON.parse(localStorage['unsynced_photos'] || '[]');
        // Get all unsynced facilities
        var unsynced_facilities = JSON.parse(localStorage['unsynced_facilities'] || '[]');


        // Post surveys to Dokomoforms
        unsynced_submissions.forEach(function(survey) {

            var test = JSON.stringify(survey)
            console.log('test', test)
            console.log('survey!!!!', survey)


            // Update submit time
            survey.submission_time = new Date().toISOString();
            $.ajax({
                url: '/api/v0/surveys/' + survey.survey_id + '/submit',
                type: 'POST',
                contentType: 'application/json',
                processData: false,
                data: JSON.stringify(survey),
                headers: {
                    'X-XSRFToken': cookies.getCookie('_xsrf')
                },
                dataType: 'json',
                success: function(survey, anything, hey) {
                    console.log('success', anything, hey);
                    // Get all unsynced surveys
                    var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
                    // Get array of unsynced submissions to this survey
                    var unsynced_submissions = unsynced_surveys[survey.survey_id] || [];

                    // Find unsynced_submission
                    var idx = -1;
                    unsynced_submissions.forEach(function(usurvey, i) {
                        if (Date(usurvey.save_time) === Date(survey.save_time)) {
                            idx = i;
                        }
                    });

                    // Not sure what happened, do not update localStorage
                    if (idx === -1)
                        return;

                    unsynced_submissions.splice(idx, 1);

                    unsynced_surveys[survey.survey_id] = unsynced_submissions;
                    localStorage['unsynced'] = JSON.stringify(unsynced_surveys);

                    // Update splash page if still on it
                    if (self.state.state === self.state.states.SPLASH)
                        self.splash.update();
                },

                error: function(err) {
                    console.log('Failed to post survey', err, survey);
                }
            });

            console.log('synced submission:', survey);
            console.log('survey', '/api/v0/surveys/' + survey.survey_id + '/submit');
        });

        // Post photos to dokomoforms
        unsynced_photos.forEach(function(photo) {
            if (photo.surveyID === self.props.survey.id) {
                PhotoAPI.getBase64(self.state.db, photo.photoID, function(err, base64) {
                    $.ajax({
                        url: '/api/v0/photos',
                        type: 'POST',
                        contentType: 'application/json',
                        processData: false,
                        data: JSON.stringify({
                            'id': photo.photoID,
                            'mime_type': 'image/png',
                            'image': base64
                        }),
                        headers: {
                            'X-XSRFToken': cookies.getCookie('_xsrf')
                        },
                        dataType: 'json',
                        success: function(photo) {
                            console.log('Photo success:', photo);
                            var unsynced_photos = JSON.parse(localStorage['unsynced_photos'] || '[]');
                            // Find photo
                            var idx = -1;
                            unsynced_photos.forEach(function(uphoto, i) {
                                if (uphoto.photoID === photo.id) {
                                    idx = i;
                                    PhotoAPI.removePhoto(self.state.db, uphoto.photoID, function(err, result) {
                                        if (err) {
                                            console.log('Couldnt remove from db:', err);
                                            return;
                                        }
                                        console.log('Removed:', result);
                                    });
                                }
                            });

                            // What??
                            if (idx === -1)
                                return;

                            console.log(idx, unsynced_photos.length);
                            unsynced_photos.splice(idx, 1);

                            localStorage['unsynced_photos'] = JSON.stringify(unsynced_photos);
                        },

                        error: function(err) {
                            console.log('Failed to post photo:', err, photo);
                        }
                    });
                });
            }
        });

        // Post facilities to Revisit
        unsynced_facilities.forEach(function(facility) {
            if (facility.surveyID === self.props.survey.id) {
                self.state.trees[facility.questionID].postFacility(facility.facilityData,
                    // Success
                    function(revisitFacility) {
                        console.log('Successfully posted facility', revisitFacility, facility);
                        var unsynced_facilities = JSON.parse(localStorage['unsynced_facilities'] || '[]');

                        // Find facility
                        var idx = -1;
                        console.log(idx, unsynced_facilities.length);
                        unsynced_facilities.forEach(function(ufacility, i) {
                            var ufacilityID = ufacility.facilityData.facility_id;
                            var facilityID = facility.facilityData.facility_id;
                            if (ufacilityID === facilityID) {
                                idx = i;
                            }
                        });

                        // What??
                        if (idx === -1)
                            return;

                        console.log(idx, unsynced_facilities.length);
                        unsynced_facilities.splice(idx, 1);

                        localStorage['unsynced_facilities'] = JSON.stringify(unsynced_facilities);
                    },

                    // Error
                    function(err, facility) {
                        console.log('Failed to post facility', err, facility);
                    }
                );
            }
        });
    }


    /*
     * Respond to don't know checkbox event, this is listend to by Application
     * due to app needing to resize for the increased height of the don't know
     * region
     */
    onCheckButton() {
        this.setState({
            showDontKnowBox: this.state.showDontKnowBox ? false : true,
            showDontKnow: this.state.showDontKnow
        });

        // Force questions to update
        if (this.state.state === this.state.states.QUESTION) {
            console.log('trying to update')
            this.question.update();
        }

    }

    /*
     * Load the appropiate question based on the nextQuestion state
     * Loads splash or submit content if state is either SPLASH/SUBMIT
     */
    getContent() {
        var question = this.state.question;
        var state = this.state.state;
        var survey = this.props.survey;

        if (state === this.state.states.QUESTION) {
            var questionID = question.id;
            var questionType = question.type_constraint;
            switch (questionType) {
                case 'multiple_choice':
                    return (
                        <MultipleChoice
                                ref={(c)=>{this.question = c}}
                                key={questionID}
                                question={question}
                                questionType={questionType}
                                language={this.state.language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                    );
                case 'photo':
                    return (
                        <Photo
                                ref={(c)=>{this.question = c}}
                                key={questionID}
                                question={question}
                                questionType={questionType}
                                language={this.state.language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                                db={this.state.db}
                           />
                    );

                case 'location':
                    return (
                        <Location
                                ref={(c)=>{this.question = c}}
                                key={questionID}
                                question={question}
                                questionType={questionType}
                                language={this.state.language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                    );
                case 'facility':
                    return (
                        <Facility
                                ref={(c)=>{this.question = c}}
                                key={questionID}
                                question={question}
                                questionType={questionType}
                                language={this.state.language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                                db={this.state.db}
                                tree={this.state.trees[questionID]}
                           />
                    );
                case 'note':
                    return (
                        <Note
                                // ref={(c)=>{this.question = c}}
                                key={questionID}
                                question={question}
                                questionType={questionType}
                                language={this.state.language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                    );
                default:
                    return (
                        <Question
                                ref={(c)=>{this.question = c}}
                                key={questionID}
                                question={question}
                                questionType={questionType}
                                language={this.state.language}
                                surveyID={survey.id}
                                disabled={this.state.showDontKnowBox}
                           />
                    );
            }
        } else if (state === this.state.states.SUBMIT) {
            return (
                <Submit
                        // ref={(c)=>{this.submit = c}}
                        surveyID={survey.id}
                        loggedIn={this.state.loggedIn}
                        language={this.state.language}
                    />
            );
        } else {
            return (
                <Splash
                        // ref={(c)=>{this.splash = c}}
                        surveyID={survey.id}
                        surveyTitle={survey.title}
                        language={this.state.language}
                        buttonFunction={this.onSubmit}
                    />
            );
        }
    }

    /*
     * Load the appropiate title based on the question and state
     */
    getTitle() {
        var survey = this.props.survey;
        var question = this.state.question;
        var state = this.state.state;

        console.log('title', question)
        if (state === this.state.states.QUESTION) {
            if (question.number) {
                return question.number + ".  " + question.title[this.state.language];
            }
            return question.title[this.state.language];
        } else if (state === this.state.states.SUBMIT) {
            return 'Ready to Save?';
        } else {
            return survey.title[this.state.language];
        }
    }

    /*
     * Load the appropiate 'hint' based on the question and state
     */
    getMessage() {
        var survey = this.props.survey;
        var question = this.state.question;
        var state = this.state.state;

        if (state === this.state.states.QUESTION) {
            console.log('hint section', question)
            // if (question.answerText) {
            //     return question.hint[this.state.language] + " (" + question.answerText + ")";
            // }
            return question.hint[this.state.language];
        } else if (state === this.state.states.SUBMIT) {
            return 'If you are satisfied with the answers to all the questions, you can save the survey now.';
        } else {
            return 'version ' + survey.version + ' | last updated ' + moment(survey.last_update_time).format('lll');
        }
    }

    /*
     * Load the appropiate text in the Footer's button based on state
     */
    getButtonText() {
        var state = this.state.state;
        if (state === this.state.states.QUESTION) {
            return 'Next Question';
        } else if (state === this.state.states.SUBMIT) {
            return 'Save Survey';
        } else {
            return 'Begin a New Survey';
        }
    }

    renderx(){
        return(<div></div>)
    }

    render() {
        console.log('render state?', this.onNextButton)
        var contentClasses = 'content';
        var state = this.state.state;
        var question = this.state.question;
        var questionID = question && question.id || -1;
        var surveyID = this.props.survey.id;

        // Get current length of survey and question number
        var number = -1;
        var length = 0;
        var head = this.state.head;
        var loading = null;
        while (head) {
            if (head.id === questionID) {
                number = length;
            }

            head = head.next;
            length++;
        }


        // Alter the height of content based on DontKnow state
        if (this.state.showDontKnow) {
            contentClasses += ' content-shrunk';
        }

        if (this.state.showDontKnowBox) {
            contentClasses += ' content-shrunk content-super-shrunk';
        }
        console.log('this.state.state: ', this.state.state, this.state.states.LOADING);
        if (this.state.state === this.state.states.LOADING) {
            console.log('loading!');
            loading = <Loading message="Please be patient while facility data is downloaded."/>;
        }
        return (
            <div id='wrapper'>
                {loading}
                <Header
                    ref={()=>{}}
                    buttonFunction={this.onPrevButton}
                    number={number + 1}
                    total={length + 1}
                    db={this.state.db}
                    surveyID={surveyID}
                    survey={this.props.survey}
                    language={this.state.language}
                    loggedIn={this.state.loggedIn}
                    hasFacilities={this.state.hasFacilities}
                    splash={state === this.state.states.SPLASH}/>
                <div
                    className={contentClasses}>
                    <Title title={this.getTitle()} message={this.getMessage()} />
                    {this.getContent()}
                </div>
                <Footer
                    ref={(c)=>{this.footer = c}}
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
        );
    }
};

module.exports = Application;
