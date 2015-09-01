function getCookie(name) {
    'use strict';
    // Apparently this is what you have to do to get a cookie in JavaScript...
    if (!name) {
        return null;
    }
    return decodeURIComponent(document.cookie.replace(new RegExp('(?:(?:^|.*;)\\s*' + encodeURIComponent(name).replace(/[\-\.\+\*]/g, '\\$&') + '\\s*\\=\\s*([^;]*).*$)|^.*$'), '$1')) || null;
}

(function() {
    'use strict';
    navigator.id.watch({
        loggedInUser: localStorage['email'] || null,
        onlogin: function(assertion) {
            $.ajax({
                type: 'GET',
                // GETting the same page onlogin prevents an issue when the
                // user has multiple tabs open and logs in.
                url: '',
                success: function(res, status, xhr) {
                    var user = localStorage['email'] || null;
                    if (user === null) {
                        $.ajax({
                            type: 'POST',
                            url: '/user/login',
                            data: {
                                assertion: assertion
                            },
                            headers: {
                                'X-XSRFToken': getCookie('_xsrf')
                            },
                            success: function(res, status, xhr) {
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
                    'X-XSRFToken': getCookie('_xsrf')
                },
                success: function(res, status, xhr) {
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

    $(document).on('click', '.btn-login', function() {
        navigator.id.request();
    });
    $(document).on('click', '.btn-logout', function() {
        navigator.id.logout();
    });
})();
