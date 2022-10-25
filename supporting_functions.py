# Finds the index of a list of dictionary, based on a value in the dictionaries
def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


# TODO have one find functions, that can handle 1 or more keys value pairs
def find3(lst, key1, value1, key2, value2, key3, value3):
    for i, dic in enumerate(lst):
        if (dic[key1] == value1) & (dic[key2] == value2) & (dic[key3] == value3):
            return i
    return -1





