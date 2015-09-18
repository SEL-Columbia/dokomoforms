var _ = require('lodash');


/**
 * General utility functions.
 */
module.exports = (function() {
    /**
     * Check whether a survey contains questions of a given type_constraint
     *
     * Kind of ugly, but it recursively checks sub_surveys for fields too.
     *
     * @param  {String} survey           The survey to check.
     * @param  {String} type_constraint  The type_constraint to look for.
     * @return {Boolean}                 True if the type is found, false otherwise.
     */
    function _surveyHasQuestionType(survey, type_constraint) {
        console.log('_surveyHasQuestionType', type_constraint);
        var nodes = survey.nodes || [],
            nodes_with_sub_surveys = _.filter(nodes, 'sub_surveys'),
            has_constraint = false;

        console.log('nodes_with_sub_surveys', nodes_with_sub_surveys);

        // check the nodes in this survey
        has_constraint = _.some(nodes, {'type_constraint': type_constraint});
        console.log('has_constraint', has_constraint);

        if (has_constraint) {
            return true;
        }

        // XXX yuck, but ok.
        // if there are sub_surveys, recurse through them. stop if any of them has a constraint.
        if (nodes_with_sub_surveys.length) {
            // for each node with sub_surveys
            for (var i = nodes_with_sub_surveys.length - 1; i >= 0; i--) {
                // for each sub_survey within the node, check type constraint
                for (var j = nodes_with_sub_surveys[i].sub_surveys.length - 1; j >= 0; j--) {
                    has_constraint = _surveyHasQuestionType(nodes_with_sub_surveys[i].sub_surveys[j], type_constraint);
                    if (has_constraint) break;
                }
            }
        }

        return has_constraint;
    }

    return {
        surveyHasQuestionType: _surveyHasQuestionType
    };
})();
