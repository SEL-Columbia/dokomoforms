module.exports = function() {
    var jsdom = require('jsdom').jsdom;
    var fs = require('fs');
    global.document = jsdom(fs.readFileSync("test/widgets.html", "utf-8"));
    global.window = document.parentWindow;
    window.localStorage = {};

   //var features = document.implementation._features;

   script = document.createElement('script');
   //script.onload = function() {
   //    document.implementation._features = features;
   //};
   script.text = fs.readFileSync("static/lib.js", "utf-8");
   document.body.appendChild(script);

   script = document.createElement('script');
   //script.onload = function() {
   //    document.implementation._features = features;
   //};
   script.text = fs.readFileSync("test/lib/classList_shim.js", "utf-8");
   document.body.appendChild(script);

};
