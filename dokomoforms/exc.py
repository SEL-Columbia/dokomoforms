"""
Exceptions in dokomoforms.

The base exception class is dokomoforms.exc.DokomoError
"""


class DokomoError(Exception):
    """The base class for all exceptions used in Dokomo Forms."""


class NoSuchSurveyNodeTypeError(DokomoError):
    """
    Raised when dokomoforms.models.survey.construct_survey_node is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.survey.SURVEY_NODE_TYPES.
    """
