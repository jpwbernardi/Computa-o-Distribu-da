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
    name = request.forms.getunicode('name')
    msg = request.forms.getunicode('msg')
    error = False
    if name == '' or msg == '':
        error = True
    elif name != None and msg != None:
        messages.append(name + ': ' + msg)
        print(name + msg)
    return dict(name=name, error=error)

run(host='localhost', port=8080)


