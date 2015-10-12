var $ = require('jquery'),
    _ = require('lodash'),
    base = require('./base'),
    moment = require('moment'),
    view_sub_btn_tpl = require('../templates/button-view-submission.tpl');

var ViewSurvey = (function() {
    var survey_id;

    function init(_survey_id) {
        survey_id = _survey_id;
        base.init();
        if (window.CURRENT_USER_ID !== 'None') {
            populateSurveyUrl(survey_id);
            loadActivityGraph();
            setupDataTable();
        }
    }

    function populateSurveyUrl(survey_id) {
        var domain = document.location.origin;
        $('#shareable-link').val(domain + '/enumerate/' + survey_id);
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

                console.log(the_date);

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
