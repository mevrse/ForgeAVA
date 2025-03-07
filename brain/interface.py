# Bibliotecas Python
import os, subprocess, threading, webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

# Módulos
from brain.gerador import saída_gemini, salvar_arquivo, ler_observações
from brain.ava import retornarTextoAVA, enviarArquivoAVA, obterAtributoID

# Bibliotecas
from dotenv import load_dotenv, set_key

# Cores Terminal
GRENN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0;0m'


class Gerador:
    ''' Configurações da Interface '''
    def __init__(self, root):
        self.root = root
        self.root.title("ForgeAVA")
        self.root.geometry("1000x600")
        
        ''' Logo VRSE '''
        vrse_path = os.path.join(".", "media", "VRSE.png")
        try:
            logo_imagem = tk.PhotoImage(file=vrse_path)
            self.root.iconphoto(True, logo_imagem)
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")


        '''Configurações de Usuário'''
        self.env_file = "brain/.env"
        load_dotenv(self.env_file)

        if not os.path.exists(f"{os.getcwd()}/generatedCodes"):
            os.mkdir(f"{os.getcwd()}/generatedCodes")

        self.API_KEY = os.getenv("API_KEY", "")
        self.LOGIN = os.getenv("LOGIN", "")
        self.SENHA = os.getenv("SENHA", "")
        self.PASTA_SAIDA = os.getenv("PASTA_SAIDA", f"{os.getcwd()}/generatedCodes")
        self.GET_OBSERVACOES = os.getenv("GET_OBSERVACOES", "False") == "True"
        
        try:
            self.observacoes = ler_observações("observacoes.txt")
        except UnicodeDecodeError as e:
            print(RED + f"Erro ao ler o arquivo: {e}" + RESET)
            return
        
        ''' Tela Inicial '''
        self.frame_principal = tk.Frame(self.root)
        self.frame_principal.pack(side="right", fill="both", expand=True)


        ''' Barra Lateral '''
        self.frame_lateral = tk.Frame(self.root, width=200, bg="lightgray")
        self.frame_lateral.pack(side="left", fill="y")


        ''' Botões na Barra Lateral '''
        self.botao_gerar_codigo = tk.Button(self.frame_lateral, text="Gerar Código de Atividade AVA", command=self.mostrar_gerar_codigo_ava)
        self.botao_gerar_codigo.pack(fill="x")

        self.botao_gerar_codigo_texto = tk.Button(self.frame_lateral, text="Gerar Código com Texto", command=self.mostrar_gerar_codigo_texto)
        self.botao_gerar_codigo_texto.pack(fill="x")

        self.botao_arquivos = tk.Button(self.frame_lateral, text="Arquivos Gerados", command=self.mostrar_arquivos_gerados)
        self.botao_arquivos.pack(fill="x")

        self.botao_configuracoes = tk.Button(self.frame_lateral, text="Configurações", command=self.mostrar_configuracoes)
        self.botao_configuracoes.pack(fill="x")

        self.botao_ajuda = tk.Button(self.frame_lateral, text="Ajuda", command=self.mostrar_ajuda)
        self.botao_ajuda.pack(fill="x")

        self.botao_ajuda = tk.Button(self.frame_lateral, text="Sair", bg="red3", command=self.root.quit)
        self.botao_ajuda.pack(fill="x", side="bottom")

        self.gerador_ava = tk.Label(self.frame_lateral, text="ForgeAVA - VRSE", bg="lightgray").pack(fill="x", side="bottom")



    '''Funções da Interface'''
    def limpar_tela(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()


    def criar_campo(self, parent, texto, entry_text="", senha=False, entry_camp=False):
        frame = tk.Frame(parent, relief="solid", borderwidth=1, padx=5, pady=5)
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text=texto).pack(side="top", anchor="w", pady=2)

        var = tk.StringVar(value=entry_text)
        entry = tk.Entry(frame, textvariable=var, show="*" if senha else "")
        entry.pack(fill="x", pady=2)

        if senha or entry_camp:
            return entry
        else:
            return var



    ''' Primeiro Botão: Gerar Código de Atividade AVA '''
    def mostrar_gerar_codigo_ava(self):
        self.limpar_tela()

        frame_gerar_codigo = tk.LabelFrame(self.frame_principal, text="Gerar Código de Atividade AVA", padx=10, pady=10)
        frame_gerar_codigo.pack(fill="both", padx=20, pady=20)

        # Variáveis para armazenar as opções selecionadas e campos de texto
        self.opcao_ava_selecionada = tk.StringVar()
        self.opcao_arquivo_selecionada = tk.StringVar()

        # Frame para as caixas de seleção AVA
        frame_opcoes_ava = tk.Frame(frame_gerar_codigo, relief="solid", borderwidth=1, padx=5, pady=5)
        frame_opcoes_ava.pack(fill="x", pady=5)

        # Caixas de seleção AVA
        tk.Label(frame_opcoes_ava, text="Identificação da Atividade AVA:", fg="black").pack(pady=5, side="left")
        tk.Checkbutton(frame_opcoes_ava, text="ID", variable=self.opcao_ava_selecionada, onvalue="id", offvalue="").pack(side="left", padx=5)
        tk.Checkbutton(frame_opcoes_ava, text="URL", variable=self.opcao_ava_selecionada, onvalue="url", offvalue="").pack(side="left", padx=5)

        # Frame para as caixas de seleção Arquivo
        frame_opcoes_arquivo = tk.Frame(frame_gerar_codigo, relief="solid", borderwidth=1, padx=5, pady=5)
        frame_opcoes_arquivo.pack(fill="x", pady=5)

        # Caixas de seleção Arquivo
        tk.Label(frame_opcoes_arquivo, text="Enviar arquivo para o AVA após gerar?", fg="black").pack(pady=5, side="left")
        tk.Checkbutton(frame_opcoes_arquivo, text="Sim, enviar o arquivo", variable=self.opcao_arquivo_selecionada, onvalue="enviar", offvalue="").pack(side="left", padx=5)
        tk.Checkbutton(frame_opcoes_arquivo, text="Não, apenas salvar", variable=self.opcao_arquivo_selecionada, onvalue="salvar", offvalue="").pack(side="left", padx=5)

        # Campos de texto
        self.id_or_url_atividade = self.criar_campo(frame_gerar_codigo, "ID ou URL da Atividade AVA")
        self.arquivo = self.criar_campo(frame_gerar_codigo, "Nome do Arquivo a ser salvo")

        # Mensagens
        self.mensagem_sucesso_ava = tk.Label(frame_gerar_codigo, text="", fg="green")
        self.mensagem_sucesso_ava.pack(pady=5, side="left")

        self.mensagem_erro_ava = tk.Label(frame_gerar_codigo, text="", fg="red")
        self.mensagem_erro_ava.pack(pady=5, side="left")

        self.mensagem_carregamento_ava = tk.Label(frame_gerar_codigo, text="", fg="black")
        self.mensagem_carregamento_ava.pack(pady=5, side="left")

        # Botão "Gerar Código"
        self.botao_codigo = tk.Button(frame_gerar_codigo, text="Gerar Código", command=self.botao_codigo_ava, bg="grey", fg="black", state="disabled")
        self.botao_codigo.pack(pady=10, side="right")

        if not self.API_KEY or not self.LOGIN or not self.SENHA or not os.path.isdir(self.PASTA_SAIDA):
            frame_erro = tk.LabelFrame(self.frame_principal, text="Erro", padx=10, pady=10)
            frame_erro.pack(fill="both", padx=20, pady=20)
            erro_msg = tk.Label(frame_erro, text="Configurações não encontradas:", fg="red")
            erro_msg.pack(padx=20, pady=5)
            if not self.API_KEY:
                erro_msg = tk.Label(frame_erro, text="Chave API Gemini.", fg="red")
                erro_msg.pack(padx=20, pady=5)
            if not self.LOGIN:
                erro_msg = tk.Label(frame_erro, text="Login AVA.", fg="red")
                erro_msg.pack(padx=20, pady=5)
            if not self.SENHA:
                erro_msg = tk.Label(frame_erro, text="Senha AVA.", fg="red")
                erro_msg.pack(padx=20, pady=5)
            if not os.path.isdir(self.PASTA_SAIDA):
                erro_msg = tk.Label(frame_erro, text="Pasta de Saída.", fg="red")
                erro_msg.pack(padx=20, pady=5)
            erro_msg = tk.Label(frame_erro, text="ATUALIZE AS CONFIGURAÇÕES", fg="red")
            erro_msg.pack(padx=20, pady=5)
            return
        
        # Verificação de preenchimento dos campos
        def verificar_campos():
            todos_preenchidos = (
                self.opcao_ava_selecionada.get() and
                self.opcao_arquivo_selecionada.get() and
                self.id_or_url_atividade.get().strip() and
                self.arquivo.get().strip() and
                self.API_KEY and
                self.LOGIN and
                self.SENHA and
                os.path.isdir(self.PASTA_SAIDA)
            )
            self.botao_codigo.config(
                state="normal" if todos_preenchidos else "disabled",
                bg="green" if todos_preenchidos else "grey",
                fg="white" if todos_preenchidos else "black"
            )

        # Traces para monitorar mudanças
        self.opcao_ava_selecionada.trace("w", lambda *args: verificar_campos())
        self.opcao_arquivo_selecionada.trace("w", lambda *args: verificar_campos())
        self.id_or_url_atividade.trace_add("write", lambda *args: verificar_campos())
        self.arquivo.trace_add("write", lambda *args: verificar_campos())


    def botao_codigo_ava(self):
        self.mensagem_carregamento_ava.config(text="Acessando Atividade...")
        threading.Thread(target=self.gerar_codigo_ava).start()

    def gerar_codigo_ava(self):
        # Acessa a atividade no AVA e copia o texto da mesma
        if self.opcao_ava_selecionada.get() == "url":
            # Tentar obter o atributo ID da URL
            self.id_atividade_url = obterAtributoID(self.id_or_url_atividade.get())
            if self.id_atividade_url == "erro":
                self.mensagem_carregamento_ava.config(text="")
                print(RED + "ERRO ao obter o atributo 'ID' da URL" + RESET)
                messagebox.showinfo("Gerador AVA", "ERRO ao obter atributo 'ID' da URL")
                self.root.after(3, self.mostrar_gerar_codigo_ava)

            self.texto_atividade = retornarTextoAVA(login=self.LOGIN, senha=self.SENHA, id=self.id_atividade_url)
            if self.texto_atividade == "erro":
                self.mensagem_carregamento_ava.config(text="")
                print(RED + "ERRO ao acessar atividade AVA" + RESET)
                messagebox.showinfo("Gerador AVA", "ERRO ao acessar atividade AVA")
                self.root.after(5, self.mostrar_gerar_codigo_ava)

        elif self.opcao_ava_selecionada.get() == "id":
            self.texto_atividade = retornarTextoAVA(login=self.LOGIN, senha=self.SENHA, id=self.id_or_url_atividade.get())
            if self.texto_atividade == "erro":
                self.mensagem_carregamento_ava.config(text="")
                print(RED + "ERRO ao acessar atividade AVA" + RESET)
                messagebox.showinfo("Gerador AVA", "ERRO ao acessar atividade AVA")
                self.root.after(2, self.mostrar_gerar_codigo_ava)

        # Tentar obter resposta do Gemini
        self.mensagem_carregamento_ava.config(text="Gerando Código...")
        prompt = str(self.texto_atividade) + "" + str(self.observacoes if self.GET_OBSERVACOES == "True" else "")
        try:
            resposta = saída_gemini(prompt, self.API_KEY)
        except Exception as e :
            self.mensagem_carregamento_ava.config(text="")
            print(RED + "ERRO ao obter resposta do Gemini:" + RESET, e)
            messagebox.showinfo("Gerador AVA", "ERRO ao obter a resposta do Gemini")
            self.root.after(2, self.mostrar_gerar_codigo_ava)

        # Tentar salvar arquivo
        self.mensagem_carregamento_ava.config(text="Salvando Arquivo...")
        try:
            salvar_arquivo(self.arquivo.get(), resposta, self.PASTA_SAIDA)
            self.mensagem_carregamento_ava.config(text="")
            messagebox.showinfo("Gerador AVA", f"Arquivo salvo com sucesso em: {self.PASTA_SAIDA}/{self.arquivo.get()}")
        except Exception as e:
            self.mensagem_carregamento_ava.config(text="")
            print(RED + "ERRO ao salvar o arquivo:" + RESET, e)
            messagebox.showinfo("Gerador AVA", "ERRO ao salvar arquivo")
            self.mensagem_erro_ava.config(text="")
            self.root.after(2, self.mostrar_gerar_codigo_ava)

        # Envia arquivo ao AVA se for solicitado
        if self.opcao_arquivo_selecionada.get() == "enviar":
            self.mensagem_carregamento_ava.config(text="Enviando Arquivo Para o AVA...")
            if self.opcao_ava_selecionada.get() == "url":
                # Tenta enviar arquivo para o AVA 
                if enviarArquivoAVA(login=self.LOGIN, senha=self.SENHA, id=self.id_atividade_url, caminho_arquivo=self.PASTA_SAIDA, arquivo=self.arquivo.get()) == "erro":
                    self.mensagem_carregamento_ava.config(text="")
                    print(RED + "ERRO ao enviar arquivo para o AVA" + RESET)
                    messagebox.showinfo("Gerador AVA", "ERRO ao enviar arquivo para o AVA")
                    self.root.after(5, self.mostrar_gerar_codigo_ava)

            elif self.opcao_ava_selecionada.get() == "id":
                # Tenta enviar arquivo para o AVA
                if enviarArquivoAVA(login=self.LOGIN, senha=self.SENHA, id=self.id_or_url_atividade.get(), caminho_arquivo=self.PASTA_SAIDA, arquivo=self.arquivo.get()) == "erro":
                    self.mensagem_carregamento_ava.config(text="")
                    print(RED + "ERRO ao enviar arquivo para o AVA" + RESET)
                    messagebox.showinfo("Gerador AVA", "ERRO ao enviar arquivo para o AVA")
                    self.root.after(3, self.mostrar_gerar_codigo_ava)

            self.mensagem_carregamento_ava.config(text="")
            self.mensagem_sucesso_ava.config(text="Código salvo e enviado pro AVA com sucesso!")

        self.root.after(1200, self.mostrar_gerar_codigo_ava)



    ''' Segundo Botão: Gerar Código com Texto '''
    def mostrar_gerar_codigo_texto(self):
        self.limpar_tela()

        # Criação do frame com título
        frame_gerar_codigo_texto = tk.LabelFrame(self.frame_principal, text="Gerar Código com Texto", padx=10, pady=10)
        frame_gerar_codigo_texto.pack(fill="both", padx=20, pady=20)

        # Campos para entrada de texto e nome do arquivo
        self.texto = self.criar_campo(frame_gerar_codigo_texto, "Texto para geração de código")
        self.arquivo = self.criar_campo(frame_gerar_codigo_texto, "Nome do Arquivo a ser salvo")

        # Mensagens
        self.mensagem_sucesso_texto = tk.Label(frame_gerar_codigo_texto, text="", fg="green")
        self.mensagem_sucesso_texto.pack(pady=5, side="left")

        self.mensagem_erro_texto = tk.Label(frame_gerar_codigo_texto, text="", fg="red")
        self.mensagem_erro_texto.pack(pady=5, side="left")

        self.mensagem_carregamento_texto = tk.Label(frame_gerar_codigo_texto, text="", fg="black")
        self.mensagem_carregamento_texto.pack(pady=5, side="left")

        # Botão "Gerar Código"
        self.botao_codigo = tk.Button(frame_gerar_codigo_texto, text="Gerar Código", command=self.botao_codigo_texto, bg="grey", fg="black", state="disabled")
        self.botao_codigo.pack(pady=10, side="right")

        if not self.API_KEY or not os.path.isdir(self.PASTA_SAIDA):
            frame_erro = tk.LabelFrame(self.frame_principal, text="Erro", padx=10, pady=10)
            frame_erro.pack(fill="both", padx=20, pady=20)
            erro_msg = tk.Label(frame_erro, text="Configurações não encontradas:", fg="red")
            erro_msg.pack(padx=20, pady=5)
            if not self.API_KEY:
                erro_msg = tk.Label(frame_erro, text="Chave API Gemini.", fg="red")
                erro_msg.pack(padx=20, pady=5)
            if not os.path.isdir(self.PASTA_SAIDA):
                erro_msg = tk.Label(frame_erro, text="Pasta de Saída.", fg="red")
                erro_msg.pack(padx=20, pady=5)
            erro_msg = tk.Label(frame_erro, text="ATUALIZE AS CONFIGURAÇÕES", fg="red")
            erro_msg.pack(padx=20, pady=5)
            return

        # Verificação de preenchimento dos campos
        def verificar_campos():
            todos_preenchidos = (
                self.texto.get().strip() and
                self.arquivo.get().strip() and
                self.API_KEY and
                self.PASTA_SAIDA
            )
            self.botao_codigo.config(
                state="normal" if todos_preenchidos else "disabled",
                bg="green" if todos_preenchidos else "grey",
                fg="white" if todos_preenchidos else "black"
            )

        # Traces para monitorar mudanças
        self.texto.trace_add("write", lambda *args: verificar_campos())
        self.arquivo.trace_add("write", lambda *args: verificar_campos())

    def botao_codigo_texto(self):
        self.mensagem_carregamento_texto.config(text="Gerando Código...")
        threading.Thread(target=self.gerar_codigo_texto).start()

    def gerar_codigo_texto(self):
        prompt = str(self.texto.get()) + "" + str(self.observacoes if self.GET_OBSERVACOES == "True" else "")
        # Tenta obter a resposta do Gemini
        try:
            resposta = saída_gemini(prompt=prompt, api_key=self.API_KEY)
            self.mensagem_carregamento_texto.config(text="Salvando Arquivo...")
        except Exception as e:
            self.mensagem_carregamento_texto.config(text="")
            print(RED + "ERRO ao obter resposta do Gemini:" + RESET, e)
            messagebox.showinfo("Gerador AVA", "ERRO ao obter resposta do Gemini")
            self.root.after(2, self.mostrar_gerar_codigo_texto)
        
        # Tenta salvar o arquivo 
        try:
            salvar_arquivo(self.arquivo.get(), resposta, self.PASTA_SAIDA)
            self.mensagem_carregamento_texto.config(text="")
            messagebox.showinfo("Gerador AVA", f"Código salvo com sucesso em: {self.PASTA_SAIDA}/{self.arquivo.get()}")
            self.root.after(2, self.mostrar_gerar_codigo_texto)
        except Exception as e:
            self.mensagem_carregamento_texto.config(text="")
            print(RED + "ERRO ao salvar arquivo:" + RESET, e)
            messagebox.showinfo("Gerador AVA", "ERRO ao salvar arquivo")
            self.root.after(2, self.mostrar_gerar_codigo_texto)



    ''' Terceiro Botão: Arquivos Gerados '''
    def mostrar_arquivos_gerados(self):
        self.limpar_tela()
        if not os.path.isdir(self.PASTA_SAIDA):
            frame_erro = tk.LabelFrame(self.frame_principal, text="Erro", padx=10, pady=10)
            frame_erro.pack(fill="both", padx=20, pady=20)
            erro_msg = tk.Label(frame_erro, text="Não foi possível encontrar a pasta de saída.", fg="red")
            erro_msg.pack(padx=20, pady=20)
            return

        frame_arquivos = tk.LabelFrame(self.frame_principal, text="Arquivos Gerados", padx=10, pady=10)
        frame_arquivos.pack(fill="both", padx=20, pady=20)

        arquivos = [f for f in os.listdir(self.PASTA_SAIDA) if os.path.isfile(os.path.join(self.PASTA_SAIDA, f))]
        
        if not arquivos:
            msg = tk.Label(frame_arquivos, text="Nenhum arquivo encontrado na pasta de saída.", fg="red")
            msg.pack(padx=20, pady=10)
            return

        self.lista_arquivos = tk.Listbox(frame_arquivos, selectmode="single", height=10, width=60)
        for arquivo in arquivos:
            self.lista_arquivos.insert(tk.END, arquivo)
        self.lista_arquivos.pack(padx=20, pady=10)

        tk.Button(frame_arquivos, text="Selecionar Arquivo", command=self.abrirArquivo).pack(pady=10)

    def abrirArquivo(self):
        self.arquivo_selecionado = self.lista_arquivos.get(tk.ACTIVE)
        if not self.arquivo_selecionado:
            return
        
        caminho_arquivo = os.path.join(self.PASTA_SAIDA, self.arquivo_selecionado)
        self.limpar_tela()


        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as file:
                conteudo = file.read()
            
            frame_edicao = tk.LabelFrame(self.frame_principal, text=f"Edição do Arquivo: {self.arquivo_selecionado}", padx=10, pady=10)
            frame_edicao.pack(fill="both", padx=20, pady=20)

            self.area_edicao = tk.Text(frame_edicao, wrap="word", height=20, bg="white", fg="black")
            self.area_edicao.pack(fill="both", expand=True, padx=10, pady=10)

            if self.arquivo_selecionado.endswith(".py"):
                btn_rodar_codigo = tk.Button(frame_edicao, text="Rodar Código Python", command=lambda: self.rodarCódigo(caminho_arquivo))
                btn_rodar_codigo.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
            
            conteudo = conteudo.replace("\t", "    ")
            self.area_edicao.insert(tk.END, conteudo)

            self.area_edicao.bind('<Tab>', self.inserirEspaço)

            # Frame Botões
            frame_botoes = tk.Frame(frame_edicao)
            frame_botoes.pack(fill="x", pady=10, padx=10, anchor="e")
            
            btn_salvar = tk.Button(frame_botoes, text="Salvar Alterações", command=lambda: self.salvarEdições(self.arquivo_selecionado), fg="white", bg="green")
            btn_salvar.pack(side="right", padx=5)
            btn_selecionar = tk.Button(frame_botoes, text="Voltar", command=self.mostrar_arquivos_gerados)
            btn_selecionar.pack(side="right", padx=5)

        except Exception as e:
            print(RED + f"Erro ao tentar abrir o arquivo: {caminho_arquivo}" + RESET, e)
            messagebox.showerror("Erro", f"Erro ao tentar abrir o arquivo: {caminho_arquivo}, arquivo não suportado.")
            self.mostrar_arquivos_gerados()

    def inserirEspaço(self, event):
        pos_cursor = self.area_edicao.index(tk.INSERT)
        self.area_edicao.insert(pos_cursor, '    ')
        return 'break'

    def salvarEdições(self, nome_arquivo):
        conteudo_editado = self.area_edicao.get("1.0", tk.END)
        caminho_arquivo = os.path.join(self.PASTA_SAIDA, nome_arquivo)
        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            file.write(conteudo_editado)

        messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")

    def rodarCódigo(self, caminho_arquivo):
        def terminal():
            try:
                if os.name == 'nt':  # Para Windows
                    comando = f'start cmd /K "cd {self.PASTA_SAIDA} && python {self.arquivo_selecionado} && pause && exit"'
                else: # Linux e MacOS
                    comando = f'gnome-terminal -- bash -c "python3 \"{caminho_arquivo}\"; exec bash"'

                    if subprocess.call(["which", "gnome-terminal"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
                        comando = f'xterm -hold -e "python3 {caminho_arquivo}"'

                subprocess.Popen(comando, shell=True)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao executar o código: {str(e)}")

        threading.Thread(target=terminal).start()



    ''' Quarto Botão: Configurações '''
    def mostrar_configuracoes(self):
        """Exibe os campos de configurações"""
        self.limpar_tela()

        frame_configuracoes = tk.LabelFrame(self.frame_principal, text="Configurações", padx=10, pady=10)
        frame_configuracoes.pack(fill="both", padx=20, pady=20)

        self.api_key_entry = self.criar_campo(frame_configuracoes, "Chave API Gemini", self.API_KEY)
        self.login_ava_entry = self.criar_campo(frame_configuracoes, "Login AVA", self.LOGIN)

        # Campo de Senha
        frame_senha_ava = tk.Frame(frame_configuracoes, relief="solid", borderwidth=1, padx=5, pady=5)
        frame_senha_ava.pack(fill="x", pady=5)
        tk.Label(frame_senha_ava, text="Senha AVA").pack(side="top", anchor="w", pady=2)
        senha_var = tk.StringVar(value=str(self.SENHA))
        self.senha_ava_entry = tk.Entry(frame_senha_ava, textvariable=senha_var, show="*")
        self.senha_ava_entry.pack(fill="x", pady=2)

        self.botao_visualizar_senha = tk.Button(frame_senha_ava, text="Visualizar Senha", command=self.toggle_senha)
        self.botao_visualizar_senha.pack(pady=5, side="right")

        # Campo para pasta de saída
        pasta_frame = tk.Frame(frame_configuracoes, relief="solid", borderwidth=1, padx=5, pady=5)
        pasta_frame.pack(fill="x", pady=5)
        tk.Label(pasta_frame, text="Pasta de Saída:").pack(side="left")
        self.label_PASTA_SAIDA = tk.Label(pasta_frame, text=self.PASTA_SAIDA if self.PASTA_SAIDA else "Nenhuma pasta selecionada", fg="green" if self.PASTA_SAIDA else "red")
        self.label_PASTA_SAIDA.pack(side="left")

        tk.Button(pasta_frame, text="Selecionar Outra Pasta" if self.PASTA_SAIDA else "Selecionar Pasta", command=self.selecionar_pasta).pack(pady=10, side="right")

        self.opcao_observacoes = tk.StringVar(value=str(self.GET_OBSERVACOES))
        # Frame para checkbox de observações
        frame_check_obs = tk.Frame(frame_configuracoes, relief="solid", borderwidth=1, padx=5, pady=5)
        frame_check_obs.pack(fill="x", pady=5)

        # Checkbox de observações
        tk.Label(frame_check_obs, text="Usar Observações:", fg="black").pack(pady=5, side="left")
        tk.Checkbutton(frame_check_obs, text="", variable=self.opcao_observacoes, onvalue="True", offvalue="False").pack(side="left", padx=5)
        tk.Button(frame_check_obs, text="Editar Observações", command=self.abrirObservações).pack(pady=10, side="left")

        tk.Button(frame_configuracoes, text="Salvar Configurações", command=self.salvar_configuracoes, bg="green", fg="white").pack(pady=10, side="right")

    def salvar_configuracoes(self):
        # Atualizar valores no arquivo .env
        set_key(self.env_file, "API_KEY", self.api_key_entry.get())
        set_key(self.env_file, "LOGIN", self.login_ava_entry.get())
        set_key(self.env_file, "SENHA", self.senha_ava_entry.get())
        set_key(self.env_file, "PASTA_SAIDA", self.PASTA_SAIDA)
        set_key(self.env_file, "GET_OBSERVACOES", "True" if self.opcao_observacoes.get() == "True" else "False")

        # Atualizar os valores armazenados
        self.API_KEY = self.api_key_entry.get()
        self.LOGIN = self.login_ava_entry.get()
        self.SENHA = self.senha_ava_entry.get()
        self.GET_OBSERVACOES = self.opcao_observacoes.get()

        messagebox.showinfo("Configurações", "As configurações foram salvas com sucesso!")
        self.mostrar_configuracoes()

    def toggle_senha(self):
        """Alterna a visualização da senha"""
        if self.senha_ava_entry.cget('show') == "*":
            self.senha_ava_entry.config(show="")
            self.botao_visualizar_senha.config(text="Esconder Senha")
        else:
            self.senha_ava_entry.config(show="*")
            self.botao_visualizar_senha.config(text="Visualizar Senha")

    def selecionar_pasta(self):
        """Abre o seletor de pastas e atualiza o caminho"""
        nova_pasta = filedialog.askdirectory()
        if nova_pasta:
            self.PASTA_SAIDA = nova_pasta
            self.label_PASTA_SAIDA.config(text=self.PASTA_SAIDA)

    def abrirObservações(self):
        self.caminho_arquivo_observacoes = os.path.join('brain', 'files', 'observacoes.txt')

        self.limpar_tela()

        frame_edicao = tk.LabelFrame(self.frame_principal, text="Edição de observações.txt", padx=10, pady=10)
        frame_edicao.pack(fill="both", padx=20, pady=20)

        self.area_edicao = tk.Text(frame_edicao, wrap="word", height=20, bg="white", fg="black")
        self.area_edicao.pack(fill="both", expand=True, padx=10, pady=10)

        with open(self.caminho_arquivo_observacoes, "r", encoding="utf-8") as file:
            conteudo = file.read()

        conteudo = conteudo.replace("\t", "    ")
        self.area_edicao.insert(tk.END, conteudo)

        self.area_edicao.bind('<Tab>', self.inserirEspaçoObservações)

        # Frame Botões
        frame_botoes = tk.Frame(frame_edicao)
        frame_botoes.pack(fill="x", pady=10, padx=10, anchor="e")
        
        btn_salvar = tk.Button(frame_botoes, text="Salvar Alterações", command=lambda: self.salvarEdiçõesObservações(self.caminho_arquivo_observacoes), fg="white", bg="green")
        btn_salvar.pack(side="right", padx=5)
        btn_selecionar = tk.Button(frame_botoes, text="Voltar", command=self.mostrar_configuracoes)
        btn_selecionar.pack(side="right", padx=5)

    def inserirEspaçoObservações(self, event):
        pos_cursor = self.area_edicao.index(tk.INSERT)
        self.area_edicao.insert(pos_cursor, '    ')
        return 'break'

    def salvarEdiçõesObservações(self, nome_arquivo):
        conteudo_editado = self.area_edicao.get("1.0", tk.END)
        caminho_arquivo = os.path.join('brain', 'files', 'observacoes.txt')
        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            file.write(conteudo_editado)

        messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")



    ''' Quinto Botão: Ajuda '''
    def mostrar_ajuda(self):
        self.limpar_tela()

        frame_ajuda = tk.LabelFrame(self.frame_principal, text="Ajuda", padx=10, pady=10)
        frame_ajuda.pack(fill="both", padx=20, pady=20)

        try:
            ajuda_caminho = os.path.join("brain", "files", "ajuda.txt")
            with open(ajuda_caminho, "r", encoding="utf-8") as arquivo_ajuda:
                conteudo_ajuda = arquivo_ajuda.read()
        except FileNotFoundError:
            conteudo_ajuda = "Arquivo de ajuda não encontrado. Certifique-se de que 'ajuda.txt' está no mesmo diretório do programa."
        except Exception as e:
            conteudo_ajuda = f"Erro ao carregar a ajuda: {e}"

        # Exibindo o conteúdo de ajuda em um widget Text
        texto_ajuda = tk.Text(frame_ajuda, wrap="word", bg="white", fg="black", height=20)
        texto_ajuda.insert("1.0", conteudo_ajuda)
        texto_ajuda.configure(state="normal")  # Permitir edição temporária para adicionar tags
        texto_ajuda.pack(fill="both", expand=True, padx=10, pady=10)

        # Detectar e marcar links no texto
        def marcar_links():
            import re
            padrao_url = r"https?://[^\s]+"
            for match in re.finditer(padrao_url, conteudo_ajuda):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                texto_ajuda.tag_add("link", start_idx, end_idx)
                texto_ajuda.tag_config("link", foreground="blue", underline=True)

                # Evento para abrir o link no navegador
                texto_ajuda.tag_bind("link", "<Button-1>", lambda e, url=match.group(): webbrowser.open(url))
                texto_ajuda.tag_bind("link", "<Enter>", lambda e: texto_ajuda.config(cursor="hand2"))
                texto_ajuda.tag_bind("link", "<Leave>", lambda e: texto_ajuda.config(cursor=""))

        # Aplicar tags para links
        marcar_links()
        texto_ajuda.configure(state="disabled")  # Desativar edição novamente

        # Botão para atualizar ajuda
        # tk.Button(frame_ajuda, text="Recarregar Ajuda", command=self.mostrar_ajuda, bg="blue", fg="white").pack(pady=10)


def interface():
    root = tk.Tk()
    app = Gerador(root)
    root.mainloop()

if __name__ == '__main__':
    interface()