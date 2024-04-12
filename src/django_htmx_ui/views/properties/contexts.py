
from dataclasses import KW_ONLY
import inspect
from typing import Any
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.base import BaseValueProperty


class BaseContextProperty(BaseValueProperty):
    pass


class ContextProperty(BaseContextProperty):
    getter: Any
    _: KW_ONLY
    cache: bool = False

    def __context__(self):
        return self.getter(self.parent)


class ContextCachedProperty(ContextProperty):
    _: KW_ONLY
    cache: bool = True

    def __context__(self):
        return self.parent.context.data.setdefault(
            self.name,
            self.getter(self.parent),
        )


class ContextStatic(BaseContextProperty):
    value: Any
    _: KW_ONLY

    def __context__(self):
        return self.value


class ContextVariable(BaseContextProperty):
    default: Any = NotDefined
    _: KW_ONLY
    converters: tuple = ()
    required: bool = False

    getter = None

    def __call__(self, getter):
        if self.parent and self.name in self.parent.context.data:
            raise ValueError('Cannot set a getter function after setting up a value for the ContextVariable property.')
        self.getter = getter
        return self
    
    @property
    def getter_ancestor(self):
        candidates = [ancestor for ancestor in self.ancestors if type(ancestor) is inspect._findclass(self.getter)]
        if not candidates:
            raise ValueError(f"Getter function '{self.getter}' cannot be found in ancestors list for object '{self}'.")
        elif len(candidates) > 1:
            raise ValueError(f"Getter function '{self.getter}' found in {len(candidates)} ancestors for object '{self}'.")
        return candidates[0]
    
    def apply_converters(self, value):
        for converter in reversed(self.converters):
            value = converter(value)
        return value

    def __context__(self):
        try:
            value = self.parent.context.data[self.name]
        except KeyError:
            if self.getter:
                value = self.getter(self.getter_ancestor)

                value = self.apply_converters(value)

                if self.cache:
                    self.parent.context.data[self.name] = value

            else:
                value = self.apply_converters(self.default) if self.default is not NotDefined else self.default

        if self.required and value is NotDefined:
            raise ValueError(f"Required context variable '{self.name}' is not defined.")

        return value
    
    def _set(self, instance, value):
        instance.context.data[self.name] = self.apply_converters(value)

    def _del(self, instance):
        try:
            del instance.context.data[self.name]
        except KeyError:
            pass


class ContextAncestor(BaseContextProperty):
    foreign_name: str = None
    _: KW_ONLY
    required: bool = True
    limit: int = None

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        if self.foreign_name is None:
            self.foreign_name = self.name

    def __context__(self):
        try:
            ancestor = self.parent
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
                raise ValueError(f"Required context variable '{self.foreign_name}' not found in the context of {self.limit} ancestor(s) of '{self.parent}'.'{self.descriptor_name}'.")


class ContextParent(ContextAncestor):
    _: KW_ONLY
    limit: int = 1
