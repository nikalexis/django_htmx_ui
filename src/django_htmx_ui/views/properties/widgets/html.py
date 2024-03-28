from django_htmx_ui.utils import ContextCachedProperty, ContextProperty, NotDefined
from django_htmx_ui.views.properties.widgets.base import BaseWidget
from django_htmx_ui.views.properties.widgets.helpers import ContextVariable, LocalProperties


class HtmlWidget(BaseWidget):
    pass


class HtmlAttribute(HtmlWidget):

    def __init__(self, default=NotDefined, name=None, add_in_context=True) -> None:
        self.default = default
        super().__init__(name, add_in_context)

    @ContextProperty
    def attr(self):
        return self.name

    @ContextVariable()
    def value(self, widget):
        widget.default = self.default

    def _set(self, instance, value):
        self.value = value


class HtmlAttributeId(HtmlAttribute):

    @ContextVariable()
    def value(self, widget):
        if self.default is not NotDefined:
            widget.default = self.default
        else:
            return f'{self.slug_global}'


class HtmlContent(HtmlWidget):

    def __init__(self, name=None, add_in_context=True) -> None:
        super().__init__(name, add_in_context)


class HtmlTag(ContextVariable):
    pass
    

class HtmlElement(HtmlContent):

    tag = HtmlTag()
    attributes = LocalProperties(HtmlAttribute, separator=' ')
    contents = LocalProperties(HtmlContent, separator='\n')

    def __init__(self, tag=None, wrap=True, name=None, add_in_context=True) -> None:
        if tag is not None:
            self.tag = tag
        self.wrap = wrap

        super().__init__(name, add_in_context)

    @property
    def wrapper_class(self):
        return HtmlWrapper if self.wrap is True else self.wrap
    
    def _get(self, instance, owner):
        response = super()._get(instance, owner)
        
        if self.wrap:
            if self.tag is NotDefined:
                raise ValueError(f"The 'tag' parameter is required for wrapped element {self}.")

            wrapper = self.wrapper_class(tag=self.tag, attributes=self.attributes, contents=response)
            return wrapper.rendered_response()
        else:
            return response


class HtmlWrapper(HtmlElement):

    tag = HtmlTag(required=True)
    attributes = ContextVariable()
    contents = ContextVariable()

    def __init__(self, tag, attributes, contents) -> None:
        self.tag = tag
        self.attributes = attributes
        self.contents = contents
        super().__init__(tag=tag, wrap=False, name=None, add_in_context=False)


class HtmlElementId(HtmlElement):

    id = HtmlAttributeId()
