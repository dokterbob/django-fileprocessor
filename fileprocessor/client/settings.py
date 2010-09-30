from django.conf import settings
from django.core.urlresolvers import reverse

ENDPOINT_URL = getattr(settings, 'FILEPROCESSOR_ENDPOINT_URL')
