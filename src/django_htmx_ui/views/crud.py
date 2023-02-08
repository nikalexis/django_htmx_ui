from django_htmx_ui.utils import to_snake_case, ContextProperty, ContextCachedProperty


class FormMixin:
    form_initial = {}

    @property
    def form_instance(self):
        return getattr(self, 'instance', None)

    @ContextCachedProperty
    def form(self):
        Form = getattr(self.__class__, 'Form', None)
        if Form:
            if self.request.method == 'GET':
                return Form(instance=self.form_instance, initial=self.form_initial)
            if self.request.method == 'POST':
                return Form(self.request.POST, instance=self.form_instance)

    def on_post(self, request, *args, **kwargs):
        if self.form.is_valid():
            self.form.save()
            return self.on_post_success(request, *args, **kwargs)
        else:
            return self.on_post_invalid(request, *args, **kwargs)

    def on_post_success(self, request, *args, **kwargs):
        pass

    def on_post_invalid(self, request, *args, **kwargs):
        pass


class InstanceMixin(FormMixin):

    @classmethod
    @property
    def path_root(cls):
        return '<str:pk>/' + super().path_root

    @ContextProperty
    def url(self):
        return self.reverse(self.slug, args=[self.instance.pk])

    def setup(self, request, *args, **kwargs):
        if not hasattr(self, 'model_pk'):
            self.model_pk = kwargs['pk']
        return super().setup(request, *args, **kwargs)

    @ContextCachedProperty
    def instance(self):
        return self.module.MODEL.objects.get(pk=self.model_pk)

    @property
    def instance_slug(self):
        return '%s_%s' % (to_snake_case(self.__class__.__name__), self.instance.pk)

    @ContextProperty
    def title(self):
        return str(self.instance)

    @classmethod
    def as_instance(cls, instance):
        assert isinstance(instance, cls.module.MODEL)
        obj = cls()
        obj.model_pk = instance.pk
        return obj

    @property
    def permission(self):
        return self.instance


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

    @ContextProperty
    def breadcrumb(self):
        return {
            self.module.TITLE: self.reverse('list') if hasattr(self.module, 'List') else '',
            **({
                str(self.instance): '',
            } if hasattr(self, 'instance') else {}),
        }


class CrudListMixin(CrudMixin):
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


class CrudCreateMixin(CrudMixin, FormMixin):
    pass


class CrudDisplayMixin(InstanceMixin, CrudMixin):
    pass


class CrudUpdateMixin(InstanceMixin, CrudMixin):
    pass


class CrudListUpdateMixin(CrudListMixin):
    pass


class CrudDeleteMixin(InstanceMixin, CrudMixin):
    pass


class CrudActionMixin(InstanceMixin, CrudMixin):
    pass
