var React = require('react');

var Card = require('./baseComponents/Card.js');
var BigButton = require('./baseComponents/BigButton.js');

/*
 * Splash page component
 * Renders the appropiate card for the main page
 *
 * props:
 *     @language: current survey language
 *     @surveyID: current survey id
 *     @buttonFunction: What to do when submit is clicked
 */
module.exports = React.createClass({
    getInitialState: function() {
        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.surveyID] || [];

        return { 
            count: unsynced_submissions.length,
            online: navigator.onLine,
        }
    },

    // Force react to update
    update: function() {
        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.surveyID] || [];

        this.setState({ 
            count: unsynced_submissions.length,
            online: navigator.onLine,
        });
    },

    buttonFunction: function(event) {
        if (this.props.buttonFunction)
            this.props.buttonFunction(event);

        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.surveyID] || [];

        this.setState({ 
            count: unsynced_submissions.length,
            online: navigator.onLine,
        });

    },

    getCard: function() {
        if (this.state.count) {
            if (this.state.online) {
                return (
                        <span>
                        <Card messages={[this.props.surveyID, this.state.count,
                            [<b>love</b>], "toast", "unsynced and online"]} type={"message-warning"}/>

                        <BigButton text={"Submit Completed Surveys"} buttonFunction={this.buttonFunction} /> 
                        </span>
                       )
            } else {
                return (
                        <Card messages={[this.props.surveyID, this.state.count, 
                            [<b>love</b>], "toast", "unsynced and NOT online"]} type={"message-error"}/>
                       )
            }
        } else {
            return (
                    <Card messages={[this.props.surveyID, this.state.count, 
                        [<b>love</b>], "toast", "no unsynced"]} type={"message-primary"}/>
                   )
        }
    },

    render: function() {
        return this.getCard()
    }
});
