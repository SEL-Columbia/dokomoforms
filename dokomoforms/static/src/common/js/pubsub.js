var $ = require('jquery');

module.exports = (function() {

    var o = $({}),
        self = {};

    self.subscribe = function() {
        o.on.apply(o, arguments);
    };

    self.unsubscribe = function() {
        o.off.apply(o, arguments);
    };

    self.publish = function() {
        o.trigger.apply(o, arguments);
    };

    return self;

}());
