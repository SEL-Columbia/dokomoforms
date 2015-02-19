module.exports = (function() {
   var jsdom = require('jsdom').jsdom;
   var fs = require('fs');
   document = new jsdom(fs.readFileSync("js_tests/widgets.html", "utf-8"));
   window = document.parentWindow;

   script = document.createElement('script');
   script.text = fs.readFileSync("static/lib.js", "utf-8");
   document.body.appendChild(script);

   script = document.createElement('script');
   script.text = fs.readFileSync("js_tests/lib/classList_shim.js", "utf-8");
   document.body.appendChild(script);

   return window;

})();
