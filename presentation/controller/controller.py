import os
import datetime
from bottle import Bottle, request, template, redirect
from business_logic.business_logic import FacebookBusinessLogic, InstagramBusinessLogic

root = os.path.realpath('./presentation/view')
app = Bottle()


@app.route('/')
def index():
    return template(
        './presentation/view/index.html',
        date='{:%m/%d/%Y}'.format(datetime.datetime.today()))


@app.route('/pages')
def view_all_pages():
    return template('./presentation/view/pages.html', page_list=FacebookBusinessLogic().get_all_pages())


@app.get('/page')
def view_page():
    page_fbid = request.query.page_fbid
    return template('./presentation/view/page.html',
                    page=FacebookBusinessLogic().get_page_by_fbid(page_fbid),
                    post_list=FacebookBusinessLogic().get_page_recent_posts(page_fbid, 100))


@app.get('/page/reload')
def reload_page():
    page_fbid = request.query.page_fbid
    FacebookBusinessLogic().update_page(page_fbid)
    redirect('/page?page_fbid={}'.format(page_fbid))


@app.route('/add_page', method='POST')
def add_page():
    page_url = request.forms.get('page_url')
    FacebookBusinessLogic().add_page(page_url)
    return view_all_pages()


@app.route('/remove_page/<fbid>')
def remove_page(fbid):
    FacebookBusinessLogic().remove_page(fbid)
    return view_all_pages()


@app.route('/best_posts')
def view_best_posts():
    return template('./presentation/view/best_posts.html',
                    pages_best_posts=FacebookBusinessLogic().get_all_pages_best_posts(3))


@app.get('/best_posts_by_date')
def view_best_posts_by_date():
    str_date = request.query.date
    if not str_date:
        str_date = 'Today'
        now = datetime.datetime.today()
        date = datetime.datetime(now.year, now.month, now.day, )
    else:
        date_parts = str_date.split('/')
        date = datetime.datetime(int(date_parts[2]), int(date_parts[0]), int(date_parts[1]), )
        if str_date == '{:%m/%d/%Y}'.format(datetime.datetime.today()):
            str_date = 'Today'
    return template('./presentation/view/best_posts_by_date.html',
                    str_date=str_date,
                    best_posts=FacebookBusinessLogic().get_best_posts_by_date(date, 10))


@app.route('/recent_posts')
def view_recent_posts():
    return template('./presentation/view/recent_posts.html',
                    pages_recent_posts=FacebookBusinessLogic().get_all_pages_recent_posts(5))


@app.route('/insta_users')
def view_all_insta_users():
    return template('./presentation/view/insta_users.html',
                    users=InstagramBusinessLogic().get_all_users())


@app.route('/add_insta_user', method='POST')
def add_page():
    user_name = request.forms.get('user_name')
    InstagramBusinessLogic().add_user(user_name)
    return view_all_insta_users()
