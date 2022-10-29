import PySimpleGUI as sg
import socket, sys, pickle


# Socket Variables
HEADER = 64
PORT = None
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = None
ADDR = (SERVER, PORT)


def transfer_win(client):
    pass


def start():
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text('Server: ', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='server_in')],
              [sg.Text('Port: ', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='port_in', pad=(35, 0))],
              [sg.Button('Exit', font=('Helvetica', 15)), sg.Button('Connect', font=('Helvetica', 15))]]
    
    window = sg.Window('File Transfer (Client)', layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            return
        
        
        if event == 'Connect':
            if values['server_in'] and values['port_in']:
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ADDR = SERVER, PORT = values['server_in'], int(values['port_in'])
                    client.connect(ADDR)
                    window.close()
                    transfer_win(client)
                    return
                except:
                    sg.Popup('Check Server And Port Values And Check Server', keep_on_top=True)
            else:
                sg.Popup('Check Server And Port Values', keep_on_top=True)


start()