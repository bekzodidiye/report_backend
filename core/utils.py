import uuid
import os

def rename_file_to_uuid(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    # This might need to be overridden in models to specify path
    return filename

def get_upload_path(instance, filename):
    # This will be used in models like: upload_to=get_upload_path
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    
    model_name = instance.__class__.__name__.lower()
    return os.path.join(f"{model_name}s", filename)
