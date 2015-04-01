"""API endpoints dealing with data tables."""
from collections import Iterator

from sqlalchemy import select, distinct
from sqlalchemy.sql.functions import count
from tornado.escape import json_encode, json_decode

from dokomoforms.db import auth_user_table, survey_table, submission_table
from dokomoforms.handlers.util.base import APIHandler


def _get_orderings(args: dict) -> Iterator:
    for ordering in args['order']:
        idx = ordering['column']
        direction = ordering['dir']
        yield '{} {}'.format(args['columns'][idx]['name'], direction)


class SurveyDataTableHandler(APIHandler):
    """The endpoint for getting a user's surveys for use in a jQuery
    DataTable."""

    def get(self):
        args = json_decode(self.get_argument('args'))
        email = self.get_email()

        total_query = select(
            [count(distinct(survey_table.c.survey_id))]
        ).select_from(
            auth_user_table.join(survey_table)
        ).where(
            auth_user_table.c.email == email
        )
        total_surveys = self.db.execute(total_query).scalar()

        table = auth_user_table.join(survey_table).outerjoin(submission_table)
        submission_id = submission_table.c.submission_id
        submission_count = count(distinct(submission_id))
        survey_title = survey_table.c.survey_title
        query = select(
            [survey_title,
             submission_count.label('num_submissions'),
             count().over()]
        ).select_from(
            table
        ).group_by(
            survey_title, survey_table.c.created_on
        ).where(
            auth_user_table.c.email == email
        )

        # Title filter
        search_value = args['search']['value']
        if search_value:
            query = query.where(
                survey_title.like('%{}%'.format(search_value))
            )

        # Ordering
        if args['order']:
            query = query.order_by(', '.join(_get_orderings(args)))
        else:
            query = query.order_by('created_on asc')

        # Limiting
        limit = int(args['length'])
        if limit != -1:
            offset = int(args.get('start', 0))
            query = query.limit(limit).offset(offset)

        result = self.db.execute(query).fetchall()

        response = {
            'draw': int(args['draw']),
            'recordsTotal': total_surveys,
            'recordsFiltered': result[0][2] if result else 0,
            'data': [
                [str(title), str(num)] for title, num, _ in result
            ]
        }
        self.write(json_encode(response))
