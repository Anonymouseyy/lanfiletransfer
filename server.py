import PySimpleGUI as sg
import socket, sys, pickle, pyperclip

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

def handle_client(conn, addr):
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text(f'Server: {SERVER} Port: {PORT}', font=('Helvetica', 20))],
              [sg.Button('Exit', font=('Helvetica', 15)), sg.Button('Start', font=('Helvetica', 15)),
               sg.Button('Copy Server', font=('Helvetica', 15), key='server'), sg.Button('Copy Port', font=('Helvetica', 15), key='port')]]
    print(f'connected to {conn} {addr}')
    conn.close()


def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    conn, addr = server.accept()
    handle_client(conn, addr)


def home():
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text(f'Server: {SERVER} Port: {PORT}', font=('Helvetica', 20))],
              [sg.Button('Exit', font=('Helvetica', 15)), sg.Button('Start', font=('Helvetica', 15)),
               sg.Button('Copy Server', font=('Helvetica', 15), key='server'), sg.Button('Copy Port', font=('Helvetica', 15), key='port')]]

    window = sg.Window('File Transfer (Server)', layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            return
        
        if event == 'Start':
            window.close()
            start()
            return
        
        if event == 'server':
            pyperclip.copy(SERVER)
        
        if event == 'port':
            pyperclip.copy(PORT)
            
home()