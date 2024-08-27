from markupsafe import Markup
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.contexts import ContextStatic, ContextVariable
from django_htmx_ui.views.properties.widgets.helpers import Join
from django_htmx_ui.views.properties.widgets.html import HtmlAttribute
from django_htmx_ui.views.properties.widgets.javascript import JavascriptInline, JavascriptVarSet


def to_alpine_name(name, force_prepend='x-'):
    replaced_name = name.replace('_', '-')
    prepend = force_prepend if force_prepend and not replaced_name.startswith(force_prepend) else ''
    return f'{prepend}{replaced_name}'


class AlpineAttribute(HtmlAttribute):

    def __set_name__(self, owner, name):
        super().__set_name__(owner, to_alpine_name(name))


class AlpineInitCommand(JavascriptInline):
    pass


class AlpineInit(AlpineAttribute):
    attr = ContextStatic('x-init')
    value: Join = Join(JavascriptInline, separator='; ', ancestors=1)


class AlpineData(AlpineAttribute):
    attr = ContextStatic('x-data')
    value = ContextVariable(converters=(Markup.escape,))

    def __init__(self, default=NotDefined, name=None, add_in_context=True) -> None:
        self.default = default
        if self.default is not NotDefined:
            self.value = self.default
        super().__init__(name=name, add_in_context=add_in_context)


class AlpineDataSet(JavascriptVarSet):
    pass
