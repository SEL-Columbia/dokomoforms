var React = require('react'),
    createReactClass = require('create-react-class');

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
module.exports = createReactClass({
    getInitialState: function() {
        var self = this;
        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.surveyID] || [];

        // Update navigator.onLine
        var interval = window.setInterval(function() {
            if (self.state.online !== navigator.onLine) {
                self.setState({
                    online: navigator.onLine
                });
            }
        }, 1000);

        return {
            count: unsynced_submissions.length,
            online: navigator.onLine,
            interval: interval
        };
    },

    // Force react to update
    update: function() {
        // Get all unsynced surveys
        var unsynced_surveys = JSON.parse(localStorage['unsynced'] || '{}');
        // Get array of unsynced submissions to this survey
        var unsynced_submissions = unsynced_surveys[this.props.surveyID] || [];

        this.setState({
            count: unsynced_submissions.length,
            online: navigator.onLine
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
            online: navigator.onLine
        });

    },

    componentWillUnmount: function() {
        window.clearInterval(this.state.interval);
    },

    getCard: function() {
        var admin_email = window.ADMIN_EMAIL || '';
        var admin_email_link = 'mailto:' + admin_email;
        if (this.state.count) {
            if (this.state.online) {
                // Unsynced and online
                return (
                        <span>
                        <Card messages={[['You have ',  <b>{this.state.count}</b>, ' unsynced surveys.', ' Please submit them now.']
                            ]} type={'message-warning'}/>
                        <BigButton text={'Submit Completed Surveys'} buttonFunction={this.buttonFunction} />
                        </span>
                       );
            } else {
                // Unsynced and offline
                return (
                        <Card messages={[['You have ',  <b>{this.state.count}</b>, ' unsynced surveys.'],
                            '',
                            'At present, you do not have a network connection — please remember to submit'
                                + ' these surveys the next time you do have access to the internet.'
                        ]} type={'message-warning'}/>
                       );
            }
        } else {
            // No unsynced surveys
            return (
                    <Card
                        messages={[
                            ['If you have any questions regarding the survey, please ',
                                <a href={admin_email_link}>contact the survey adminstrator.</a>]
                        ]}
                        type={'message-primary'} />
                   );
        }
    },

    render: function() {
        return this.getCard();
    }
});
