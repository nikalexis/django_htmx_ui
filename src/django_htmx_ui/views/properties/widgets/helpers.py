from typing import Any
from django_htmx_ui.views.properties.contexts import ContextCachedProperty, ContextVariable
from django_htmx_ui.views.properties.widgets.base import BaseWidget
from dataclasses import KW_ONLY


class Join(BaseWidget):
    _: KW_ONLY
    include: tuple = ()
    exclude: tuple = ()
    filter: Any = bool
    separator: ContextVariable = ContextVariable('')
    ancestors: int = 0
    cache: bool = False

    def __init_args__(self, *args, **kwargs):
        if args:
            kwargs['include'] = tuple(set(args) | set(kwargs.get('include', ())))
        return (), kwargs

    @ContextCachedProperty
    def contents(self):
        ancestor = self.parent
        for _ in range(0, self.ancestors):
            ancestor = ancestor.parent
        return [
            getattr(ancestor, descriptor_name)
            for descriptor_name, member in ancestor.get_properties(include=self.include, exclude=self.exclude, filter=self.filter)
        ]

    def __raw__(self):
        return self.separator.join([str(c) for c in self.contents])
