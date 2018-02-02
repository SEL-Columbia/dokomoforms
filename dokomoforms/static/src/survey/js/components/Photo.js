var React = require('react'),
    createReactClass = require('create-react-class'),
    PhotoField = require('./baseComponents/PhotoField'),
    LittleButton = require('./baseComponents/LittleButton'),
    BigButton = require('./baseComponents/BigButton'),
    PhotoAPI = require('../api/PhotoAPI'),
    uuid = require('uuid');

//XXX use this: navigator.vibrate(50);

/*
 * Photo question component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 *     @disabled: boolean for disabling all inputs
 *     @db: pouchdb database
 */
module.exports = createReactClass({
    getInitialState: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length ? answers.length : 1;

        var camera = null;
        var src = null;

        return {
            questionCount: length,
            requested: false,
            camera: camera,
            sources: [],
            photos: [],
            src: src
        };
    },

    // This is how you react to the render call back. Once video is mounted I can attach a source
    // and re-render the page with it using the autoPlay feature. No DOM manipulation required!!
    componentDidMount: function() {
        this.getPhotos();
        this.getCameraSources();
        // stream is started once sources are gotten
        console.log('window.orientation', window.orientation);
        // window.addEventListener('deviceorientation', this.updateOrientation, true);
    },

    componentWillUnmount: function() {
        if (this.stream) {
	    // https://github.com/andyet/SimpleWebRTC/issues/363#issuecomment-163178700
	    this.stream.getTracks().forEach(function (track) { track.stop(); });
        }
    },

    updateOrientation: function(e) {
        // console.log('orientation updated: ', e, window.orientation);
    },

    startStream: function() {
        var self = this;
        if (self.stream) {
	    // https://github.com/andyet/SimpleWebRTC/issues/363#issuecomment-163178700
	    self.stream.getTracks().forEach(function (track) { track.stop(); });
        }
        // Browser implementations
        navigator.getUserMedia = navigator.getUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.msGetUserMedia;

        var config;

        if (self.state.nosources) {
            config = {
                video: true
            };
        } else {
            config = {
                video: {
                    optional: [{
                        // facingMode: 'environment', <--- not implemented in chrome for Android
                        sourceId: self.state.camera
                    }]
                }
            };
        }

        navigator.getUserMedia(config, function(stream) {
            // store the stream on this component so that we can stop it later...
            self.stream = stream;
            console.log('STREAM: ', stream);
            var src = window.URL.createObjectURL(stream);
            console.log(src);
            self.setState({
                src: src
            });
        }, function(err) {
            console.log('Video failed:', err);
        });

    },

    getCameraSources: function() {
        if (typeof MediaStreamTrack === 'undefined' ||
            typeof MediaStreamTrack.getSources === 'undefined') {
            console.log('This browser does not support MediaStreamTrack... trying MediaStream.enumerateDevices()');
            // try MediaStream.enumerateDevices()
            if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
                console.log('This browser does not support MediaStream.enumerateDevices() either... use basic video capture');
                this.setState({nosources: true}, this.startStream);
                return;
            } else {
                navigator.mediaDevices.enumerateDevices()
                    .then(this.getMediaStreamSourcesSuccess)
                    .catch(function(err) {
                        console.log(err.name + ': ' + err.message);
                    });
            }
        } else {
            MediaStreamTrack.getSources(this.getMediaStreamTrackSourcesSuccess);
        }
    },

    getMediaStreamTrackSourcesSuccess: function(sourceInfos) {
        var self = this,
            cameraSources = [],
            cameraIdx = 0,
            camera = null;

        sourceInfos.forEach(function(sourceInfo) {
            if (sourceInfo.kind === 'video') {
                var cameraSource = {
                    selected: '',
                    value: sourceInfo.id,
                    text: sourceInfo.label || 'camera ' + cameraIdx
                };
                cameraSources.push(cameraSource);
                cameraIdx += 1;
            } else {
                console.log('Some other kind of source: ', sourceInfo);
            }
        });

        // set the last camera found to the selected camera.
        if (cameraSources.length) {
            camera = cameraSources[cameraSources.length - 1].value;
            cameraSources[cameraSources.length - 1].selected = 'selected';
        }

        this.setState({
            camera: camera,
            sources: cameraSources
        }, function() {
            self.startStream();
        });
    },

    getMediaStreamSourcesSuccess: function(devices) {
        var self = this,
            cameraSources = [],
            cameraIdx = 0,
            camera = null;
        devices.forEach(function(device) {
            if (device.kind === 'videoinput') {
                var cameraSource = {
                    selected: '',
                    value: device.id,
                    text: device.label || 'camera ' + cameraIdx
                };
                cameraSources.push(cameraSource);
                cameraIdx += 1;
            } else {
                console.log('Some other kind of source: ', device);
            }
        });

        // set the last camera found to the selected camera.
        if (cameraSources.length) {
            camera = cameraSources[cameraSources.length - 1].value;
            cameraSources[cameraSources.length - 1].selected = 'selected';
        }

        this.setState({
            camera: camera,
            sources: cameraSources
        }, function() {
            self.startStream();
        });
    },

    changeCamera: function(e) {
        this.setState({
            camera: e.target.value
        }, this.startStream);
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
            PhotoAPI.getPhoto(self.props.db, answer.response, function(err, photo) {
                if (err) {
                    console.log('DB query failed:', err);
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
     * Hack to force react to update child components
     * Gets called by parent element through 'refs' when state of something changed
     * (usually localStorage)
     */
    update: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length;
        this.setState({
            questionCount: length
        });
    },

    /*
     * Add new input if and only if they've responded to all previous inputs
     */
    addNewInput: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var length = answers.length;

        console.log('Length:', length, 'Count', this.state.questionCount);
        if (answers[length] && answers[length].response_type || length > 0 && length === this.state.questionCount) {

            this.setState({
                questionCount: this.state.questionCount + 1
            });
        }
    },

    /*
     * Remove input and update localStorage
     */
    removeInput: function(index) {
        console.log('Remove', index);

        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var photoID = answers[index] && answers[index].response || 0;

        // Removing an empty input
        if (photoID === 0) {
            return;
        }

        // Remove from localStorage;
        answers.splice(index, 1);
        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

        // Remove from pouchDB
        console.log('removing', photoID);
        this.state.photos.splice(index, 1);
        PhotoAPI.removePhoto(this.props.db, photoID, function(err, result) {
            if (err) {
                console.log('Could not remove attachment?:', err);
                return;
            }
            console.log('Removed attachement:', result);
        });

        var count = this.state.questionCount - 1;
        count = count ? count : 1;
        this.setState({
            photos: this.state.photos,
            questionCount: count
        });
    },

    /*
     * Capture still and record into localStorage.
     * Updates questionCount on success, triggering rerender of page
     * causing input fields to have values reloaded.
     *
     * Only updates the LAST active input field.
     */
    onCapture: function(e) {
        navigator.vibrate(80);

        var self = this;
        var orientation = window.orientation;
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        var index = answers.length === 0 ? 0 : this.refs[answers.length] ? answers.length : answers.length - 1; // So sorry

        // Capture still from video element and write into new canvas
        //XXX Delete canvas? canvas;
        var canvas = document.createElement('canvas');
        var video = React.findDOMNode(this.refs.video);

        // hack to get the aspect ratio right... assuming portait orientation (0 or 180) means swapped ratio on mobile.
        canvas.height = (orientation === 0 || orientation === 180) ? video.clientWidth : video.clientHeight;
        canvas.width = (orientation === 0 || orientation === 180) ? video.clientHeight : video.clientWidth;

        var ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Extract photo from canvas and write it into pouchDB
        var photo = canvas.toDataURL('image/png');
        var photoID = uuid.v4();
        PhotoAPI.addPhoto(this.props.db, photoID, photo);

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

        // If allow_multiple, add a new input after the capture.
        if (this.props.question.allow_multiple) {
            this.addNewInput();
        }
    },

    render: function() {
        var self = this;
        var children = Array.apply(null, {
            length: this.state.questionCount
        });
        var classes = 'question__video';
        // if (this.state.status === 'captured') {
        //     classes += ' captured';
        // }
        console.log('STATE', this.state);
        var select_source = null;
        if (!this.state.nosources) {
            select_source = (
                <select className="camera_select" onChange={this.changeCamera}>
                    {this.state.sources.map(function(source) {
                        return (
                            <option value={source.value} selected={source.selected}>{source.text}</option>
                        );
                    })}
                </select>
            );
        }
        return (
            <span>
            <div className="video_container">
                <video
                    autoPlay
                    ref='video'
                    className={classes}
                    onClick={this.onCapture}
                    src={this.state.src}
                />

                <div className="photo_shutter" onClick={this.onCapture}>

                </div>
            </div>

            <div className='photo_thumbnails'>
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
                        />
                       );
            })}
            </div>

            {select_source}

            </span>
        );
    }
});
