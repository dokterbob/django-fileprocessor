from django import template

from fileprocessor.client.models import FileProcessorHead

register = template.Library()

@register.tag
def fileprocessor(parser, token):
    nodelist = parser.parse(('endfileprocessor',))
    parser.delete_first_token()
    
    return FileProcessorNode(nodelist)

class FileProcessorNode(template.Node):
    """ For now this tag is simply replaced by the output. In other scenario's
        we might actually want to have the output assigned to a variable. TODO
    
    """
    def __init__(self, nodelist):
        self.nodelist = nodelist
        
    def render(self, context):
        instructions = self.nodelist.render(context)

        processor = FileProcessorHead(instructions=instructions)

        return processor.get_output()
