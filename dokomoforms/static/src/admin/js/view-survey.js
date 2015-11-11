var $ = require('jquery'),
    _ = require('lodash'),
    moment = require('moment'),
    base = require('./base'),
    utils = require('./utils'),
    ps = require('../../common/js/pubsub'),
    SubmissionModal = require('./modals/submission-modal'),
    activityGraph = require('./activity-graph'),
    shareable_link_tpl = require('../templates/shareable-link.tpl'),
    edit_link_tpl = require('../templates/edit-shareable-link.tpl');

var ViewSurvey = (function() {
    var survey_id,
        survey_slug,
        good_slug = true,
        domain = document.location.origin,
        $datatable;

    function init(_survey_id, _survey_slug) {
        survey_id = _survey_id;
        survey_slug = _survey_slug !== 'None' ? _survey_slug : '';
        base.init();
        if (window.CURRENT_USER_ID !== 'None') {
            populateSurveyUrl();
            utils.populateDates(window.DATETIMES);
            setupEventHandlers();
            loadActivityGraph();
            setupDataTable();
        }

    }

    function setupEventHandlers() {
        $(document).on('click', '.edit-survey-url', function() {
            editSurveyUrl();
        });

        $(document).on('click', '.save-survey-url', function() {
            if (!good_slug) {
                return;
            }
            var slug = $('.shareable-url-slug').val();
            saveSurveyUrl(slug)
                .done(function() {
                    slug = slug || survey_id;
                    var url = domain + '/enumerate/' + slug;
                    $('.shareable-link-wrap').html(shareable_link_tpl({
                        shareable_link: url
                    }));
                    survey_slug = slug;
                });
        });

        $(document).on('keypress', '.shareable-url-slug', function(e) {
            var char = String.fromCharCode(e.charCode),
                re = new RegExp(/[;/?:@&=+$,\s#%]/);
            if (re.test(char)) {
                return false;
            }
        });

        $(document).on('input', '.shareable-url-slug', function(e) {
            var slug = e.target.value,
                $saveBtn = $('.save-survey-url');

            // if slug is empty, we're good... go no further.
            if (slug === '') {
                good_slug = true;
                return;
            }

            // otherwise check if it's available...
            testSurveySlug(slug)
                .done(function() {
                    // good only if it's the current slug... the ajax request will return not error,
                    // but we should still be able to save.
                    good_slug = slug === survey_slug;
                })
                .fail(function(jqXHR) {
                    // good only if 404 (i.e. no such url yet)
                    good_slug = jqXHR.status === 404;
                })
                .always(function() {
                    if (!good_slug) {
                        $saveBtn.addClass('disabled');
                        $saveBtn.html('URL unavailable');
                    } else {
                        $saveBtn.removeClass('disabled');
                        $saveBtn.text('Save');
                    }
                });
        });

        $(document).on('paste', '.shareable-url-slug', function(e) {
            // hack, seems necessary though (in order to wait for redraw?)
            setTimeout(function() {
                var slug = cleanSlug(e.target.value),
                    $input = $(e.target);
                $input.val(slug);
            }, 1);
        });

        $(document).on('click', 'table#submissions tbody tr', function() {
            // select this row in the datatable and open detail modal
            var selectedRow = selectSubmissionRow($(this));
            new SubmissionModal({dataTable: $datatable, initialRow: selectedRow}).open();
        });

        $(document).on('click', 'a.survey-language', function(e) {
            var lang = $(e.target).data('surveylang');
            if (lang === 'default') {
                if (window.CURRENT_USER_PREFS[survey_id]
                    && window.CURRENT_USER_PREFS[survey_id]['display_language']) {
                    delete window.CURRENT_USER_PREFS[survey_id]['display_language'];
                }
            } else {
                window.CURRENT_USER_PREFS[survey_id] = {
                    display_language: lang
                };
            }
            savePreferences().done(function() {
                console.log('prefs saved, refresh');
                window.location.reload();
            });
        });

        ps.subscribe('submissions:select_row', function(e, el) {
            console.log(el);
            selectSubmissionRow($(el));
        });
    }

    // TODO: We're already using backbone model for user, why not here too?
    function savePreferences() {
        // quick and dirty, post to API
        var userObj = {
            preferences: window.CURRENT_USER_PREFS
        };

        console.log('saving prefs... ', userObj.preferences);

        return $.ajax({
            url: '/api/v0/users/' + window.CURRENT_USER_ID,
            method: 'PUT',
            data: JSON.stringify(userObj)
        });
    }

    function selectSubmissionRow($el) {
        $('table#submissions tbody tr').removeClass('selected');
        $el.addClass('selected');
        return $datatable.row($el);
    }

    function cleanSlug(slug) {
        slug = slug.trim().replace(/[;/?:@&=+$,\s#%]+/g, '-');
        console.log('cleanSlug: ', slug);
        return slug;
    }

    function populateSurveyUrl() {
        var slug = survey_slug || survey_id;
        var url = domain + '/enumerate/' + slug;
        $('.shareable-link-wrap').html(shareable_link_tpl({
            shareable_link: url
        }));

        // $('.survey-permalink-icon').tooltip('destroy');
        $('.survey-permalink-icon')
            .attr('title', domain + '/enumerate/' + survey_id);
        // .tooltip();
    }

    function testSurveySlug(slug) {
        if (slug === '') {
            return $.Deferred().resolve();
        }
        return $.ajax({
            type: 'GET',
            url: '/enumerate/' + slug
        });
    }

    function editSurveyUrl() {
        var shaLinWra = $('.shareable-link-wrap');
        shaLinWra.html(edit_link_tpl({
            domain: domain,
            slug: survey_slug
        }));
        var slutInput = shaLinWra.find('.shareable-url-slug').focus();
        slutInput[0].setSelectionRange(0, slutInput.val().length);
    }

    function saveSurveyUrl(slug) {
        return $.ajax({
            type: 'PUT',
            url: '/api/v0/surveys/' + survey_id,
            data: JSON.stringify({
                url_slug: slug || null
            })
        });
    }

    function loadActivityGraph() {
        activityGraph('/api/v0/surveys/' + survey_id + '/activity', 30, '.activity-graph');
    }

    function setupDataTable() {
        // DataTables

        $datatable = $('#submissions').DataTable({
            language: {
                search: 'Search by submitter name:'
            },
            'lengthMenu': [
                [20, 50, 100],
                [20, 50, 100]
            ],
            'pagingType': 'full_numbers',
            'order': [
                [1, 'desc']
            ],
            'columnDefs': [{
                data: 'submitter_name',
                targets: 0
            }, {
                'data': 'save_time',
                'render': function(data) {
                    var datetime = moment(data);
                    return datetime.format('MMM D, YYYY [at] HH:mm:ss');
                },
                'targets': 1
            }, {
                'data': 'submission_time',
                'render': function(data) {
                    var datetime = moment(data);
                    return datetime.format('MMM D, YYYY [at] HH:mm:ss');
                },
                'targets': 2
            }, {
                'data': 'id',
                'targets': 3,
                'visible': false
            }],
            'columns': [{
                'name': 'submitter_name'
            }, {
                'name': 'save_time'
            }, {
                'name': 'submission_time'
            }, {
                'name': 'id'
            }],
            'processing': true,
            'serverSide': true,
            'ajax': function(data, callback) {
                $.ajax({
                    'url': '/api/v0/surveys/' + survey_id + '/submissions',
                    'data': {
                        draw: data.draw,
                        offset: data.start,
                        limit: data.length === -1 ? undefined : data.length,
                        order_by: data.order.map(function(ord) {
                            return data.columns[ord.column].name + ':' + ord.dir;
                        }).join(','),
                        fields: data.columns.map(function(c) {
                            return c.name;
                        }).join(','),
                        search: data.search.value,
                        regex: data.search.regex,
                        search_fields: 'submitter_name'
                    },
                    'success': function(json) {
                        var data = json.submissions.map(function(submission) {
                                return [
                                    submission.submitter_name,
                                    submission.save_time,
                                    submission.submission_time,
                                    submission.id
                                ];
                            });
                        console.log('data: ', data);
                        var response = {
                            draw: json.draw,
                            recordsTotal: json.total_entries,
                            recordsFiltered: json.filtered_entries,
                            data: json.submissions.map(function(submission) {
                                return {
                                    submitter_name: submission.submitter_name,
                                    save_time: submission.save_time,
                                    submission_time: submission.submission_time,
                                    id: submission.id
                                };
                            })
                        };
                        callback(response);
                    }
                });
            }
        }).on('xhr.dt', function(e, settings, json) {
            console.log('data returned: ', json);
            // for ( var i=0, ien=json.aaData.length ; i<ien ; i++ ) {
            //     json.aaData[i].sum = json.aaData[i].one + json.aaData[i].two;
            // }
            // Note no return - manipulate the data directly in the JSON object.
        });
    }


    return {
        init: init
    };


})();

// expose this module globally so that we can bootstrap it
window.ViewSurvey = ViewSurvey;
