import json
from datetime import datetime
path = "C:/Users/Alvaro Marques/Desktop/projetoDeIA/temp/atividades.json"

def carregar_atividades():
    try:
        with open(path, 'r', encoding='utf-8') as file:
            atividades = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        atividades = [] 
    return atividades

def salvar_atividades(atividades):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(atividades, file, ensure_ascii=False, indent=4)

def criar_atividade(texto_atividade):
    atividades = carregar_atividades()

    data_atividade = datetime.now().strftime("%d/%m/%Y")
    nova_atividade = {
        "text": texto_atividade,
        "status": False,
        "date": data_atividade,
    }
    atividades.append(nova_atividade)
    print(f"Atividade '{texto_atividade}' criada com data '{data_atividade}'.")

    salvar_atividades(atividades)

def deletar_atividade(texto_atividade):
    atividades = carregar_atividades()

    atividades_filtradas = [atividade for atividade in atividades if atividade["text"] != texto_atividade]
    
    if len(atividades_filtradas) == len(atividades):
        print(f"Atividade '{texto_atividade}' não encontrada.")
        error = f"Atividade '{texto_atividade}' não encontrada."
    else:
        print(f"Atividade '{texto_atividade}' deletada.")
        error = None


    salvar_atividades(atividades_filtradas)
    return error

def concluir_atividade(texto_atividade):
    atividades = carregar_atividades()

    for atividade in atividades:
        if atividade["text"] == texto_atividade:
            atividade["status"] = True
            print(f"Atividade '{texto_atividade}' concluída.")
            salvar_atividades(atividades) 
            return None

    error = f"Atividade '{texto_atividade}' não encontrada."
    print(error)
    return error

def atualizar_atividade(objeto):
    atividades = carregar_atividades()
    count_atividade = 0
    pos = 0

    while count_atividade < 2:
        pos = objeto.find("atividade", pos)
        if pos == -1:
            break
        count_atividade += 1
        pos += len("atividade")

    texto_atividade_antiga = objeto[:pos - len("atividade")].strip()
    texto_atividade_nova = objeto[pos - len("atividade"):].strip()

    print(f"texto_atividade_antiga: {texto_atividade_antiga}")
    print(f"texto_atividade_nova: {texto_atividade_nova}")

    for atividade in atividades:
        if atividade["text"] == texto_atividade_antiga:
            atividade["text"] = texto_atividade_nova
            atividade["status"] = False
            print(f"Atividade '{texto_atividade_antiga}' atualizada para '{texto_atividade_nova}'.")
            salvar_atividades(atividades) 
            return None

    error = f"Atividade '{texto_atividade_antiga}' não encontrada."
    print(error)
    return  error
