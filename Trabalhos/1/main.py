from bottle import run, get, post, view, request, redirect, route, static_file
import bottle

messages = []

@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

@get('/chat')
@view('chat')
def chat():
    return dict(msg=messages)

@route('/')
def index():
    return

@get('/client')
@post('/client')
@view('client')
def renderClient():
    if request.forms.get('name') == '' or request.forms.get('msg') == '':
        print('Olá')
        return dict(error=True)
    elif request.forms.get('name') != None and request.forms.get('msg') != None:
        print('Tchaaaau')
        messages.append(request.forms.get('name') + ': ' + request.forms.get('msg'))
    return dict(error=False)
run(host='localhost', port=8080)


