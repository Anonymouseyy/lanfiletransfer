import math, pickle, random


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def pickle_msg(msg, num_bytes: int):
    pickled_data = pickle.dumps(msg)
    random_bytes = bytes([random.getrandbits(8) for _ in range(0, num_bytes - len(pickled_data))])

    return pickled_data + random_bytes

