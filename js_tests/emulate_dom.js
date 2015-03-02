module.exports = (function() {
   var jsdom = require('jsdom');
   var fs = require('fs');
   document = new jsdom.jsdom(fs.readFileSync("js_tests/widgets.html", "utf-8"),
           {
               url: "http://localhost:7777"
           });
   window = document.parentWindow;

   script = document.createElement('script');
   script.text = fs.readFileSync("static/lib.js", "utf-8");
   document.body.appendChild(script);

   script = document.createElement('script');
   script.text = fs.readFileSync("js_tests/lib/persona_include.js", "utf-8");
   document.body.appendChild(script);

   script = document.createElement('script');
   script.text = fs.readFileSync("js_tests/lib/classList_shim.js", "utf-8");
   document.body.appendChild(script);

   jsdom.getVirtualConsole(window).sendTo(console);

   return window;

})();
