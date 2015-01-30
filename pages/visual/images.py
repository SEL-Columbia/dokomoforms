"""API endpoints dealing with images."""
import dateutil
import matplotlib
from matplotlib.ticker import MaxNLocator

from db.question import question_select

from pages.util.visual import user_owns_question


matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
from api.aggregation import time_series, bar_graph
from pages.util.base import BaseHandler
import tornado.web
import numpy as np


def _get_line_graph(self, question_id: str):
    time_series_data = time_series(question_id, email=self.current_user)
    question = question_select(question_id)
    x, y = time_series_data['result']
    x = list(map(dateutil.parser.parse, x))
    fig, ax = plt.subplots()
    ax.margins(0.04)
    plt.title(question.question_title, fontsize=25)
    plt.xlabel('Time', fontsize=18)
    plt.ylabel('Value', fontsize=18)
    ax.plot_date(x, y, linestyle='-', markersize=5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    fig.autofmt_xdate()
    mem = io.BytesIO()
    plt.tight_layout()
    plt.savefig(mem, format='png')
    return mem.getvalue()


def _get_bar_graph(self, question_id: str):
    bar_graph_data = bar_graph(question_id, email=self.current_user)
    question = question_select(question_id)
    x, y = bar_graph_data['result']
    x = np.array(x)
    fig, ax = plt.subplots()
    plt.title(question.question_title, fontsize=25)
    plt.xlabel('Value', fontsize=18)
    ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
    plt.ylabel('Count', fontsize=18)
    ax.get_yaxis().set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim([0, np.max(y) + 0.25])
    ax.bar(x, y, width=0.5, align='center')
    mem = io.BytesIO()
    plt.tight_layout()
    plt.savefig(mem, format='png')
    return mem.getvalue()


class LineGraphHandler(BaseHandler):
    @tornado.web.authenticated
    @user_owns_question
    def get(self, question_id: str, graph_type: str):
        if graph_type == 'time':
            image = _get_line_graph(self, question_id)
        elif graph_type == 'bar':
            image = _get_bar_graph(self, question_id)
        else:
            assert False
        self.set_header('Content-type', 'image/png')
        self.set_header('Content-length', len(image))
        self.write(image)
