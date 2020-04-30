from django.urls import path

import page.views
import secure.views
import client.views


def prefix_patterns(uri_prefix, view, name_prefix, *patterns):

    urlpatterns = []

    for uri, view_name, kwargs, uri_name in patterns:

        urlpattern = path(
            uri_prefix + uri,
            getattr(view, view_name),
            kwargs,
            name_prefix + uri_name,
        )

        urlpatterns.append(urlpattern)

    return urlpatterns


urlpatterns = []

urlpatterns += prefix_patterns(
        'api/', page.views, 'page-',
        ('', 'homepage', {}, 'homepage'),
    )

urlpatterns += prefix_patterns(
        'api/p/', page.views, 'page-',
        ('instructions/', 'instructions', {}, 'instructions'),
    )

urlpatterns += prefix_patterns(
        'api/', secure.views, 'secure-',
        ('login/', 'login', {}, 'login'),
        ('logout/', 'logout', {}, 'logout'),
    )

urlpatterns += prefix_patterns(
        'api/client/', client.views, 'client-',
        ('index/', 'index', {}, 'index'),
        ('<int:pk>/delete/', 'delete', {}, 'delete'),
        ('<int:pk>/toggle-active/', 'toggle_active', {}, 'toggle-active'),
    )
