import unittest
from assistente import *

CRIAR_ATIVIDADE = "audios/criar-atividade.wav"
ATUALIZAR_ATIVIDADE = "audios/atualizar-atividade.wav"
CONCLUIR_ATIVIDADE = "audios/concluir-atividade.wav"
DELETAR_ATIVIDADE = "audios/deletar-atividade.wav"

class TesteAcoesAssistente(unittest.TestCase):
  def setUp(self):
    self.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu" 
    iniciado, self.processador, self.modelo, self.gravador, self.palavras_de_parada, self.acoes = iniciar(self.dispositivo)

    self.assertTrue(iniciado)

    return super().setUp()
  
  def test_cria_atividade(self):
    tamanho_da_lista_de_atividades = len(carregar_atividades())
    transcricao = transcrever_fala(self.dispositivo, carregar_fala(CRIAR_ATIVIDADE), self.modelo, self.processador)
    self.assertIsNotNone(transcricao, "A transcrição não pode ser nula")

    comando = processar_transcricao(transcricao, self.palavras_de_parada)
    valido, acao, objeto = validar_comando(comando, self.acoes)

    self.assertTrue(valido, "Comando inválido")
    self.assertNotEqual(acao, "", "Ação não pode ser vazia")
    self.assertNotEqual(objeto, "", "Objeto não pode ser vazio")
    criar_atividade(objeto)

    novas_atividades = carregar_atividades()
    novo_tamanhao_da_lista_de_atividades = len(novas_atividades)

    self.assertGreater(novo_tamanhao_da_lista_de_atividades, tamanho_da_lista_de_atividades, "Atividade não foi criada com sucesso, o tamanho da lista não aumentou.")
   
    atividade_criada = False
    for atividade in novas_atividades:
        if atividade["text"] == objeto:
            atividade_criada = True
            break
        
    self.assertTrue(atividade_criada, f"A atividade '{objeto}' não foi criada corretamente.")

  def test_atualizar_atividade(self):
    transcricao = transcrever_fala(self.dispositivo, carregar_fala(ATUALIZAR_ATIVIDADE), self.modelo, self.processador)
    self.assertIsNotNone(transcricao, "A transcrição não pode ser nula")

    comando = processar_transcricao(transcricao, self.palavras_de_parada)
    valido, acao, objeto = validar_comando(comando, self.acoes)

    count_atividade = 0
    pos = 0

    while count_atividade < 2:
        pos = objeto.find("atividade", pos)
        if pos == -1:
            break
        count_atividade += 1
        pos += len("atividade")

    atividade_antiga = objeto[:pos - len("atividade")].strip()
    atividade_nova = objeto[pos - len("atividade"):].strip()

    self.assertTrue(valido, "Comando inválido")
    self.assertNotEqual(acao, "", "Ação não pode ser vazia")
    self.assertNotEqual(objeto, "", "Objeto não pode ser vazio")

    error = atualizar_atividade(objeto)
    self.assertEqual(error, None, f"Erro na atualização da atividade: {error}")

    atividades = carregar_atividades()
    atividade_atualizada = False
    atividade_antiga_ainda_existe = False

    for atividade in atividades: 
       if atividade["text"] == atividade_antiga:
            atividade_antiga_ainda_existe = True
       if atividade["text"] == atividade_nova:
            atividade_atualizada = True
       
  
    self.assertTrue(atividade_atualizada, f"Atividade não foi atualizada para '{atividade_nova}'.")
    self.assertFalse(atividade_antiga_ainda_existe, f"Atividade antiga '{atividade_antiga}' ainda existe após a atualização.")
     
  def test_concluir_atividade(self):
    transcricao = transcrever_fala(self.dispositivo, carregar_fala(CONCLUIR_ATIVIDADE), self.modelo, self.processador)
    self.assertIsNotNone(transcricao, "A transcrição não pode ser nula")

    comando = processar_transcricao(transcricao, self.palavras_de_parada)
    valido, acao, objeto = validar_comando(comando, self.acoes)

    self.assertTrue(valido, "Comando inválido")
    self.assertNotEqual(acao, "", "Ação não pode ser vazia")
    self.assertNotEqual(objeto, "", "Objeto não pode ser vazio")
    error = concluir_atividade(objeto)
    self.assertEqual(error, None, f"Erro na conclusão da atividade: {error}")

    atividades = carregar_atividades()

    atividade_concluida = False
    for atividade in atividades:
      if atividade["text"] == objeto and atividade["status"] == True:
         atividade_concluida = True
         break

    self.assertTrue(atividade_concluida, "A atividade não foi atualizada com sucesso")
   
  def test_deletar_atividade(self):
    tamanho_da_lista_de_atividades = len(carregar_atividades())
    transcricao = transcrever_fala(self.dispositivo, carregar_fala(DELETAR_ATIVIDADE), self.modelo, self.processador)
    self.assertIsNotNone(transcricao, "A transcrição não pode ser nula")

    comando = processar_transcricao(transcricao, self.palavras_de_parada)
    valido, acao, objeto = validar_comando(comando, self.acoes)

    self.assertTrue(valido, "Comando inválido")
    self.assertNotEqual(acao, "", "Ação não pode ser vazia")
    self.assertNotEqual(objeto, "", "Objeto não pode ser vazio")
    error = deletar_atividade(objeto)
    self.assertEqual(error, None, f"Erro ao deletar atividade: {error}")

    novas_atividades = carregar_atividades()
    novo_tamanhao_da_lista_de_atividades = len(novas_atividades)
    self.assertLess(novo_tamanhao_da_lista_de_atividades, tamanho_da_lista_de_atividades,f"A atividade '{objeto}' não foi deletada, o tamanho da lista não diminuiu.")

    atividade_deletada = True 
    for atividade in novas_atividades:
        if atividade["text"] == objeto:
            atividade_deletada = False 
            break
    
 
    self.assertTrue(atividade_deletada, f"A atividade '{objeto}' não foi deletada corretamente.")

if __name__ == "__main__":
    suite = unittest.TestSuite()

    # Adicionando os testes na ordem desejada
    suite.addTest(TesteAcoesAssistente('test_cria_atividade'))
    suite.addTest(TesteAcoesAssistente('test_atualizar_atividade'))
    suite.addTest(TesteAcoesAssistente('test_concluir_atividade'))
    suite.addTest(TesteAcoesAssistente('test_deletar_atividade'))

    # Executando a suite de testes
    runner = unittest.TextTestRunner()
    runner.run(suite)