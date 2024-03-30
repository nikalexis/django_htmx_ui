from django_htmx_ui.views.properties.contexts import ContextProperty, ContextVariable
from django_htmx_ui.views.properties.misc import Alias
from django_htmx_ui.views.properties.widgets.html import HtmlAttribute, HtmlElementId


def to_htmx_name(name, force_prepend='hx-'):
    replaced_name = name.replace('_', '-')
    prepend = force_prepend if force_prepend and not replaced_name.startswith(force_prepend) else ''
    return f'{prepend}{replaced_name}'


class HtmxAttribute(HtmlAttribute):

    def __set_name__(self, owner, name):
        super().__set_name__(owner, to_htmx_name(name))


class HtmxRequestMethod(HtmxAttribute):

    method = ContextVariable(required=True)
    url = ContextVariable(required=True)
    value = Alias(url)

    def __init__(self, method=None, add_in_context=True) -> None:
        if method is not None:
            self.method = method
        super().__init__(add_in_context=add_in_context)

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


class HtmxElementId(HtmlElementId):
    pass


class HtmxSwapElementId(HtmxElementId):

    hx_swap_oob = HtmxAttribute('outerHTML')

    def __init__(self, swap=None, tag=None, wrap=True, name=None, add_in_context=True) -> None:
        if swap:
            self.id = swap.id.slug_global
        super().__init__(tag, wrap, name, add_in_context)
