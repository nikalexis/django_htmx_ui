from typing import Any
from django_htmx_ui.views.properties.contexts import ContextProperty, ContextVariable
from django_htmx_ui.views.properties.misc import Alias
from django_htmx_ui.views.properties.widgets.html import HtmlAttribute, HtmlElementId
from dataclasses import KW_ONLY


def to_htmx_name(name, force_prepend='hx-'):
    replaced_name = name.replace('_', '-')
    prepend = force_prepend if force_prepend and not replaced_name.startswith(force_prepend) else ''
    return f'{prepend}{replaced_name}'


class HtmxAttribute(HtmlAttribute):

    def __set_name__(self, owner, name):
        super().__set_name__(owner, to_htmx_name(name))


class HtmxRequestMethod(HtmxAttribute):
    _: KW_ONLY
    method: ContextVariable = ContextVariable(required=True)
    url: ContextVariable = ContextVariable(required=True)
    value: Alias = Alias(url)

    @ContextProperty
    def attr(self):
        return to_htmx_name(self.method.lower())


class HtmxGet(HtmxRequestMethod):
    method = ContextVariable('GET', required=True)


class HtmxPost(HtmxRequestMethod):
    method = ContextVariable('POST', required=True)


class HtmxPatch(HtmxRequestMethod):
    method = ContextVariable('PATCH', required=True)


class HtmxPut(HtmxRequestMethod):
    method = ContextVariable('PUT', required=True)


class HtmxDelete(HtmxRequestMethod):
    method = ContextVariable('DELETE', required=True)


class HtmxTarget(HtmxAttribute):
    pass


class HtmxSwap(HtmxAttribute):
    pass


class HtmxTrigger(HtmxAttribute):
    pass


class HtmxElementId(HtmlElementId):
    pass


class HtmxSwapElementId(HtmxElementId):
    _: KW_ONLY
    swap: Any = None
    
    hx_swap_oob = HtmxAttribute('outerHTML')

    def __post_init__(self):
        if self.swap:
            self.id = self.swap.id.slug_global
