import validators
import unicodedata
from urlparse import urlparse, urljoin
import requests

IGNORE_LINK_PATHS = {'', '/', '/activity', '/login', '/direct_messages', '/similar_to', '/tweetbutton',
                     '/notifications', '/media_signup', '/apirules', '/rules', '/devices', '/welcome', '/logo',
                     '/replies', '/logout', '/statistics', '/intent/tweet', '/following', '/search', '/intent/retweet',
                     '/signup', '/contacts', '/privacy', '/help', '/trends', '/anywhere', '/buttons', '/mentions',
                     '/users', '/me', '/retweets_by_others', '/account', '/faq', '/saved_searches', '/related_tweets',
                     '/retweeted_of_mine', '/accounts', '/announcements', '/business', '/retweets', '/newtwitter',
                     '/messages', '/zendesk_auth', '/followers', '/tos', '/edit_announcements', '/inbox', '/download',
                     '/positions', '/favorites', '/goodies', '/about', '/auth', '/blog', '/home', '/sent', '/mockview',
                     '/jobs', '/translate', '/signin', '/settings', '/twttr', '/api_terms', '/find_sources',
                     '/friend_request', '/all', '/friends', '/who_to_follow', '/widgets', '/nudge', '/invitations',
                     '/intent/like', '/im_account', '/intent', '/downloads', '/terms', '/', '/messages/compose',
                     '/list', '/find_users', '/update_discoverability', '/phoenix_search', '/intent/user', '/share',
                     '/api_rules', '/oauth', '/badges', '/public_timeline', '/apps', '/intent/follow', '/friendrequest',
                     '/invite', '/intent/favorite', '/account/begin_password_reset', '/account/resend_password'}

NAME_WORDS_TO_IGNORE = ["'s", "s'", "'", ".", "jr", "sr", "biography", "vote smart", "votes", "vote", "commissioner"]


def user_name_to_list(user_name):
    if not (isinstance(user_name, str) or isinstance(user_name, unicode)):
        raise TypeError("String or unicode expected. {} found".format(type(user_name)))
    if isinstance(user_name, unicode):
        user_name = unicodedata.normalize('NFKD', user_name).encode('ascii', 'ignore')
    user_name = user_name.lower()
    user_name = user_name.replace("s's", "s")
    user_name = user_name.replace("s'", "s")
    for n in NAME_WORDS_TO_IGNORE:
        user_name = user_name.replace(n, "")
    result_list = set(filter(lambda x: len(x) > 2, user_name.split(" ")))
    result_list.discard("-")
    return result_list


def email_user_name_to_list(email):
    if not (isinstance(email, str) or isinstance(email, unicode)):
        raise TypeError("String or unicode expected. {} found".format(type(email)))
    if isinstance(email, unicode):
        user_name = unicodedata.normalize('NFKD', email).encode('ascii', 'ignore')
    if not validators.email(email):
        raise TypeError("Invalid e-mail. {} found".format(email))
    user_name = email.split("@")[0]
    user_name = user_name.replace("_", " ").replace(".", " ").replace("-", " ")
    user_name = ''.join([i for i in user_name if not i.isdigit()])
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


def check_is_twitter(link_candidate):
    if not (isinstance(link_candidate, str) or isinstance(link_candidate, unicode)):
        raise TypeError("String or unicode expected. Found {}".format(type(link_candidate)))
    if not validators.url(link_candidate):
        return
    if isinstance(link_candidate, unicode):
        link_candidate = unicodedata.normalize('NFKD', link_candidate).encode('ascii', 'ignore')
    link_candidate = link_candidate.replace("/#!/", "/")
    parsed = urlparse(link_candidate)
    netloc, path = parsed.netloc, parsed.path.lower()
    if "twitter.com" not in netloc:
        return
    if path in IGNORE_LINK_PATHS:
        return
    if "https://twitter.com/hashtag/" in link_candidate:
        return
    if "/status/" in path:
        path = path.split("/status/")[0]
    return urljoin("https://twitter.com", path)


def check_name_in_link(link, name, email_name):
    if not (isinstance(link, str) or isinstance(link, unicode)):
        raise TypeError
    if not isinstance(name, set):
        raise TypeError
    if not isinstance(email_name, set):
        raise TypeError
    if not validators.url(link):
        raise TypeError("URL expected. {} found.".format(link))
    any_flag = False
    all_flag = False
    path = urlparse(link).path

    def check(seq, path_):
        return [sub_name in path_ and len(sub_name) > 2 for sub_name in seq]

    any_flag = any(check(name, path))
    any_flag = any_flag or any(check(email_name, path))
    all_flag = all(check(name, path))
    all_flag = all_flag or all(check(email_name, path))
    if any_flag:
        return [link, str(any_flag), str(all_flag)]


def is_internet_available(url='https://8.8.8.8', timeout=5):
    try:
        req = requests.get(url, timeout=timeout)
        # HTTP errors are not raised by default, this statement does that
        req.raise_for_status()
        return True
    except requests.HTTPError as e:
        print("Checking internet connection failed, status code {0}.".format(
        e.response.status_code))
    except requests.ConnectionError:
        print("No internet connection available.")
    return False

