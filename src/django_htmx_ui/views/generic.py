import importlib
import inspect
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import engines
from django.urls import path, reverse, NoReverseMatch
from django.views.generic import TemplateView, RedirectView

from django_htmx_ui.utils import ContextProperty, ContextCachedProperty, merge, to_snake_case


class PublicTemplateView(TemplateView):

    def setup(self, request, *args, **kwargs):
        self.headers = {}
        self.request = request
        self.add_context('request', request)
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ret = self.on_get(request, *args, **kwargs)
        if ret:
            return ret
        else:
            return super().get(request, *args, **kwargs)

    def on_get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        ret = self.on_post(request, *args, **kwargs)
        if ret:
            return ret
        else:
            return super().get(request, *args, **kwargs)

    def on_post(self, request, *args, **kwargs):
        pass

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        for key, value in self.headers.items():
            response[key] = value
        return response

    def decorators_context(self):
        return {
            name: getattr(self, name)
            for name, method in inspect.getmembers(self.__class__, lambda o: isinstance(o, (ContextProperty, ContextCachedProperty)))
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **self.decorators_context(),
            **getattr(self, '_context', {}),
        }

    def get_template_names(self):
        if not self.request.htmx:
            return self.template_root
        else:
            return super().get_template_names()

    def add_context(self, key, value):
        setattr(self, '_context', merge(getattr(self, '_context', {}), {key: value}))

    @classmethod
    @property
    def module(cls):
        return importlib.import_module(cls.__module__)

    @classmethod
    @property
    def slug(cls):
        return to_snake_case(cls.__name__)

    @classmethod
    @property
    def instance_slug(cls):
        return cls.slug

    @classmethod
    @property
    def slug_module(cls):
        slug = getattr(cls.module, 'SLUG', cls.__module__.replace('.', '_'))
        return slug

    @classmethod
    @property
    def path_root(cls):
        return cls.slug + '/'

    @classmethod
    @property
    def path(cls):
        return path(cls.path_root, cls.as_view(), name=cls.slug)

    @property
    def prefix(self):
        if hasattr(self.module, 'PREFIX'):
            prefix = self.module.PREFIX
        else:
            app, views, crud = self.__class__.__module__.split('.')
            prefix = f'{app}:{crud}:'
        return prefix

    def reverse(self, viewname, args=None):
        return reverse(self.prefix + viewname, args=args)

    @ContextProperty
    def url(self):
        try:
            return self.reverse(self.slug)
        except NoReverseMatch:
            return '/'

    @property
    def templates_dir(self):
        if hasattr(self.module, 'TEMPLATES_DIR'):
            return self.module.TEMPLATES_DIR
        else:
            app, views, crud = self.__class__.__module__.split('.')
            return f'{app}/{crud}/'

    @property
    def template_file(self):
        return self.slug + '.html'

    @property
    def template_name(self):
        return self.templates_dir + self.template_file

    def render(self, context):
        template = engines['django'].get_template(self.template_name)
        return template(self.get_context_data(**context))

    @ContextProperty
    def slug_panel(self):
        return self.slug_module

    @ContextProperty
    def title(self):
        return getattr(self.module, 'TITLE', self.project_title)

    @ContextProperty
    def icon(self):
        return getattr(self.module, 'ICON', '')

    @ContextProperty
    def project_title(self):
        return os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]


class PrivateTemplateView(LoginRequiredMixin, PublicTemplateView):

    @ContextProperty
    def user(self):
        return self.request.user


class PrivateRedirectView(LoginRequiredMixin, RedirectView):
    pass
