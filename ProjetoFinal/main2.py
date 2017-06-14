from bottle import run, get, post, view, request, redirect, route, static_file, template
from frozendict import frozendict
import bottle
import json
import threading
import requests
import time
import sys

peers = [p for p in sys.argv[2:]]
bd = {}
acoes = {}
porta = sys.argv[1]

def main():
    global acoes
    acoes[porta] = [];
    for p in peers:
        acoes[p] = [];

    #Responsável por atualizar o banco
    t = threading.Thread(target=attBD)
    t.start()

    run(host='localhost', port=int(porta))

@get('/')
@view('index')
def index():
    return dict(dados=bd)

@post('/send')
def send():
    global acoes;
    acao = request.forms.getunicode('select')
    par1 = request.forms.getunicode('par1')
    par2 = request.forms.getunicode('par2')
    
    #Enviar essa ação para todo mundo

    acoes[porta].append((acao, par1, par2));

    redirect('/');


def attBD():
    #Vejo se em toda fila de acoes existe pelo menos 1 acao
    while True:
        print("AttBD");
        print(bd)
        time.sleep(1);
        vazio = False
        for p in peers:
            if len(acoes[p]) == 0:
                vazio = True;
        if len(acoes[porta]) == 0:
            vazio = True
        if vazio == False:
            executaGeral();


def executaGeral():
    global acoes
    #Quando for adicionado o VC, precisa ordenar tudo!
    fila = []
    fila.append(acoes[porta][0]); #Adicionar o que tem na minha fila
    del acoes[porta][0];
    for p in peers:
        fila.append(acoes[p][0]);
        del acoes[p][0];
    print(fila);
    for f in fila:
        executa(f);

def executa(tupla):
    global bd
    print("tupla: " + str(tupla));
    acao = tupla[0];
    par1 = tupla[1];
    par2 = tupla[2];
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

if __name__ == "__main__":
    main();
