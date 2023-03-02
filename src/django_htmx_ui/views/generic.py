import importlib
import inspect
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import engines
from django.urls import re_path
from django.views.generic import TemplateView, RedirectView
from django_htmx.http import HttpResponseLocation, trigger_client_event, HttpResponseClientRedirect

from django_htmx_ui.utils import ContextProperty, ContextCachedProperty, merge, to_snake_case, UrlView, Location
from django_htmx_ui.views.mixins import OriginTemplateMixin


class BaseTemplateView(TemplateView):
    response = None

    def setup(self, request, *args, **kwargs):
        self.headers = {}
        self.triggers = []
        self.request = request
        self.location_bar = Location.create_from_url(self.bar_url())
        self.location_req = Location.create_from_url(request.META['PATH_INFO'])
        self.add_context('request', request)
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ret = self.on_get(request, *args, **kwargs)
        if ret:
            return ret
        elif self.response:
            return self.response_prepare(self.response)
        else:
            return self.response_prepare(super().get(request, *args, **kwargs))

    def on_get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        ret = self.on_post(request, *args, **kwargs)
        if ret:
            return ret
        elif self.response:
            return self.response_prepare(self.response)
        else:
            return self.response_prepare(super().get(request, *args, **kwargs))

    def on_post(self, request, *args, **kwargs):
        pass

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        return self.response_prepare(response)

    def response_location(self, *args, **kwargs):
        self.response = HttpResponseLocation(*args, **kwargs)
        return self.response

    def response_no_content(self):
        self.response = HttpResponse(status=204)
        return self.response

    def response_prepare(self, response):
        for func in (self.apply_triggers, self.apply_headers, self.apply_location):
            response = func(response)
        return response

    def apply_headers(self, response):
        for key, value in self.headers.items():
            response[key] = value
        return response

    def apply_triggers(self, response):
        for args, kwargs in self.triggers:
            trigger_client_event(response, *args, **kwargs)
        return response

    def apply_location(self, response):
        if self.request.htmx and self.location_bar != Location.create_from_url(self.bar_url()):
            response['HX-Push-Url' if self.location_bar.push else 'HX-Replace-Url'] = str(self.location_bar)
        return response

    def trigger_client_event(self, *args, **kwargs):
        self.triggers.append((args, kwargs))

    def decorators_context(self):
        return {
            name: getattr(self, name)
            for name, method in inspect.getmembers_static(
                self.__class__,
                lambda o:
                    isinstance(o, (
                        ContextProperty,
                        ContextCachedProperty,
                    ))
            )
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **self.decorators_context(),
            **getattr(self, '_context', {}),
        }

    def get_template_names(self):
        if not self.request.htmx:
            return self.template_origin
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
    def slug_global(cls):
        return f'{cls.slug_module}_{cls.slug}'

    @classmethod
    @property
    def path_route(cls):
        return cls.slug + '/'

    @classmethod
    @property
    def path(cls):
        return re_path(rf'^{cls.path_route}$', cls.as_view(), name=cls.slug)

    def redirect(self, url):
        if self.request.htmx:
            return HttpResponseClientRedirect(url)
        else:
            return redirect(url)

    @ContextProperty
    def url(self):
        return UrlView(self)

    def bar_url(self):
        return self.request.headers.get('HX-Current-URL', self.request.META['PATH_INFO'])

    @classmethod
    @property
    def templates_dir(cls):
        if hasattr(cls.module, 'TEMPLATES_DIR'):
            return cls.module.TEMPLATES_DIR
        else:
            app, views, crud = cls.__module__.split('.')
            return f'{app}/{crud}/'

    @classmethod
    @property
    def template_file(cls):
        return cls.slug + '.html'

    @classmethod
    @property
    def template_name(cls):
        return cls.templates_dir + cls.template_file

    @classmethod
    @property
    def template_origin(cls):
        for super_cls in cls.__mro__:
            if OriginTemplateMixin in super_cls.__bases__:
                return super_cls.template_name
        raise ValueError('You must define an `OriginTemplateMixin`.')

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


class PublicTemplateView(BaseTemplateView):
    pass


class PrivateTemplateView(LoginRequiredMixin, PublicTemplateView):

    @ContextProperty
    def user(self):
        return self.request.user
