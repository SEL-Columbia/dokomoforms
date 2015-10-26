var $ = require('jquery'),
    _ = require('lodash'),
    ps = require('../../../common/js/pubsub'),
    utils = require('../utils'),
    tpl = require('../../templates/submission-modal.tpl');

/**
 * Submission modal module.
 *
 * If submission_data is String, assume it's a submission id and load the submission.
 *
 * If submission_data is an array of submission IDs
 * @param {[type]} submission_data [description]
 */
var SubmissionModal = function(dataTable, initialRow) {
    console.log('SubmissionModal');

    var selectedRow = initialRow,
        submission_id,
        $modal = $(tpl()),
        $next = $modal.find('.btn-next'),
        $prev = $modal.find('.btn-prev'),
        $loading = $modal.find('.loading-overlay');

    if (_.isString(dataTable)) {
        // assume we're passing a submission UUID
        submission_id = dataTable;
        $modal.find('.modal-header').empty();
    } else {
        submission_id = selectedRow.data()[3];
        // setup event handlers for buttons
        $next.on('click', _next);
        $prev.on('click', _prev);
    }



    function open() {
        console.log('opening modal');
        $modal.modal();
        $modal.on('shown.bs.modal', function() {
            utils.initTooltips('.modal');
            // on open, load first data
            _updateData(submission_id);
        });
        $modal.on('hidden.bs.modal', function() {
            console.log('closed.');
            $modal.remove();
        });
    }

    function showLoading() {
        $loading.removeClass('hide');
    }

    function hideLoading() {
        $loading.addClass('hide');
    }

    /**
     * Load the rendered submission detail page from the server and populate the modal.
     * @param  {String} submission_id
     */
    function loadSubmission(submission_id) {
        var dfd = $.Deferred(),
            url = '/view/submission/' + submission_id;

        $modal.find('.modal-body').load(url, function() {
            $('.modal-submission').modal();
            utils.populateDates(window.SUB_DATETIMES, 'MMM D, YYYY HH:mm');
            dfd.resolve();
        });

        return dfd;
    }

    function close() {
        $modal.modal('hide');
    }

    function _updatePositionIndicator(currentIndex) {
        var pageInfo = dataTable.page.info(),
            total = pageInfo.recordsDisplay,
            curPos = pageInfo.page * pageInfo.length + currentIndex + 1,
            posText = curPos + '/' + total;

        // if at the start or end, disable buttons as needed
        $prev.removeClass('disabled');
        $next.removeClass('disabled');
        if (curPos === 1) {
            // start
            $prev.addClass('disabled');
        }
        if (curPos === total) {
            // end
            $next.addClass('disabled');
        }

        $('.submission-position').text(posText);
    }

    function _next() {
        var pageInfo = dataTable.page.info(),
            indexes = dataTable.rows( {search: 'applied'} ).indexes(),
            currentIndex = selectedRow.index(),
            currentPosition = indexes.indexOf( currentIndex );

        console.log(currentIndex, currentPosition);



        if ( currentPosition < indexes.length-1 ) {
            selectedRow = dataTable.row( indexes[ currentPosition + 1 ] );
            _updateData(selectedRow.data()[3]);
        } else if (pageInfo.page < pageInfo.pages - 1) {
            dataTable.page(pageInfo.page + 1).draw(false);
            dataTable.on('draw.dt', function() {
                console.log('page updated');
                selectedRow = dataTable.row(0);
                _updateData(selectedRow.data()[3]);
            });
        }
    }

    function _prev(submission) {
        var pageInfo = dataTable.page.info(),
            indexes = dataTable.rows( {search: 'applied'} ).indexes(),
            currentIndex = selectedRow.index(),
            currentPosition = indexes.indexOf( currentIndex );

        if ( currentPosition > 0 ) {
            selectedRow = dataTable.row( indexes[ currentPosition - 1 ] );
            _updateData(selectedRow.data()[3]);
        } else if (pageInfo.page > 0) {
            dataTable.page(pageInfo.page - 1).draw(false);
            dataTable.on('draw.dt', function() {
                console.log('page updated');
                selectedRow = dataTable.row(pageInfo.length - 1);
                _updateData(selectedRow.data()[3]);
            });
        }
    }

    function _updateData(sub_id) {
        // remove listener to draw (it gets re-bound on demand as needed)
        if (selectedRow) dataTable.off('draw.dt');

        // load the new submission
        loadSubmission(sub_id)
            .done(function() {
                // update the '[current]/[total]' text in the modal header
                if (selectedRow) _updatePositionIndicator(selectedRow.index());
                // render dates using moment.js
                utils.populateDates(window.SUB_DATETIMES, 'MMM D, YYYY HH:mm');
            });
    }


    return {
        open: open,
        close: close
    };

};


module.exports = SubmissionModal;
