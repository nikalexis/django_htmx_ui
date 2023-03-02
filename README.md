# Intro

## What is `django_htmx_ui` library

This library is made to combine and help leveraging:
* the full-stack [django](https://www.djangoproject.com/) framework
* the frontend [htmx](https://htmx.org/) framework
* the [django-htmx](https://django-htmx.readthedocs.io/en/latest/) library
* the [jinja](https://jinja.palletsprojects.com/en/3.1.x/) template engine

It is basically a django app that provides:
* Extended django `Views` with htmx build-in functionality
* `CRUD Views` (Create, Retrieve, Update, Delete) for django models
* Some extra `Mixins` to use with your `Views` to make life easier
* A ready to use `jinja` environment
* Some `Middlewares` for automations
* Extra `utils` and `decorators` for common use cases

# Requirements

* Python 3.11
* Django 4.1
* htmx 1.8
* jinja 3.1

# Installation

  * via pip

        pip install django_htmx_ui`

  * or add library into requirements.txt

        django_htmx_ui

# Usage

## Setup

1. Add the app in your `settings.py`:

        INSTALLED_APPS = [
            # ...
            'django_htmx_ui',
            # ...
        ]

2. Add the middlewares you would like to use in your `settings.py`:

        MIDDLEWARE = [
             # ...
            'django_htmx_ui.middleware.HtmxMessagesMiddleware',
             # ...
        ]

3. Add the jinja environment in your `settings.py`:

        TEMPLATES = [
             {
                 'BACKEND': 'django.template.backends.jinja2.Jinja2',
                 'DIRS': [BASE_DIR / 'jinja2'],
                 'APP_DIRS': True,
                 'OPTIONS': {
                     'environment': 'django_htmx_ui.jinja.environment',
                 },
             },
             # ... you can also keep your django templates engine here ...
        ]
      
    You can also extend it by creating your own in `your_project/jinja.py` module:

        import django_htmx_ui.jinja

        def environment(**options):
            env = django_htmx_ui.jinja.environment(**options)

            # Add your own jinja functionalities like globals or filters here.
          
            return env

    and then replace the `'environment'` variable inside the `'OPTIONS'` key:

        # ...
        'OPTIONS': {
            'environment': 'your_project.jinja.environment',
        },
        # ...

## Views

### Defining views

The recommended structure to place your views inside your project is the following:

* `django_project/`
  * `django_app/`
    * `views/`
      * `module_a.py`
      * `module_b.py`

Inside each view module (e.g. `module_a.py`) you can assign some optional module globals,
that will be used by all your `ViewTemplate` classes inside the module, such as:

`SLUG`: A slug name for the module  
`TEMPLATES_DIR`: The directory of the view's templates    
`TITLE`: A title for all views  
`ICON`: An icon for all views  
`MODEL`: A model in your database to automate the CRUD functionality for this module  

Then you can create some `TemplateView` classes, like this:

`module_a` file:

    class UserDashboard(PrivateTemplateView):
        ... your special properties go here ...

`module_b` file:

    MODEL = User

    class List(CrudListMixin, PrivateTemplateView):
        ... your special properties go here ...

    class Update(CrudUpdateMixin, PrivateTemplateView):
        ... your special properties go here ...

    class Display(CrudDisplayMixin, PrivateTemplateView):
        ... your special properties go here ...

By default, the templates will be searched automatically in the directories:

* `django_project/`
  * `django_app/`
    * `jinja2/`
      * `django_app/`
        * `module_a/`
          * `user_dashboard.html` for class named `UserDashboard` in your `module_a`
        * `module_b/`
          * `list.html` for class named `List` in your `module_b`
          * `update.html` for class named `Update` in your `module_b`
          * `display.html` for class named `Display` in your `module_b`

To make you life even easier you can use the `django_htmx_ui.utils.collect_paths`
function to help you automatically build your app's `urls.py` file.

For example `django_project/django_app/urls.py` should be:

    from django_app.views import module_a, module_b
    from django_htmx_ui.utils import collect_paths
    
    
    app_name = 'django_app'
    urlpatterns = [
        collect_paths(module_a, app_name),
        collect_paths(module_b, app_name),
    ]

### Best practices when developing your project

#### Creating origin root templates containing the <html> tag pages.

When the browser makes the first http, this will be outside htmx.
From now on, we will call this page an origin page, because it must serve all the basic
components to load a standard html page, like <html>, <head> tag and javascript
libraries including htmx.

If you build a big project, chances are that you will need more than one origin pages.

For example, login, signup, password forget, errors etc. pages, can be part of an origin
page called `WelcomeOrigin(OriginTemplateMixin, PublicTemplateView)`.
Please notive that we used the `OriginTemplateMixin` to tag that this view is an origin
and the `PublicTemplateView` to tag that it will be accessible by everyone.

Other pages, like dashboard, account, user profile, etc. need to be accessible only by
the signed-in user, so the origin page could be called
`DefaultPanelOrigin(OriginTemplateMixin, PrivateTemplateView)`.

`WelcomeOrigin` and `DefaultPanelOrigin` templates will be used as the base html page.

#### Creating your sub-pages

All sub-pages can extend these two basic classes like this:
`Login(WelcomeOrigin)` or `Dashboard(DefaultPanelOrigin)`.
These sub-pages will have their own templates, but will be served by a htmx lazy-load get.

#### Creating a partial sub-page

If you now want to create a Widget inside your user's dashboard page, you can define
its view as `Widget(PartialMixin, DefaultPanelOrigin)`. Please, notice the usage of the
`PartialMixin`. When you add this Mixin, it means that this view can only be requested
via a htmx request, therefore it can't be opened directly from the browser's address
bar.

#### Creating your first html with htmx usage

This is a very simplified example to make you understand what this library does.

Firstlt, we must create some views:

`app_name/views/welcome.py`:

    class WelcomeOrigin(OriginTemplateMixin, PublicTemplateView):
        pass

    class Login(FormMixin, WelcomeOrigin):
        
        class Form(forms.Form):
            user = forms.CharField()
            password = forms.CharField()

In order to display the above views, we create also their templates:

`app_name/jinja2/app_name/welcome/welcome_origin.html`:

    <html>
        <head>...</head>
        <body>
            <div hx-get="{{ url }}">
        </body>
    </html>

`app_name/jinja2/app_name/welcome/login.html`:
    
    <p>Login Form:</p>
    <form>
        {{ form }}
    </form>

This an incomplete and simplified example to demonstrate how this library works.
You can create more complex scenarios, if you dive in the following documentation.

### Generic Views

The following `Views` are basically an extended version of django's class `TemplateView`
to include all the helper properties and the shortcuts to make your life easier
with the combination of the htmx library. The first step is to choose the right
class type to extend, according to your needs, and apply all the extra properties.
Feel free to override any properties and extend futher more your own classes. 

#### *django_htmx_ui.views.generic.*__PublicTemplateView__

This class extends the django's `TemplateView` class and
is the main class that provides the basic functionality.
The `Public` keyword in the name refers that the class is
__not__ requiring the user to be authenticated in order to
access the view.

_Provides the following attributes:_

`on_get (self, request, *args, **kwargs)` method

This is called any time a http __GET__ request is made to the view.
You can return a django's `Response` object.
If you don't return, the template of the view will be
rendered and returned as a response.

`on_post (self, request, *args, **kwargs)` method

This is called any time a http __POST__ request is made to the view.
You can return a django's `Response` object.
If you don't return, the template of the view will be
rendered and returned as a response.

`request` property

This property refers to the `Request` django's object.
You can use this property in any method you describe in your views.

`response` property

Another way you can set a response, is by setting the `self.response` property.
This is a rare case and in most cases you will not need to set or access this
property directly.

`response_location (self, *args, **kwargs)` method

When the view is used by a htmx request, you can use this function to make a
`django_htmx.http.HttpResponseLocation` response. All `args` and `kwargs` are
passed through.

`response_no_content (self)` method

Use this as a response when you have no content to send.

`redirect (self, url)` method

Use this as a response to redirect the browser's location in another path.
Keep in mind that the whole will be refreshed, even if you are inside a htmx request.

`url` context property

Use this property to retrieve current view's `UrlView` object.
You can use inside your template file via the variable `{{ url }}`.
You can also add GET query parameters easily with `{{ url.query(page=1) }}`.
See the `UrlView` object description for more.

`url(view, *args, **kwargs)` method

The `url` attribute can also be called as a method.
Use this method to build a new `UrlView` object, based on a `TemplateView` object.
The `view` parameter can be either a view name (e.g. `'django_app:module:my_view'`) or
a python view path (e.g. `'django_app.views.module.MyView'`) or
a `TemplateView` object.
All `args` and `kwargs` are passed through to the django `reverse` function to build
the url.
You can use inside your template file with `{{ url('django_app:module:my_view') }}`.

`location_bar` property

This property refers to the location (URL) bar of the browser.
Under the hook, it reads the htmx's `HX-Current-URL` header, and if this is not
available (aka is not a htmx request), it will read the `request.META['PATH_INFO']`.
You can also update the location bar anywhere in your view.
See the `Location` object description for more.

`location_req` property

This property refers to the location (URL) of the current server request.
Under the hook, it will always read the `request.META['PATH_INFO']` and create a
`Location` object for you.
See the `Location` object description for more.

`headers` dictionary

Use this dictionary property to add headers at the response.

`trigger_client_event (self, *args, **kwargs)` method

When the view is used by a htmx request, you can send a htmx client event using this
function. All `args` and `kwargs` are passed through to the
`django_htmx.http.trigger_client_event` function and finally to the browser event object.

`slug_global` class property

This class property defines a global slug to use as a unique identifier for the `TemplateView`
in you entire project.
By default, it's a combination of `slug_module` + `slug` described below.

`slug_module` class property

This class property defines the slug name of the module that your view belongs to.
You can alter this property and build your own method if needed.

`slug` class property

This class property defines the slug name of your view.
By default, it returns the name of the class with snake case conversion
(e.g. MyClass becomes my_class).
This will be used with the module slug to build the view path ('my_module/my_class/').
You can alter this property and build your own method if needed.

`path_route` class property

This class property defines the path route that your view wants to define in django's
url system.
This property is a shortcut for the parameter route of django's `re_path`,
using regular expressions to describe the route and the url parameters. 
See also the `path` property following, if you need greater path handling.

`path` class property

This class property returns the actual path object that django can recognize.
You can overwrite the property and return any of `path` or `re_path`.

Be aware, that you must include the path of the view in your urls.
An easy way to do this, is by using the `collect_paths` helper method in the `utils.py`.

`templates_dir` property

This property defines the directory that contains the templates files.
The default directory for every view module is the `app_name/module_name/` directory.
You can also change the module-wide default directory by setting a property called
`TEMPLATES_DIR` inside the module.

`template_file` property

You can set the template file of the view.
By default, the path is taken by the name of the view in a snake case plus a `.html`
extension (e.g. `MyView` template file becomes `my_view.html`).

`template_name` property

This is the full path of the template.
It is recommended as a first option to alter the templates_dir or templates_file
properties, by fill free to provide the final full path if needed.
By default, this property equals to `templates_dir` + `template_file`.

`project_title` context property

This is the title of your project. It's part of the context for every view, so you can
use it inside your templates as a variable.
By default, the project title is the name of the directory that contains the
`settings.py` file.

`title` context property

This is the title of the view.
You can set this property and read it inside your templates.
By default, this property is derived by the module variable called `TITLE`.
If `TITLE` is not available, the project title is the default fallback.

`icon` context property

It is sometimes useful in the frontend to print an icon, relative to the module the
user is viewing.
You can set this property and read it inside your templates.
By default, this property is derived by the module variable called `ICON`.
If `ICON` is not available, the empty string `''` is the default fallback.

`message_info (self, message)` method  
`message_success(self, message)` method  
`message_warning(self, message)` method  
`message_error(self, message)` method  

You can use these shortcut methods to send messages in the django's messaging system.
Enable also the `HtmxMessagesMiddleware` to automatically send a htmx event every time
new messages are available to display in the frontend.


#### *django_htmx_ui.views.generic.*__PrivateTemplateView__

This class extends the `PublicTemplateView` class and uses
the django's `LoginRequiredMixin` to check if the current user
is authenticated. If not, makes a redirect to the login page.

_Provides the following attributes:_

`user` context property

This is a shortcut to the `request.user`.
You can use this inside your templates with `{{ user }}` to refer to the user object
as needed.

### Decorators

Using the following decorators you can tag any method inside your `TemplateView`
and benefit from the automations it applies.

#### *django_htmx_ui.utils.*__ContextProperty__

If you decorate any method with this magic decorator it will automatically convert it
in a property and pass it through the template engine context as a variable.

For example:

    class MyView(PublicTemplateView):

        @ContextProperty
        def variable_name(self):
            return 'This is a test string to demonstrate the functionality.'

Now you can use `{{ variable_name }}` inside your template file `my_view.html`.

#### *django_htmx_ui.utils.*__ContextCachedProperty__

The same as `django_htmx_ui.utils.ContextProperty`, but the result is cached using the
`functools.cached_property`. You can call many times the property
(e.g. print a variable in many places inside a template), but the method will be called
only once.

### CRUD Views

#### *django_htmx_ui.views.crud.*__CrudMixin__

This is the Base Mixin for all following Crud* classes.

_Provides the following attributes:_

`permission` property

You can define this property to check if the current request or user has the permission
to access the view and return True or False based on your own criteria.
By default, this property will return True and grant access to the view.

#### *django_htmx_ui.views.crud.*__CrudCreateMixin__ (CrudMixin, FormMixin)

Add this Mixin to your `TemplateView` classes to add the object creation functionality.
It basically combines the `CrudMixin` and the `FormMixin` mixnins.

#### *django_htmx_ui.views.crud.*__CrudRetrieveMixin__ (CrudMixin, FormMixin)
#### *django_htmx_ui.views.crud.*__CrudListMixin__ (CrudMixin, FormMixin)

`CrudListMixin` is an alias of `CrudRetrieveMixin`.
Add this Mixin to your `TemplateView` classes to add the object listing functionality.
It basically combines the `CrudMixin` mixnin, with some extra helper attributes.

_Provides the following attributes:_

`filter` dictionary property

You can define a django filter to list only the item you want.
By default, all model objects will be listed.

`filters_get` dictionary property

This is an automation to help you define extra filters through the query GET request
parameters.
You can add a query parameter in the form of `filter_ + field_name` and the object will
be filtered out.
You can create more complex scenarios by overwriting this behaviour.

`instances` context property

This property will return all filtered objects and is ready to use inside your
template file, using `{{ instances }}` variable.
In combines `filter` dictionary and `filters_get` dictionary, as described above. 

#### *django_htmx_ui.views.crud.*__CrudUpdateMixin__ (InstanceMixin, CrudMixin)

Add this Mixin to your `TemplateView` classes to add the object update functionality.
It basically combines the `CrudMixin` and the `InstanceMixin` mixnins.

#### *django_htmx_ui.views.crud.*__CrudDisplayMixin__ (InstanceMixin, CrudMixin)

Add this Mixin to your `TemplateView` classes to add the object display functionality.
It basically combines the `CrudMixin` and the `InstanceMixin` mixnins.

#### *django_htmx_ui.views.crud.*__CrudActionMixin__ (InstanceMixin, CrudMixin)

Add this Mixin to your `TemplateView` classes to add the object action functionality.
It basically combines the `ResponseNoContentMixin`, `CrudMixin`
and the `InstanceMixin` mixnins.
It can be used to build custom object actions, according to your specific needs. 

#### *django_htmx_ui.views.crud.*__CrudDeleteMixin__ (CrudActionMixin)

Add this Mixin to your `TemplateView` classes to add the object delete functionality.
It basically is a `CrudActionMixin` subclass to implement the delete function,
which is the most common action in an object based on the CRUD modeling.

If you send a http POST in this view, the object will be deleted using the
`self.instance.delete()` django's function and a success or invalid message will be set.
You can alter these behaviours by overwriting `on_post`, `on_post_success_message` and
`on_post_invalid_message` attributes.

### Mixins

The following Mixins are available to automate some common scenarios.
Feel free to extend them more or overwriting the attributes.

#### *django_htmx_ui.views.mixins.*__FormMixin__

Add this Mixin in your `TemplateView`, if the view contains a form.
You can define a `Form` class inside the `TemplateView` class, which is recommended to
be a subclass of django's `Form` or `ModelForm` or any other similar kind.

For example:

    class MyView(PrivateTemplateView):

        class Form(forms.Form):
            user = forms.CharField()
            password = forms.CharField()

Or as a ModelForm:

    class MyView(PrivateTemplateView):

        class Form(forms.ModelForm):

            class Meta:
                model = MyModel
                fields = ['field1', 'field2']

Also, when a POST http request is made, `FormMixIn` will automatically test the form.

If the form is in a valid state, the `on_post` method will call
* the `save()` method of the form
* the `on_post_success_message` method, so you can overwrite it
* the `on_post_success` method, so you can overwrite it

If the form is not in a valid state, the `on_post` method will call:
*  the `on_post_invalid_message` method, so you can overwrite it
*  the `on_post_invalid` method, so you can overwrite it

_Provides the following attributes:_

`form` context cached property

Use this property as a variable `{{ form }}` in your template file to refer at the form
instance and print the form.
You can also overwrite the property in your `TemplateView` class, in order to change
the attributes of the instance of the form.

`form_instance` property

This attribute defines the django form's instance parameter, if using a `forms.ModelForm`.
By default, gets its value from the instance property, if it is available.

#### *django_htmx_ui.views.mixins.*__InstanceMixin__ (FormMixin)

Add this Mixin in your `TemplateView`, if the view contains a model form.
See `FormMixin` attributes, as this Mixin is a subclass.

_Provides the following attributes:_

`path_route` class property

It extends the path route url to include automatically the primary key (pk field) of the
model instance, in the form of `'(?P<pk>\w+)/' + super().path_route`.
You can overwrite this class property to describe your own.

`instance` context cached property

It returns the model object of the instance, reading the pk field from the url path.

`instance_slug` property

It returns a unique slug for the instance.

`title` context property

It returns the view title, taken from the string representation of the model's instance.

`on_post_success_message` method

Sets a "'Instance' saved" message, when the form is successfully saved.

`on_post_success_message` method

Sets a "'Instance' not saved" message, when the form is not valid.

#### *django_htmx_ui.views.mixins.*__PartialMixin__

Add this Mixin in your `TemplateView` for the view to be only accessible via a htmx
request.
By default, if the url of view is called directly from the browser (outside htmx call),
a redirection will happen to the `/` route path.
You can overwrite the default redirection route path by defining the `redirect_partial`
attribute of the view.

#### *django_htmx_ui.views.mixins.*__ResponseNoContentMixin__

Add this Mixin in your `TemplateView` to return `HTTP 204 No Content` as a response.
No template rendering will happen.

#### *django_htmx_ui.views.mixins.*__TabsMixin__

It is common sometimes to use Tabs (subpages) in your project.
Add this Mixin in your `TemplateView` to implement tabs' functionality.

You can use the subclass `Tab` and its subclass `Link` to define your `tabs` atttribute:

    @ContextCachedProperty
    def tabs(self):
        return self.Tabs(
            self.Tabs.Link(
                title='First tab',
                url=self.url(FirstTabView),
                slug='first_tab',
            ),
            self.Tabs.Link(
                title='Second Tab',
                url=self.url(SecondTabView),
                slug='second_tab',
            ),
            remember=True,
        )

Then you can use the `{{ tabs }}` variable to print your tabs.
The `Tabs` class provides the following attributes to use in your template file:

* `active`: the active tab `Link` object
* `selected`: the selected index as a number representation, stating from 0
* `remember`: boolean option, if you want the last tab clicked to be remembered
              automatically and be activated the next time, using a django session
* `links`: a list of all links in the `Tabs` object, with the following attributes:
  * `index`: the index number of the link, starting from 0 for the first link
  * `title`: the title of the link/tab
  * `url`: the url of the link/tab
  * `slug`: the slug of the link/tab

_Provides the following attributes:_

`slug_tab` class property

A unique slug for the tab.

`tab_query_var` property

The query keyword used on the GET request to display the selected tab.
By default, it used the `slug_tab` attribute.

`path_route` class property

The `path_route` to push or replace on the location_bar.
This will only be pushed or replaced when the active link has a slug.
By default, it binds to `super().path_route + f'(?:(?P<{cls.slug_tab}>\w+)/)?'`

#### *django_htmx_ui.views.mixins.*__ModalMixin__

It is common sometimes to use Modals in your project.
Add this Mixin in your `TemplateView` to implement a modal functionality.

You can use the subclass `Modal` to define your `modal_*` atttribute:

    @ContextCachedProperty
    def modal_create(self):
        return self.Modal(
            url=self.url(Create).query(event=self.request.GET.get('event')),
        )

In this view a `{{ modal_create }}` variable will be available in your template.
You can basically use the two attributes defined:

* `url`: the htmx url to load inside your modal
* `id`: a unique id for your modal, which is basically `modal_` + `self.slug_global`

### Utils

#### Utils Classes

`Url` class

This class represents an `Url` model you can use inside your views controller class or
in your templates files.
It converts to a url string automatically if you pass it through str() or use it inside
a `{{ url }}` brackets variable.

_Provides the following attributes:_

`__init__` (path, query_list) method

You can initialize a `Url` object by providing a path string and a query_list in the
form of tuples (name, value).

`__call__` (path=None, query_list=None) method

You can alter the path or the query_list or both as needed if you call the object again.

`path` string

The string of the url's path.

`query` Url.Query object

See below for the attributes provided.

`resolver_match` property

Returns the django's `ResolverMatch` object for the path.

`view` property

Returns the `TemplateView` class, provided by the `resolver_match` above.
Usually, it will be the view that resolves to the `Url` object.

`Url.Query` class

This class represents an `Query` model you can use inside your views controller class or
in your templates files to alter the query part of the `Url`. It automatically built
by the `Url` object and is ready to use as sub-object / attribute inside.

Please be aware that the query consists of a list of tupled variables (name, value).
So, the same name can be represented more than once.
This is a standard behaviour of the url's query.
Although, if you provide a kwargs directory (name, value) this name will become unique.

_Provides the following attributes:_

`reset` (*args, **kwargs) method

Builds from scratch the query_list based on args list tuples (name, value) and
the kwargs dictionary.

`set` (query_list) method

Replaces the query_list with the list provided in the method parameter.

`__call__` (*args, **kwargs) method  
`add` (*args, **kwargs) method  

* Appends all `args` tuples (name, value) in the query_list.
* Updates all `kwargs` named values. If name exists, it removes first all instances. 

`remove` (name)

Removes any instances of `name` in the query_list.

`update` (**kwargs)

Updates all `kwargs` named values. If name exists, it removes first all instances. 

`UrlView` class

This is basically a wrapper of the `Url` class mentioned above, to represent a view.
It passes through the attributes `path` and `query` to the `Url` sub-object.

_Provides the following attributes:_

`__init__` (view, *args, **kwargs) method
`__call__` (view=None, *args, **kwargs) method

Defines the view that will represent the `Url` object.

The `view` parameter can be in the form of:
* named view, like `app_name:module_a:my_view`
* python path of the class child `TemplateView`, like `app_name.views.module_a.MyView`
* any class child of `TemplateView`
* any instance of `TemplateView`

The `*args` and `**kwargs` parameters, represents the url path parameters (if any).
These parameters are described in the `path` or `re_path` functions. 

`update` (*args, **kwargs) method

Updates the url path parameters.

`path` property

Passed to the `Url.path` sub-object, see details above.

`query` property

Passed to the `Url.Query` sub-object, see details above.

`Location` class

This class is a subclass of `Url` class, representing a location object that can be
read by any path string in the request process, like the browser's location bar,
or the location derived from the request itself.

`__init__` (path, query_list, push=False) method
`__call__` (path=None, query_list=None, push=False) method

Initializes or updates the `Url` object (see details above for the parameters `path` and
`query_list`).
The `push` parameter is a flag to be used optionally to remember / set if the engine
will push this location back to the browser's url location bar.

`resolver_match` property

This returns a resolver django's object, representing the url view resolved path.

`create_from_url` class method

This class method creates a `Location` object from a url string.

#### Utils Methods

`collect_paths`(module, app_name) method

Use this method to collect the paths of the `TemplateView` classed inside a module.
The app_name is the name of the application the path belongs to.
This method will automatically add:
* an application namespace (e.g. `app_name`)
* followed by a module namespace, derived by:
  * module's `SLUG` attribute, if applicable (e.g. `module_a.SLUG`), and if not
  * the name of the module (e.g. module_a.py has a name of `module_a`)
* followed by the `slug` attribute of the `TemplateView` (e.g. `MyView.slug`)

So the final full-name django's internal view name will be `app_name:module_a:my_view`

You can anytime refer to this view name and use all django standard calls.
For example, use the `reverse` method like this: `reverse('app_name:module_a:my_view')`.

For more info, how to use the collect_paths inside the django's `urls.py` file,
see the `Defining views` section above.

`to_snake_case`(name) method

Converts a string (name) from `CamelCase` to `snake_case`. 

`to_camel_case`(name) method

Converts a string (name) from `snake_case` to `CamelCase`.
