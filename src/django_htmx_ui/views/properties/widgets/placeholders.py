from typing import Any
from django_htmx_ui.views.properties.widgets.helpers import ContextVariable
from django_htmx_ui.views.properties.widgets.html import HtmlElement, HtmlElementId
from django_htmx_ui.views.properties.widgets.htmx import HtmxAttribute, HtmxMethod


class Placeholder(HtmlElement):

    def __init__(self, tag, name=None, add_in_context=True) -> None:
        super().__init__(tag=tag, wrap=False, name=name, add_in_context=add_in_context)


class PlaceholderId(HtmlElementId):

    def __init__(self, tag='div', name=None, add_in_context=True) -> None:
        super().__init__(tag=tag, wrap=False, name=name, add_in_context=add_in_context)


# class ElementPlaceholderId(PlaceholderId):

#     def __init__(self, element, tag=None, name=None, add_in_context=True) -> None:
        
#         if not issubclass(element, HtmlElementId):
#             raise ValueError("The 'element' parameter must be a subclass of 'HtmlElementId'.")

#         super().__init__(tag=tag or element.tag, name=name, add_in_context=add_in_context)


class Lazyload(Placeholder):

    method = ContextVariable('GET', required=True)
    url = ContextVariable(required=True)

    hx_method = HtmxMethod()
    hx_target = HtmxAttribute('this')
    hx_swap = HtmxAttribute('outerHTML')
    hx_trigger = HtmxAttribute('load once delay:0.02s, htmx:afterSettle from:body once delay:0.01s')

    def __init__(self, tag='div', name=None, add_in_context=True) -> None:
        super().__init__(tag=tag, name=name, add_in_context=add_in_context)


class LazyloadSelf(Lazyload):

    def __init__(self, tag='div', name=None, add_in_context=True) -> None:
        super().__init__(tag=tag, name=name, add_in_context=add_in_context)

    def _get(self, instance, owner):
        self.url = instance.url
        return super()._get(instance, owner)
