import inspect
import os
from vix.models import Buffer
from vix.models import EditAreaModel
from vix.models import TextDocument

def get(name, dirname="fixtures"):
    frames = inspect.getouterframes(inspect.currentframe())
    for frame_info in frames:
        if frame_info[0].f_globals['__file__'] != __file__:
            return os.path.join(os.path.dirname(frame_info[1]), dirname, name)

def buffer(name):
    return Buffer.Buffer(TextDocument.TextDocument(get(name)), EditAreaModel.EditAreaModel())

def tempFile(name):
    path = get(name, "_test_")
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))
    return path
