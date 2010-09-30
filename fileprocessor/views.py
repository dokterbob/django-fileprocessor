from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse

from fileprocessor.models import FileProcessor

def get_file(request, checksum):
    processor = get_object_or_404(FileProcessor, pk=checksum)
    url = processor.get_file_url()
    
    return redirect(url, permanent=True)

def request_file(request):
    assert request.method == 'POST'
    assert 'instructions' in request.POST

    processor = FileProcessor(instructions=request.POST['instructions'])
    processor.save()
    
    return HttpResponse(processor.get_output())