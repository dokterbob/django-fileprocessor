from django.shortcuts import get_object_or_404, redirect

from fileprocessor.models import FileProcessor

def get_file(request, basename, extension):
    processor = get_object_or_404(FileProcessor, pk=basename)
    
    return redirect(processor, permanent=True)
