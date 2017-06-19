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

peers = [p for p in sys.argv[2:]]
bd = {}
acoes = {}
porta = sys.argv[1]
vc = VC('http://localhost:' + sys.argv[1]);

lock = 0
sendNop = True

def getlock():
    global lock
    while lock == 1:
        continue;
    lock = 1;

def unlock():
    global lock;
    lock = 0;

def main():
    global acoes
    acoes[porta] = [];
    for p in peers:
        acoes[p] = [];

    #Responsável por atualizar o banco
    t = threading.Thread(target=attBD)
    t.start()

    t1 = threading.Thread(target=nop)
    t1.start()

    run(host='localhost', port=int(porta))

@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

@get('/')
@view('index')
def index():
    #print(bd);
    #print(acoes)
    return dict(dados=bd)

@post('/send')
def sendGetInfo(next):
    global sendNop
    sendNop = False
    acao = request.forms.getunicode('select')
    par1 = request.forms.getunicode('par1')
    par2 = request.forms.getunicode('par2')
    send()


def send(acao, par1, par2):
    global acoes, vc
    vc.increment();
    getlock();
    #Enviar essa ação para todo mundo
    _vc = ""
    for k in vc.vectorClock.keys():
        _vc += str(k) + "*"+ str(vc.vectorClock[k]) + "&"
    unlock();

    print(_vc)
    data = {'id': porta, 'acao': acao, 'par1': par1, 'par2': par2, 'vc': _vc}
    for p in peers:
        try:
            r = requests.post('http://localhost:' + p + '/addaction', data=data);
        except:
            print('link: ' + 'localhost:' + p + '/addaction');
            print("Deu bosta no server da porta " + p)

    getlock();
    acoes[porta].append([(acao, par1, par2), frozendict(vc.vectorClock)]);
    unlock();

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
            _vc[s1[0]] = int(s1[1]);
    print(_vc)
    getlock()
    acoes[id].append([(acao, par1, par2), frozendict(_vc)]);
    unlock()

def attBD():
    #Vejo se em toda fila de acoes existe pelo menos 1 acao
    while True:
        print("AttBD");
        print(bd)
        time.sleep(1);
        vazio = False
        getlock()
        for p in peers:
            if len(acoes[p]) == 0:
                vazio = True;
        if len(acoes[porta]) == 0:
            vazio = True
        unlock();
        if vazio == False:
            executaGeral();

#Ordenação--------------------------------------------------

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

def ordena(vetor):
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
#-----------------------------------------------------------

def executaGeral():
    global acoes
    #Quando for adicionado o VC, precisa ordenar tudo!
    getlock();
    fila = [acoes[porta][0]]
    del acoes[porta][0];
    for p in peers:
        fila.append(acoes[p][0]); #Adicionar o que tem na minha fila
        del acoes[p][0];
    unlock()
    ordena(fila)
    for f in fila:
        executa(f);

def executa(tupla):
    global bd
    print("tupla: " + str(tupla));
    acao = tupla[0][0];
    par1 = tupla[0][1];
    par2 = tupla[0][2];
    if acao == 'Nop':
        return
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

def nop():
    global sendNop
    while True:
        time.sleep(5);
        if (sendNop == True):
            #Enviar essa ação para todo mundo
            send('Nop', 0, 0);
            getlock();
            acoes[porta].append([(5, 0, 0), vc.vectorClock]);
            unlock();
        sendNop = True;

if __name__ == "__main__":
    main();
