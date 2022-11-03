import PySimpleGUI as sg
import socket, sys, pickle, pyperclip, os

HEADER = 64
PORT = 5050
SIZE = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
END_MESSAGE = 'END'


def send_file(conn, filepath):
    pass


def handle_client(conn, addr):
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text('File Select:    ', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='file'), sg.FileBrowse(font=('Helvetica', 15))],
              [sg.Text('Folder Select:', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='folder'), sg.FolderBrowse(font=('Helvetica', 15))], 
              [sg.Text('0/0', font=('Helvetica', 15), key='fraction'), sg.StatusBar('Transfer Status', key='status')],
              [sg.Button('Exit', font=('Helvetica', 15)), sg.Button('Send File', font=('Helvetica', 15), key='send_file'),
               sg.Button('Send Folder', font=('Helvetica', 15), key='send_folder')]]
    
    window = sg.Window('File Transfer (Server)', layout)

    while True:
        event, values = window.read()
        try:
            conn.send(pickle.dumps('OK'))
            msg = pickle.loads(conn.recv(SIZE))
        except socket.error as e:
            print(e)
        
        if msg == DISCONNECT_MESSAGE:
            window.close()
            conn.send(pickle.dumps(DISCONNECT_MESSAGE))
            conn.close()
            sys.exit()

        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            conn.send(pickle.dumps(DISCONNECT_MESSAGE))
            conn.close()
            sys.exit()
        
        if event == 'send_file':
            if not os.DirEntry.is_file(values['file']):
                sg.Popup('Not Valid File')
            else:
                filepath = values['file']
                file = open(filepath, 'rb')
                file_size = os.path.getsize(filepath)
                file_name = os.path.basename(filepath)

                conn.send(pickle.dumps(file_name))
                msg = pickle.loads(conn.recv(SIZE))
                if msg == 'NO':
                    continue
                else:
                    conn.send(pickle.dumps(file_size))

                    line = file.read(SIZE)
                    count = 0

                    while line:
                        conn.send(line)
                        line = file.read(SIZE)
                        count += SIZE
                        if count > file_size:
                            count = file_size
                        window['status'].update(max=file_size, current_count=count)
                        window['fraction'].update(f'{count}/{file_size}')
            
                    conn.send(pickle.dumps(END_MESSAGE))

                    file.close()


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