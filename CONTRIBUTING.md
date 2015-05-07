# Contributor's Guide

Dokomo Forms is an open-source project and we encourage people to open issues at https://github.com/SEL-Columbia/dokomoforms/issues for bug reports and feature requests. We also accept pull requests as long as they meet our guidelines.

## Issues

If you notice a problem when using Dokomo Forms or perusing its source code, feel free to open an issue at https://github.com/SEL-Columbia/dokomoforms/issues. Please include as much relevant information as you can, such as the steps leading to the problem, or a screenshot depicting it.

You should also open an issue if you feel that Dokomo Forms is missing a feature.

Once you open an issue, the developers of Dokomo Forms will receive a notification and take a look. If it is a bug report, we will leave comments on the issue's page pertaining to the issue's scope and severity, as well as how we intend to handle it. If it is a feature request, we will discuss whether we want to implement the requested feature and, if so, how we intend to do that.

## Pull requests

If you wish to make a code contribution to Dokomo Forms, please follow the steps below in order to open a pull request on the dokomoforms GitHub repository.  If you do not follow these steps, we may ask you to modify your pull request, or make the necessary changes ourselves.

Take a look at GitHub's guide to contributing to Open Source projects for reference: https://guides.github.com/activities/contributing-to-open-source/

1. Open or comment on an issue.

  * If an issue exists for your bug or feature, write a comment explaining that you would like to help fix it.

  * If an issue doesn't exist for the bug you intend to fix or the feature you intend to implement, open one at https://github.com/SEL-Columbia/dokomoforms/issues with a description of the existing behavior and the desired behavior.

2. Fork the https://github.com/SEL-Columbia/dokomoforms repository. Refer to https://help.github.com/articles/fork-a-repo/.

3. One of your commits, possibly the first one, should reference the issue from step 1 in its commit message: https://help.github.com/articles/closing-issues-via-commit-messages/

  This associates your fork with the issue, and automatically closes the issue if your pull request is accepted.

4. If you are fixing a bug, the first thing you should do in your fork is write one or more test cases that assert correct behavior but fail due to the bug.

  Add your tests to the files in the [tests](/tests) directory according to which code path or paths are involved.

  Please end the commit message of any commit which adds a failing test like so: `... [Adds test TestClassName.testName]`

5. Write your code. 

  * Please try to follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines for Python code. 

  * Documentation and comments are important! 

  * Try to keep functions short. One small function that calls several other small functions is preferable to one huge function.

  * Sync your fork often to avoid large merge conflicts. Refer to https://help.github.com/articles/syncing-a-fork/

6. Add tests to the [tests](/tests) directory that cover your code contributions. As much as possible, these tests should assert all possible scenarios your contribution could encounter.

  If you are fixing a bug, make sure that your contribution causes any tests you wrote in step 4 to pass.

7. When you feel that your contribution is ready to be pulled into the SEL-Columbia/dokomoforms repository, open a pull request. The Dokomo Forms developers will take a look at your contribution and communicate with you if we would like you to make any changes.

  Once everything is in order, we will accept your pull request.
  
