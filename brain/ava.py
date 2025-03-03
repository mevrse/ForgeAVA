# Bibliotecas Python
import time, os, sys
from urllib.parse import urlparse, parse_qs

# Bibliotecas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Cores Terminal
GRENN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0;0m'


def retornarTextoAVA(login, senha, id):
    # Configurações do AVA
    URL_SITE = "https://ava3.cefor.ifes.edu.br/"
    URL_AREA_ESPECIFICA = f"https://ava3.cefor.ifes.edu.br/mod/vpl/view.php?id={id}"
    
    # Configuações do Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar em modo headless
    chrome_options.add_argument("--disable-gpu")  # Necessário para alguns sistemas operacionais
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Login
        driver.get(URL_SITE)
        wait = WebDriverWait(driver, 10)

        campo_usuario = wait.until(EC.presence_of_element_located((By.ID, "username")))
        campo_usuario.send_keys(login)

        campo_senha = wait.until(EC.presence_of_element_located((By.ID, "password")))
        campo_senha.send_keys(senha)
        
        campo_senha.send_keys(Keys.TAB)
        campo_senha.send_keys(Keys.ENTER)

        time.sleep(1)

        # Ir pra atividade
        driver.get(URL_AREA_ESPECIFICA)

        # Procurar o container que contém todos os parágrafos de texto e copiar o texto
        element = driver.execute_script("""
            return document.getElementById("region-main")
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .nextElementSibling
                .nextElementSibling
                .lastElementChild
                .firstElementChild;
        """)

        paragraphs = element.find_elements("tag name", "p")
        texto_ava = "\n".join(paragraph.text for paragraph in paragraphs)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return "erro"
    finally:
        driver.quit()
        return texto_ava


def enviarArquivoAVA(login, senha, id, caminho_arquivo, arquivo):
    # Configurações do AVA
    URL_SITE = "https://ava3.cefor.ifes.edu.br/"
    URL_AREA_ESPECIFICA = f"https://ava3.cefor.ifes.edu.br/mod/vpl/view.php?id={id}"
    caminho_completo_arquivo = os.path.join(caminho_arquivo, arquivo)
    
    # Configurações Selenium
    driver = webdriver.Chrome()
    acao = ActionChains(driver)

    try:
        driver.get(URL_SITE)
        wait = WebDriverWait(driver, 10)

        # Login
        campo_usuario = wait.until(EC.presence_of_element_located((By.ID, "username")))
        campo_usuario.send_keys(login)

        campo_senha = wait.until(EC.presence_of_element_located((By.ID, "password")))
        campo_senha.send_keys(senha)
        
        campo_senha.send_keys(Keys.ENTER)

        time.sleep(2)

        # Ir até a atividade
        driver.get(URL_AREA_ESPECIFICA)

        # Localizar e clicar no botão "Enviar" na barra superior
        enviar_button = driver.execute_script("""
            return document.getElementById("region-main")
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild;
        """)

        if enviar_button:
            driver.execute_script("arguments[0].click();", enviar_button)
        else:
            raise Exception("Botão de envio não encontrado.")

        time.sleep(2)

        # Localizar o botão para escolha de arquivo
        enviar = driver.execute_script("""
            return document.getElementById("region-main")
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .firstElementChild
                .nextElementSibling
                .nextElementSibling
                .firstElementChild
                .firstElementChild
        """)
        
        enviar.send_keys(Keys.ENTER)

        time.sleep(2)

        # Selecionar arquivo
        botao_enviar = driver.find_element(By.NAME, "repo_upload_file")
        botao_enviar.send_keys(caminho_completo_arquivo)

        time.sleep(1)

        # Clicar no primeiro enviar para salvar o arquivo
        acao.send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.ENTER).perform()

        time.sleep(1)

        # Localizar o botão de enviar o arquivo e clicar
        mandar_arquivo = driver.execute_script("""
            return document.getElementById("region-main")
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .firstElementChild
                .firstElementChild
        """)
        mandar_arquivo.send_keys(Keys.ENTER)

        time.sleep(1)

        # Localizar e ir pra página de editar envios
        editar_envio = driver.execute_script("""
            return document.getElementById("region-main")
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .firstElementChild
                .nextElementSibling
                .nextElementSibling
                .firstElementChild
        """)

        if editar_envio:
            driver.execute_script("arguments[0].click();", editar_envio)
        else:
            raise Exception("Botão de visualizar envios não encontrado.")
        
        # Apenas para não fechar a janela
        while True:
            try:
                driver.title
                time.sleep(1)
            except Exception as e:
                break
        return 0

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return "erro"
    
    finally:
        driver.quit()


def obterAtributoID(url):
    try:
        parsed_url = urlparse(url)
        query_parametros = parse_qs(parsed_url.query)
        id = query_parametros.get("id", [None])[0]
        
        return id
    except Exception as e:
        print(f"ocorreu um erro {e}")
        return "erro"