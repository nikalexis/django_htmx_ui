import functools
import importlib
import inspect
import re
from urllib.parse import urlencode, urlparse, parse_qsl

from django.urls import path, include, reverse, resolve
from django.shortcuts import redirect
from django_htmx.http import HttpResponseClientRedirect


class ContextProperty(property):
    pass


class ContextCachedProperty(functools.cached_property):
    pass


class Url:

    class Query:

        def __init__(self, query_list, url):
            self.query_list = query_list
            self.url = url

        def __call__(self, *args, **kwargs):
            self.add(*args, **kwargs)
            return self.url

        def reset(self, *args, **kwargs):
            self.query_list = []
            self.add(*args, **kwargs)
            return self.url

        def set(self, query_list):
            self.query_list = query_list
            return self.url

        def add(self, *args, **kwargs):
            for name, value in args:
                self.query_list.append((name, value))
            self.update(**kwargs)
            return self.url

        def remove(self, name):
            self.query_list = [(n, v) for n, v in self.query_list if n != name]
            return self.url

        def update(self, **kwargs):
            for name, value in kwargs.items():
                self.remove(name)
                self.query_list.append((name, value))
            return self.url

    def __init__(self, path, query_list):
        self.path = str(path)
        self.query = Url.Query(query_list, self)

    def __call__(self, path=None, query_list=None):
        if path is not None:
            self.path = path
        if query_list is not None:
            self.query = Url.Query(query_list, self)
        return self

    def __str__(self):
        urlencoded = urlencode(self.query.query_list)
        return (str(self.path) + '?' + urlencoded) if urlencoded else str(self.path)

    def __eq__(self, other):
        return str(self) == str(other)

    @classmethod
    def create(cls, view, *args, **kwargs):
        if type(view) is str and view.find('.') == -1:
            path = reverse(view, args=args, kwargs=kwargs)
            # view_class = getattr(resolve(path).func, 'view_class', None)
        else:
            if type(view) is str and view.find('.') >= 0:
                module_name, class_name = view.rsplit(".", 1)
                module = importlib.import_module(module_name)
                klass = getattr(module, class_name)
            elif type(view) is type:
                klass = view
            else:
                klass = view.__class__
            app, views, crud = klass.__module__.split('.')
            path = reverse(f'{app}:{crud}:{klass.slug}', args=args, kwargs=kwargs)
            # view_class = resolve(path).func.view_class

        url = cls(path, [])
        return url


class UrlView:

    def __init__(self, view, *args, **kwargs):
        self.view = view
        self.args = args
        self.kwargs = kwargs

    def update(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        del self._url
        return self

    @functools.cached_property
    def _url(self):
        return Url.create(self.view, *self.args, **self.kwargs)

    @property
    def path(self):
        return self._url.path

    @property
    def query(self):
        return self._url.query

    def __str__(self):
        return str(self._url)

    def __call__(self, view=None, *args, **kwargs):
        if view is None:
            return UrlView(self.view, *(args or self.args), **{**self.kwargs, **kwargs})
        else:
            return UrlView(view, *args, **kwargs)


class Location(Url):

    def __init__(self, path, query_list, push=False):
        self.push = push
        super().__init__(path, query_list)

    def __call__(self, path=None, query_list=None, push=False):
        if push is not None:
            self.push = push
        return super().__call__(path, query_list)

    @property
    def resolver_match(self):
        return resolve(self.path)

    @classmethod
    def create_from_url(cls, location_url):
        parsed_url = urlparse(location_url)
        parsed_path = parsed_url.path
        parsed_qsl = parse_qsl(parsed_url.query)

        url = cls(parsed_path, parsed_qsl)
        return url


def collect_paths(module, app_name):
    from django_htmx_ui.views.generic import BaseTemplateView
    from django_htmx_ui.views.mixins import OriginTemplateMixin
    members = inspect.getmembers(
        module,
        lambda o:
            inspect.isclass(o) and
            issubclass(o, BaseTemplateView) and
            OriginTemplateMixin not in o.__bases__ and
            o.__module__ == module.__name__
    )
    slug = getattr(module, 'SLUG', module.__name__.split('.')[-1])
    path_route = getattr(module, 'PATH_ROOT', slug + '/')
    includes = [
        klass.path
        for name, klass in members
        if hasattr(klass, 'path')
    ]
    paths = path(path_route, include((includes, app_name), namespace=slug))
    return paths


def x_redirect(request,  url):
    if request.htmx:
        return HttpResponseClientRedirect(url)
    else:
        return redirect(url)


def paginated(items_per_page):
    def inner(func):
        def wrapper(self, *args, **kwargs):
            page = max(1, int(self.request.GET.get('page', 1)))
            index = (page - 1) * items_per_page
            return func(self, *args, **kwargs)[index:index+items_per_page]
        return wrapper
    return inner


def indexed(field, items_per_round, reverse=False):
    def inner(func):
        def wrapper(self, *args, **kwargs):
            qs = func(self, *args, **kwargs).order_by(f'-{field}' if reverse else field)
            last_field = getattr(self, f'last_{field}', self.request.GET.get(f'last_{field}'))
            if last_field:
                qs = qs.filter(**{
                    f'{field}__' + ('lt' if reverse else 'gt'): last_field,
                })
            return qs[0:items_per_round]
        return wrapper
    return inner


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def to_camel_case(name):
    return ''.join(word.title() for word in name.split('_'))


def merge(a, b, path=None, raise_conflicts=True):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif raise_conflicts:
                raise ValueError('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a
