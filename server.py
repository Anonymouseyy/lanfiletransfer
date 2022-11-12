import PySimpleGUI as sg
import helpers as h
import socket, sys, pickle, pyperclip, os

HEADER = 64
PORT = 5050
SIZE = 2048
SERVER = 'localhost'
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
    subfolders = None
    files = None
    cur_file = None
    subfolder_items =None
    layer = None
    count = None

    while True:
        event, values = window.read(timeout=1)
        msg = None
        try:
            if file is None and file_size is None and count is None:
                conn.send(h.pickle_msg('OK', SIZE))
            msg = conn.recv(SIZE)
            while len(msg) < SIZE:
                msg += conn.recv(SIZE - len(msg))
            msg = pickle.loads(msg)
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
                msg = conn.recv(SIZE)
                while len(msg) < SIZE:
                    msg += conn.recv(SIZE - len(msg))
                msg = pickle.loads(msg)
                count = 0
                layer = 0

                if msg == 'NO':
                    file.close()
                    file, file_size, count = None, None, None

        if event == 'send_folder':
            if not os.path.isdir(values['folder']):
                sg.Popup('Not Valid Folder')
            else:
                folderpath = values['folder']
                subfolders = []
                files = []
                dir_name = os.path.basename(folderpath)

                for item in os.listdir(folderpath):
                    x = os.path.join(folderpath, item)
                    if os.path.isdir(x):
                        subfolders.append(x)
                    else:
                        files.append(x)

                conn.send(h.pickle_msg(dir_name, SIZE))
                msg = conn.recv(SIZE)
                while len(msg) < SIZE:
                    msg += conn.recv(SIZE - len(msg))
                msg = pickle.loads(msg)
                subfolder_items = dict()
                count = 0

                if msg == 'NO':
                    subfolders, files, count, subfolder_items = None, None, None, None

        if file and file_size and count is not None:
            if count == 0:
                conn.send(h.pickle_msg(file_size, SIZE))

            line = file.read(SIZE-50)
            conn.send(h.pickle_msg(line, SIZE))

            count += SIZE - 50
            if count > file_size:
                count = file_size
            window['status'].update(max=file_size, current_count=count)
            window['fraction'].update(f'{h.convert_size(count)}/{h.convert_size(file_size)}')

            if count >= file_size:
                file.close()
                file, file_size, count = None, None, None
                conn.send(h.pickle_msg(END_MESSAGE, SIZE))

        if subfolders and files and count is not None:
            if count == 0:
                if layer == 0:
                    layer += 1
                    subfolder_items[f'{layer}folders'] = list()
                    subfolder_items[f'{layer}files'] = list()
                    subfolder = subfolders[0]
                    subfolders.pop(0)

                    for item in os.listdir(subfolder):
                        x = os.path.join(subfolder, item)
                        if os.path.isdir(x):
                            subfolder_items[f'{layer}folders'].append(x)
                        else:
                            subfolder_items[f'{layer}files'].append(x)

                    dir_name = os.path.basename(subfolder)
                    conn.send(h.pickle_msg(dir_name, SIZE))
                elif layer != 0 and subfolder_items[f'{layer}folders']:
                    pass
                if files:
                    filepath = files[0]
                    cur_file = open(filepath, 'rb')
                    file_size = os.path.getsize(filepath)
                    file_name = os.path.basename(filepath)

                    conn.send(h.pickle_msg(file_name, SIZE))
                    conn.send(h.pickle_msg(file_size, SIZE))
                else:
                    layer += 1
                    subfolder_items[f'{layer}folders'] = list()
                    subfolder_items[f'{layer}files'] = list()
                    subfolder = subfolders[0]

                    for item in os.listdir(subfolder):
                        x = os.path.join(subfolder, item)
                        if os.path.isdir(x):
                            subfolder_items[f'{layer}folders'].append(x)
                        else:
                            subfolder_items[f'{layer}files'].append(x)

                    dir_name = os.path.basename(subfolder)
                    conn.send(h.pickle_msg(dir_name, SIZE))

            line = cur_file.read(SIZE - 50)
            conn.send(h.pickle_msg(line, SIZE))

            count += SIZE - 50
            if count > file_size:
                count = file_size
            window['status'].update(max=file_size, current_count=count)
            window['fraction'].update(f'{h.convert_size(count)}/{h.convert_size(file_size)}')

            if count >= file_size:
                file.close()
                dir_name, count = None, None
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
