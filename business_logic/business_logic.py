import facebook
from data_access.data_access import DataAccessManager, DuplicateEntityError
from dateutil import parser as date_parser
from utils.facebook_secrets import ACCESS_TOKEN as FB_ACCESS_TOKEN


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FacebookBusinessLogic(metaclass=Singleton):
    def __init__(self):
        manager = DataAccessManager()
        self.pages_data_access = manager.get_pages_data_access()
        self.posts_data_access = manager.get_posts_data_access()

    def add_page(self, page_url):
        """
        Gets a page through facebook api,
        saves it in the db,
        and returns it.
        :param page_url: page id/url/slug
        :return: the page
        """
        graph = facebook.GraphAPI(access_token=FB_ACCESS_TOKEN, version='2.5')
        try:
            page = graph.get_object(page_url, fields="about,name,fan_count,picture,link")

            # Optimize schema
            page['fbid'] = page['id']
            page['picture'] = page['picture']['data']['url']
            del page['id']

            try:
                self.pages_data_access.insert(page)
                self.update_page_posts(page['fbid'], 100)
                return page
            except DuplicateEntityError as err:
                return err
        except facebook.GraphAPIError as err:
            return err

    def get_page_by_fbid(self, page_fbid):
        return self.pages_data_access.find_by_fbid(page_fbid)

    def get_all_pages(self):
        """
        Gets all the pages in the db
        :return: the pages
        """
        return self.pages_data_access.find_all()

    def update_page(self, page_url):
        """
        Gets a page through facebook api,
        updates it in the db,
        and returns it.
        :param page_url: page id/url/slug
        :return: the page
        """
        graph = facebook.GraphAPI(access_token=FB_ACCESS_TOKEN, version='2.5')
        try:
            page = graph.get_object(page_url, fields="about,name,fan_count,picture,link")

            # Optimize schema
            page['fbid'] = page['id']
            page['picture'] = page['picture']['data']['url']
            del page['id']

            self.pages_data_access.update(page)
            self.update_page_posts(page['fbid'], 100)
            return page
        except facebook.GraphAPIError as err:
            return err

    def get_page_recent_posts(self, page_fbid, count):
        """
        Returns the recent @count posts of a page in the db
        :param page_fbid: the facebook kid of the post
        :param count: posts count
        :returns posts
        """
        return self.posts_data_access.find_recent_by_page(page_fbid, count)

    def remove_page(self, page_fbid):
        self.pages_data_access.remove_by_fbid(page_fbid)
        self.posts_data_access.remove_by_page(page_fbid)

    # Unused

    def update_all_pages(self, count):
        for page in self.get_all_pages():
            self.update_page(page['fbid'])

    def get_all_pages_recent_posts(self, count):
        """
        Returns the recent @count posts of each page in the db
        :param count: posts count per page
        :returns: posts
        """
        return {
            page['name']: self.get_page_recent_posts(page['fbid'], count)
            for page in self.pages_data_access.find_all()
            }

    def get_best_posts_by_date(self, post_date, count):
        """
        Gets all the posts of a date, ordered by likes count.
        :param count: posts count
        :param post_date: the date
        :return: the posts
        """
        return [
            (self.pages_data_access.find_by_fbid(post['page_fbid'])['name'], post)
            for post in self.posts_data_access.find_best_by_date(post_date, count)
            ]

    def get_page_best_posts(self, page_fbid, count):
        return self.posts_data_access.find_best_by_page(page_fbid, count)

    def get_all_pages_best_posts(self, count):
        return {
            page['name']: self.get_page_best_posts(page['fbid'], count)
            for page in self.pages_data_access.find_all()
            }

    # Utils

    def update_page_posts(self, page_fbid, count):
        """
        Gets the latest @count posts of a page through facebook api
        saves them in the db, or updates the current @count posts if already exist in the db
        and returns the number of the new posts and the number of the updated posts
        :param page_fbid: the facebook id of the page in the db
        :param count: posts count
        :return: inserted amount, updated amount
        """
        graph = facebook.GraphAPI(access_token=FB_ACCESS_TOKEN, version='2.5')
        try:
            posts = graph.get_object(
                page_fbid,
                fields="posts.limit(" + str(
                    count) + "){likes.limit(0).summary(true),created_time,message,picture,link,permalink_url}"
            )['posts']['data']  # TODO change to % to avoid stringing
            for post in posts:
                # Optimize schema
                post['page_fbid'] = page_fbid
                post['created_time'] = date_parser.parse(post['created_time'])
                post['fbid'] = post['id']
                post['likes'] = post['likes']['summary']['total_count']
                del post['id']
            return self.posts_data_access.upsert_many(posts)
        except facebook.GraphAPIError as err:
            return err
        pass


class InstagramBusinessLogic(metaclass=Singleton):
    def __init__(self):
        manager = DataAccessManager()
        self.insta_users_data_access = manager.get_insta_users_data_access()
        self.photos_data_access = manager.get_photos_data_access()

    def get_all_users(self):
        return self.insta_users_data_access.find_all()

    def add_user(self, user_name):
        pass
