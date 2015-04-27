module.exports = (function(url) {
    var jsdom = require('jsdom');
    var fs = require('fs');

    document = new jsdom.jsdom(fs.readFileSync("js_tests/widgets.html", "utf-8"),
        {
            features: {
                FetchExternalResources : ['script', 'css']
            },
            url: url || "http://localhost" //XXX Cross domain error otherwise
        });
    
    window = document._global;
    window.applicationCache = { 
        addEventListener : function() {}
    };

    script = document.createElement('script');
    script.text = fs.readFileSync("dokomoforms/static/lib.js", "utf-8");
    document.body.appendChild(script);

    script = document.createElement('script');
    script.text = fs.readFileSync("js_tests/lib/persona_include.js", "utf-8");
    document.body.appendChild(script);

    script = document.createElement('script');
    script.text = fs.readFileSync("js_tests/lib/classList_shim.js", "utf-8");
    document.body.appendChild(script);

    script = document.createElement('script');
    script.text = fs.readFileSync("js_tests/lib/jquery.mockjax.js", "utf-8");
    document.body.appendChild(script);

    //jsdom.getVirtualConsole(window).sendTo(console);

    // leaflet monkeypatches thanks to jieter on github
    window.L.Map.prototype.getSize = function () {
        return L.point(1024, 1024);
    };

    document._ce = document.createElement;
    document.createElement = function(elem) {
        var div = document._ce(elem);
        if (elem === 'canvas') {
            div.getContext = function() {
                return {
                    drawImage: function() {}
                }
            }

            div.toDataURL = function() { return "troolollol" }
        }

        return div;
    }

    return window;

})();
