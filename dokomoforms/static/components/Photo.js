var React = require('react');

var PhotoField = require('./baseComponents/PhotoField.js');
var LittleButton = require('./baseComponents/LittleButton.js');
var $ = require('jquery');

                //XXX use this: navigator.vibrate(50);
/*
 * Location question component
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
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length === 0 ? 1 : answers.length;

        var camera = null;
        var src = null;

        return { 
            questionCount: length,
            requested: false,
            camera: camera,
            src: src
        }
    },

    componentDidMount: function() {
        console.log("WHAT");
        console.log("WHAT");
        console.log("WHAT");
        this.getStream();
    },

    componentWillMount: function() {
        console.log("WHT");
        console.log("WHT");
        console.log("WHT");
    },

    getStream: function() {
        var self = this;
        // Browser implementations
        navigator.getUserMedia = navigator.getUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.msGetUserMedia;

        navigator.getUserMedia ({
            video: {optional: [{sourceId: self.state.camera}]}
        }, function(stream) {
            var src = window.URL.createObjectURL(stream);
            console.log(src);
            //var video = React.findDOMNode(this.refs.video);
            //video.src = src;
            //video.play();
            self.setState({
                src: src
            });
        }, function(err) {
            console.log("Video failed:", err);
        });

    },

    /*
     * Hack to force react to update child components
     * Gets called by parent element through 'refs' when state of something changed 
     * (usually localStorage)
     */
    update: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length === 0 ? 1 : answers.length;
        this.setState({
            questionCount: length,
        });
    },

    /*
     * Add new input if and only if they've responded to all previous inputs
     */
    addNewInput: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length === 0 ? 1 : answers.length;

        if (length == this.state.questionCount) {
          this.setState({
              questionCount: this.state.questionCount + 1
          })
        }
    },

    /*
     * Remove input and update localStorage
     */
    removeInput: function(index) {
        console.log("Remove", index);

        if (!(this.state.questionCount > 1))
            return;

        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length === 0 ? 1 : answers.length;

        answers.splice(index, 1);
        survey[this.props.question.id] = answers;

        localStorage[this.props.surveyID] = JSON.stringify(survey);

        this.setState({
            questionCount: this.state.questionCount - 1
        })
    },

    /*
     * Retrieve location and record into localStorage on success.
     * Updates questionCount on success, triggering rerender of page
     * causing input fields to have values reloaded.
     *
     * Only updates the LAST active input field.
     */
    onCapture: function() {
        var self = this;
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var index = answers.length === 0 ? 0 : this.refs[answers.length] ? answers.length : answers.length - 1; // So sorry

        var canvas = document.createElement('canvas');
        var video = React.findDOMNode(this.refs.video);
        canvas.height = video.clientHeight;
        canvas.width = video.clientWidth;

        var ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        console.log(canvas.toDataURL('image/webp'));

        navigator.geolocation.getCurrentPosition(
            function success(position) {
                //answers[index] = {
                //    'response': loc, 
                //    'response_type': 'answer'
                //};

                //survey[self.props.question.id] = answers; // Update localstorage
                //localStorage[self.props.surveyID] = JSON.stringify(survey);

                //var length = answers.length === 0 ? 1 : answers.length;
                //self.setState({
                //    questionCount: length
                //});
            }, 
            
            function error() {
                console.log("Location could not be grabbed");
            }, 
            
            {
                enableHighAccuracy: true,
                timeout: 20000,
                maximumAge: 0
            }
        );


    },

    /*
     * Get default value for an input at a given index from localStorage
     *
     * @index: The location in the answer array in localStorage to search
     */
    getAnswer: function(index) {
        console.log("In:", index);

        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length === 0 ? 1 : answers.length;

        console.log(answers, index);
        return answers[index] && JSON.stringify(answers[index].response) || null;
    },

    render: function() {
        var children = Array.apply(null, {length: this.state.questionCount})
        var self = this;
        return (
                <span>
                <LittleButton 
                buttonFunction={this.onCapture}
                    iconClass={'icon-star'}
                    text={'take a photo'} />

                <canvas ref='canvas' className="question__canvas" />
                <video  
                    autoPlay
                    ref='video' 
                    className="question__video" 
                    src={this.state.src}
                    width={640}
                    height={480}
                />

                {children.map(function(child, idx) {
                    return (
                            <PhotoField 
                                buttonFunction={self.removeInput}
                                type={self.props.questionType}
                                key={Math.random()} 
                                index={idx} 
                                ref={idx}
                                disabled={true}
                                initValue={self.getAnswer(idx)} 
                                showMinus={self.state.questionCount > 1}
                            />
                           )
                })}
                {this.props.question.allow_multiple
                    ? <LittleButton buttonFunction={this.addNewInput}
                        disabled={this.props.disabled}
                        text={'add another answer'} />
                    : null 
                }
                </span>
               )
    }
});
