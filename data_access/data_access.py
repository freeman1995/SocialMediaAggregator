from datetime import timedelta
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataAccessManager(metaclass=Singleton):
    def __init__(self):
        mongo_client = MongoClient('mongodb://localhost:27017/')
        self.db = mongo_client.sma_db
        self.page_collection = self.db.page_collection
        self.post_collection = self.db.post_collection
        self.page_collection.create_index([('fbid', ASCENDING)], unique=True)

    def get_pages_data_access(self):
        return PagesDataAccess(self.page_collection)

    def get_posts_data_access(self):
        return PostsDataAccess(self.post_collection)


class PostsDataAccess:
    def __init__(self, post_collection):
        self.post_collection = post_collection

    def upsert_many(self, posts):
        bulk = self.post_collection.initialize_ordered_bulk_op()
        for post in posts:
            bulk.find({'fbid': post['fbid']}).upsert().update({'$set': post})
        return bulk.execute()

    def find_recent_by_page(self, page_fbid, count):
        return [post for post in self.post_collection.find({'page_fbid': page_fbid}).limit(count)]

    def find_best_by_page(self, page_fbid, count):
        return [post for post in self.post_collection.find({'page_fbid': page_fbid}).sort('likes', -1).limit(count)]

    def find_best_by_date(self, post_date):
        return [post for post in self.post_collection.find(
            {'created_time': {'$gte': post_date, '$lt': post_date + timedelta(days=1)}}
        ).sort('likes', -1)]

    def remove_by_page(self, page_fbid):
        self.post_collection.remove({'page_fbid': page_fbid})


class PagesDataAccess:
    def __init__(self, page_collection):
        self.page_collection = page_collection

    def insert(self, page):
        try:
            self.page_collection.insert_one(page)
        except DuplicateKeyError:
            raise DuplicatePageError(page)

    def find_by_id(self, _id):
        return self.page_collection.find_one({'_id': _id})

    def find_all(self):
        return [page for page in self.page_collection.find()]

    def remove_by_fbid(self, fbid):
        self.page_collection.remove({'fbid': fbid})


class DuplicatePageError(Exception):
    def __init__(self, page):
        Exception.__init__(self, 'A page with facebook id:{fbid} already exists'.format(**page))
