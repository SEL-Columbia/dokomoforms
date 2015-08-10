REVISIT_URL = $(shell grep -r ^REVISIT_URL revisit.conf)

bundle.js: Application.js Facilities.js PhotoAPI.js $(wildcard components/baseComponents/*.js) $(wildcard components/*.js)
	sed -i '1 s|^.*|var $(REVISIT_URL)|g' Facilities.js
	browserify -t reactify Application.js -o bundle.js
	sed -i "s/^# Version.*/# Version `date +%s`/" cache.appcache

clean:
	rm bundle.js

.PHONY: all clean 

all: bundle.js
