# Dokomo Forms

Dokomo Forms is a free and open source data collection and analysis platform.

[![Build Status](https://travis-ci.org/SEL-Columbia/dokomoforms.svg?branch=master)](https://travis-ci.org/SEL-Columbia/dokomoforms)
[![Coverage Status](https://coveralls.io/repos/SEL-Columbia/dokomoforms/badge.svg?branch=master)](https://coveralls.io/r/SEL-Columbia/dokomoforms?branch=master)
[![Documentation Status](https://readthedocs.org/projects/dokomoforms/badge/?version=latest)](https://readthedocs.org/projects/dokomoforms/?badge=latest)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/SEL-Columbia/dokomoforms?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Dependency Status](https://gemnasium.com/SEL-Columbia/dokomoforms.svg)](https://gemnasium.com/SEL-Columbia/dokomoforms)
[![Sauce Test Status](https://saucelabs.com/browser-matrix/dokomo_sauce_matrix.svg)](https://saucelabs.com/u/dokomo_sauce_matrix)

## About the Project

Several solutions exist to handle offline mobile data collection. While this type of technology is increasingly valuable to organizations working in the developing world, the available solutions are cumbersome to use, often requiring a confusing mélange of individual software components and advanced technical skills to setup and manage.

**Dokomo strives to simplify the process by integrating the elements of a data collection effort into a unified system, from creation of mobile-ready surveys to quick analysis and visualization of the collected data.**

## Features

#### Mobile-Web Technology

Instead of relying on platform-specific apps, Dokomo's surveys are conducted using an offline-capable mobile web app. This makes for an easier workflow for enumerators and administrators — surveys can be accessed via a normal web link, and can be conducted on (almost) any device that has a web browser.

![alt Dokomo Forms Admin - Manage](https://i.imgur.com/saW5zcB.jpg)

#### Survey Monitoring

As an adminstrator of a surveying effort, it's important to know where, when, and by whom data is being submitted. Dokomo Forms lets administrators quickly see the current progress of an effort, providing a quick list and map of the latest submissions and a graph showing submissions/day for the recent past.

![alt Dokomo Forms Admin - Manage](https://i.imgur.com/6z7UJt2.jpg)

#### Submission Data Quick Views

Administrators can quickly view data from individual submissions and get some basic statistics and aggregations from each question on a survey.

![alt Dokomo Forms Admin - Data](https://i.imgur.com/hwYRf8e.jpg)

#### Revisit Integration

Dokomo Forms integrates with [Revisit](http://revisit.global), a global facility registry API built here at the Sustainable Engineering Lab. Leveraging Revisit, multiple surveys conducted at the same facility can be easily linked, allowing changes in data points at survey locations to be tracked over time.

## Under Development

Dokomo Forms is under active development, with some pretty nifty features on the horizon.

#### Survey Creation GUI

Soon survey administrators will be able to quickly create surveys though a web-based creation tool, built directly into Dokomo Forms.

#### Better Survey Administration

- Publish surveys directly from the administration panel to enumerators' mobile devices.
- Send updates and communications to enumerators

#### Data Visualization

- View collected data on map
- See quick statistics and aggregations on a per-question basis

## Guides and Documentation

- [User Guide](https://github.com/SEL-Columbia/dokomoforms/wiki/User-Guide)
- [Local Development Environment Setup](https://github.com/SEL-Columbia/dokomoforms/wiki/Local-Development-Environment)
- [Deployment](https://github.com/SEL-Columbia/dokomoforms/wiki/Deployment)
- [REST API Documentation](https://github.com/SEL-Columbia/dokomoforms/wiki/REST-API-v0.2.0)
