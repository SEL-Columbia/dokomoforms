var handlers = {};
navigator.id = {
        watch: function(obj) { handlers = obj; },
        request: function() { 
            handlers.onlogin('anything'); 
        },
        logout: function() { handlers.onlogout(); }
};
