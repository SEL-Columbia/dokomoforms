bundle.js: app.js
	browserify -t reactify app.js -o bundle.js
	sed -i "s/^# Version.*/# Version `date +%s`/" cache.appcache

clean:
	rm bundle.js

.PHONY: all clean 

all: bundle.js
