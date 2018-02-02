var React = require('react'),
    createReactClass = require('create-react-class');

/*
 * Note component
 *
 * props:
 *     @question: node object from survey
 *     @questionType: type constraint
 *     @language: current survey language
 *     @surveyID: current survey id
 */
module.exports = createReactClass({
    // Every question component needs this method
    update: function() {
    },

    render: function() {
        return (
                <span></span>
               )
    }
});
