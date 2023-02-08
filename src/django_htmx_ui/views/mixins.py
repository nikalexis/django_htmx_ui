
class TabsMixin:

    class Tabs:

        class Link:
            index = None

            def __init__(self, title, url):
                self.title = title
                self.url = url

        def __init__(self, *links, selected=0, remember=False):
            self.selected = selected
            self.remember = remember
            self.links = links

            for i, l in enumerate(self.links):
                l.index = i

        @property
        def active(self):
            return self.links[self.selected]

    def on_get(self, request, *args, **kwargs):
        super().on_get(request, *args, **kwargs)

        selected = request.GET.get('selected', '')
        if selected.isnumeric():
            self.tabs.selected = int(selected)

        if self.tabs.remember:
            session_key = 'tabs-remember-%s' % (self.prefix + self.slug)
            if selected:
                request.session[session_key] = selected
            else:
                self.tabs.selected = request.session.setdefault(session_key, self.tabs.selected)
