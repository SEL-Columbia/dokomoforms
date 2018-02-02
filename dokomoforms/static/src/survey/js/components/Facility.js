var $ = require('jquery'),
    React = require('react'),
    createReactClass = require('create-react-class'),

    ResponseField = require('./baseComponents/ResponseField.js'),
    LittleButton = require('./baseComponents/LittleButton.js'),

    FacilityRadios = require('./baseComponents/FacilityRadios.js'),
    Select = require('./baseComponents/Select.js');

/*
 * Facilities question component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 *     @disabled: boolean for disabling all inputs
 *     @db: pouchdb database
 *     @tree: Facility Tree object
 */
module.exports = createReactClass({
    getInitialState: function() {
        var answer = this.getAnswer();
        var selectOff = answer && answer.metadata && answer.metadata.is_new;
        return {
            loc: null,
            loading: true,
            selectFacility: !selectOff,
            facilities: [],
            choices: [
                {'value': 'water', 'text': 'Water'},
                {'value': 'energy', 'text': 'Energy'},
                {'value': 'education', 'text': 'Education'},
                {'value': 'health', 'text': 'Health'}
            ]
        };
    },

    /*
     * Deal with async call to getFacilities
     */
    componentWillMount: function() {
        var loc = JSON.parse(localStorage['location'] || '{}');
        var self = this;
        // If we have a location fix, display the facilities,
        // otherwise start fetching location fix
        if (loc.lat) {
            self.getFacilities(loc).done(function(facilities) {
                self.setState({
                    loc: loc,
                    facilities: facilities,
                    loading: false
                });
            });
        } else {
            this.onLocate();
        }
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
            questionCount: length
        });
    },

    /*
     * Switch view to new Facility View
     */
    toggleAddFacility: function() {
        this.setState({
            selectFacility : this.state.selectFacility ? false : true
        });
    },

    /*
     * Record newly chosen facility into localStorage
     *
     * @option: The facility uuid chosen
     * @data: I have no idea why i have this?
     */
    selectFacility: function(option, data) {
        console.log('Selected facility');
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        answers = [];

        this.state.facilities.forEach(function(facility) {
            if (facility.uuid === option) {
                answers = [{
                    'response': {
                        'facility_id': facility.uuid,
                        'facility_name': facility.name,
                        'facility_sector': facility.properties.sector,
                        'lat': facility.coordinates[1],
                        'lng': facility.coordinates[0]
                    },
                    'response_type': 'answer'
                }];
                return false;
            }
            return true;
        });

        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);

    },

    /*
     * Query the tree for nearby facilities near given location when possible
     *
     * @loc: The location ({lat: NUM, lng: NUM}) to query around
     */
    getFacilities: function(loc) {
        // console.log('getFacilities', this.props.tree);
        // var d = $.Deferred();
        // if (!loc || !loc.lat || !loc.lng || !this.props.tree || !this.props.tree.root) {

        //     d.resolve([]);
        //     return d;
        // }

        console.log('Getting facilities ...');
        return this.props.tree.getNNearestFacilities(loc.lat, loc.lng, 1000, 10);
    },

    /*
     * Get response from localStorage
     */
    getAnswer: function() {
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        console.log('Selected facility', answers[0]);
        if (answers[0]) return answers[0];
    },

    /*
     * Generate objectID compatitable with Mongo for the Revisit API
     *
     * Returns an objectID string
     */
    createObjectID: function() {
        return 'xxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[x]/g, function() {
            var r = Math.random()*16|0;
            return r.toString(16);
        });
    },

    /*
     * Deal with all new facility input fields, type is bound to function call
     *
     * @type: Type of input that was updated
     * @value: newly supplied input
     */
    onInput: function(type, value) {
        console.log('Dealing with input', value, type);
        var survey = JSON.parse(localStorage[this.props.surveyID] || '{}');
        var answers = survey[this.props.question.id] || [];
        if (answers[0] && (!answers[0].metadata || !answers[0].metadata.is_new)) {
            answers = [];
        }

        // Load up previous response, update values
        var response = (answers[0] && answers[0].response) || {};
        var uuid = response.facility_id || this.createObjectID();
        response.facility_id = uuid;
        // XXX This kind of assumes that current lat/lng is correct at the time of last field update
        response.lat = this.state.loc.lat;
        response.lng = this.state.loc.lng;

        switch(type) {
            case 'text':
                response.facility_name = value;
                break;
            case 'select':
                var v = value[0]; // Only one ever
                console.log('Selected v', v);
                response.facility_sector = v;
                break;
            case 'other':
                console.log('Other v', value);
                response.facility_sector = value;
                break;
            case 'has_grid_power':
                console.log('Has grid power', value);
                response.grid_power = value;
                break;
            case 'has_improved_water_supply':
                console.log('Has improved water', value);
                response.improved_water_supply = value;
                break;
            case 'has_improved_sanitation':
                console.log('Has improved santiation', value);
                response.improved_sanitation = value;
                break;
        }

        //XXX Failed validation messes up facility question
        //TODO: Properly handle null values

        answers = [{
            'response': response,
            'response_type': 'answer',
            'metadata': {
                'is_new': true
            }
        }];

        console.log('Built response', answers);

        survey[this.props.question.id] = answers;
        localStorage[this.props.surveyID] = JSON.stringify(survey);
    },

    onChangeGrid: function(e) {
        console.log(e);
        this.onInput('has_grid_power', e.target.checked);
    },

    onChangeWater: function(e) {
        console.log(e);
        this.onInput('has_improved_water_supply', e.target.checked);
    },

    onChangeSanitation: function(e) {
        console.log(e);
        this.onInput('has_improved_sanitation', e.target.checked);
    },

    /*
     * Retrieve location and record into state on success.
     */
    onLocate: function() {
        var self = this;
        self.setState({
            loading: true
        });
        navigator.geolocation.getCurrentPosition(
            function success(position) {
                var loc = {
                    'lat': position.coords.latitude,
                    'lng': position.coords.longitude
                };

                // Record location for survey
                localStorage['location'] = JSON.stringify(loc);

                self.getFacilities(loc).done(function(facilities) {
                    self.setState({
                        loc: loc,
                        facilities: facilities,
                        loading: false
                    });
                });
            },

            function error() {
                console.error('Location could not be grabbed');
            },

            {
                enableHighAccuracy: true,
                timeout: 20000,
                maximumAge: 0
            }
        );


    },

    render: function() {
        // Retrieve respone for initValues
        var answer = this.getAnswer();
        var choiceOptions = this.state.choices.map(function(choice) { return choice.value; });

        var hasLocation = this.state.loc && this.state.loc.lat && this.state.loc.lng;
        var isNew = answer && answer.metadata && answer.metadata.is_new;

        // Update sector field to match initSelect expected value
        var sector = answer && answer.response.facility_sector;
        var isOther = choiceOptions.indexOf(sector) === -1;
        sector = isOther ? sector && 'other' : sector;

        var locStr;
        if (hasLocation) {
            locStr = this.state.loc.lat + ', ' + this.state.loc.lng;
        }

        var isLoading = null;
        if (this.state.loading) {
            isLoading = (
                <div className='content-padded'>Loading...</div>
            );
        }
        var content = (
            <span>
                <LittleButton buttonFunction={this.onLocate}
                    icon={'icon-star'}
                    text={'find nearby facilities'}
                    disabled={this.props.disabled}
                />

                <FacilityRadios
                    key={this.props.disabled}
                    selectFunction={this.selectFacility}
                    facilities={this.state.facilities}
                    initValue={answer && !isNew && answer.response.facility_id}
                    disabled={this.props.disabled}
                />

                { hasLocation  ?
                    <LittleButton buttonFunction={this.toggleAddFacility}
                        disabled={this.props.disabled}
                        text={'add new facility'}
                        extraClasses='btn-add-facility'
                    />
                    : null
                }
            </span>
        );

        if (!this.state.selectFacility) {
            content = (
                <span>
                    <ResponseField
                        onInput={this.onInput.bind(null, 'text')}
                        initValue={isNew && answer.response.facility_name}
                        type={'text'}
                        placeholder="Facility name"
                        disabled={this.props.disabled}
                    />
                    <ResponseField
                        initValue={locStr}
                        type={'location'}
                        disabled={true}
                    />
                    <Select
                        placeholder='Choose a sector...'
                        choices={this.state.choices}
                        initValue={isNew && isOther ? answer.response.facility_sector : null}
                        initSelect={isNew && [sector]}
                        withOther={true}
                        multiSelect={false}
                        onInput={this.onInput.bind(null, 'other')}
                        onSelect={this.onInput.bind(null, 'select')}
                        disabled={this.props.disabled}
                    />
                    <div className='content-padded'>
                        <div className='has-grid-power'>
                            <input
                                type='checkbox'
                                id='has-grid-power'
                                name='has-grid-power'
                                onChange={this.onInput.bind(null, 'has_grid_power')}
                                onChange={this.onChangeGrid}
                            />
                            <label htmlFor='has-grid-power'>has grid power</label>
                        </div>

                        <div className='has-improved-water-supply'>
                            <input
                                type='checkbox'
                                id='has-improved-water-supply'
                                name='has-improved-water-supply'
                                onChange={this.onChangeWater}
                            />
                            <label htmlFor='has-improved-water-supply'>has improved water supply</label>
                        </div>

                        <div className='has-improved-sanitation'>
                            <input
                                type='checkbox'
                                id='has-improved-sanitation'
                                name='has-improved-sanitation'
                                onChange={this.onChangeSanitation}
                            />
                            <label htmlFor='has-improved-sanitation'>has improved sanitation</label>
                        </div>
                    </div>

                    <LittleButton
                        buttonFunction={this.toggleAddFacility}
                        text={'cancel'}
                        disabled={this.props.disabled}
                        extraClasses='btn-cancel'
                     />
                </span>
            );
        }

        return (
            <span>
                {this.state.loading ? isLoading : content}
            </span>
       );
    }
});
