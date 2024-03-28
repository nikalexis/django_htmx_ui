
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.base import BaseProperty


class BaseContextProperty(BaseProperty):
    pass


class ContextProperty(BaseContextProperty):

    _getter = None

    def __init__(self, getter, name=None) -> None:
        self._getter = getter
        super(BaseContextProperty, self).__init__(name, add_in_context=True, cache=False)

    def _get(self, instance, owner):
        return self._getter(instance)


class ContextCachedProperty(ContextProperty):

    def __init__(self, getter, name=None) -> None:
        self._getter = getter
        super(BaseContextProperty, self).__init__(name, add_in_context=True, cache=True)

    def _get(self, instance, owner):
        return instance.context.data.setdefault(
            self.name,
            self._getter(instance),
        )


class ContextVariable(BaseContextProperty):

    _getter = None

    def __init__(self, default=NotDefined, required=False, name=None, add_in_context=True, cache=True) -> None:
        self.default = default
        self.required = required
        super().__init__(name, add_in_context, cache)

    def __call__(self, getter):
        self._getter = getter
        return self
    
    def _get(self, instance, owner):
        try:
            value = instance.context.data[self.name]
        except KeyError:
            if self._getter:
                value = self._getter(instance, self)

                if self.cache:
                    instance.context.data[self.name] = value

            else:
                value = self.default

        if self.required and value is NotDefined:
            raise ValueError(f"Required context variable '{self.name}' is not defined.")

        return value
    
    def _set(self, instance, value):
        instance.context.data[self.name] = value


class ContextAncestor(BaseContextProperty):

    def __init__(self, foreign_name=None, required=True, limit=None, name=None, add_in_context=True) -> None:
        super().__init__(name, add_in_context, cache=False)
        self.required = required
        self.foreign_name = foreign_name
        self.limit = limit

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        if self.foreign_name is None:
            self.foreign_name = self.name

    def _get(self, instance, owner):
        try:
            ancestor = instance
            counter = 1
            while self.limit is None or counter <= self.limit:
                ancestor = ancestor.parent
                try:
                    return ancestor.context[self.foreign_name]
                except KeyError:
                    if counter + 1 == self.limit:
                        raise
                counter += 1
        except (KeyError, AttributeError):
            if self.required:
                raise ValueError(f"Required context variable '{self.foreign_name}' not found in the context of {self.limit} ancestor(s) of '{instance}'.'{self.descriptor_name}'.")


class ContextParent(ContextAncestor):

    def __init__(self, foreign_name=None, required=True, name=None, add_in_context=True) -> None:
        limit = 1
        super().__init__(foreign_name, required, limit, name, add_in_context)
