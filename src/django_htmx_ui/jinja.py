from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django_htmx.jinja import django_htmx_script
from django.utils.translation import gettext, ngettext
import humanize

from jinja2 import Environment


def environment(**options):
    options.update({'extensions':['jinja2.ext.i18n']})
    env = Environment(**options)
    env.install_gettext_callables(gettext=gettext, ngettext=ngettext, newstyle=True)
    env.globals.update({
        'static': static,
        'url': reverse,
        'humanize': humanize,
        'now': timezone.now,
        'django_htmx_script': django_htmx_script,
    })
    return env
