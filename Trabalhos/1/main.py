# -*- coding: utf-8 -*-
from bottle import run, get, post, view, request, redirect, route, static_file, template
import bottle

messages = []

@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

@get('/chat')
@view('chat')
def chat():
    name = request.query.name
    error = request.query.error
    return dict(msg=messages, name=name, error=error)

@route('/')
def index():
    return


@post('/send')
def sendmsg():
    name = request.forms.getunicode('name')
    msg = request.forms.getunicode('msg')
    error = False
    if name == '' or msg == '':
        error = True
    elif name != None and msg != None:
        messages.append(name + ': ' + msg)
        redirect('chat?name=' + name)
    if name != None:
        redirect('chat?name=' + name + '&error=t')
    else:
        redirect('chat?error=t')

run(host='localhost', port=8081)


