from django.urls import path

import config.views
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
        'api/config/', config.views, 'config-',
        ('', 'index', {}, 'index'),
        ('<int:pk>/', 'index', {}, 'index'),
        ('<int:pk>/delete/', 'delete', {}, 'delete'),
    )

urlpatterns += prefix_patterns(
        'api/', page.views, 'page-',
        ('', 'homepage', {}, 'homepage'),
    )

urlpatterns += prefix_patterns(
        'api/p/', page.views, 'page-',
        ('instructions/', 'instructions', {}, 'instructions'),
        ('dashboard/', 'dashboard', {}, 'dashboard'),
    )

urlpatterns += prefix_patterns(
        'api/admin/', secure.views, 'secure-',
        ('login/', 'login', {}, 'login'),
        ('logout/', 'logout', {}, 'logout'),
    )

urlpatterns += prefix_patterns(
        'api/client/', client.views, 'client-',
        ('index/', 'index', {}, 'index'),
        ('<int:pk>/delete/', 'delete', {}, 'delete'),
        ('<int:pk>/toggle-active/', 'toggle_active', {}, 'toggle-active'),
    )

urlpatterns += prefix_patterns(
        'api/', oauth2.views, 'oauth2-',
        ('dan/', 'dan', {}, 'dan'),
        ('login/', 'login', {}, 'login'),
        ('auth/', 'authorize', {}, 'authorize'),
        ('service/', 'service', {}, 'service'),
    )
