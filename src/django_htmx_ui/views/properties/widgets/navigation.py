from dataclasses import KW_ONLY
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.contexts import ContextVariable
from django_htmx_ui.views.properties.widgets.helpers import Join
from django_htmx_ui.views.properties.widgets.html import HtmlAttribute, HtmlElement, HtmlTag
from django_htmx_ui.views.properties.widgets.htmx import HtmxRequestMethod, HtmxSwap, HtmxTarget, HtmxTrigger


class Link(HtmlElement):
    text: ContextVariable = ContextVariable()
    url: ContextVariable = ContextVariable('#')
    _: KW_ONLY
    tag: HtmlTag = HtmlTag('a')
    
    # print(url, type(url))
    href = HtmlAttribute()

    @href
    def href_value(self):
        return self.url

    def __raw__(self):
        return str(self.text)

    # def __init__(self, text, url, tag=None, wrap=True, name=None, add_in_context=True) -> None:
    #     self.text = text
    #     self.href = url
    #     super().__init__(tag, wrap, name, add_in_context)


class LinkButton(Link):
    tag = HtmlTag('button')


class HtmxLink(Link):
    hx_method = HtmxRequestMethod()
    hx_target = HtmxTarget()
    hx_swap = HtmxSwap()
    hx_trigger = HtmxTrigger()

    def __init__(self, text, url, target=NotDefined, method='GET', swap='outerHTML', trigger='click', tag=None, wrap=True, name=None, add_in_context=True) -> None:
        self.hx_method.method = method
        self.hx_method.url = url
        self.hx_target = target
        self.hx_swap = swap
        self.hx_trigger = trigger
        super().__init__(text, url, tag, wrap, name, add_in_context)


class HtmxLinkButton(HtmxLink):
    tag = HtmlTag('button')


class MenuItem(HtmlElement):
    pass


class Menu(HtmlElement):
    contents = Join(MenuItem, separator='\n')
