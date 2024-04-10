import random

def get_random_topic(array):
    min_val = 0
    max_val = len(array) - 1
    random_index = get_random_int_inclusive(min_val, max_val)
    return array[random_index]


def get_random_int_inclusive(min_val, max_val):
    return random.randint(min_val, max_val)


def item_is_valid(item):
    for key in item.keys():
        if key != 'id' and key != 'data':
            return False
    return True