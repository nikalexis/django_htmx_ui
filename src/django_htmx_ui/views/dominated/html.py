from dominate.document import document
from dominate.tags import *
from dominate.util import *

from django_htmx_ui.views.dominated.alpine import AlpineDominated
from django_htmx_ui.views.dominated.htmx import HtmxDominated


class template(html_tag):
    pass


alpine = x = AlpineDominated()

htmx = hx = HtmxDominated()
