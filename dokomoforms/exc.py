"""The base exception class is :py:class:`DokomoError`."""


class DokomoError(Exception):

    """The base class for all exceptions used in Dokomo Forms."""


class SurveyAccessForbidden(DokomoError):

    """The logged-in user does not have access to the survey."""


class NotJSONifiableError(DokomoError):

    """The jsonify function encountered a strange object."""


class NoSuchNodeTypeError(DokomoError):

    """Invalid type_constraint for construct_node.

    Raised when dokomoforms.models.node.construct_node is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.node.NODE_TYPES.
    """


class NoSuchSubmissionTypeError(DokomoError):

    """Invalid submission_type for construct_submission.

    Raised when dokomoforms.models.submission.construct_submission
    is called with an invalid submission_type.

    The valid types are 'unathenticated' and 'enumerator_only_submission'
    """


class NotAnAnswerTypeError(DokomoError):

    """Invalid type_constraint for construct_answer.

    Raised when dokomoforms.models.node.construct_answer is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.answer.ANSWER_TYPES.
    """


class UserRequiresEmailError(DokomoError):

    """A user must have at least one e-mail address."""


class PhotoIdDoesNotExistError(DokomoError):

    """The submitted photo ID does not exist in the database."""


class RequiredQuestionSkipped(DokomoError):

    """A submission has no answer for a required question."""


class NotAResponseTypeError(DokomoError):

    """Invalid response_type Answer.response.setter.

    Raised when trying to set the response field on an Answer with an invalid
    response_type.

    The valid response_types are 'answer', 'other', and 'dont_know'.
    """


class NoSuchBucketTypeError(DokomoError):

    """Invalid type_constraint for construct_bucket.

    Raised when dokomoforms.models.survey.construct_bucket is called with
    an invalid type_constraint.

    The valid type_constraints are the keys of
    dokomoforms.models.survey.BUCKET_TYPES.
    """


class InvalidTypeForOperation(DokomoError):

    """Invalid type for the selected aggregation function.

    For instance, you can't find the maximum of a text answer.
    """
