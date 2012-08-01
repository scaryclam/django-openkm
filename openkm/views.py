import os
import StringIO

from django.http import HttpResponse

import client, utils

def get_document_by_uuid(request, uuid):
    """
    Returns a document from OpenKM
    """
    # Get the file object and convert the string back to binary
    file_obj, doc_meta = get_document_buffer_by_uuid(request, uuid)
    document = utils.java_byte_array_to_binary(file_obj)
    file_name = doc_meta.path.split("/")[-1]
    file_name = os.path.basename(doc_meta.path)
    print file_name
    
    # set the headers and return the file
    response = HttpResponse(document, doc_meta.mimeType)
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    return response

def get_document_buffer_by_uuid(request, uuid):
    """
    Returns a document StringIO buffer and document meta data from OpenKM
    """
    # get path from the uuid, and from that get the content
    document = client.Document()
    document_path = document.get_path(uuid)
    doc_meta = document.get_properties(document_path)
    java_byte_array = document.get_content(document_path, False)
  
    # convert the string back to binary
    file_obj = StringIO.StringIO(java_byte_array)

    return file_obj, doc_meta

