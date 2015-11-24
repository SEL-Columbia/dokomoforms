# JavaScript Tests

### Unit Tests

The frontend javascript is set up for unit testing using the [Jest](http://facebook.github.io/jest/) testing framework. At the time of this writing, only a small portion of the javascript code base was adequately unit tested, but each React component has a stub test file which can be populated with tests.

As per Jest's recommended best practice, tests for components are located in an **__tests__** directory which sits along side the components themselves.

#### Running the Unit Tests

Assuming the npm dependencies have been installed, run `$ npm test`.

### Functional Tests

Frontend functionality is covered using Selenium tests. These tests can be found in **/tests/python/test_selenium.py**. For more info about running these tests, see [the wiki](https://github.com/SEL-Columbia/dokomoforms/wiki/Local-Development-Environment#running-tests).
