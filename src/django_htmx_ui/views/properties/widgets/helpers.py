from django_htmx_ui.utils import ContextCachedProperty, ContextProperty, NotDefined
from django_htmx_ui.views.properties.base import BaseProperty
from django_htmx_ui.views.properties.widgets.base import BaseWidget


class ContextVariable(BaseProperty):

    def __init__(self, default=NotDefined, required=False, name=None, add_in_context=True) -> None:
        self.default = default
        self.required = required
        super().__init__(name, add_in_context)

    def _get(self, instance, owner):
        value = instance.__dict__.get(self.descriptor_name, self.default)

        if self.required and value is NotDefined:
            raise ValueError(f"Required context variable '{self.name}' is not defined.")

        return value
    
    def __set__(self, instance, value):
        instance.__dict__[self.descriptor_name] = value


class LocalProperties(BaseWidget):

    def __init__(self, *include_args, include=(), exclude=(), filter=bool, separator='', name=None, add_in_context=True) -> None:
        self.include = tuple(set(include_args) | set(include))
        self.exclude = exclude
        self.filter = filter
        self._separator = separator
        super().__init__(name, add_in_context)

    @ContextProperty
    def separator(self):
        return self._separator

    def _get(self, instance, owner):
        self.context['contents'] = [
            getattr(instance, descriptor_name)
            for descriptor_name, member in instance.get_properties(include=self.include, exclude=self.exclude, filter=self.filter)
        ]
        return super()._get(instance, owner)
