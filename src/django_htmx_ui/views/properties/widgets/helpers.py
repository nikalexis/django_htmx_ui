from django_htmx_ui.views.properties.contexts import ContextCachedProperty, ContextProperty
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.base import BaseProperty
from django_htmx_ui.views.properties.widgets.base import BaseWidget


class Join(BaseWidget):

    def __init__(self, *include_args, include=(), exclude=(), filter=bool, separator='', name=None, add_in_context=True) -> None:
        self.include = tuple(set(include_args) | set(include))
        self.exclude = exclude
        self.filter = filter
        self._separator = separator
        super().__init__(name, add_in_context)

    @ContextProperty
    def separator(self):
        return self._separator

    @ContextCachedProperty
    def contents(self):
        return [
            getattr(self.parent, descriptor_name)
            for descriptor_name, member in self.parent.get_properties(include=self.include, exclude=self.exclude, filter=self.filter)
        ]
