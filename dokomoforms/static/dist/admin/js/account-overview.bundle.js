(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
(function (global){
var $ = (typeof window !== "undefined" ? window['jQuery'] : typeof global !== "undefined" ? global['jQuery'] : null),
    _ = (typeof window !== "undefined" ? window['_'] : typeof global !== "undefined" ? global['_'] : null),
    moment = (typeof window !== "undefined" ? window['moment'] : typeof global !== "undefined" ? global['moment'] : null),
    base = require('./base'),
    view_btn_tpl = require('../templates/button-view-data.tpl'),
    manage_btn_tpl = require('../templates/button-manage-survey.tpl'),
    dl_btn_tpl = require('../templates/button-download-data.tpl');

var AccountOverview = (function() {

    function init() {
        base.init();

        loadActivityGraph();

        setupDataTable();
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
                                        JSON.stringify(survey.title),
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

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"../templates/button-download-data.tpl":4,"../templates/button-manage-survey.tpl":5,"../templates/button-view-data.tpl":6,"./base":2}],2:[function(require,module,exports){
(function (global){
var $ = (typeof window !== "undefined" ? window['jQuery'] : typeof global !== "undefined" ? global['jQuery'] : null),
    submissionModals = require('./submission-modal'),
    persona = require('../../common/js/persona');

module.exports = (function() {

    /**
     * [initTooltips description]
     * @return {[type]} [description]
     */
    function initTooltips() {
        // enable tooltips
        $('[data-toggle="tooltip"]').tooltip({
            container: 'body'
        });
    }


    function init() {
        initTooltips();

        // setup handlers for submission modals
        submissionModals.init();

        // setup handlers for persona events
        persona.init();
    }

    return {
        init: init
    };

})();

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"../../common/js/persona":8,"./submission-modal":3}],3:[function(require,module,exports){
(function (global){
var $ = (typeof window !== "undefined" ? window['jQuery'] : typeof global !== "undefined" ? global['jQuery'] : null);

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
        init: initSubmissionModalHandler
    };

})();

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{}],4:[function(require,module,exports){
module.exports = function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='<div class="btn-group">\n    <button class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown" aria-expanded="false">\n        <span class="glyphicon glyphicon-cloud-download"></span> Download Data <span class="caret"></span>\n    </button>\n    <ul class="dropdown-menu dropdown-menu-right" role="menu">\n        <li><a target="_blank" href="/api/v0/surveys/'+
((__t=( survey_id ))==null?'':__t)+
'/submissions?user_id='+
((__t=( current_user_id ))==null?'':__t)+
'">JSON</a></li>\n        <li><a href="#">CSV (coming soon)</a></li>\n        <li><a href="#">KML (maybe someday)</a></li>\n    </ul>\n</div>';
}
return __p;
};

},{}],5:[function(require,module,exports){
module.exports = function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='<a class="btn btn-secondary btn-xs btn-manage" href="/view/'+
((__t=( survey_id ))==null?'':__t)+
'" data-id="'+
((__t=( survey_id ))==null?'':__t)+
'">Manage Survey</a>';
}
return __p;
};

},{}],6:[function(require,module,exports){
module.exports = function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='<a class="btn btn-default btn-xs" href="/view/data/'+
((__t=( survey_id ))==null?'':__t)+
'">\n    <span class="glyphicon glyphicon-stats"></span> View Data\n</a>';
}
return __p;
};

},{}],7:[function(require,module,exports){
/*\
|*|
|*|  :: cookies.js ::
|*|
|*|  A complete cookies reader/writer framework with full unicode support.
|*|
|*|  Revision #1 - September 4, 2014
|*|
|*|  https://developer.mozilla.org/en-US/docs/Web/API/document.cookie
|*|  https://developer.mozilla.org/User:fusionchess
|*|
|*|  This framework is released under the GNU Public License, version 3 or later.
|*|  http://www.gnu.org/licenses/gpl-3.0-standalone.html
|*|
|*|  Syntaxes:
|*|
|*|  * docCookies.setItem(name, value[, end[, path[, domain[, secure]]]])
|*|  * docCookies.getItem(name)
|*|  * docCookies.removeItem(name[, path[, domain]])
|*|  * docCookies.hasItem(name)
|*|  * docCookies.keys()
|*|
\*/
module.exports = {
    getCookie: function(sKey) {
        if (!sKey) {
            return null;
        }
        return decodeURIComponent(document.cookie.replace(new RegExp('(?:(?:^|.*;)\\s*' + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, '\\$&') + '\\s*\\=\\s*([^;]*).*$)|^.*$'), '$1')) || null;
    },
    setCookie: function(sKey, sValue, vEnd, sPath, sDomain, bSecure) {
        if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) {
            return false;
        }
        var sExpires = '';
        if (vEnd) {
            switch (vEnd.constructor) {
                case Number:
                    sExpires = vEnd === Infinity ? '; expires=Fri, 31 Dec 9999 23:59:59 GMT' : '; max-age=' + vEnd;
                    break;
                case String:
                    sExpires = '; expires=' + vEnd;
                    break;
                case Date:
                    sExpires = '; expires=' + vEnd.toUTCString();
                    break;
            }
        }
        document.cookie = encodeURIComponent(sKey) + '=' + encodeURIComponent(sValue) + sExpires + (sDomain ? '; domain=' + sDomain : '') + (sPath ? '; path=' + sPath : '') + (bSecure ? '; secure' : '');
        return true;
    },
    removeCookie: function(sKey, sPath, sDomain) {
        if (!this.hasItem(sKey)) {
            return false;
        }
        document.cookie = encodeURIComponent(sKey) + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT' + (sDomain ? '; domain=' + sDomain : '') + (sPath ? '; path=' + sPath : '');
        return true;
    },
    hasCookie: function(sKey) {
        if (!sKey) {
            return false;
        }
        return (new RegExp('(?:^|;\\s*)' + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, '\\$&') + '\\s*\\=')).test(document.cookie);
    },
    getCookieKeys: function() {
        var aKeys = document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, '').split(/\s*(?:\=[^;]*)?;\s*/);
        for (var nLen = aKeys.length, nIdx = 0; nIdx < nLen; nIdx++) {
            aKeys[nIdx] = decodeURIComponent(aKeys[nIdx]);
        }
        return aKeys;
    }
};

},{}],8:[function(require,module,exports){
(function (global){
var $ = (typeof window !== "undefined" ? window['jQuery'] : typeof global !== "undefined" ? global['jQuery'] : null),
    cookies = require('./cookies');


var Persona = (function() {

    /**
     * Set up browser event handlers for login/logout buttons.
     */
    function setupBrowserEvents() {
        $(document).on('click', '.btn-login', function() {
            navigator.id.request();
        });
        $(document).on('click', '.btn-logout', function() {
            navigator.id.logout();
        });
    }

    function init() {
        'use strict';
        navigator.id.watch({
            loggedInUser: localStorage['email'] || null,
            onlogin: function(assertion) {
                $.ajax({
                    type: 'GET',
                    // GETting the same page onlogin prevents an issue when the
                    // user has multiple tabs open and logs in.
                    url: '',
                    success: function() {
                        var user = localStorage['email'] || null;
                        if (user === null) {
                            $.ajax({
                                type: 'POST',
                                url: '/user/login',
                                data: {
                                    assertion: assertion
                                },
                                headers: {
                                    'X-XSRFToken': cookies.getCookie('_xsrf')
                                },
                                success: function(res) {
                                    localStorage['email'] = res.email;
                                    // Pick where to go from ?next=
                                    var next_url = decodeURIComponent(window.location.search.substring(6));
                                    if (next_url) {
                                        location.href = next_url;
                                    } else {
                                        location.reload();
                                    }
                                },
                                error: function(xhr, status, err) {
                                    localStorage['login_error'] = err;
                                    navigator.id.logout();
                                }
                            });
                        }
                    }
                });
            },
            onlogout: function() {
                $.ajax({
                    type: 'POST',
                    url: '/user/logout', // The 'user' cookie is httponly
                    headers: {
                        'X-XSRFToken': cookies.getCookie('_xsrf')
                    },
                    success: function() {
                        localStorage.removeItem('email');
                        if (localStorage['login_error']) {
                            // TODO: clean this up
                            $('#msg').empty();
                            $('#msg').text('Login failure: ' + localStorage['login_error']);
                            localStorage.removeItem('login_error');
                        } else {
                            location.href = '/';
                        }
                    },
                    error: function(xhr, status, err) {
                        alert('Logout failure: ' + err);
                    }
                });
            }
        });

        setupBrowserEvents();
    }

    return {
        init: init
    };

})();

module.exports = Persona;
}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"./cookies":7}]},{},[1]);
