import logging

from hashlib import sha1

from django.db import models

class FileProcessorBase(object):
    """ Base class for FileProcessor. 
    
    >>> f = FileProcessorBase('my instructions')
    >>> f.get_checksum()
    'b29f9e2949f7877561a7dd380543afc2e941516c'
    >>> f.get_url()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "/Users/drbob/Development/testproj/env/src/django-fileprocessor/fileprocessor/models.py", line 23, in get_url
        raise NotImplementedError
    NotImplementedError
    
    """
    
    def __init__(self, instructions=None):
        super(FileProcessorBase, self).__init__()
        
        logging.debug('Instantiating new FileProcessor.')
        
        if not getattr(self, 'instructions', False):
            logging.debug('No instructions found. Settings from parameter.')
            self.instructions = instructions
        
        assert self.instructions, 'No instructions at initialization.'
        logging.debug('Processor instantiated with instructions: %s', self.instructions)
    
    def get_checksum(self):
        """ Calculate a checksum for the specified instructions. """
        
        assert self.instructions, 'No instructions to calculate checksum for.'
        return sha1(self.instructions).hexdigest()
    
    def get_url(self):
        """ Get the URL for a rendered version of the specified instructiions. """
        raise NotImplementedError

class FileProcessor(FileProcessorBase, models.Model):
    """ Basic skeleton for file processing. 
    
    >>> f = FileProcessor(instructions='my instructions')
    >>> f.save()
    >>> f.checksum
    'b29f9e2949f7877561a7dd380543afc2e941516c'
    >>> f.get_checksum()
    'b29f9e2949f7877561a7dd380543afc2e941516c'
    >>> f.is_processed()
    False
    
    """
    checksum = models.CharField(primary_key=True, max_length=20)
    instructions = models.TextField()
    processed_file = models.FileField(upload_to='processed_file', null=True)
    
    def is_processed(self):
        """ Has the current file already been processed? """
        if self.processed_file:
            return True
        
        return False
    
    def process(self):
        """ Process the instructions, resulting in processed_file."""
        pass
    
    def get_url(self):
        """ See whether we already have done processing. If so, give back the resulting URL. """
        if self.is_processed:
            return self.processed_file.url
        
        self.process()
        
        assert self.is_processed, 'A processed file should now have been generated.'
        
        return self.get_url()
        
    def save(self, *args, **kwargs):
        """ Make sure we generate a checksum before saving. """
        
        self.checksum = self.get_checksum()
        
        super(FileProcessor, self).save(*args, **kwargs)