
from django_htmx_ui.utils import ContextCachedProperty, ContextProperty, NotDefined
from django_htmx_ui.views.properties.widgets.base import BaseWidget
from django_htmx_ui.views.properties.widgets.helpers import ContextVariable, LocalProperties


class HtmlWidget(BaseWidget):
    pass


class HtmlAttribute(HtmlWidget):

    def __init__(self, default=None, name=None, add_in_context=True) -> None:
        self.default = default
        super().__init__(name, add_in_context)

    def get_default(self, instance, owner):
        if self.default is not None:
            return self.default(self, instance, owner) if callable(self.default) else self.default

    @ContextProperty
    def attr(self):
        return self.name

    def _get(self, instance, owner):
        if not 'value' in self.context.keys():
            self.context['value'] = self.get_default(instance, owner)
        return super()._get(instance, owner)

    def __set__(self, instance, value):
        self.context['value'] = value


class HtmlAttributeId(HtmlAttribute):

    def __init__(self, default=None, name=None, add_in_context=True) -> None:
        super().__init__(default if default is not None else self.auto_id, name, add_in_context)

    @staticmethod
    def auto_id(descriptor, instance, owner):
        return f'{descriptor.slug_global}'


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
