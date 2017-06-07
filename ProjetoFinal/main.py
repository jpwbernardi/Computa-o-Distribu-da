# -*- coding: utf-8 -*-
from bottle import run, get, post, view, request, redirect, route, static_file, template
from frozendict import frozendict
import bottle
import json
import threading
import requests
import time
import sys

class VC:
    def __init__(self, name):
        self.name = name
        self.vectorClock = { self.name: 0 }

    def __repr__(self):
        return "V%s" % repr(self.vectorClock)

    def increment(self):
        self.vectorClock[self.name] += 1
        return self

    def update(self, t):
        self.increment()
        for k, v in t.items():
            if k not in vc.vectorClock or vc.vectorClock[k] < t[k]:
                vc.vectorClock[k] = v

actions = {}
peers = ['http://localhost:' + p for p in sys.argv[2:]]
fila = {}
filaGeral = []
tempoGeral = [time.time() for p in sys.argv[2:]]
sendNop = True

for id in sys.argv[1:]:
    fila[id] = [];

lock = threading.Lock()
vc = VC('http://localhost:' + sys.argv[1]);
bd = {}

@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')


def menor(a, b):
    keys  = list(set(a[2].keys()).union(b[2].keys()))
    keys.sort()
    a = tuple(a[2][k] if k in a[2] else 0 for k in keys)
    b = tuple(b[2][k] if k in b[2] else 0 for k in keys)
    for i in range(0, len(a)):
        if a < b: return True
        if b < a: return False
    return False

def ordenar():
    global allmsg
    for i in range(1, len(allmsg)):
        chave = allmsg[i]
        k = i
        while k > 0 and menor(chave, allmsg[k - 1]):
            allmsg[k] = allmsg[k - 1]
            k -= 1
            allmsg[k] = chave

@get('/')
@view('index')
def index():
    return dict(dados=bd)

def executaGeral():
    #Temos que pegar lock da fila global!
    del filaGeral[:]
    menor = 112345678
    for f in fila:
        ordenar(f);
        menor = len(f) if len(f) < menor;
    for f in fila:
        for i in range (0, menor):
            filaGeral.append(f[i]);
            del f[i];
    ordenar(filaGeral);
    for f in fila:
        executa(f[0]);
    #Tirar o lock

def executa((acao, par1, par2)):
    global bd
    if par1 not in bd.keys():
        bd[par1] = 0
    if acao == 'c':
        bd[par1] = int(par2);
    elif acao == 'r':
        del bd[par1]
    elif acao == 'a':
        bd[par1] += int(bd[par2])
    elif acao == 'ai':
        bd[par1] += int(par2)
    redirect('/')

@post('/send')
def send():
    sendNop = False
    acao = request.forms.getunicode('select')
    par1 = request.forms.getunicode('par1')
    par2 = request.forms.getunicode('par2')
    if vc.name not in actions.keys():
        actions[vc.name] = []
    actions[vc.name].append((acao, par1, par2, vc.vectorClock))
    _vc = ""
    for k in vc.vectorClock.keys():
        _vc += str(k) + "*"+ str(vc.vectorClock[k]) + "&"
        
    data = {'id': sys.argv[1], 'acao': acao, 'par1': par1, 'par2': par2, 'vc': _vc}
    for p in peers:
        r = requests.post(p + '/addaction', data=data);
    redirect('/');

@post('/addaction')
def addaction():
    acao = request.forms.getunicode('acao')
    par1 = request.forms.getunicode('par1')
    par2 = request.forms.getunicode('par2')
    id = request.forms.getunicode('id')
    pvc = request.forms.getunicode('vc')
    _vc = {}
    for s in pvc.split('&'):
        s1 = s.split('*');
        if (len(s1) > 1):
            _vc[s1[0]] = s1[1];
    print(_vc)
    fila[id].append([(acao, par1, par2), _vc])
    for f in fila:
        if len(f) == 0:
            return;
    executaGeral();

def nop():
    while True:
        time.sleep(1);
        if (sendNop == True):
            data = {'select': 5, 'par1': 0, 'par2': 5}
            requests.post(p + '/send', data=data);
        sendNop = True;

def eliminarServ():
    while True:
        time.sleep(1);
        for i in range(0, len(tempoGeral)):
            if time.time() - tempoGeral[i] > 10: #Passou 10 segundos
                del fila[p];
                del vc.vectorClock[peers[p]]; #Isso pode causar ações
                                              #com o mesmo
                                              #vectorClock?
                del peers[p]
@get('/peers')
def dora():
    return json.dumps(peers)

@get('/messages')
def msg():
    return json.dumps([(n, m, dict(t)) for (n, m, t) in messages])

t = threading.Thread(target=nop)
t.start()

#t1 = threading.Thread(target=attmessage)
#t1.start()

run(host='localhost', port=int(sys.argv[1]))
