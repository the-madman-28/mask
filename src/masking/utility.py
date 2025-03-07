import json
import numpy as np

class numpy_encoder(json.JSONEncoder):
    '''
    JSONEncoder to handle numpy to save in json.
    Usually jsonEncoder doesn't support numpy and throws error while saving.
    '''
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(numpy_encoder, self).default(obj)

# Utility function
def load_json(file_name):
    """
    Load JSON file and return object
    """
    with open(file_name) as file:
        json_object = json.load(file)
    return json_object

def save_json(json_dict, file_name):
    """
    Save json_dict to file_name passed
    """
    with open(file_name, 'w') as fp:
        json.dump(json_dict, fp, indent=4, cls=numpy_encoder)

def flatten(t):
    return [item for sublist in t for item in sublist]

def read_template_file(templates_file):
    with open(templates_file) as f:
        lines = f.readlines()
        lines = [line.replace("\\n", "\n") for line in lines]

    return lines

def get_duplicate(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list( seen_twice )

def split_to_int(x):
    return [int(i) for i in x.split()]

def split_to_float(x):
    return [float(i) for i in x.split()]

def list_to_str(a):
    return ' '.join(str(e) for e in a)