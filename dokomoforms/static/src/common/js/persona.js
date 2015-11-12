var $ = require('jquery'),
    cookies = require('./cookies');


var Persona = (function() {

    /**
     * Set up browser event handlers for login/logout buttons.
     */
    function setupBrowserEvents() {
        console.log('setupBrowserEvents');
        $(document).on('click', '.btn-login', function(e) {
            e.preventDefault();
            navigator.id.request();
        });
        $(document).on('click', '.btn-logout', function(e) {
            e.preventDefault();
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
