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
    >>> unicode(f)
    u'b29f9e2949f7877561a7dd380543afc2e941516c'
    
    """
    
    def __init__(self, instructions=None):
        super(FileProcessorBase, self).__init__()
        
        logging.debug('Instantiating new %s.', self.__class__)
        
        if not getattr(self, 'instructions', False):
            logging.debug('No instructions found. Settings from parameter.')
            self.instructions = instructions
        
        assert self.instructions, 'No instructions at initialization.'
        logging.debug('Processor instantiated with instructions: %s', self.instructions)
    
    def get_checksum(self):
        """ Calculate a checksum for the specified instructions. """

        assert self.instructions, 'No instructions to calculate checksum for.'

        checksum = getattr(self, 'checksum', False)
        
        return checksum or sha1(self.instructions).hexdigest()
    
    def get_url(self):
        """ Get the URL for a rendered version of the specified instructiions. """
        raise NotImplementedError
    
    def __unicode__(self):
        return self.get_checksum()

class FileProcessor(models.Model, FileProcessorBase):
    """ Basic skeleton for file processing. 
    
    >>> f = FileProcessor(instructions='my instructions')
    >>> f.instructions
    'my instructions'
    >>> f.save()
    >>> f.checksum
    'b29f9e2949f7877561a7dd380543afc2e941516c'
    >>> f
    <FileProcessor: b29f9e2949f7877561a7dd380543afc2e941516c>
    >>> FileProcessor.objects.all()
    [<FileProcessor: b29f9e2949f7877561a7dd380543afc2e941516c>]
    
    """
    checksum = models.CharField(primary_key=True, max_length=20)
    instructions = models.TextField()
    processed_file = models.FileField(upload_to='processed_file', null=True)

    def __init__(self, instructions=None, *args, **kwargs):
        """ It makes sense to do a call like FileProcessor('my instructions'). """
        kwargs.update({'instructions': instructions})
        super(FileProcessor, self).__init__(*args, **kwargs)
    
    def is_processed(self):
        """ Has the current file already been processed? """
        
        if self.processed_file:
            return True
        
        return False
    
    def process(self):
        """ Process the instructions, resulting in processed_file.
        
            For now, we implement bogus functionality:
            - instructions is a URL
            - we fetch the URL
            - we store the results in processed_file 
            
            >>> FileProcessor.objects.all().delete()
            >>> f = FileProcessor('http://www.google.com')
            >>> f.get_url()
            u'/media/processed_file/738ddf35b3a85a7a6ba7b232bd3d5f1e4d284ad1.html'
            
            """
        
        assert self.instructions, 'No instructions specified.'
        
        logging.debug('Fetching URL: %s', self.instructions)
        
        import urllib2
        infile = urllib2.urlopen(self.instructions)
        
        # from django.core.files import File
        # f = File(infile.read())
        from django.core.files.base import File, ContentFile
        f = ContentFile(infile.read())
        
        filename = '%(basename)s.%(extension)s' \
                        % {'basename': self.get_checksum(),
                           'extension': 'html'}
        
        logging.debug('Saving file as %s' % filename)
        self.processed_file.save(filename, f)
    
    def get_url(self):
        """ See whether we already have done processing. If so, give back the resulting URL. """
        if self.is_processed():
            return self.processed_file.url
        
        self.process()
        
        assert self.is_processed, 'A processed file should now have been generated.'
        
        logging.debug('Returning URL: %s' % self.get_url())
        return self.get_url()
        
    def save(self, *args, **kwargs):
        """ Make sure we generate a checksum before saving. """
        
        self.checksum = self.get_checksum()
        logging.debug('Saving file processor with checksum: %s', self.checksum)
        super(FileProcessor, self).save(*args, **kwargs)