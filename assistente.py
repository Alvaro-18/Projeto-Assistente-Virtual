from inicializador_modelos import *
from transcritor import *
from flask import Flask, request, jsonify, send_from_directory
from acoes_assistente import *
from nltk import word_tokenize, corpus

import secrets
import pyaudio
import wave
import json

import os

AMOSTRAS = 1024
FORMATO = pyaudio.paInt16
CANAIS = 1
TEMPO_DE_GRAVACAO = 5
CAMINHO_AUDIO_FALA = "C:/Users/Alvaro Marques/Desktop/projetoDeIA/temp"
IDIOMA_CORPUS = "portuguese"
CONFIGURACAO = "C:/Users/Alvaro Marques/Desktop/projetoDeIA/config.json"

ATIVAR_INTERFACE_WEB = True

def iniciar(dispositivo):
    gravador = pyaudio.PyAudio()

    assistente_iniciado, processador, modelo = iniciar_modelo(MODELOS[0], dispositivo)

    palavras_de_parada, acoes = None, None
    if assistente_iniciado:
        palavras_de_parada = corpus.stopwords.words(IDIOMA_CORPUS)

        with open(CONFIGURACAO, "r") as arquivo_configuracao:
            configuracao = json.load(arquivo_configuracao)
            acoes = configuracao["acoes"]

    return assistente_iniciado, processador, modelo, gravador, palavras_de_parada, acoes

def capturar_fala(gravador):
    gravacao = gravador.open(format=FORMATO, channels=CANAIS, rate=TAXA_AMOSTRAGEM, input=True, frames_per_buffer=AMOSTRAS)

    print("fale alguma coisa")

    fala = []
    for _ in range(0, int(TAXA_AMOSTRAGEM / AMOSTRAS * TEMPO_DE_GRAVACAO)):
        fala.append(gravacao.read(AMOSTRAS))

    gravacao.stop_stream()
    gravacao.close()

    print("fala capturada")

    return fala

def gravar_fala(fala):
    gravado, arquivo = False, f"{CAMINHO_AUDIO_FALA}/{secrets.token_hex(32).lower()}.wav" 

    try:
        wav = wave.open(arquivo, 'wb')
        wav.setnchannels(CANAIS)
        wav.setsampwidth(gravador.get_sample_size(FORMATO))
        wav.setframerate(TAXA_AMOSTRAGEM)
        wav.writeframes(b''.join(fala))
        wav.close()    

        gravado = True
    except Exception as e:
        print(f"ocorreu um erro gravando arquivo temporário: {str(e)}")

    return gravado, arquivo

def processar_transcricao(transcricao, palavras_de_parada):
    comando = []
    tokens = word_tokenize(transcricao)
    for token in tokens:
        if token not in palavras_de_parada:
            comando.append(token)

    return comando

def validar_comando(comando, acoes): 
    valido, acao, objeto = False, None, None

    if len(comando) >= 2:
        acao = comando[0]
        objeto = " ".join(comando[1:]) 

        for acao_esperada in acoes:
            if acao == acao_esperada["nome"]:
                if objeto.startswith("atividade"):
                    valido = True
                    break

    return valido, acao, objeto


def ativar_linha_de_comando():
    while True:
        fala = capturar_fala(gravador)
        gravado, arquivo_fala = gravar_fala(fala)

        if gravado:
            transcricao = transcrever_fala(dispositivo, carregar_fala(arquivo_fala), modelo, processador)
            os.remove(arquivo_fala)

            print(f"transcrição: {transcricao}")

            comando = processar_transcricao(transcricao, palavras_de_parada)
            valido, acao, objeto = validar_comando(comando, acoes)
            if valido:
                atuar_sobre_atividade(acao, objeto)

def atuar_sobre_atividade(acao, objeto):
    error = None
    if acao == "criar":
        error = criar_atividade(objeto)
    elif acao == "deletar":
       error = deletar_atividade(objeto)
    elif acao == "concluir":
        error = concluir_atividade(objeto)
    elif acao == "atualizar":
        error = atualizar_atividade(objeto)
    return error 

servico = Flask("assistente", static_folder="public")

@servico.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@servico.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

@servico.post("/reconhecer_comando")
def reconhecer_comando():
    if 'audio' not in request.files:
        return jsonify({"message": "Nenhum arquivo de áudio encontrado"}), 400
    
    arquivo = request.files['audio']

    caminho_arquivo = f"{CAMINHO_AUDIO_FALA}/{secrets.token_hex(32).lower()}.wav"

    arquivo.save(caminho_arquivo)

    try:
        transcricao = transcrever_fala(servico.config["dispositivo"], carregar_fala(caminho_arquivo), servico.config["modelo"], servico.config["processador"])
        error = None
        print(f"transcrição: {transcricao}")

        comando = processar_transcricao(transcricao, servico.config["palavras_de_parada"])
        valido, acao, objeto = validar_comando(comando, acoes)

        if valido:
            error = atuar_sobre_atividade(acao, objeto)      
            print(f"error: {error}")
            if(error != None):
                return jsonify({"message": f"Error: {error}"}), 400

            return jsonify({"message": f"{acao} realizada com sucesso"}), 200
        else: 
            return jsonify({"message": f"Erro ao processar o comando"}), 400
    except Exception as e:
        print("Erro ao processar o áudio:", e)

        return jsonify({"message": "Erro ao processar o áudio"}), 500
    finally:
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)

@servico.get("/pegar_dados")
def pegar_dados():
    data = carregar_atividades()
    if data:
        return jsonify({"dados": data}), 200
    else:
        return jsonify({"dados": []}), 200

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    iniciado, processador, modelo, gravador, palavras_de_parada, acoes = iniciar(dispositivo)
    if iniciado:
        if ATIVAR_INTERFACE_WEB:
            servico.config["dispositivo"] = dispositivo
            servico.config["modelo"] = modelo
            servico.config["processador"] = processador
            servico.config["palavras_de_parada"] = palavras_de_parada

            servico.run(debug=True)
        else:
            ativar_linha_de_comando()