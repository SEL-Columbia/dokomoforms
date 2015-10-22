var $ = require('jquery'),
    _ = require('lodash'),
    base = require('./base'),
    utils = require('./utils'),
    moment = require('moment'),
    view_sub_btn_tpl = require('../templates/button-view-submission.tpl'),
    shareable_link_tpl = require('../templates/shareable-link.tpl'),
    edit_link_tpl = require('../templates/edit-shareable-link.tpl');

var ViewSurvey = (function() {
    var survey_id,
        survey_slug,
        good_slug = false,
        domain = document.location.origin;

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

        // TODO: is on input better?
        $(document).on('input', '.shareable-url-slug', function(e) {
            var slug = e.target.value,
                $input = $(e.target),
                $saveBtn = $('.save-survey-url');

            testSurveySlug(slug)
                .done(function() {
                    // good only if it's the current slug... the ajax request will return not error,
                    // but we should still be able to save.
                    good_slug = slug === survey_slug;
                })
                .fail(function(jqXHR) {
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
            setTimeout(function() {
                var slug = cleanSlug(e.target.value),
                    $input = $(e.target);
                $input.val(slug);
                // do something with text
            }, 1);
        });
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
        // Activity Graph
        $.getJSON('/api/v0/surveys/' + survey_id + '/activity', function(data) {

            var results = data.activity,
                cats = [];

            data = [];

            if (!results.length) {
                $('.no-activity-message').removeClass('hide');
                return;
            }

            var sorted = _.sortBy(results, function(result) {
                return result.date;
            });

            _.each(sorted, function(result) {
                var the_date = moment(result.date, 'YYYY-MM-DD').format('MMM D');

                data.push(result.num_submissions);
                cats.push(the_date);
            });


            $('.activity-graph').highcharts({
                chart: {
                    type: 'line'
                },
                title: {
                    text: null
                },
                colors: [
                    '#666'
                ],
                xAxis: {
                    categories: cats
                },
                yAxis: {
                    title: {
                        text: '# of submissions'
                    }
                },
                series: [{
                    name: 'Submissions',
                    data: data
                }],
                credits: {
                    enabled: false
                }
            });
        });
    }

    function setupDataTable() {
        // DataTables

        $('#submissions').dataTable({
            language: {
                search: 'Search by submitter name:'
            },
            'lengthMenu': [
                [5, 20, 50],
                [5, 20, 50]
            ],
            'pagingType': 'full_numbers',
            'order': [
                [1, 'desc']
            ],
            'columnDefs': [{
                data: 0,
                targets: 0
            }, {
                'data': 1,
                'render': function(data) {
                    var datetime = moment(data);
                    return datetime.format('MMM D, YYYY [at] HH:mm:ss');
                },
                'targets': 1
            }, {
                'data': 2,
                'render': function(data) {
                    var datetime = moment(data);
                    return datetime.format('MMM D, YYYY [at] HH:mm:ss');
                },
                'targets': 2
            }, {
                data: 3,
                'render': function(data) {
                    return view_sub_btn_tpl({
                        submission_id: data
                    });
                },
                'targets': 3,
                'sortable': false
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
                        var response = {
                            draw: json.draw,
                            recordsTotal: json.total_entries,
                            recordsFiltered: json.filtered_entries,
                            data: json.submissions.map(function(submission) {
                                return [
                                    submission.submitter_name,
                                    submission.save_time,
                                    submission.submission_time,
                                    submission.id
                                ];
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
