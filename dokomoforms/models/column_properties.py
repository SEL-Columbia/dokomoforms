"""Extra properties for models.

These could not be defined inline with the models do to import issues. See
http://docs.sqlalchemy.org/en/rel_1_0/orm/mapped_sql_expr.html
#using-column-property

"""
import sqlalchemy as sa
from sqlalchemy.orm import column_property, object_session
from sqlalchemy.sql.functions import Function

from dokomoforms.models import (
    Answer, Node, Survey, Submission, AnswerableSurveyNode,
    survey_sequentialization
)
from dokomoforms.models.answer import ANSWER_TYPES
from dokomoforms.exc import InvalidTypeForOperation


# Answer
Answer.question_title = column_property(
    sa.select([Node.title])
    .where(Node.id == Answer.question_id)
    .label('question_title')
)


# Survey
Survey.num_submissions = column_property(
    sa.select([sa.func.count(Submission.id)])
    .where(Submission.survey_id == Survey.id)
    .label('num_submissions')
)


Survey.earliest_submission_time = column_property(
    sa.select([sa.func.min(Submission.save_time)])
    .where(Submission.survey_id == Survey.id)
    .label('earliest_submission_time')
)


Survey.latest_submission_time = column_property(
    sa.select([sa.func.max(Submission.save_time)])
    .where(Submission.survey_id == Survey.id)
    .label('latest_submission_time')
)


# AnswerableSurveyNode
AnswerableSurveyNode.answer_count = column_property(
    sa.select([sa.func.count(Answer.id)])
    .where(Answer.survey_node_id == AnswerableSurveyNode.id)
    .label('answer_count')
)


def _answer_stat(survey_node: AnswerableSurveyNode,
                 allowable_types: set,
                 func: Function) -> object:
    type_constraint = survey_node.the_type_constraint
    if type_constraint not in allowable_types:
        raise InvalidTypeForOperation(
            (type_constraint, func._FunctionGenerator__names[0])
        )
    answer_cls = ANSWER_TYPES[survey_node.the_type_constraint]
    return (
        object_session(survey_node)
        .scalar(
            sa.select([func(answer_cls.main_answer)])
            .where(answer_cls.survey_node_id == survey_node.id)
        )
    )


def answer_min(survey_node: AnswerableSurveyNode):
    """Get the minimum answer."""
    return _answer_stat(
        survey_node,
        {'integer', 'decimal', 'date', 'time', 'timestamp'},
        sa.func.min,
    )


def answer_max(survey_node: AnswerableSurveyNode):
    """Get the maximum answer."""
    return _answer_stat(
        survey_node,
        {'integer', 'decimal', 'date', 'time', 'timestamp'},
        sa.func.max,
    )


def answer_sum(survey_node: AnswerableSurveyNode):
    """Get the sum of the answers."""
    return _answer_stat(
        survey_node,
        {'integer', 'decimal'},
        sa.func.sum,
    )


def answer_avg(survey_node: AnswerableSurveyNode):
    """Get the average of the answers."""
    return _answer_stat(
        survey_node,
        {'integer', 'decimal'},
        sa.func.avg,
    )


def answer_mode(survey_node: AnswerableSurveyNode):
    """Get the mode of the answers."""
    type_constraint = survey_node.the_type_constraint
    allowable_types = {
        'text', 'integer', 'decimal', 'date', 'time', 'timestamp', 'location',
        'facility', 'multiple_choice'
    }
    if type_constraint not in allowable_types:
        raise InvalidTypeForOperation((type_constraint, 'mode'))
    answer_cls = ANSWER_TYPES[survey_node.the_type_constraint]
    return (
        object_session(survey_node)
        .execute(sa.text(
            "SELECT MODE() WITHIN GROUP (ORDER BY main_answer) AS answer_mode"
            " FROM {table} JOIN {answer_table} ON"
            " {table}.id = {answer_table}.id"
            " WHERE {answer_table}.survey_node_id = '{survey_node_id}'".format(
                table=str(answer_cls.__table__),
                answer_table=str(Answer.__table__),
                survey_node_id=survey_node.id,
            )
        ))
        .scalar()
    )


def answer_stddev_pop(survey_node: AnswerableSurveyNode):
    """Get the population standard deviation of the answers."""
    return _answer_stat(
        survey_node,
        {'integer', 'decimal'},
        sa.func.stddev_pop,
    )


def answer_stddev_samp(survey_node: AnswerableSurveyNode):
    """Get the sample standard deviation of the answers."""
    return _answer_stat(
        survey_node,
        {'integer', 'decimal'},
        sa.func.stddev_samp,
    )


def _question_stats(survey_node):
    yield {'query': 'count', 'result': survey_node.answer_count}
    aggregators = (
        (answer_min, 'min'),
        (answer_max, 'max'),
        (answer_sum, 'sum'),
        (answer_avg, 'avg'),
        (answer_mode, 'mode'),
        (answer_stddev_pop, 'stddev_pop'),
        (answer_stddev_samp, 'stddev_samp'),
    )
    for func, name in aggregators:
        try:
            yield {'query': name, 'result': func(survey_node)}
        except InvalidTypeForOperation:
            pass


def generate_question_stats(survey):
    """Get answer statistics for the nodes in a survey."""
    answerable_survey_nodes = survey_sequentialization(
        survey, include_non_answerable=False
    )
    for survey_node in answerable_survey_nodes:
        stats = list(_question_stats(survey_node))
        yield {'survey_node': survey_node, 'stats': stats}
