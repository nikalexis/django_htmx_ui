
from django_htmx_ui.views.properties.widgets.html import HtmlAttribute, HtmlElementId


class HtmxAttribute(HtmlAttribute):

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name.replace('_', '-'))


class HtmxElementId(HtmlElementId):
    pass


class HtmxSwapElementId(HtmxElementId):

    hx_swap_oob = HtmxAttribute('outerHTML')

    def __init__(self, swap=None, tag=None, wrap=True, name=None, add_in_context=True) -> None:
        if swap:
            self.id = swap.slug_global
        super().__init__(tag, wrap, name, add_in_context)
