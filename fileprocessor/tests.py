from django.test import TestCase

from django.core.urlresolvers import reverse

from fileprocessor.models import FileProcessor, FileProcessorBase

class SimpleTestCase(TestCase):        
    def test_request(self):
        request_url = reverse('request_file')
        
        instructions = 'http://www.google.com/'
        
        baseprocessor =  FileProcessorBase(instructions=instructions)
        checksum = baseprocessor.get_checksum()
        
        response = self.client.post(request_url, {'instructions': instructions})
        
        processor = FileProcessor.objects.get(pk=checksum)
        
        self.assertEquals(response.content, processor.get_absolute_url())