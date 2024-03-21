
from django_htmx_ui.views.properties.widgets.html import HtmlElement, HtmlElementId


class ForeignPlaceholder(HtmlElementId):

    def __init__(self, element, tag='div', wrap=False, name=None, add_in_context=True) -> None:
        
        if not issubclass(element, HtmlElementId):
            raise ValueError("The 'element' parameter must be a subclass of 'HtmlElementId'.")

        self.element = element
        super().__init__(tag, wrap, name, add_in_context)
