echo "SETTING ENV"
export ISTANBUL_REPORTERS=text-summary,text

echo "INSTRUMENTING app.js"
./node_modules/.bin/istanbul instrument --output static/app.js.ist static/app.js

echo "MOVING app.js to app.js.og"
mv static/app.js static/app.js.og && mv static/app.js.ist static/app.js

echo "RUNNING mocha && istanbul"
./node_modules/.bin/mocha -R mocha-istanbul test/

echo "MOVING app.js.og back to app.js"
mv static/app.js.og static/app.js
