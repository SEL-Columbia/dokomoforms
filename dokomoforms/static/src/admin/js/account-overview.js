var $ = require('jquery'),
    _ = require('lodash'),
    L = require('leaflet'),
    moment = require('moment'),
    base = require('./base'),
    ps = require('../../common/js/pubsub'),
    SubmissionModal = require('./modals/submission-modal'),
    view_btn_tpl = require('../templates/button-view-data.tpl'),
    manage_btn_tpl = require('../templates/button-manage-survey.tpl'),
    dl_btn_tpl = require('../templates/button-download-data.tpl'),
    recent_sub_tpl = require('../templates/recent-submission-row.tpl'),
    _t = require('./lang'),
    activityGraph = require('./activity-graph');

var AccountOverview = (function() {
    var recentSubmissions = [];

    function init() {
        base.init();
        if (window.CURRENT_USER_ID !== 'None') {
            loadActivityGraph();
            loadRecentSubmissions()
                .done(function(data) {
                    // store recent subs for detail modal browsing
                    recentSubmissions = _.pluck(data.submissions, 'id');
                    console.log('recentSubmissions', recentSubmissions);
                })
                .done(drawMap)
                .done(drawRecentSubs);
            setupDataTable();
            setupEventHandlers();

        }
    }

    function setupEventHandlers() {
        $(document).on('click', 'tr.submission-row', function() {
            // select this row in the datatable
            selectSubmissionRow($(this));
            var submission_id = $(this).data('id');
            var idx = recentSubmissions.indexOf(submission_id);
            new SubmissionModal({submissions: recentSubmissions, initialIndex: idx}).open();
        });

        ps.subscribe('submissions:select_row', function(e, el) {
            console.log(el);
            selectSubmissionRow($(el));
        });
    }

    function selectSubmissionRow($el) {
        $('tr.submission-row').removeClass('selected');
        $el.addClass('selected');
    }

    function drawRecentSubs(data) {
        console.log('drawRecentSubs', data);
        var submissions = data.submissions,
            $table = $('#recent-list table tbody');
        submissions.forEach(function(sub) {
            sub.submission_time = moment(sub.submission_time).format('MMM D, YYYY [at] HH:mm');
            sub.survey = {
                id: sub.survey_id,
                default_language: sub.survey_default_language
            };
            var displayData = _.extend(sub, { _t: _t});
            $table.append(recent_sub_tpl(displayData));
        });
    }

    function loadRecentSubmissions() {
        var limit = 5;
        return $.getJSON('/api/v0/submissions?order_by=save_time:DESC&limit=' + limit +
            '&fields=id,submission_time,submitter_name,survey_title,survey_id,survey_default_language,answers');
    }

    function drawMap(data) {
        console.log('drawMap');
        // Map
        var map;
        var submissions = data.submissions;
        if (submissions.length) {
            $(document).on('shown.bs.tab', 'a[href="#recent-map"]', function() {
                if (!map) {
                    map = L.map('recent-map-container', {
                        dragging: true,
                        zoom: 14,
                        attributionControl: false
                    });
                    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {}).addTo(map);
                    var markers = [];
                    _.each(submissions, function(submission) {
                        console.log(submission);
                        var answers = submission.answers,
                            locations = _.filter(answers, function(answer) {
                                return answer.type_constraint === 'location' || answer.type_constraint === 'facility';
                            });
                        // if no locations/facilties found, return
                        if (!locations || !locations.length) {
                            return;
                        }
                        locations.forEach(function(location) {
                            location = location.response;
                            // stored lon/lat in revisit, switch around
                            var marker = new L.marker([location.lat, location.lng], {
                                riseOnHover: true
                            });
                            marker.options.icon = new L.icon({
                                iconUrl: '/static/dist/admin/img/icons/normal_base.png',
                                iconAnchor: [15, 48]
                            });
                            // marker.bindPopup();
                            marker.on('click', function() {
                                new SubmissionModal({submission_id: submission.id}).open();
                            });
                            markers.push(marker);
                        });
                    });

                    if (markers.length) {
                        var markers_group = new L.featureGroup(markers);
                        markers_group.addTo(map);
                        map.fitBounds(markers_group.getBounds(), {
                            padding: [40, 40]
                        });
                    } else {
                        console.log('No submissions include location.');
                    }
                }
            });
        }
    }

    function loadActivityGraph() {

        activityGraph('/api/v0/surveys/activity?user_id=' + window.CURRENT_USER_ID, 30, '.activity-graph');

        // // Activity Graph
        // $.getJSON('/api/v0/surveys/activity?user_id=' + window.CURRENT_USER_ID, function(resp) {

        //     var results = resp.activity,
        //         cats = [],
        //         data = [];

        //     if (!results.length) {
        //         $('.no-activity-message').removeClass('hide');
        //         return;
        //     }

        //     var sorted = _.sortBy(results, function(result) {
        //         return result.date;
        //     });

        //     _.each(sorted, function(result) {
        //         var the_date = moment(result.date, 'YYYY-MM-DD').format('MMM D');
        //         data.push(result.num_submissions);
        //         cats.push(the_date);
        //     });


        //     $('.activity-graph').highcharts({
        //         chart: {
        //             type: 'column'
        //         },
        //         title: {
        //             text: null
        //         },
        //         colors: [
        //             '#666'
        //         ],
        //         xAxis: {
        //             categories: cats
        //         },
        //         yAxis: {
        //             title: {
        //                 text: '# of submissions'
        //             },
        //             allowDecimals: false
        //         },
        //         series: [{
        //             name: 'Submissions',
        //             data: data
        //         }],
        //         legend: {
        //             enabled: false
        //         },
        //         credits: {
        //             enabled: false
        //         }
        //     });
        // });
    }

    function setupDataTable() {
        // DataTables
        var $surveys = $('#surveys');

        if ($surveys.length > 0) {
            $('#surveys').dataTable({
                language: {
                    search: 'Search by survey title:'
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
                    'data': function(row) {
                        return {
                            title: row.title,
                            id: row.id
                        };
                    },
                    'targets': 0,
                    'render': function(data) {
                        return '<a href="/admin/' + data.id + '">' + data.title + '</a>';
                    }
                }, {
                    'data': 'created_on',
                    targets: 1,
                    'render': function(data, type, row) {
                        if (data) {
                            var datetime = moment(data);
                            return datetime.format('MMM D, YYYY');
                        } else {
                            return '';
                        }
                    }
                }, {
                    'data': 'num_submissions',
                    'targets': 2
                }, {
                    'data': 'latest_submission_time',
                    'render': function(data, type, row) {
                        if (data) {
                            var datetime = moment(data);
                            return datetime.format('MMM D, YYYY');
                        } else {
                            return '';
                        }
                    },
                    'targets': 3
                }, {
                    'data': 'id',
                    'render': function(data, type, row) {
                        // console.log(data);
                        var view = view_btn_tpl({
                                survey_id: data
                            }),
                            dl = dl_btn_tpl({
                                survey_id: data,
                                current_user_id: window.CURRENT_USER_ID
                            }),
                            manage = manage_btn_tpl({
                                survey_id: data
                            });

                        return view + '&nbsp;' + dl + '&nbsp;' + manage;
                    },
                    'targets': 4,
                    'width': '340px',
                    'class': 'text-center',
                    'sortable': false
                }, {
                    'data': 'id',
                    'targets': 5,
                    'visible': false
                }],
                'columns': [{
                    'name': 'title'
                },  {
                    'name': 'created_on'
                }, {
                    'name': 'num_submissions'
                }, {
                    'name': 'latest_submission_time'
                }, {
                    'name': 'id'
                }, {
                    'name': 'default_language'
                }],
                'processing': true,
                'serverSide': true,
                'ajax': function(data, callback, settings) {
                    $.ajax({
                        // This does not handle searching in the exact way specified by
                        // the DataTables documentation. Instead, it searches in the way
                        // that the API expects (search_term, search_fields).
                        'url': '/api/v0/surveys?user_id=' + window.CURRENT_USER_ID,
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
                            // TODO: search language???
                            search_fields: 'title'
                        },
                        'success': function(json) {
                            var response = {
                                draw: json.draw,
                                recordsTotal: json.total_entries,
                                recordsFiltered: json.filtered_entries,
                                data: json.surveys.map(function(survey) {
                                    return {
                                        title: _t(survey.title, survey),
                                        created_on: survey.created_on,
                                        num_submissions: survey.num_submissions,
                                        latest_submission_time: survey.latest_submission_time,
                                        id: survey.id
                                    };
                                })
                            };
                            callback(response);
                        }
                    });
                }
            });
        }
    }


    return {
        init: init
    };
})();

AccountOverview.init();
