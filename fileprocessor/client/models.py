import logging

from fileprocessor.models import FileProcessorBase
from fileprocessor.client.settings import ENDPOINT_URL

class FileProcessorHead(FileProcessorBase):
    def get_output(self):
        """ Get the absolute URL for the FileProcessor specified by instructions. """
        
        if ENDPOINT_URL == 'LOCAL':
            logging.debug('Running processing locally.')
            
            from fileprocessor.models import FileProcessor
            processor = FileProcessor(instructions=self.instructions)
            
            return processor.get_output()
        
        else:
            logging.debug('Fetching output from %s', ENDPOINT_URL)

            import urllib2
    
            return urllib2.urlopen(ENDPOINT_URL, {'instructions': self.instructions})
        
