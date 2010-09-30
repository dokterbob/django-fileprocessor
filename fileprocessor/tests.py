import logging

from django.test import TestCase

from django.core.urlresolvers import reverse

from fileprocessor.models import FileProcessor, FileProcessorBase

class SimpleTestCase(TestCase):        
    def setUp(self):
        FileProcessor.objects.all().delete()
        self.instructions = 'http://www.dokterbob.net/files/hart.gif'

    def tearDown(self):
        FileProcessor.objects.all().delete()
        
    def test_request(self):
        request_url = reverse('request_file')
        
        baseprocessor =  FileProcessorBase(instructions=self.instructions)
        checksum = baseprocessor.get_checksum()
        
        response = self.client.post(request_url, {'instructions': self.instructions,
                                                  'checksum': checksum })
        
        processor = FileProcessor.objects.get(pk=checksum)
        
        self.assertEquals(processor.output, processor.get_output())
        self.assertEquals(response.content, processor.get_output())
    
    def test_tag(self):
        from django.template import Template, Context
        
        t = Template('{% load fileprocessor_tags %}{% fileprocessor %}{{ instructions }}{% endfileprocessor %}')
        c = Context({'instructions': self.instructions})
        result = t.render(c)
        
        baseprocessor =  FileProcessorBase(instructions=self.instructions)
        checksum = baseprocessor.get_checksum()
        
        processor = FileProcessor.objects.get(pk=checksum)
        
        self.assertEquals(processor.get_output(), result)
