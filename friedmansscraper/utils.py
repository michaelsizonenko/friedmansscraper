import validators
import unicodedata
from urlparse import urlparse, urljoin


IGNORE_LINK_PATHS = {'/activity', '/login', '/direct_messages', '/similar_to', '/tweetbutton', '/notifications',
                     '/media_signup', '/apirules', '/rules', '/devices', '/welcome', '/logo', '/replies', '/logout',
                     '/statistics', '/intent/tweet', '/following', '/search', '/intent/retweet', '/signup', '/contacts',
                     '/privacy', '/help', '/trends', '/anywhere', '/buttons', '/mentions', '/users', '/me',
                     '/retweets_by_others', '/account', '/faq', '/saved_searches', '/related_tweets',
                     '/retweeted_of_mine', '/accounts', '/announcements', '/business', '/retweets', '/newtwitter',
                     '/messages', '/zendesk_auth', '/followers', '/tos', '/edit_announcements', '/inbox', '/download',
                     '/positions', '/favorites', '/goodies', '/about', '/auth', '/blog', '/home', '/sent', '/mockview',
                     '/jobs', '/translate', '/signin', '/settings', '/twttr', '/api_terms', '/find_sources',
                     '/friend_request', '/all', '/friends', '/who_to_follow', '/widgets', '/nudge', '/invitations',
                     '/intent/like', '/im_account', '/intent', '/downloads', '/terms', '/', '/messages/compose',
                     '/list', '/find_users', '/update_discoverability', '/phoenix_search', '/intent/user', '/share',
                     '/api_rules', '/oauth', '/badges', '/public_timeline', '/apps', '/intent/follow', '/friendrequest',
                     '/invite', '/', ''}


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


# url_obj = urlparse(link_candidate)
#             if url_obj.netloc == 'twitter.com':
#                 # removing mobile. and www. is here
#                 twitter_links.add('twitter.com' + str(url_obj.path).lower())
#         twitter_links = filter(lambda x: "twitter.com" in x, all_links)
#         self.logger.debug(twitter_links)
#         twitter_links = [x.split("?")[0] if "?" in x else x for x in twitter_links]
#         self.logger.debug(twitter_links)
#         for link in twitter_links:
#             if "/status/" in link:
#                 link = link.split("/status/")[0]
#             if link not in ignore_links:
#                 self.all_twitter_links.add("https://" + link)


def check_is_twitter(link_candidate):
    if not (isinstance(link_candidate, str) or isinstance(link_candidate, unicode)):
        raise TypeError("String or unicode expected. Found {}".format(type(link_candidate)))
    if not validators.url(link_candidate):
        raise Exception("Invalid URL found {}".format(link_candidate))
    if isinstance(link_candidate, unicode):
        link_candidate = unicodedata.normalize('NFKD', link_candidate).encode('ascii', 'ignore')
    link_candidate = link_candidate.replace("/#!/", "/")
    parsed = urlparse(link_candidate)
    netloc, path = parsed.netloc, parsed.path.lower()
    print(parsed)
    if "twitter.com" not in netloc:
        return
    if path in IGNORE_LINK_PATHS:
        return
    return urljoin("https://twitter.com", path)
