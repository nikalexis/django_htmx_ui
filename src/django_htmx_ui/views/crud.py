from django_htmx_ui.utils import ContextProperty
from django_htmx_ui.views.mixins import ResponseNoContentMixin, FormMixin, InstanceMixin
from django_htmx_ui.views.properties import BaseProperty


class CrudMixin:

    @property
    def permission(self):
        return True

    def on_get(self, *args, **kwargs):
        if not self.permission:
            raise ValueError('Pemission error')
        return super().on_get(*args, **kwargs)

    def on_post(self, *args, **kwargs):
        if not self.permission:
            raise ValueError('Pemission error')
        return super().on_post(*args, **kwargs)


class CrudCreateMixin(CrudMixin, FormMixin):
    pass


class CrudRetrieveMixin(CrudMixin):
    filter = {}

    def filters_get(self):
        return {
            key[7:]: value
            for key, value in self.request.GET.items()
            if key.startswith('filter_')
        }

    def filters_properties(self):
        filters = {}

        for key in self.__class__.__dict__:
            obj = getattr(self.__class__, key)
            
            if isinstance(obj, BaseProperty) and hasattr(obj, 'filter'):
                if type(obj.filter) is bool and obj.filter:
                    filters[obj.name] = getattr(self, key)
                
                if type(obj.filter) is str:
                    filters[obj.filter] = getattr(self, key)
        
        return filters

    @ContextProperty
    def instances(self):
        return self.module.MODEL.objects.filter(**self.filter).filter(**self.filters_get()).filter(**self.filters_properties())


class CrudListMixin(CrudRetrieveMixin):
    pass


class CrudUpdateMixin(InstanceMixin, CrudMixin):
    pass


class CrudDisplayMixin(InstanceMixin, CrudMixin):
    pass


class CrudActionMixin(ResponseNoContentMixin, InstanceMixin, CrudMixin):
    pass


class CrudDeleteMixin(CrudActionMixin):

    def on_post(self, request, *args, **kwargs):
        count, deleted = self.instance.delete()
        if count:
            self.on_post_success_message(request, *args, **kwargs)
            return self.on_post_success(request, *args, **kwargs)
        else:
            self.on_post_invalid_message(request, *args, **kwargs)
            return self.on_post_invalid(request, *args, **kwargs)

    def on_post_success_message(self, request, *args, **kwargs):
        self.message_success('%s deleted!' % self.instance)

    def on_post_invalid_message(self, request, *args, **kwargs):
        self.message_error('%s not deleted!' % self.instance)
