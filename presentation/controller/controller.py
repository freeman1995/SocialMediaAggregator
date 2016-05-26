import os
from bottle import Bottle, request, template
from business_logic.business_logic import BusinessLogicManager

root = os.path.realpath('./presentation/view')
app = Bottle()


@app.route('/')
def index():
    return template('./presentation/view/index.tpl', page_list=BusinessLogicManager().get_all_pages())


@app.route('/load_page', method='POST')
def load_page():
    page_url = request.forms.get('page_url')
    BusinessLogicManager().load_page(page_url)
    return index()


@app.route('/remove_page/<fbid>')
def remove_page(fbid):
    BusinessLogicManager().remove_page(fbid)
    return index()


@app.route('/posts/<fbid>/<name>')
def posts(fbid, name):
    BusinessLogicManager().load_page_posts(fbid, 100)
    return template('./presentation/view/posts.tpl', page_name=name,
                    post_list=BusinessLogicManager().get_page_recent_posts(fbid, 100))
