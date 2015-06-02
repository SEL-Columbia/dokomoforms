bundle.js: application.js widgets.js survey.js facilities.js 
	$(echo "Building bundle.js")
	browserfiy application.js -o bundle.js

clean:
	rm bundle.js

build:
	browserify application.js -o bundle.js
	sed -i "s/^# Version.*/# Version `date +%s`/" cache.appcache

all: bundle.js
