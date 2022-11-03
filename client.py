import PySimpleGUI as sg
import socket, sys, pickle, os


# Socket Variables
HEADER = 64
PORT = None
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
END_MESSAGE = 'END'
SERVER = None
SIZE = 2048
ADDR = (SERVER, PORT)


def transfer_win(client):
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text('File Destination: ', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='dest'), sg.FolderBrowse(font=('Helvetica', 15))],
              [sg.Text('0/0', font=('Helvetica', 15), key='fraction'), sg.StatusBar('Transfer Status', key='status')],
              [sg.Button('Exit', font=('Helvetica', 15))]]
    
    window = sg.Window('File Transfer (Client)', layout)
    msg = None

    while True:
        event, values = window.read()
        try:
            client.send(pickle.dumps('CONNECTED'))
            msg = pickle.loads(client.recv(2048))
        except socket.error as e:
            print(e)

        if msg == DISCONNECT_MESSAGE:
            window.close()
            client.close()
            sys.exit()
        elif msg != 'OK':
            path = (values['dest'])
            if not os.DirEntry.isdir(path):
                client.send(pickle.dumps('NO'))
                sg.Popup('Select Directory To Transfer To', keep_on_top=True)
                continue
            else:
                client.send(pickle.dumps('OK'))

                write_file = open(f'{path}\\{msg}', 'wb')
                file_size = pickle.loads(client.recv(2048))

                line = pickle.loads(client.recv(SIZE))
                count = 0

                while line != END_MESSAGE:
                    write_file.write(line)
                    line = pickle.loads(client.recv(SIZE))
                    count += SIZE
                    if count > file_size:
                        count = file_size
                    window['status'].update(max=file_size, current_count=count)
                    window['fraction'].update(f'{count}/{file_size}')
            
                write_file.close()

        if event == sg.WIN_CLOSED or event == 'Exit':
            client.send(pickle.dumps(DISCONNECT_MESSAGE))
            window.close()
            client.close()
            sys.exit()


def start():
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text('Server: ', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='server_in')],
              [sg.Text('Port: ', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='port_in', pad=(35, 0))],
              [sg.Button('Exit', font=('Helvetica', 15)), sg.Button('Connect', font=('Helvetica', 15))]]
    
    window = sg.Window('File Transfer (Client)', layout)

    client = None
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
                except:
                    sg.Popup('Check Server And Port Values And Check Server', keep_on_top=True)
                    client = None
            else:
                sg.Popup('Check Server And Port Values', keep_on_top=True)

        if client:
            transfer_win(client)

start()