# instalar biblioteca 
# pip install  dotenv
# pip install groq
#
# Permite acessar recursos do sistema operacional 
# criando e incluindo variaveis de ambiente 
import os

# importar a classe Groq da biblioteca  grop
from groq import Groq

# import a funÇão load_dortenv da biblioteca python dot env
# esta funçãoo permite carregar variaveis  python dot env
from dotenv import load_dotenv

# Carregar as variaveis de ambiente
load_dotenv()

# Recuperar a cheve  da API
# A função os.getenv procura  o valor de uma variavel de 
# ambiente pelo seu nome
# Se aa variavel não existir, o resultado sera None.

api_key = os.getenv('GROQ_API_KEY')

# Verificar  se a   chave existe
if  not api_key:
    print('Chave GROQ_API_KEY não encontrada!')
    # raise  é utilizado para provocar uma exceção

    # ValueError indica que existe um problema relacionado com o valor esperado.
    # neste caso, interrompemos o programa porque não foi
    # encontrada uma chave de API
    raise ValueError('Chave GROQ_API_KEY não encontrada!')


# criar o cliente Groq

client = Groq(api_key=api_key)


# criar  a função de comversa com a IA


def chat_groq(prompt):
    # enviar uma requisição para   a API
    # a variavel completion armazenará o resultado retornado pela API 
    # client representa os recursos de conversa
    # completions representa as repostas geradas
    # creat()  envia uma solicitação a API, iformandoos modelos
    # e aas configurações das conversas
    completion = client.chat.completions.create(
        model= "openai/gpt-oss-20b",
        # definir as mensagens da conversa
        messages= [
            {
                # a chave role identifica que e sta mandando uma mensagem
                # system instruções para o modelo
                # "assistant" mensagens anteriores da IA
                "role":"user",
                # a chave content armazena o conteudo da mensagem enviada para a IA
                # prompt contem o texto recebido como argumento da função.
                "content" : prompt
            }
        ],
        # configurar a temperatura
        # o parametro temperatura controla o nivel  de aleatoriedade 
        # na geração das reostas
        # valores menores tendem a produzirem respostas mais previsiveis.
        # valores maiores tendem a produzirem respostas mais variaveis.
        # a temperatura não representa porcentagem de acerto ou
        # inteligencia do modelo
        temperature=0.7,
        # definir o limite de tokens
        max_tokens=1024
    )

    



 # recuperara resposta gerada

    return completion.choices[0].message.content  
#__name__ é uma variavel especoial do Python, criada  
# automaticamente quando um modulo é executado ou importado.
# __main__ é o nome especial utilizado pelo Python para eidentificar
# o modulo que e sta sendo executado diretamente,
# # execute o codigo a baixo: 
if __name__== "__main__":
    while True:
        user_input = input("Digite sua pergunta (ou 'sair' para encerrar):  ")
       
        # verifica se o texto e igual a sair e finaliza o programa
        if user_input.lower().strip() == 'sair':
          print("Chat encerrado!")
          break
        # verifica se o texto esta vazio e volta no inicio do while e retorna a perguntar
        if not user_input.strip():
            continue
       
        try:
            response = chat_groq(user_input)
           
            print('Resposta do Grop')
            print(response)
        except Exception as erro:
            print(f'Erro: {erro}')
       
        
                                                     