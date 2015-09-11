var $ = require('jquery'),
    ps = require('./pubsub'),
    tpl = require('../templates/notification.tpl');

var Notification = function(message, type) {
    console.log('Notification', type, message);

    // if no message supplied, ignore
    if (!message) {
        throw new Error('Notifications must include a message.');
    }

    type = type || 'info';

    var dataForDisplay = {
        type: type,
        message: message
    };

    var $notification = $(tpl(dataForDisplay));

    // append alert
    $('.notification-container').append($notification);

    $notification.slideDown(300);

    setTimeout(function() {
        $notification.slideUp(300, function() {
            $notification.remove();
        });
    }, 5000);


};


module.exports = Notification;
