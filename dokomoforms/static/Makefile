bundle.js: Application.js FacilityAPI.js PhotoAPI.js $(wildcard components/baseComponents/*.js) $(wildcard components/*.js)
	browserify -t reactify Application.js -o bundle.js
	sed -i "s/^# Version.*/# Version `date +%s`/" cache.appcache

clean:
	rm bundle.js

.PHONY: all clean 

all: bundle.js
