from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker
from dokomoforms.options import options, inject_options

inject_options(schema='doko_test')

from dokomoforms.models import create_engine
import dokomoforms.models as models


engine = create_engine(echo=False)
Session = sessionmaker()


def load_fixtures():
    # creates db schema
    session = Session(bind=engine, autocommit=True)

    with session.begin():
        creator = models.SurveyCreator(
            name='test_user',
            emails=[models.Email(address='test_user')],
        )
        node_types = list(models.NODE_TYPES)
        for node_type in node_types:
            sn = (
                models.NonAnswerableSurveyNode if node_type == 'note' else
                models.AnswerableSurveyNode
            )
            survey = models.Survey(
                title=node_type + '_survey',
                nodes=[
                    sn(
                        node=models.construct_node(
                            type_constraint=node_type,
                            title=node_type + '_node',
                        ),
                    ),
                ],
            )
            creator.surveys.append(survey)
        session.add(creator)


def unload_fixtures():
    print('unload_fixtures')
    engine.execute(DDL('DROP SCHEMA IF EXISTS ' + options.schema + ' CASCADE'))
