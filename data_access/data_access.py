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
        self.insta_user_collection = self.db.insta_user_collection
        self.photo_collection = self.db.photo_collection
        self.page_collection.create_index([('fbid', ASCENDING)], unique=True)
        self.insta_user_collection.create_index([('insta_id', ASCENDING)], unique=True)

    def get_pages_data_access(self):
        return PagesDataAccess(self.page_collection)

    def get_posts_data_access(self):
        return PostsDataAccess(self.post_collection)

    def get_insta_users_data_access(self):
        return InstaUsersDataAccess(self.insta_user_collection)

    def get_photos_data_access(self):
        return PhotosDataAccess(self.photo_collection)


class PhotosDataAccess:
    def __init__(self, photo_collection):
        self.photo_collection = photo_collection


class InstaUsersDataAccess:
    def __init__(self, insta_user_collection):
        self.insta_user_collection = insta_user_collection

    def insert(self, user):
        try:
            self.insta_user_collection.insert_one(user)
        except DuplicateKeyError:
            raise DuplicateEntityError()

    def find_all(self):
        return [insta_user for insta_user in self.insta_user_collection.find()]


class PostsDataAccess:
    def __init__(self, post_collection):
        self.post_collection = post_collection

    def upsert_many(self, posts):
        bulk = self.post_collection.initialize_ordered_bulk_op()
        for post in posts:
            bulk.find({'fbid': post['fbid']}).upsert().update({'$set': post})
        return bulk.execute()

    def find_recent_by_page(self, page_fbid, count):
        return [post for post in
                self.post_collection.find({'page_fbid': page_fbid}).sort('created_time', -1).limit(count)]

    def find_best_by_page(self, page_fbid, count):
        return [post for post in self.post_collection.find({'page_fbid': page_fbid}).sort('likes', -1).limit(count)]

    def find_best_by_date(self, post_date, count):
        return [post for post in self.post_collection.find(
            {'created_time': {'$gte': post_date, '$lt': post_date + timedelta(days=1)}}
        ).sort('likes', -1).limit(count)]

    def remove_by_page(self, page_fbid):
        self.post_collection.remove({'page_fbid': page_fbid})


class PagesDataAccess:
    def __init__(self, page_collection):
        self.page_collection = page_collection

    def insert(self, page):
        try:
            self.page_collection.insert_one(page)
        except DuplicateKeyError:
            raise DuplicateEntityError(page)

    def update(self, page):
        self.page_collection.update({'fbid': page['fbid']}, page)

    def find_by_id(self, _id):
        return self.page_collection.find_one({'_id': _id})

    def find_by_fbid(self, fbid):
        return self.page_collection.find_one({'fbid': fbid})

    def find_all(self):
        return [page for page in self.page_collection.find()]

    def remove_by_fbid(self, fbid):
        self.page_collection.remove({'fbid': fbid})


class DuplicateEntityError(Exception):
    def __init__(self):
        Exception.__init__(self, 'This entity already exists')
