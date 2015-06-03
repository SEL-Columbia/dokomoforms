bundle.js: application.js widgets.js survey.js facilities.js 
	browserify application.js -o bundle.js
	sed -i "s/^# Version.*/# Version `date +%s`/" cache.appcache

clean:
	rm bundle.js

.PHONY: all update clean 

all: bundle.js
