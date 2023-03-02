from django.core.exceptions import ViewDoesNotExist
from django.shortcuts import redirect

from django_htmx_ui.utils import ContextProperty, ContextCachedProperty, UrlView, to_snake_case


class OriginTemplateMixin:

    def get(self, request, *args, **kwargs):
        if request.htmx and OriginTemplateMixin in self.__class__.__bases__:
            raise ViewDoesNotExist("View '%s' is an 'OriginTemplateMixin'." % self.__class__.__name__)
        else:
            return super().get(request, *args, **kwargs)


class PartialTemplateMixin:
    redirect_partial = '/'

    def get(self, request, *args, **kwargs):
        if request.htmx:
            return super().get(request, *args, **kwargs)
        elif self.redirect_partial:
            return redirect(self.redirect_partial)
        else:
            raise ViewDoesNotExist("View '%s' is a 'PartialTemplateMixin'." % self.__class__.__name__)


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
                if self.form_instance:
                    return Form(instance=self.form_instance, initial=self.form_initial)
                else:
                    return Form(initial=self.form_initial)
            if self.request.method == 'POST':
                if self.form_instance:
                    return Form(self.request.POST, instance=self.form_instance)
                else:
                    return Form(self.request.POST)

    def on_post(self, request, *args, **kwargs):
        if self.form.is_valid():
            self.form.save()
            self.on_post_success_message(request, *args, **kwargs)
            return self.on_post_success(request, *args, **kwargs)
        else:
            self.on_post_invalid_message(request, *args, **kwargs)
            return self.on_post_invalid(request, *args, **kwargs)

    def on_post_success(self, request, *args, **kwargs):
        pass

    def on_post_success_message(self, request, *args, **kwargs):
        self.message_success('Saved!')

    def on_post_invalid(self, request, *args, **kwargs):
        pass

    def on_post_invalid_message(self, request, *args, **kwargs):
        self.message_error('Not saved!')


class InstanceMixin(FormMixin):

    @classmethod
    @property
    def path_route(cls):
        return '(?P<pk>\w+)/' + super().path_route

    @ContextProperty
    def url(self):
        return UrlView(self, self.instance.pk)

    @ContextCachedProperty
    def instance(self):
        return self.module.MODEL.objects.get(pk=self.request.resolver_match.kwargs['pk'])

    @property
    def instance_slug(self):
        return '%s_%s' % (to_snake_case(self.__class__.__name__), self.instance.pk)

    @ContextProperty
    def title(self):
        return str(self.instance)

    @property
    def permission(self):
        return self.instance

    def on_post_success_message(self, request, *args, **kwargs):
        self.message_success('%s saved!' % self.instance)

    def on_post_invalid_message(self, request, *args, **kwargs):
        self.message_error('%s not saved!' % self.instance)


class ResponseNoContentMixin:

    def get(self, request, *args, **kwargs):
        self.response_no_content()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.response_no_content()
        return super().post(request, *args, **kwargs)


class TabsMixin:

    class Tabs:

        class Link:
            index = None

            def __init__(self, title, url, slug=None):
                self.title = title
                self.url = url
                self._slug = slug

            @property
            def slug(self):
                return self._slug or self.index

        def __init__(self, *links, selected=0, remember=False):
            self.selected = selected
            self.remember = remember
            self.links = links

            for i, l in enumerate(self.links):
                l.index = i

        @property
        def active(self):
            return self.links[self.selected]

    def __init__(self, *args, **kwargs):
        class TabsView(TabsMixin.Tabs):
            view = self
        self.Tabs = TabsView
        super().__init__(*args, **kwargs)

    @ContextProperty
    def tabs(self):
        raise NotImplementedError()

    @classmethod
    @property
    def slug_tab(cls):
        return f'{cls.slug_module}_tab'

    @property
    def tab_query_var(self):
        return self.slug_tab

    @classmethod
    @property
    def path_route(cls):
        return super().path_route + f'(?:(?P<{cls.slug_tab}>\w+)/)?'

    def on_get(self, request, *args, **kwargs):
        super().on_get(request, *args, **kwargs)

        session_key = f'tabs-remember-{self.slug_tab}'
        if self.tabs.remember and session_key in request.session:
            self.tabs.selected = int(request.session[session_key])

        if self.tab_query_var in request.GET:
            self.tabs.selected = int(request.GET[self.tab_query_var])

        slug_tab_value = self.request.resolver_match.kwargs.get(self.slug_tab)
        if slug_tab_value:
            for link in self.tabs.links:
                if link.slug == slug_tab_value:
                    self.tabs.selected = int(link.index)
                    break
            else:
                raise ValueError(f"Tab slug '{slug_tab_value}' not found.")

        if self.tabs.active.slug:
            new_path = self.url(**{self.slug_tab: self.tabs.active.slug})
            slug_location_bar = self.location_bar.resolver_match.kwargs.get(self.slug_tab)
            push = slug_location_bar not in (None, slug_tab_value)
            self.location_bar(path=new_path, push=push)

        if self.tabs.remember:
            request.session[session_key] = int(self.tabs.selected)


class ModalMixin:

    class Modal:

        def __init__(self, url, _id=None):
            self.url = url
            self.id = _id or f'modal_{self.view.slug_global}'

    def __init__(self, *args, **kwargs):
        class ModalView(ModalMixin.Modal):
            view = self
        self.Modal = ModalView
        super().__init__(*args, **kwargs)

