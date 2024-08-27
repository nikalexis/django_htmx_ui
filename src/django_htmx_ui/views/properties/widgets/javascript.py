import json
from markupsafe import Markup
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.contexts import ContextVariable
from django_htmx_ui.views.properties.misc import Alias
from django_htmx_ui.views.properties.widgets.html import HtmlAttribute, HtmlElement, HtmlTag


class Javascript(HtmlElement):

    tag = HtmlTag("script")
    type = HtmlAttribute("application/javascript")
    contents = ContextVariable('', converters=(Markup.escape,))
    script = Alias('contents')

    def __init__(self, default=NotDefined, wrap=True, name=None, add_in_context=True) -> None:
        self.default = default
        if self.default is not NotDefined:
            self.script = self.default
        super().__init__(wrap=wrap, name=name, add_in_context=add_in_context)


class JavascriptInline(Javascript):

    def __init__(self, default=NotDefined, name=None, add_in_context=True) -> None:
        super().__init__(default=default, wrap=False, name=name, add_in_context=add_in_context)


class JavascriptVarSet(JavascriptInline):

    variable = ContextVariable()
    value = ContextVariable(required=True, converters=(Markup.escape, json.dumps))

    def __init__(self, variable=NotDefined, value=NotDefined, name=None, add_in_context=True) -> None:
        if self.variable is not NotDefined:
            self.variable = variable
        if self.value is not NotDefined:
            self.value = value
        super().__init__(name=name, add_in_context=add_in_context)

    def __raw__(self):
        return f'{self.variable} = {self.value}'