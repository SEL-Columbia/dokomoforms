"""Answer models."""

# from collections import OrderedDict
#
# import sqlalchemy as sa
# from sqlalchemy.dialects import postgresql as pg
# from sqlalchemy.orm import relationship
from sqlalchemy.sql.type_api import UserDefinedType

from dokomoforms.models import util, Base


class Geometry(UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"


class Answer(Base):
    __tablename__ = 'answer'

    id = util.pk()
