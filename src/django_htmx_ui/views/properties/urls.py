
from dataclasses import KW_ONLY
from typing import Any
from django_htmx_ui.views.properties.base import BasePropertyMixin, BaseValueProperty


class UrlBaseProperty(BaseValueProperty):
    _: KW_ONLY
    required: bool = True


class UrlParameter(UrlBaseProperty):
    _: KW_ONLY
    origin: bool = False
    fallback: bool = True

    @property
    def origin_or_partial(self):
        return ('origin' if self.origin else 'partial') + (('/partial' if self.origin else '/origin') if self.fallback else '')

    def locations(self):
        return [
            self.view.location_bar if self.origin else self.view.location_req
        ] + ([
            self.view.location_req if self.origin else self.view.location_bar
        ] if self.fallback else [])


class UrlModelMixin(BasePropertyMixin):
    model: Any
    _: KW_ONLY
    filter: bool = True
    field: str = 'pk'

    def __view__(self):
        value = super().__view__()
        obj = self.model.objects.get_or_none(**{ self.field: value})
        
        if self.required and obj is None:
            raise ValueError(f"'{self.model.__name__}' instance not exists with {self.field}='{value}'")
        
        return obj


class UrlPathParameter(UrlParameter):

    def __view__(self):
        for location in self.locations():
            value = location.resolver_match.kwargs.get(self.name)
            if value is not None:
                break

        if self.required and value is None:
            raise ValueError(f"'{self.name}' parameter not found in {self.origin_or_partial} request's path")

        return value


class UrlPathModel(UrlModelMixin, UrlPathParameter):
    pass


class UrlQueryParameter(UrlParameter):

    def __view__(self):
        for location in self.locations():
            value = location.query.get(self.name)
            if value is not None:
                break

        if self.required and value is None:
            raise ValueError(f"'{self.name}' parameter not found in {self.origin_or_partial} request's query")

        return value


class UrlQueryModel(UrlModelMixin, UrlQueryParameter):
    pass
