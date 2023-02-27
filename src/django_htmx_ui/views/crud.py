from django_htmx_ui.utils import ContextProperty
from django_htmx_ui.views.mixins import ResponseNoContentMixin, FormMixin, InstanceMixin


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

    @ContextProperty
    def instances(self):
        return self.module.MODEL.objects.filter(**self.filter).filter(**self.filters_get())


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
