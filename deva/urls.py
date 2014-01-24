from django.conf.urls import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from searchengine.views import FileListView, FileAddView, FileAddHashedView

admin.autodiscover()
from settings import MEDIA_ROOT, STATIC_ROOT

urlpatterns = patterns('',
                       url(r'^$', 'searchengine.views.search', name='home'),
                       url(r'^add/?$', FileAddView.as_view(), name='file-add'),
                       # This view hashes uploads to create directories
                       url(r'^add$', FileAddHashedView.as_view(), name='file-add'),
                       #
                       # This view lists uploaded files
                       url(r'^files/?$', FileListView.as_view(), name='file-view'),
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^static/(?P<path>.*)$',
                        'django.views.static.serve',
                        {'document_root': STATIC_ROOT}),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                           'document_root': MEDIA_ROOT}))