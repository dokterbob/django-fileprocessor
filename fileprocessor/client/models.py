from fileprocessor.models import FileProcessorBase

from fileprocessor.client.settings import ENDPOINT_URL

class FileProcessorHead(FileProcessorBase):
    def get_absolute_url(self):
        """ Get the absolute URL for the FileProcessor specified by instructions. """
        
        import urllib2
    
        return urllib2.urlopen(ENDPOINT_URL, {'instructions': self.instructions})
        
