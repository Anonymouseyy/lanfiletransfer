import PySimpleGUI as sg
import helpers as h
import socket, sys, pickle, pyperclip, os

HEADER = 64
PORT = 5050
SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
END_MESSAGE = 'END'


def handle_client(conn, addr):
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text(f'Connected to: IP: {addr[0]}  Port: {addr[1]}', font=('Helvetica', 10))],
              [sg.Text('File Select:', font=('Helvetica', 20)), sg.Push(), sg.Input('', font=('Helvetica', 20), key='file'), sg.FileBrowse(font=('Helvetica', 15))],
              [sg.Text('Folder Select:', font=('Helvetica', 20)), sg.Push(), sg.Input('', font=('Helvetica', 20), key='folder'), sg.FolderBrowse(font=('Helvetica', 15))],
              [sg.ProgressBar(50, orientation='h', size=(90, 20), border_width=2, bar_color=('grey', 'lightgrey'), key='status')],
              [sg.Button('Exit', font=('Helvetica', 15)), sg.Button('Send File', font=('Helvetica', 15), key='send_file'),
               sg.Button('Send Folder', font=('Helvetica', 15), key='send_folder'), sg.Push(), sg.Text('0/0', font=('Helvetica', 15), key='fraction')]]
    
    window = sg.Window('File Transfer (Server)', layout)
    file = None
    file_size = None
    count = None

    while True:
        event, values = window.read(timeout=1)
        msg = None
        try:
            if file is None and file_size is None and count is None:
                conn.send(h.pickle_msg('OK', SIZE))
            msg = pickle.loads(conn.recv(SIZE))
        except socket.error as e:
            print(e)
        
        if msg == DISCONNECT_MESSAGE:
            window.close()
            conn.close()
            sys.exit()

        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            conn.send(h.pickle_msg(DISCONNECT_MESSAGE, SIZE))
            conn.close()
            sys.exit()
        
        if event == 'send_file':
            if not os.path.exists(values['file']):
                sg.Popup('Not Valid File')
            elif file and file_size and count is not None:
                sg.Popup('Currently Send Files... Please Wait')
            else:
                filepath = values['file']
                file = open(filepath, 'rb')
                file_size = os.path.getsize(filepath)
                file_name = os.path.basename(filepath)

                conn.send(h.pickle_msg(file_name, SIZE))
                msg = pickle.loads(conn.recv(SIZE))
                count = 0

                if msg == 'NO':
                    file.close()
                    file, file_size, count = None, None, None

        if event == 'send_folder':
            if not os.path.isdir('folder'):
                sg.Popup('Not Valid Folder')

        if file and file_size and count is not None:
            if count == 0:
                conn.send(h.pickle_msg(file_size, SIZE))

            line = file.read(SIZE-50)
            conn.send(h.pickle_msg(line, SIZE))

            count += SIZE
            if count > file_size:
                count = file_size
            window['status'].update(max=file_size, current_count=count)
            window['fraction'].update(f'{h.convert_size(count)}/{h.convert_size(file_size)}')

            if count >= file_size:
                file.close()
                file, file_size, count = None, None, None
                conn.send(h.pickle_msg(END_MESSAGE, SIZE))


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
        
        if event == 'server':
            pyperclip.copy(SERVER)
        
        if event == 'port':
            pyperclip.copy(PORT)
            
home()
