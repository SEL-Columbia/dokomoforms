browserify dokomoforms/static/application.js -o dokomoforms/static/bundle.js
sed -i "s/^# Version.*/# Version `date +%s`/" dokomoforms/static/cache.appcache
