
class BaseProperty:

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name

    def __get__(self, instance, owner=None):
        return self if instance is None else self._get(instance, owner)
    
    def _get(self, instance, owner):
        raise NotImplementedError()


class UrlParameter(BaseProperty):

    def __init__(self, name=None, required=True, origin=False, context=True) -> None:
        self.name = name
        self.required = required
        self.origin = origin
        self.context = context

    @property
    def origin_or_partial(self):
        return 'origin' if self.origin else 'partial'

    def location(self, instance):
        return instance.location_bar if self.origin else instance.location_req

    def _get(self, instance, owner):
        value = self._get(instance, owner)
        
        if self.context:
            instance.add_context(self.name, value)
        
        return value


class UrlModelMixin:
    
    def __init__(self, model, name=None, required=True, origin=False, filter=True) -> None:
        super().__init__(name, required, origin)
        self.model = model
        self.filter = filter

    def _get(self, instance, owner):
        pk = super()._get(instance, owner)
        obj = self.model.objects.get_or_none(pk=pk)
        
        if obj is None:
            raise ValueError(f"'{self.model.__name__}' instance not exists with pk='{pk}'")
        
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

