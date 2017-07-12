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

_nossolock = 0;

#def getlock():
#    global _nossolock
#    while _nossolock == 1:
#        continue;
#    _nossolock = 1;

#def unlock():
#    global _nossolock
#    _nossolock = 0;


def menor(a, b):
    print(">>")
    print(a)
    print("<<")
    print(b)
    keys  = list(set(a[1].keys()).union(b[1].keys()))
    keys.sort()
    a = tuple(a[1][k] if k in a[1] else 0 for k in keys)
    b = tuple(b[1][k] if k in b[1] else 0 for k in keys)
    for i in range(0, len(a)):
        if a < b: return True
        if b < a: return False
    return False

def ordenar(vetor):
    print("----")
    print(vetor)
    print("!!!!")
    for i in range(1, len(vetor)):
        chave = vetor[i]
        k = i
        while k > 0 and menor(chave, vetor[k - 1]):
            vetor[k] = vetor[k - 1]
            k -= 1
            vetor[k] = chave

@get('/')
@view('index')
def index():
    return dict(dados=bd)

def executaGeral():
    #getlock();
    global filaGeral
#    print("Nao tem terror")
#    print(fila)
#    print("Não tem ko")
    #Temos que pegar lock da fila global!
    del filaGeral[:]
    print("1")
    menor = 112345678
    for f in fila:
        print("2")
#        print(fila[f]);
#        print("!@!@!@!@")
        ordenar(fila[f]);
        if len(fila[f]) < menor:
            menor = len(fila[f])
    print("3")
    for f in fila:
        print("*****")
        print(f)
        print("*-*-*")
        filaGeral.append(fila[f][0]);
        del fila[f][0];
    print("4")
    #print("Ai")
    #print(filaGeral)
    #print("misericórdia")
    ordenar(filaGeral);
    #print(filaGeral)
    for f in filaGeral:
        executa(f[0]);
    #Tirar o lock
    #unlock();

def executa(tupla):
    acao = tupla[0];
    par1 = tupla[1];
    par2 = tupla[2];
    if acao == '5': #nop
        return;
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
    print(bd);
    redirect('/')

@post('/send')
def send():
    global fila
    sendNop = False
    acao = request.forms.getunicode('select')
    par1 = request.forms.getunicode('par1')
    par2 = request.forms.getunicode('par2')
    #getlock();
    if vc.name not in fila.keys():
        fila[vc.name] = []
    fila[vc.name].append([(acao, par1, par2), vc.vectorClock])
    lala = True #Precisamos executar a ação?
    #unlock();
    for f in fila:
        if len(fila[f]) == 0:
            lala = False
    if (lala == True):
        executaGeral();

    _vc = ""
    for k in vc.vectorClock.keys():
        _vc += str(k) + "*"+ str(vc.vectorClock[k]) + "&"
        
    data = {'id': sys.argv[1], 'acao': acao, 'par1': par1, 'par2': par2, 'vc': _vc}
    for p in peers:
        r = requests.post(p + '/addaction', data=data);
    redirect('/');

@post('/addaction')
def addaction():
    global fila
    acao = request.forms.getunicode('acao')
    par1 = request.forms.getunicode('par1')
    par2 = request.forms.getunicode('par2')
    id = request.forms.getunicode('id')
    pvc = request.forms.getunicode('vc')
    _vc = {}
    for s in pvc.split('&'):
        s1 = s.split('*');
        if (len(s1) > 1):
            _vc[s1[0]] = int(s1[1]);
    print(_vc)
    #getlock();
    fila[id].append([(acao, par1, par2), _vc])
    print("Olalalalalao")
    print(fila)
    print("oalalalalaO")
    for f in fila:
        if len(fila[f]) == 0:
            #unlock();
            return;
    #unlock();
    executaGeral();

def nop():
    global sendNop
    while True:
        time.sleep(8);
        if (sendNop == True):
            data = {'select': 5, 'par1': 0, 'par2': 0}
            for p in peers:
                try:
                    requests.post(p + '/send', data=data);
                except:
                    print('Não foi possivel conectar a ' + p);
            #getlock();
            fila[sys.argv[1]].append([(5, 0, 0), vc.vectorClock]);
            #unlock();
        sendNop = True;

def eliminarServ():
    global fila
    while True:
        time.sleep(10);
        getlock()
        for i in range(0, len(tempoGeral)):
            if time.time() - tempoGeral[i] > 10: #Passou 10 segundos
                del fila[p];
                del vc.vectorClock[peers[p]]; #Isso pode causar ações
                                              #com o mesmo
                                              #vectorClock?
                del peers[p]
        #unlock();


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
