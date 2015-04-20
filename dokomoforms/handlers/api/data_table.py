"""
API endpoints dealing with data tables. Ideas taken from
https://github.com/DataTables/DataTables/blob
/e0f2cfd81e61103d88ea215797bdde1bc19a2935/examples/server_side/scripts/ssp
.class.php
"""
from abc import abstractmethod, ABCMeta
from collections import Iterator

from sqlalchemy import select, Table, Column
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import count, max as sqlmax
from tornado.escape import json_encode, json_decode
from dokomoforms.api import maybe_isoformat

from dokomoforms.db import auth_user_table, survey_table, submission_table
from dokomoforms.db.submission import get_number_of_submissions
from dokomoforms.db.survey import get_number_of_surveys
from dokomoforms.handlers.util.base import APIHandler


def _base_query(table: Table,
                email: str,
                selected: list,
                where: BinaryExpression=None) -> Select:
    """
    Return a query for a DataTable without any text filtering, ordering,
    or limiting applied.

    :param table: the SQLAlchemy table. Should be one or more tables joined
                  with the auth_user table
    :param email: the user's e-mail address
    :param selected: the columns to select from the table
    :param where: an optional WHERE clause to apply to the query
    :return: the query object
    """
    # Selected columns (but not aggregate functions) must also appear in the
    # GROUP BY clause
    grouped = (column for column in selected if type(column) is Column)

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
                    default_direction: str='DESC') -> Select:
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
    return query.order_by(order_by + ' NULLS LAST')


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


class DataTableBaseHandler(APIHandler, metaclass=ABCMeta):
    """DataTable handlers should inherit from this class to access the
    _get_records method."""

    @staticmethod
    @abstractmethod
    def _data_formatter(record: tuple) -> list:  # pragma: no cover
        """
        _get_records() uses this method to transform values returned from
        the database into strings for use in a DataTable.

        Generally this method should return something like
        [transform(val) for val in record]

        For example, if you wanted to select [survey_title, created_on,
        number_of_submissions], the record you would get might look like
        ('my survey', {April 14, 2015}, 5), and you would need to return
        ['my_survey', '2015/3/14', '5'], by applying your formatting.

        :param record: the values returned for one row in the DataTable
        :return: the same values stringified
        """
        pass

    def _get_records(self,
                     *,
                     table: Table,
                     email: str,
                     selected: list,
                     where: BinaryExpression=None,
                     text_filter_column: Column,
                     default_sort_column_name: str,
                     default_sort_direction: str='DESC',
                     total_records: int) -> str:
        """
        For use in responding to a DataTable AJAX request. Uses the 'args'
        query parameter and the supplied arguments to get the data out of
        the specified table.

        :param table: the SQLAlchemy table (probably involves a join)
        :param email: the user's e-mail address
        :param selected: the columns and SQL functions to select from the table
        :param where: an optional WHERE clause
        :param text_filter_column: the SQLAlchemy Column to use for the
                                   DataTable search box.
        :param default_sort_column_name: the name of the column to sort by
                                         if the query did not specify one
        :param default_sort_direction: the sort direction for
                                       default_sort_column_name (default DESC)
        :param total_records: the total number of records that the DataTable
                              could contain
        :return: the JSON-encoded data
        """
        args = json_decode(self.get_argument('args'))

        query = _base_query(
            table, email, selected, where=where
        )

        query = _apply_text_filter(query, args, column=text_filter_column)

        query = _apply_ordering(
            query, args,
            default_sort_column_name=default_sort_column_name,
            default_direction=default_sort_direction
        )

        query = _apply_limit(query, args)

        result = self.db.execute(query).fetchall()

        response = {
            'draw': int(args['draw']),
            'recordsTotal': total_records,
            'recordsFiltered': result[0]['filtered'] if result else 0,
            'data': [self._data_formatter(record[:-1]) for record in result]
        }

        return json_encode(response)


class SurveyDataTableHandler(DataTableBaseHandler):
    """The endpoint for getting a user's surveys for use in a jQuery
    DataTable."""

    @staticmethod
    def _data_formatter(record: tuple) -> list:
        title, survey_id, created_on, num = record
        return [title, survey_id, created_on.isoformat(), str(num)]

    def get(self):
        email = self.get_email()

        # Shorter variable names
        auth_user = auth_user_table
        survey = survey_table
        submission = submission_table
        submission_id = submission_table.c.submission_id

        result = self._get_records(
            table=auth_user.join(survey).outerjoin(submission),
            email=email,
            selected=[
                survey_table.c.survey_title,
                survey_table.c.survey_id,
                survey_table.c.created_on,
                count(submission_id).label('num_submissions')
            ],
            text_filter_column=survey_table.c.survey_title,
            default_sort_column_name='created_on',
            total_records=get_number_of_surveys(self.db, email)
        )

        self.write(result)


class SubmissionDataTableHandler(DataTableBaseHandler):
    """The endpoint for getting submissions to a survey for use in a jQuery
    DataTable."""

    @staticmethod
    def _data_formatter(record: tuple) -> list:
        sub_id, submitter, sub_time = record
        return sub_id, submitter, sub_time.isoformat()

    def get(self, survey_id):
        email = self.get_email()

        result = self._get_records(
            table=auth_user_table.join(survey_table).join(submission_table),
            email=email,
            selected=[
                submission_table.c.submission_id,
                submission_table.c.submitter,
                submission_table.c.submission_time
            ],
            where=submission_table.c.survey_id == survey_id,
            text_filter_column=submission_table.c.submitter,
            default_sort_column_name='submission_time',
            total_records=get_number_of_submissions(self.db, survey_id)
        )
        self.write(result)


class IndexSurveyDataTableHandler(DataTableBaseHandler):
    """The endpoint for getting a summary of a user's survey information for
    a jQuery DataTable."""

    @staticmethod
    def _data_formatter(record: tuple) -> list:
        title, num, latest_sub, survey_id = record
        return [
            title,
            str(num),
            # created_on.isoformat(),
            maybe_isoformat(latest_sub),
            survey_id
        ]

    def get(self):
        email = self.get_email()

        # Shorter variable names
        auth_user = auth_user_table
        survey = survey_table
        submission = submission_table
        submission_id = submission_table.c.submission_id
        submission_time = submission_table.c.submission_time

        result = self._get_records(
            table=auth_user.join(survey).outerjoin(submission),
            email=email,
            selected=[
                survey_table.c.survey_title,
                count(submission_id).label('num_submissions'),
                # survey_table.c.created_on,
                sqlmax(submission_time).label('latest_submission'),
                survey_table.c.survey_id,
            ],
            text_filter_column=survey_table.c.survey_title,
            default_sort_column_name='latest_submission',
            total_records=get_number_of_surveys(self.db, email)
        )

        self.write(result)
