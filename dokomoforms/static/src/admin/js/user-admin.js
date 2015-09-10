var $ = require('jquery'),
    _ = require('lodash'),
    base = require('./base'),
    Users = require('./models').Users,
    User = require('./models').User,
    UserModal = require('./modals/user-modal'),
    edit_btn_tpl = require('../templates/button-edit-user.tpl'),
    email_link_tpl = require('../templates/email-link.tpl');

var UserAdmin = (function() {
    var modal;

    function init() {
        base.init();
        if (window.CURRENT_USER_ID !== 'None') {
            setupDataTable();

            setupEventHandlers();
        }
    }

    function setupEventHandlers() {
        $(document).on('click', '.btn-edit-user, .btn-add-user', function() {
            var user_id = $(this).data('id') || null;
            modal = new UserModal(user_id);
        });
    }

    function setupDataTable() {
        // DataTables
        var $users = $('#users');

        if ($users.length > 0) {
            $users.dataTable({
                language: {
                    search: 'Search users:'
                },
                'lengthMenu': [
                    [20, 50, 100],
                    [20, 50, 100]
                ],
                'pagingType': 'full_numbers',
                'order': [
                    [0, 'asc']
                ],
                'columnDefs': [{
                    'data': 0,
                    'targets': 0
                }, {
                    'data': 1,
                    'render': function(data) {
                        return email_link_tpl({
                            email_address: data
                        });
                    },
                    'targets': 1
                }, {
                    'data': 2,
                    'targets': 2
                }, {
                    'data': 3,
                    'render': function(data) {
                        return '...'; // TODO: ask @jmwohl about this.
                    },
                    'targets': 3,
                    'sortable': false
                }, {
                    'data': 4,
                    'render': function(data) {
                        console.log(data);
                        return edit_btn_tpl({
                            user_id: data
                        });
                    },
                    'targets': 4,
                    'class': 'text-center',
                    'sortable': false
                }],
                'columns': [{
                    'name': 'name'
                }, {
                    'name': 'emails'
                }, {
                    'name': 'role'
                }, {
                    'name': 'allowed_surveys'
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
                        'url': '/api/v0/users',
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
                            search_fields: 'name'
                        },
                        'success': function(json) {
                            var response = {
                                draw: json.draw,
                                recordsTotal: json.total_entries,
                                recordsFiltered: json.filtered_entries,
                                data: json.users.map(function(user) {
                                    return [
                                        user.name,
                                        user.emails[0],
                                        user.role,
                                        user.allowed_surveys,
                                        user.id
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

UserAdmin.init();
