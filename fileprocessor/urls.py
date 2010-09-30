from django.conf.urls.defaults import *

from surlex.dj import surl

urlpatterns = patterns('fileprocessor.views',
    surl(r'^request/$', 'request_file', name='request_file'),
    surl(r'^<checksum:s>/$', 'get_file', name='get_file'),
)