var $ = require('jquery'),
    uuid = require('uuid'),
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
        loginUrl = '/?next=' + encodeURIComponent(curUrl) + '&logged-in=' + uuid.v4();

    console.log('logIn: ', loginUrl);

    logOut().done(function() {
        console.log('logIn: ', loginUrl);
        window.location.href = loginUrl;
    });
}

module.exports = {
    logOut: logOut,
    logIn: logIn
};
