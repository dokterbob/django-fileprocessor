import logging

from hashlib import sha1

from django.db import models

class FileProcessorBase(object):
    """ Base class for FileProcessor. 
    
    >>> f = FileProcessorBase(instructions='my instructions')
    >>> f.get_checksum()
    'b29f9e2949f7877561a7dd380543afc2e941516c'
    >>> f.get_file_url()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "/Users/drbob/Development/testproj/env/src/django-fileprocessor/fileprocessor/models.py", line 23, in get_file_url
        raise NotImplementedError
    NotImplementedError
    >>> unicode(f)
    u'b29f9e2949f7877561a7dd380543afc2e941516c'
    
    """
    
    checksum = None
    
    def __init__(self, instructions=None):
        super(FileProcessorBase, self).__init__()
        
        logging.debug('Instantiating new %s.', self.__class__)
        
        if not getattr(self, 'instructions', False):
            logging.debug('No instructions found. Settings from parameter.')
            self.instructions = instructions
        
        assert self.instructions, 'No instructions at initialization.'
        logging.debug('Processor instantiated with instructions: %s', self.instructions)
    
    def calculate_checksum(self):
        assert self.instructions, 'No instructions to calculate checksum for.'

        checksum = sha1(self.instructions).hexdigest()
        
        logging.debug('Calculated checksum for \'%s\', result: %s', self.instructions, checksum)
        
        return checksum

    def get_checksum(self):
        """ Calculate a checksum for the specified instructions. """


        if not self.checksum:
            self.checksum = self.calculate_checksum()

        logging.debug('Returning checksum: %s', self.checksum)
        
        return self.checksum
    
    def get_output(self):
        """ Get the replacement output. This code should replace the orignal
            tag - and can be cached on the client side efficiently. """

        raise NotImplementedError

    def get_file_url(self):
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
    output = models.TextField(blank=True, null=True)
    processed_file = models.FileField(upload_to='processed_file', null=True)
    
    def is_processed(self):
        """ Has the current file already been processed? """
        
        if self.processed_file:
            return True
        
        return False        
    
    def is_preprocessed(self):
        """ Is preprocessed? """
        
        if self.output:
            return True
        
        return False
    
    def preprocess(self):
        """ Do preprocessing. Basically, generate the output necessary for
            including/embedding/displaying the file on site. For an image
            this should just be an image tag, but we want to know the size
            right away. So we would want to do something like this:
            
            - parse instructions
            - find image dimensions therein
            - find scaling/cropping properties therein
            - calculate destination properties from them
            - generate proper image tag with right dimensions in output
        """
        
        self.output = '<img src="%s" />' % self.get_absolute_url()
        self.save()

    def process(self):
        """ Process the instructions, resulting in processed_file.
        
            For now, we implement bogus functionality:
            - instructions is a URL
            - we fetch the URL
            - we store the results in processed_file 
            
            Generally, this structure goes as follows:
            - parse instructions
            - get or create a file 
            - do stuff with the file (ie. scale an image)
            - write the file to database

            >>> FileProcessor.objects.all().delete()
            >>> f = FileProcessor(instructions='http://www.dokterbob.net/files/hart.gif')
            >>> f.get_output()
            '<img src="/fileprocessor/1a3d8c82fa67e422cf94c567bda53f3adfe43025/" />'
            >>> f.get_file_url()
            u'/media/processed_file/1a3d8c82fa67e422cf94c567bda53f3adfe43025.gif'
            >>> f.get_checksum()
            '1a3d8c82fa67e422cf94c567bda53f3adfe43025'
            >>> f.delete()
            >>> 
            
            
            """
        
        assert self.instructions, 'No instructions specified.'
        
        logging.debug('Fetching URL: %s', self.instructions)
        
        import urllib2
        infile = urllib2.urlopen(self.instructions)
        
        # from django.core.files import File
        # f = File(infile.read())
        

        from django.core.files.base import File, ContentFile
        f = ContentFile(infile.read())

        self.save_processed_file(f, 'gif')
    
    def save_processed_file(self, content, extension):
        filename = '%(basename)s.%(extension)s' \
                        % {'basename': self.get_checksum(),
                           'extension': extension}
        
        logging.debug('Saving file as %s' % filename)
        self.processed_file.save(filename, content)
        self.processed_file.close()
        
        assert self.processed_file.name.endswith(filename), 'Different filename. This is weird.'
    
    def get_file_url(self):
        """ See whether we already have done processing. If so, give back the resulting URL. """
        if self.is_processed():
            return self.processed_file.url
        
        self.process()
        
        assert self.is_processed, 'A processed file should now have been generated.'
        
        file_url = self.get_file_url()
        
        logging.debug('Returning URL: %s' % file_url)
        return file_url        
    
    @models.permalink
    def get_absolute_url(self):
        return ('get_file', None, {'checksum': self.get_checksum()})

    def get_output(self):
        if self.is_preprocessed():
            assert getattr(self, 'output', False), \
                    'No output has been generated during preprocessing.'

            return self.output
        
        self.preprocess()

        assert self.is_preprocessed, 'A preprocessed file should now have been generated.'
        
        self.output = self.get_output()

        logging.debug('Returning output: %s' % self.output)
        
        return self.output
        
    def save(self, *args, **kwargs):
        """ Make sure we generate a checksum before saving. """
        
        self.checksum = self.get_checksum()
        
        logging.debug('Saving file processor with checksum: %s', self.checksum)
        super(FileProcessor, self).save(*args, **kwargs)