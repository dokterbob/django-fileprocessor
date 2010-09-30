from django.conf.urls.defaults import *

from surlex.dj import surl

urlpatterns = patterns('fileprocessor.views',
    surl(r'^<basename:s>.<extension:s>$', 'get_file', name='get_file'),
)