from django.template import TemplateDoesNotExist
from dominate.util import escape
from django_htmx_ui.views.properties.contexts import ContextProperty
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.contexts import ContextVariable
from django_htmx_ui.views.properties.widgets.base import BaseWidget
from django_htmx_ui.views.properties.widgets.helpers import Join
from dataclasses import KW_ONLY


def to_html_name(name):
    replaced_name = name
    if replaced_name.endswith('_'):
        replaced_name = replaced_name[0:-1]
    return f'{replaced_name}'


class HtmlWidget(BaseWidget):
    pass


class HtmlAttribute(HtmlWidget):
    value: ContextVariable = ContextVariable()
    _: KW_ONLY

    @ContextProperty
    def attr(self):
        return to_html_name(self.name)

    def __call__(self, getter):
        self.value(getter)

    def _set(self, instance, value):
        self.value = value

    def __raw__(self):
        return f'{escape(str(self.attr))}="{escape(str(self.value))}"'


class HtmlAttributeId(HtmlAttribute):
    value: ContextVariable = ContextVariable()
    _: KW_ONLY

    @value
    def default_value(self):
        return  f'{self.slug_global}'


class HtmlContent(HtmlWidget):
    pass


class HtmlTag(ContextVariable):
    pass
    

class HtmlElement(HtmlContent):
    tag: HtmlTag = HtmlTag()
    _: KW_ONLY
    attributes: Join = Join(HtmlAttribute, separator=' ')
    contents: Join = Join(HtmlContent, separator='\n')
    wrap: bool = True

    @property
    def wrapper_class(self):
        return HtmlWrapper if self.wrap is True else self.wrap
    
    def render_to_response(self):
        try:
            response = super().render_to_response()
            if type(response) is self.response_class:
                response.render()
        except TemplateDoesNotExist:
            response = self.contents
        
        if self.wrap:
            if self.tag is NotDefined:
                raise ValueError(f"The 'tag' parameter is required for wrapped element {self}.")

            wrapper = self.wrapper_class(tag=self.tag, attributes=self.attributes, contents=response)
            return wrapper.render_to_response()
        else:
            return response


class HtmlWrapper(HtmlElement):
    tag: HtmlTag = HtmlTag(required=True)
    attributes: ContextVariable = ContextVariable()
    contents: ContextVariable = ContextVariable()

    def render_to_response(self):
        return super(HtmlContent, self).render_to_response()

    def __raw__(self):
        return f'<{escape(str(self.tag))} {self.attributes}>{self.contents}</{escape(str(self.tag))}>'


class HtmlElementId(HtmlElement):
    _: KW_ONLY
    id: HtmlAttributeId = HtmlAttributeId()
