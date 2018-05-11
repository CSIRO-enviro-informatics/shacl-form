from flask import Blueprint, render_template, Response, request

routes = Blueprint('controller', __name__)


@routes.route('/')
def index():
    return render_template(
        'index.html'
    )


@routes.route('/form')
def form():
    return render_template(
        'form.html'
    )


@routes.route('/post', methods=['POST'])
def post():
    laura = request.form.get('laura')
    return Response('Laura is ' + laura, status=201, mimetype='text/plain')
