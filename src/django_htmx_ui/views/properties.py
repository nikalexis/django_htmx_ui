
class BaseProperty:

    def __init__(self, name=None, add_in_context=True) -> None:
        self.name = name
        self.add_in_context = add_in_context

    def __set_name__(self, owner, name):
        self.descriptor_name = name
        if not self.name:
            self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self._get(instance, owner)
    
    def _get(self, instance, owner):
        return self


class UrlBaseProperty(BaseProperty):

    def __init__(self, name=None, required=True, add_in_context=True) -> None:
        super().__init__(name, add_in_context)
        self.required = required


class UrlParameter(UrlBaseProperty):

    def __init__(self, name=None, required=True, add_in_context=True, origin=False) -> None:
        super().__init__(name, required, add_in_context)
        self.origin = origin

    @property
    def origin_or_partial(self):
        return 'origin' if self.origin else 'partial'

    def location(self, instance):
        return instance.location_bar if self.origin else instance.location_req


class UrlModelMixin:
    
    def __init__(self, model, name=None, required=True, add_in_context=True, origin=False, filter=True, field='pk') -> None:
        super().__init__(name, required, add_in_context, origin)
        self.model = model
        self.filter = filter
        self.field = field

    def _get(self, instance, owner):
        value = super()._get(instance, owner)
        obj = self.model.objects.get_or_none(**{ self.field: value})
        
        if obj is None:
            raise ValueError(f"'{self.model.__name__}' instance not exists with {self.field}='{value}'")
        
        return obj


class UrlPathParameter(UrlParameter):

    def _get(self, instance, owner):
        location = self.location(instance)
        value = location.resolver_match.kwargs.get(self.name)

        if self.required and value is None:
            raise ValueError(f"'{self.name}' parameter not found in {self.origin_or_partial} request's path")

        return value


class UrlPathModel(UrlModelMixin, UrlPathParameter):
    pass


class UrlQueryParameter(UrlParameter):

    def _get(self, instance, owner):
        location = self.location(instance)
        value = location.query.get(self.name)

        if self.required and value is None:
            raise ValueError(f"'{self.name}' parameter not found in {self.origin_or_partial} request's query")

        return value


class UrlQueryModel(UrlModelMixin, UrlQueryParameter):
    pass


