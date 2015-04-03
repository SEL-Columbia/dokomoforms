"""
API endpoints dealing with data tables. Ideas taken from
https://github.com/DataTables/DataTables/blob
/e0f2cfd81e61103d88ea215797bdde1bc19a2935/examples/server_side/scripts/ssp
.class.php
"""
from collections import Iterator

from sqlalchemy import select, Table, Column
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import count
from tornado.escape import json_encode, json_decode

from dokomoforms.db import auth_user_table, survey_table, submission_table
from dokomoforms.db.submission import get_number_of_submissions
from dokomoforms.db.survey import get_number_of_surveys
from dokomoforms.handlers.util.base import APIHandler


def _base_query(table: Table,
                email: str,
                selected: list,
                *,
                grouped: list=None,
                where: BinaryExpression=None) -> Select:
    """
    Return a query for a DataTable without any text filtering, ordering,
    or limiting applied.

    :param table: the SQLAlchemy table. Should be one or more tables joined
                  with the auth_user table
    :param email: the user's e-mail address
    :param selected: the columns to select from the table
    :param grouped: the columns in the GROUP BY clause. If not specified,
                    defaults to the same columns as the selected argument
    :param where: an optional WHERE clause to apply to the query
    :return: the query object
    """
    if grouped is None:
        grouped = selected
    query = select(
        # The extra column is for the DataTable recordsFiltered attribute.
        # It represents the number of records found before applying a sql LIMIT
        selected + [count().over().label('filtered')]
    ).select_from(
        table
    ).group_by(
        *grouped
    ).where(
        auth_user_table.c.email == email
    )
    if where is not None:
        query = query.where(where)
    return query


def _apply_text_filter(query: Select,
                       args: dict,
                       column: Column) -> Select:
    """
    If a value has been specified by the ['search']['value'] parameter from
    a DataTable AJAX request, this adds "column LIKE %['search']['value']%"
    to the WHERE clause of the given query.

    :param query: the DataTable SQL query
    :param args: the query parameters from a DataTable AJAX request
    :param column: the column to be filtered
    :return: the query with the filter (if it exists) applied
    """
    search_value = args['search']['value']
    if search_value:
        query = query.where(
            column.like('%{}%'.format(search_value))
        )
    return query


def _get_orderings(args: dict) -> Iterator:
    """
    Given the arguments from a DataTable AJAX query, yield strings formatted
    as column_name, sort_direction for an ORDER BY clause

    :param args: the query parameters from a DataTable AJAX request
    """
    for ordering in args['order']:
        idx = ordering['column']
        direction = ordering['dir']
        yield '{} {}'.format(args['columns'][idx]['name'], direction)


def _apply_ordering(query: Select,
                    args: dict,
                    default_sort_column_name: str,
                    default_direction: str='desc') -> Select:
    """
    If an ordering has been supplied by the ['order'] parameter from a
    DataTable AJAX request, this adds it to the given query. Otherwise,
    it adds the ordering specified by the default_sort_column_name and
    default_direction.

    :param query: the DataTable SQL query
    :param args: the query parameters from a DataTable AJAX request
    :param default_sort_column_name: the name of the column for the default
                                     ordering
    :param default_direction: the default sort direction (DESC if not
                              specified)
    :return: the query with the ordering applied
    """
    ord = args['order']
    default_sort = '{} {}'.format(default_sort_column_name, default_direction)
    order_by = ', '.join(_get_orderings(args)) if ord else default_sort
    return query.order_by(order_by)


def _apply_limit(query: Select,
                 args: dict) -> Select:
    """
    If a limit has been supplied by the 'length' parameter (and an offset
    supplied by the 'start' parameter) from a DataTable AJAX request,
    this adds it to the given query. A length of -1 represents no limit or
    offset. The offset index is 0-based.

    :param query: the DataTable SQL query
    :param args: the query parameters from a DataTable AJAX request
    :return: the query with the limit (if it exists) applied
    """
    limit = int(args['length'])
    if limit != -1:
        offset = int(args.get('start', 0))
        query = query.limit(limit).offset(offset)
    return query


class SurveyDataTableHandler(APIHandler):
    """The endpoint for getting a user's surveys for use in a jQuery
    DataTable."""

    def get(self):
        args = json_decode(self.get_argument('args'))

        email = self.get_email()
        table = auth_user_table.join(survey_table).outerjoin(submission_table)
        num_submissions = count(submission_table.c.submission_id)
        selected = [
            survey_table.c.survey_title,
            survey_table.c.survey_id,
            survey_table.c.created_on,
            num_submissions.label('num_submissions')
        ]

        query = _base_query(table, email, selected, grouped=selected[:2])

        # Title filter
        query = _apply_text_filter(query, args, survey_table.c.survey_title)

        # Ordering
        query = _apply_ordering(query, args, 'created_on')

        # Limiting
        query = _apply_limit(query, args)

        result = self.db.execute(query).fetchall()

        response = {
            'draw': int(args['draw']),
            'recordsTotal': get_number_of_surveys(self.db, email),
            'recordsFiltered': result[0]['filtered'] if result else 0,
            'data': [
                [title,
                 survey_id,
                 created_on.isoformat(),
                 str(num)]
                for title, survey_id, created_on, num, _ in result
            ]
        }
        self.write(json_encode(response))


class SubmissionDataTableHandler(APIHandler):
    """The endpoint for getting submissions to a survey for use in a jQuery
    DataTable."""

    def get(self, survey_id):
        args = json_decode(self.get_argument('args'))

        email = self.get_email()
        table = auth_user_table.join(survey_table).join(submission_table)
        selected = [
            submission_table.c.submission_id,
            submission_table.c.submitter,
            submission_table.c.submission_time,
        ]
        where = submission_table.c.survey_id == survey_id

        query = _base_query(table, email, selected, where=where)

        # Submitter name filter
        query = _apply_text_filter(query, args, submission_table.c.submitter)

        # Ordering
        query = _apply_ordering(query, args, 'submission_time')

        # Limiting
        query = _apply_limit(query, args)

        result = self.db.execute(query).fetchall()

        response = {
            'draw': int(args['draw']),
            'recordsTotal': get_number_of_submissions(self.db, survey_id),
            'recordsFiltered': result[0]['filtered'] if result else 0,
            'data': [
                [sub_id,
                 submitter,
                 sub_time.isoformat()]
                for sub_id, submitter, sub_time, _ in result
            ]
        }
        self.write(json_encode(response))
