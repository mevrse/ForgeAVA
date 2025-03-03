# Bibliotecas Python
import os, sys

# Bibliotecas
import google.generativeai as genai

# Cores Terminal
GRENN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0;0m'


def limpar_saída_gemini(resposta):
    linhas = resposta.splitlines()
    if linhas and linhas[0] in ['```python', '```python 3.xxx', '```python3']:
        linhas = linhas[1:]    
    if linhas and linhas[-1] == '```':
        linhas = linhas[:-1]
    return "\n".join(linhas)


def saída_gemini(prompt, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    try:
        response = model.generate_content(prompt)
        resposta_limpa = limpar_saída_gemini(response.text)
        return resposta_limpa
    except Exception as e:
        return (RED + f"Erro ao conectar à API Gemini: {e}" + RESET)


def salvar_arquivo(nome_arquivo, conteudo, pasta):
    caminho_pasta = os.path.join(pasta, nome_arquivo)
    try:
        with open(caminho_pasta, "w", encoding="utf-8") as file:
            file.write(conteudo)
        print(GRENN + "Arquivo salvo com sucesso!" + RESET)
    except Exception as e:
        print(RED + f"Erro ao salvar o arquivo: {e}" + RESET)


def ler_observações(file_name):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "brain", "files", file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo '{file_name}' não encontrado na pasta 'files'.")

    common_encodings = ["utf-8", "latin-1", "cp1252"]
    for encoding in common_encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue

    try:
        with open(file_path, "rb") as file:
            raw_data = file.read()

        # Teste manual de algumas codificações adicionais
        for encoding in ["utf-16", "utf-32"]:
            try:
                return raw_data.decode(encoding)
            except UnicodeDecodeError:
                continue
    except Exception as e:
        raise Exception(f"Erro ao processar o arquivo '{file_name}': {e}")

    raise UnicodeDecodeError("Falha ao ler o arquivo de Observações com as codificações testadas.")