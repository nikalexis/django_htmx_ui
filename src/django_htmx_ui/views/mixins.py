from django.core.exceptions import ViewDoesNotExist
from django.shortcuts import redirect
from django.utils.text import slugify

from django_htmx_ui.utils import ContextProperty, ContextCachedProperty, UrlView, to_snake_case


class OriginTemplateMixin:
    push_url = True

    def get(self, request, *args, **kwargs):
        if request.htmx and OriginTemplateMixin in self.__class__.__bases__:
            raise ViewDoesNotExist("View '%s' is an 'OriginTemplateMixin'." % self.__class__.__name__)
        else:
            if self.push_url is not None and self.location_bar.path != self.location_req.path:
                self.location_bar(path=self.location_req.path, query_list=self.location_req.query.query_list, push=self.push_url)
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
        return super().url(self, self.instance.pk)

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
                return self._slug or str(self.index)

        def __init__(self, *links, selected=0, remember=False, titles_slugify=True):
            self.selected = selected
            self.remember = remember
            self.links = links

            for i, l in enumerate(self.links):
                l.index = i
                if titles_slugify and l._slug is None:
                    l._slug = slugify(l.title).replace('-', '_') or None
                    if l._slug in [ls.slug for ls in self.links if ls.index != l.index]:
                        l._slug = None

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
        return f'{cls.slug_global}_tab'

    @property
    def tab_query_var(self):
        return self.slug_tab
    
    @property
    def tab_session_key(self):
        return f'tabs-remember-{self.slug_tab}'
    
    @property
    def tab_selected_candidates(self):
        return [
            self.location_req.query.get(self.tab_query_var, True),
            self.location_bar.query.get(self.tab_query_var, True),
            self.request.resolver_match.kwargs.get(self.slug_tab),
            self.request.session.get(self.tab_session_key),
        ]

    @classmethod
    @property
    def path_route(cls):
        return super().path_route + f'(?:(?P<{cls.slug_tab}>\w+)/)?'

    @ContextProperty
    def url(self):
        url = super().url
        slug = self.request.resolver_match.kwargs.get(self.slug_tab)
        if slug:
            return url(self, *(url.args + (slug,)))
        else:
            return super().url

    def on_get(self, request, *args, **kwargs):
        super().on_get(request, *args, **kwargs)

        if self.request.session.get(self.tab_session_key) not in [None] + [l.slug for l in self.tabs.links]:
            del self.request.session[self.tab_session_key]

        for c in self.tab_selected_candidates:
            if c is not None:
                for link in self.tabs.links:
                    if c in (link._slug, str(link.index)):
                        self.tabs.selected = link.index
                        break
                else:
                    raise ValueError(f"Tab slug '{c}' not found.")
                break

        if self.location_bar.resolver_match.view_name == self.url.resolver_match.view_name:
            new_path = self.url().update(**{**self.request.resolver_match.kwargs, **{self.slug_tab: self.tabs.active.slug}})
            self.location_bar(path=new_path).query.remove(self.tab_query_var)
        else:
            current_slug = self.location_bar.query.get(self.tab_query_var)
            if current_slug != self.tabs.active.slug:
                push = current_slug is not None
                self.location_bar(push=push).query(**{self.tab_query_var: self.tabs.active.slug})

        if self.tabs.remember:
            request.session[self.tab_session_key] = self.tabs.active.slug


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

