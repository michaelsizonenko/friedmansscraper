import validators


def user_name_to_list(user_name):
    user_name = user_name.lower().replace("biography", "").replace(".Jr", "").replace(".Sr", "")
    return filter(lambda x: x != "", user_name.split(" "))


def email_user_name_to_list(email):
    user_name = email.split("@")[0]
    user_name = user_name.replace("_", " ").replace(".", " ")
    return user_name_to_list(user_name)


def get_urls_from_the_row(row_list):
    if not any([isinstance(row_list, x) for x in [set, tuple, list]]):
        raise TypeError("Unexpected incoming type. Expected list, set or tuple. Found {}".format(type(row_list)))
    result = set()
    strings_with_pipes = filter(lambda x: "|" in x, row_list)
    for item in row_list:
        if validators.url(item):
            result.add(item)
    for s in strings_with_pipes:
        if validators.url(s):
            result.add(s)
            continue
        l = s.split("|")
        for url_candidate in l:
            if validators.url(url_candidate.strip()):
                result.add(url_candidate.strip())
    return result


