"""Exceptions in dokomoforms.

The base exception class is dokomoforms.exc.DokomoError
"""


class DokomoError(Exception):

    """The base class for all exceptions used in Dokomo Forms."""


class NoSuchNodeTypeError(DokomoError):

    """Invalid type_constraint for construct_node.

    Raised when dokomoforms.models.node.construct_node is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.node.NODE_TYPES.
    """


class NoSuchSubmissionTypeError(DokomoError):
    """
    Raised when dokomoforms.models.submission.construct_submission
    is called with an invalid submission_type.

    The valid types are 'unathenticated' and 'authenticated'
    """


class NotAnAnswerTypeError(DokomoError):

    """Invalid type_constraint for construct_answer.

    Raised when dokomoforms.models.node.construct_answer is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.answer.ANSWER_TYPES.
    """


class NoSuchBucketTypeError(DokomoError):

    """Invalid type_constraint for construct_bucket.

    Raised when dokomoforms.models.survey.construct_bucket is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.survey.BUCKET_TYPES.
    """
