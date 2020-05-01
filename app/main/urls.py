from django.urls import path

import page.views
import secure.views
import client.views
import oauth2.views


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
        '', page.views, 'page-',
        ('', 'homepage', {}, 'homepage'),
    )

urlpatterns += prefix_patterns(
        'p/', page.views, 'page-',
        ('instructions/', 'instructions', {}, 'instructions'),
        ('dashboard/', 'dashboard', {}, 'dashboard'),
    )

urlpatterns += prefix_patterns(
        'admin/', secure.views, 'secure-',
        ('login/', 'login', {}, 'login'),
        ('logout/', 'logout', {}, 'logout'),
    )

urlpatterns += prefix_patterns(
        'client/', client.views, 'client-',
        ('index/', 'index', {}, 'index'),
        ('<int:pk>/delete/', 'delete', {}, 'delete'),
        ('<int:pk>/toggle-active/', 'toggle_active', {}, 'toggle-active'),
    )

urlpatterns += prefix_patterns(
        '', oauth2.views, 'oauth2-',
        ('dan/', 'dan', {}, 'dan'),
        ('login/', 'login', {}, 'login'),
        ('auth/', 'authorize', {}, 'authorize'),
        ('service/', 'service', {}, 'service'),
    )
