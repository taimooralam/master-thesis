#helper.py

import math
import os

host = "10.0.0.1"
port = 4096
buf = 9126
chunks_num = 50000


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def simplify_time(time):
    frac, num = math.modf(time)
    return float(str(num)[7:-2] + str(frac)[1:-5])

def give_complete_file_path(rel_path):
    cur_path = os.path.dirname(__file__)
    new_path = os.path.relpath(rel_path, cur_path)
    #new_path = rel_path
    new_path_dir = new_path[:new_path.rfind('/')]
    if not os.path.exists(new_path_dir):
        os.makedirs(new_path_dir)
    return new_path
