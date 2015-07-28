"""Extra properties for models.

These could not be defined inline with the models do to import issues. See
http://docs.sqlalchemy.org/en/rel_1_0/orm/mapped_sql_expr.html
#using-column-property

"""
import sqlalchemy as sa
from sqlalchemy.orm import column_property, object_session

from dokomoforms.models import (
    Answer, Node, Survey, Submission, AnswerableSurveyNode
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
AnswerableSurveyNode.count = column_property(
    sa.select([sa.func.count(Answer.id)])
    .where(Answer.survey_node_id == AnswerableSurveyNode.id)
    .label('answer_count')
)


def answer_min(survey_node: AnswerableSurveyNode):
    """Get the minimum answer."""
    type_constraint = survey_node.the_type_constraint
    allowable_types = {'integer', 'decimal', 'date', 'time', 'timestamp'}
    if type_constraint not in allowable_types:
        raise InvalidTypeForOperation((type_constraint, 'min'))
    answer_cls = ANSWER_TYPES[survey_node.the_type_constraint]
    return (
        object_session(survey_node)
        .scalar(
            sa.select([sa.func.min(answer_cls.main_answer)])
            .where(answer_cls.survey_node_id == survey_node.id)
        )
    )
