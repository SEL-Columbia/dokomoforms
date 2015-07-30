var React = require('react');

var PhotoField = require('./baseComponents/PhotoField.js');
var LittleButton = require('./baseComponents/LittleButton.js');
var uuid = require('node-uuid');

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
 *     @db: pouchdb database 
 */
module.exports = React.createClass({
    getInitialState: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length;

        var camera = null;
        var src = null;

        return { 
            questionCount: length,
            requested: false,
            camera: camera,
            photos: [],
            src: src
        }
    },

    // This is how you react to the render call back. Once video is mounted I can attach a source
    // and re-render the page with it using the autoPlay feature. No DOM manipulation required!!
    componentDidMount: function() {
        this.getStream();
        this.getPhotos();
    },

    componentWillMount: function() {
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
            self.setState({
                src: src
            });
        }, function(err) {
            console.log("Video failed:", err);
        });

    },

    /*
     * Get default value for an input at a given index from localStorage
     * Use this value to query pouchDB and update state asynchronously
     */
    getPhotos: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var self = this;

        answers.forEach(function(answer, idx) {
            self.getPhoto(answer.response, function(err, photo) {
                if (err) {
                    console.log("DB query failed:", err);
                    return;
                }

                self.state.photos[idx] = photo;
                self.setState({
                    photos: self.state.photos
                });
            });
        });
    },

    /*
     * Get photo with uuid, id from pouchDB
     */
    getPhoto: function(id, callback) {
        this.props.db.getAttachment(id, 'photo').then(function(photo) {
            callback(null, URL.createObjectURL(photo));
        }).catch(function(err) {
            callback(err);
        });

        //this.props.db.get(id, {'attachments': true}).then(function(photoDoc) {
        //    callback(null, photoDoc._attachments.photo.data);
        //}).catch(function(err) {
        //    callback(err);
        //});
    },

    /*
     * Hack to force react to update child components
     * Gets called by parent element through 'refs' when state of something changed 
     * (usually localStorage)
     */
    update: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length;
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
        var length = answers.length;

        console.log("Length:", length, "Count", this.state.questionCount);
        if (answers[length] && answers[length].response_type
                || length > 0 && length == this.state.questionCount) {

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

        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length;
        var photoID = answers[index] && answers[index].response || 0;
        var self = this;

        // Remove from localStorage;
        answers.splice(index, 1);
        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

        // Remove from pouchDB
        console.log("removing", photoID);
        this.state.photos.splice(index, 1);
        this.removePhoto(photoID, function(err, result) {
            if (err) {
                console.log("Could not remove attachment?:", err);
                return;
            }
            console.log("Removed attachement:", result);
        });

        this.setState({
            photos: this.state.photos,
            questionCount: this.state.questionCount - 1
        })
    },

    removePhoto: function(photoID, callback) {
        var self = this;
        this.props.db.get(photoID).then(function (photoDoc) {
            self.props.db.removeAttachment(photoID, 'photo', photoDoc._rev)
                .then(function(result) {
                    self.props.db.remove(photoID, result.rev);
                    callback(null, result)
                }).catch(function(err) {
                    callback(err)
                });
        });
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

        // Capture still from video element and write into new canvas
        //XXX Delete canvas? canvas;
        var canvas = document.createElement('canvas');
        var video = React.findDOMNode(this.refs.video);
        canvas.height = video.clientHeight;
        canvas.width = video.clientWidth;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Extract photo from canvas and write it into pouchDB
        var photo = canvas.toDataURL('image/png');
        var photo64 = photo.substring(photo.indexOf(',')+1)
        var photoID = uuid.v4();

        console.log(photo);
        console.log(photoID);
        this.props.db.put({
            '_id': photoID,
            '_attachments': {
                'photo': {
                    "content_type": "image/png",
                    "data": photo64
                }
            }
        });

        // Record the ID into localStorage
        answers[index] = {
            'response': photoID, 
            'response_type': 'answer'
        };

        survey[self.props.question.id] = answers; // Update localstorage
        localStorage[self.props.surveyID] = JSON.stringify(survey);

        // Update state for count and in memory photos array
        var length = answers.length === 0 ? 1 : answers.length;
        self.state.photos[index] = photo;
        self.setState({
            photos: self.state.photos,
            questionCount: length
        });

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
                                initValue={self.state.photos[idx]} 
                                showMinus={true}
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
