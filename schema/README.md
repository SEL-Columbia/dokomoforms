<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [[Schema](relationships.real.large.png) (click for diagram)](#schemarelationshipsreallargepng-click-for-diagram)
  - [High level](#high-level)
    - [Survey](#survey)
      - [Question](#question)
    - [Submission](#submission)
      - [Answer](#answer)
  - [Specifics](#specifics)
    - [Question choices](#question-choices)
    - [Question branching](#question-branching)
  - [Notes](#notes)
      - [No logical constraints](#no-logical-constraints)
      - [Geolocation support](#geolocation-support)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#[Schema](relationships.real.large.png) (click for diagram)

##High level

###Survey
At the top level, there is the survey table, which questions must reference by foreign key.

####Question
Questions have:
- a text description
- an optional hint
- a sequence number to determine the order within the survey
- a type (to constrain valid response types)

###Submission
At the top level, there is the submission table, which references a survey by foreign key and which answers must reference by foreign key.

####Answer
The answer table contains one row per answer, which must be associated with a valid submission and question. The answer type is constrained by the question type.

##Specifics

###Question choices
Because certain question types must provide the user with pre-defined choices, there is a table for choices which references the question table by foreign key. Answers to these questions go in special answer tables which reference choices by foreign key.

###Question branching
The survey creator may want to show a certain question conditionally based on the response a user gives to an earlier question. To represent this, there is a question branch table which links questions together on choices and enforces that a question can only point to another question with a larger sequence number (this prevents loops and other silliness).

##Notes

####No logical constraints
The tables only have type-level constraints (e.g., integer versus text) rather than logical constraints (min and max). While we could try to put these into the database, logical constraints can get messy fast. In order to allow for flexible constraints, the database can have a text or json field for "question metadata" and let the application deal with logical constraints.

####Geolocation support
PostgreSQL has plugins which allow for nice location support: distances, coordinates, polygons, etc.
