var $ = require('jquery'),
    cookies = require('../../../common/js/cookies');


function logOut() {
    console.log('log out');

    return $.ajax({
        method: 'POST',
        url: '/user/logout',
        headers: {
            'X-XSRFToken': cookies.getCookie('_xsrf')
        }
    });
}

function logIn() {
    var curUrl = window.location.pathname,
        loginUrl = '/?next=' + encodeURIComponent(curUrl);

    logOut().done(function() {
        window.location.href = loginUrl;
    });
}

module.exports = {
    logOut: logOut,
    logIn: logIn
};
