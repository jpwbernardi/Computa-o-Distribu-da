from bottle import route, run, template, post, request

messages = []

@route('/chat', method="GET")
@route('/chat', method="POST")
def chat():
    messages.append(request.query.msg)
    return messages

run(host='localhost', port=8080)

@route('/')
def index():
    return 
