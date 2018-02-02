var React = require('react'),
    createReactClass = require('create-react-class');

/*
 * Loading component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 */
module.exports = createReactClass({
    render: function() {
        return (
            <div className="loading-overlay">
                <div className="loading-content">
                    <img src="/static/dist/survey/img/loading.gif" />
                    <br/>
                    <p>{this.props.message}</p>
                </div>
            </div>
       );
    }
});
