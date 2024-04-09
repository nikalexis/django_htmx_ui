from django_htmx_ui.views.properties.widgets.html import HtmlElement, HtmlElementId, HtmlTag
from django_htmx_ui.views.properties.widgets.htmx import HtmxAttribute, HtmxRequestMethod
from dataclasses import KW_ONLY


class Placeholder(HtmlElement):
    tag: HtmlTag = HtmlTag(required=True)
    _: KW_ONLY


class PlaceholderId(HtmlElementId):
    tag: HtmlTag = HtmlTag('div', required=True)
    _: KW_ONLY


# class ElementPlaceholderId(PlaceholderId):

#     def __init__(self, element, tag=None, name=None, add_in_context=True) -> None:
        
#         if not issubclass(element, HtmlElementId):
#             raise ValueError("The 'element' parameter must be a subclass of 'HtmlElementId'.")

#         super().__init__(tag=tag or element.tag, name=name, add_in_context=add_in_context)


class Lazyload(Placeholder):
    method: str
    url: str
    _: KW_ONLY
    tag: HtmlTag = HtmlTag('div', required=True)

    hx_method = HtmxRequestMethod()
    hx_target = HtmxAttribute('this')
    hx_swap = HtmxAttribute('outerHTML')
    hx_trigger = HtmxAttribute('load once delay:0.02s, htmx:afterSettle from:body once delay:0.01s')

    def __post_init__(self):
        self.hx_method.method = self.method
        self.hx_method.url = self.url


class LazyloadSelf(Lazyload):
    method: str = 'GET'
    url: str = ''
    _: KW_ONLY

    def __view__(self):
        self.hx_method.url = self.view.url
        return super().__view__()
