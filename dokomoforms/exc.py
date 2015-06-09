"""
Exceptions in dokomoforms.

The base exception class is dokomoforms.exc.DokomoError
"""


class DokomoError(Exception):
    """The base class for all exceptions used in Dokomo Forms."""


class NoSuchNodeTypeError(DokomoError):
    """
    Raised when dokomoforms.models.node.construct_node is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.node.NODE_TYPES.
    """


class NoSuchBucketTypeError(DokomoError):
    """
    Raised when dokomoforms.models.survey.construct_bucket is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.survey.BUCKET_TYPES.
    """
