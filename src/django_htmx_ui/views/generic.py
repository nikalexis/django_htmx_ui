import importlib
import inspect
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import engines
from django.urls import path, reverse, NoReverseMatch
from django.views.generic import TemplateView, RedirectView
from django_htmx.http import HttpResponseLocation, trigger_client_event

from django_htmx_ui.utils import ContextProperty, ContextCachedProperty, merge, to_snake_case


class PublicTemplateView(TemplateView):
    response = None

    def setup(self, request, *args, **kwargs):
        self.headers = {}
        self.triggers = []
        self.request = request
        self.add_context('request', request)
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ret = self.on_get(request, *args, **kwargs)
        if ret:
            return ret
        elif self.response:
            return self.response_prepare(self.response)
        else:
            return super().get(request, *args, **kwargs)

    def on_get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        ret = self.on_post(request, *args, **kwargs)
        if ret:
            return ret
        elif self.response:
            return self.response_prepare(self.response)
        else:
            return super().get(request, *args, **kwargs)

    def on_post(self, request, *args, **kwargs):
        pass

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        return self.response_prepare(response)

    def response_location(self, *args, **kwargs):
        self.response = HttpResponseLocation(*args, **kwargs)
        return self.response

    def response_prepare(self, response):
        return self.apply_headers(self.apply_triggers(response))

    def apply_headers(self, response):
        for key, value in self.headers.items():
            response[key] = value
        return response

    def apply_triggers(self, response):
        for args, kwargs in self.triggers:
            trigger_client_event(response, *args, **kwargs)
        return response

    def trigger_client_event(self, *args, **kwargs):
        self.triggers.append((args, kwargs))

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

    def message_info(self, message):
        messages.info(self.request, message)

    def message_success(self, message):
        messages.success(self.request, message)

    def message_warning(self, message):
        messages.warning(self.request, message)

    def message_error(self, message):
        messages.error(self.request, message)


class PrivateTemplateView(LoginRequiredMixin, PublicTemplateView):

    @ContextProperty
    def user(self):
        return self.request.user


class PrivateRedirectView(LoginRequiredMixin, RedirectView):
    pass
