var $ = require('jquery');

module.exports = (function() {

    /**
     * Open a modal displaying submission details.
     * @param  {String} submission_id UUID of the submission
     */
    function openSubmissionDetailModal(submission_id) {
        var url = '/view/submission/' + submission_id;
        $('.modal-submission .modal-content').load(url);
        $('.modal-submission').modal();
    }

    function initSubmissionModalHandler() {
        // submission modal click handler
        $(document).on('click', '.btn-view-submission', function() {
            var submission_id = $(this).data('id');
            openSubmissionDetailModal(submission_id);
        });
    }

    return {
        init: initSubmissionModalHandler,
        openSubmissionDetailModal: openSubmissionDetailModal
    };

})();
