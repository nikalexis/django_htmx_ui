
class ViewBaseProperty:

    def __init__(self, name=None, required=True, context=True) -> None:
        self.name = name
        self.required = required
        self.context = context

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            value = self._get(instance, owner)
            
            if self.context:
                instance.add_context(self.name, value)
            
            return value
    
    def _get(self, instance, owner):
        raise NotImplementedError()


class UrlParameter(ViewBaseProperty):

    def __init__(self, name=None, required=True, context=True, origin=False) -> None:
        super().__init__(name, required, context)
        self.origin = origin

    @property
    def origin_or_partial(self):
        return 'origin' if self.origin else 'partial'

    def location(self, instance):
        return instance.location_bar if self.origin else instance.location_req


class UrlModelMixin:
    
    def __init__(self, model, name=None, required=True, context=True, origin=False, filter=True) -> None:
        super().__init__(name, required, context, origin)
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

