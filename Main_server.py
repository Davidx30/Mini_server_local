import sys
import os
import socket
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import QTimer
import http.server
import socketserver
import threading

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    connected_clients = set()  # Conjunto para armazenar IPs dos clientes

    def handle(self):
        self.connected_clients.add(self.client_address[0])  # Adicionar IP à lista de clientes
        super().handle()
        self.close_connection = True  # Fecha a conexão após servir o arquivo

class ThreadingHTTPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)

class AppServidor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 500, 400)
        self.setWindowTitle('Servidor de Compartilhamento de Arquivos')

        self.botaoIniciar = QPushButton('Iniciar Servidor', self)
        self.botaoIniciar.setGeometry(180, 70, 140, 30)
        self.botaoIniciar.clicked.connect(self.iniciarServidor)

        self.botaoParar = QPushButton('Parar Servidor', self)
        self.botaoParar.setGeometry(180, 110, 140, 30)
        self.botaoParar.clicked.connect(self.pararServidor)
        self.botaoParar.setEnabled(False)

        self.botaoSelecionarDiretorio = QPushButton('Selecionar Diretório', self)
        self.botaoSelecionarDiretorio.setGeometry(180, 150, 140, 30)
        self.botaoSelecionarDiretorio.clicked.connect(self.selecionarDiretorio)

        self.botaoSair = QPushButton('Sair', self)
        self.botaoSair.setGeometry(180, 190, 140, 30)
        self.botaoSair.clicked.connect(self.sairAplicacao)

        self.statusLabel = QLabel('Servidor não iniciado', self)
        self.statusLabel.setGeometry(170, 230, 160, 30)

        self.diretorioLabel = QLabel('Diretório do servidor: Nenhum', self)
        self.diretorioLabel.setGeometry(50, 270, 400, 30)

        self.urlLabel = QLabel('URL HTTP:', self)
        self.urlLabel.setGeometry(50, 310, 80, 30)

        self.urlMostrarLabel = QLabel('', self)
        self.urlMostrarLabel.setGeometry(130, 310, 300, 30)

        self.clientesLabel = QLabel('Clientes conectados: 0', self)
        self.clientesLabel.setGeometry(50, 350, 200, 30)

        self.servidor_thread = None
        self.httpd = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizarClientesConectados)

    def iniciarServidor(self):
        self.botaoIniciar.setEnabled(False)
        self.botaoParar.setEnabled(True)
        self.statusLabel.setText('Servidor em execução')

        diretorio_servidor = self.diretorioLabel.text().replace('Diretório do servidor: ', '')
        self.diretorioLabel.setText(f'Diretório do servidor: {diretorio_servidor}')

        ip = socket.gethostbyname(socket.gethostname())
        dominio = f'http://{ip}:8000/'
        self.urlMostrarLabel.setText(dominio)

        self.servidor_thread = threading.Thread(target=self.runServidor, args=(diretorio_servidor,))
        self.servidor_thread.start()

        self.timer.start(1000)  # Atualizar a cada 1 segundo

    def runServidor(self, diretorio_servidor):
        os.chdir(diretorio_servidor)  # Altera o diretório de trabalho
        endereco_servidor = ('', 8000)
        self.httpd = ThreadingHTTPServer(endereco_servidor, MyHTTPRequestHandler)
        self.httpd.serve_forever()

    def pararServidor(self):
        if self.servidor_thread is not None:
            self.httpd.shutdown()
            self.servidor_thread.join()
            self.botaoIniciar.setEnabled(True)
            self.botaoParar.setEnabled(False)
            self.statusLabel.setText('Servidor parado')

        self.timer.stop()

    def selecionarDiretorio(self):
        diretorio = QFileDialog.getExistingDirectory(self, 'Selecionar Diretório')
        self.diretorioLabel.setText(f'Diretório do servidor: {diretorio}')

    def atualizarClientesConectados(self):
        if self.httpd is not None:
            clientes_conectados = len(MyHTTPRequestHandler.connected_clients)
            self.clientesLabel.setText(f'Clientes conectados: {clientes_conectados}')

    def sairAplicacao(self):
        self.pararServidor()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    servidor = AppServidor()
    servidor.show()
    sys.exit(app.exec_())
