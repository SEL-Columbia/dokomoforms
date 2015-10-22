var $ = require('jquery'),
    _ = require('lodash'),
    L = require('leaflet'),
    moment = require('moment'),
    base = require('./base'),
    submissionModal = require('./submission-modal'),
    view_btn_tpl = require('../templates/button-view-data.tpl'),
    manage_btn_tpl = require('../templates/button-manage-survey.tpl'),
    dl_btn_tpl = require('../templates/button-download-data.tpl'),
    recent_sub_tpl = require('../templates/recent-submission-row.tpl'),
    _t = require('./lang');

var AccountOverview = (function() {

    function init() {
        base.init();
        if (window.CURRENT_USER_ID !== 'None') {
            loadActivityGraph();
            loadRecentSubmissions()
                .done(drawMap)
                .done(drawRecentSubs);
            // drawMap();
            setupDataTable();
        }
    }

    function drawRecentSubs(recentSubs) {
        console.log('drawRecentSubs');

        recentSubs.forEach(function(sub) {
            console.log(sub);

        });
    }

    function loadRecentSubmissions() {
        var limit = 5;
        return $.getJSON('/api/v0/submissions?order_by=save_time:DESC&limit=' + limit);
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
                                submissionModal.openSubmissionDetailModal(submission.id);
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
        // Activity Graph
        $.getJSON('/api/v0/surveys/activity?user_id=' + window.CURRENT_USER_ID, function(resp) {

            var results = resp.activity,
                cats = [],
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
                    [2, 'desc']
                ],
                'columnDefs': [{
                    'data': 0,
                    'render': function(data, type, row) {
                        return data;
                    },
                    'targets': 0
                }, {
                    'data': 1,
                    targets: 1
                }, {
                    'data': 2,
                    'render': function(data, type, row) {
                        if (data) {
                            var datetime = moment(data);
                            return datetime.format('MMM D, YYYY');
                        } else {
                            return '';
                        }
                    },
                    'targets': 2
                }, {
                    'data': 3,
                    'render': function(data, type, row) {
                        return '...'; // TODO: ask @jmwohl about this.
                    },
                    'targets': 3,
                    'sortable': false
                }, {
                    'data': 3,
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
                }],
                'columns': [{
                    'name': 'title'
                }, {
                    'name': 'num_submissions'
                }, {
                    'name': 'latest_submission_time'
                }, {
                    'name': 'id'
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
                                    return [
                                        _t(survey.title),
                                        survey.num_submissions,
                                        survey.latest_submission_time,
                                        survey.id
                                    ];
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
