from flask import Blueprint

controllers = Blueprint('controllers', __name__)

# register all sub-modules so their routes hook into `controllers`
from . import calendar_view, highlights, fraction_hunter