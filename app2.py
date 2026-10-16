# instalação das bibliotecas
# pip install pymupdf streamlit


import os # acessa variaveis de ambiente
import json # converte o histórico   do chat para o formato JSON
import hashlib# calcula o resumo SHA256 para identificar arquivos
from io import BytesIO# trata bytes de arquivos como arquivos de memoria
import pandas as pd # lê arquivos CSV/Excell e analisa tabelas
import pymupdf # abre PDF e extrai o texto de suas paginas
import streamlit as st # constroi a interface web do chatbot
from dotenv import load_dotenv # carrega variaveis do arquivo .env
from groq import Groq # clientes para enviar perguntas a API do Groq


load_dotenv() # le o arquivo .env

# define o titulo da  aba do navegador, icone
st.set_page_config(
page_title= "Assistente T_IA02", # nome mostrado na aba
page_icon="🤖", # icone mostrando aba    
layout= "wide" # ocupa uma largura maior najanela

)
# recupera  a chave da API
api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    st.error("GROQ_API_KEY não encontrada no arquivo .env")
st.stop()

# cria o cliete que fara as requisições
client = Groq(api_key=api_key)

# define o moodelo da Groq escolhido para responder as perguntas
MODELO = "openai/gpt-oss-20b"

# limita  a quantidade de caracteres extraidos de CADA arquivo

LIMITE_ARQUIVO = 12000

# limita  a soma dos caracteres de TODOS os arquivos no contexto
LIMITE_TOTAL = 30000

# função para ler arquivos pdf
def ler_pdf(arquivo):
    dados = arquivo.getvalue() # obtem o conteudo enviado, em formato de bytes

# abre o PDF na memoria sem guardar no computador
    documento = pymupdf.open(
        stream=dados, # Bytes do PDF
        filetype="pdf" # Tipo do arquivo

    )
    # guarda separadamente o texto extraido de cada pagina
    paginas = []
    try:
        # percorre todas as paginas, e coloca numeração começando em 1
        for numero, pagina in enumerate(documento, start=1):
            # extrai o texto selecionavel da pagina  atual
            texto = pagina.get_text('text')
            # associa o texto napagina de leitura
            if texto.strip():
                pagina.append(f'Pagina{numero}:\n{texto}')
    finally:
        # fecha o PDF mesmo quando acontece um erro na leitura        
         documento.close()
    return "\n\n".join(paginas)  

def ler_txt(arquivo):
    dados = arquivo.getvalue()
    # testa codificações comuns para interpretar caracteres e acertos
    for codificacao in ["utf-8-sig","cp1252","latin1"]:
        try:
            # converte os bytes em uma string e a devolve.
            return dados.decode(codificacao)
        except UnicodeDecodeError:
            # Caso falhe, testa a aproxima codificação
            continue
    # informa que a conversão falhou  
    raise ValueError("Não foi possivel ler o arquivo TXT.") 

def ler_csv(arquivo):
    dados = arquivo.getvalue()
   
    for codificacao in ["utf-8-sig","cp1252","latin1"]:
        try:
            df = pd.read_csv(
                BytesIO(dados), # permite ler bytes como arquivo
                encoding=codificacao, # codificação em teste ele testa cada um deles acima
                sep=None, # testa detectar o separador automaticamente
                engine="python" # mecanismo que permite esta detecção
            )
            return df # retorna a tabela
        except(UnicodeError, pd.errors.ParserError):
            # se a leitura falhar, tenta outra codificação
            continue
    raise ValueError("Não foi possivel ler o CSV")



# função  para transformar tabela em texto para a IA
def preparar_tabela(df,nome_aba= "Dados"):
    contexto = (
        f"Aba/tabela: {nome_aba}\n"
        f"Total de regitros: {len(df)}\n"
        f"Colunas: {list(df.colunns)}\n\n"


    )
    # selecione apenas  as colunas que contem valores numericos
    colunas_numericas = df.select_dttype(include="number")
    # verifica se existem dados numricos para descrever
    if not colunas_numericas.empty:
       # adicionar titulo para facilitar a interpretação pela IA
        contexto += "ESTATISTICAS NUMERICAS: \n" 
       # describe() calcula contagem, media, desvio-padrao, minimo 
       # quantis e maximo de cada coluna numeririca
        contexto+= colunas_numericas.decribe().to_string
        contexto+= "\n\n"
        # informar que os proximos dados são apenas uma amostra
    contexto+= "AMOSTRA DOS PRIMEIROS 30 REGISTROS:\n" 
    # converte as primeiras 30 linhas do dataframe em texto CSV
    contexto += df.head(30).to_csv(index=False)   
     # evita que  a IA trate as 30 primeiras linhas como tabela inteira
    contexto+= (
         "\nA amostra pode não conter todos os registros."
         " Não calcule totais por categoria como fosse"
         " a tabela completa.\n"

    ) 

    return contexto

def ler_excel(arquvo):
    planilhas = pd.read_excel(
        BytesIO(arquvo.getvalue()), # conteudo em memoria 
        sheet_name=None, # none significa carregar todas as abas
        engine='openpyx1' # biblioteca criada para abrir arquivos xlsx


    )

    # lista onde o texto de cada aba sera armazenado
    partes = []
    # percorre cada nome de abas e sua tabela (Dataframe) 
    for nome_aba, df in planilhas.itens():
        texto_aba = preparar_tabela(df, nome_aba=nome_aba)    
    # acrescenta e resume textual da aba a lista
        partes.append(texto_aba)    
    return "\n\n". join(partes) 
# função para identificar e processar o arquivo
def processar_arquivo(arquivo):
    # obtem a extensão
    extensao = arquivo.name.lower().rsplit(".",1)[-1]
    # divide a string  a partir do ponto
    
    if extensao == "pdf":
        texto = ler_pdf(arquivo)
    elif extensao == "txt":
         texto = ler_txt(arquivo)
    elif extensao== "csv":
        df = ler_csv(arquivo)
        texto = preparar_tabela(df,nome_aba= arquivo.name)
    elif extensao == "xlsx":
        texto = ler_excel(arquivo)  
    else:
        raise ValueError("Formato não suportado")
    return texto     

