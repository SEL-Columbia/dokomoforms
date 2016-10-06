var $ = require('jquery'),
    moment = require('moment'),
    base = require('./base'),
    _t = require('./lang');


var AccountOverview = (function() {

    function init() {
        base.init();
        if (window.CURRENT_USER_ID !== 'None') {
            if (window.CURRENT_USER_ROLE == 'enumerator') {
                setupEnumDataTable();
            }
        }
    }

    function setupEnumDataTable() {
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
                        return '<a target="_blank" href="/enumerate/' + data.id + '"">' + data.title + '</a>';
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
                    'data': 'id',
                    'targets': 2,
                    'visible': false
                }],
                'columns': [{
                    'name': 'title'
                },  {
                    'name': 'created_on'
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
                        // ?user_id=' + window.CURRENT_USER_ID
                        'url': '/api/v0/surveys',
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