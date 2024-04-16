import PySimpleGUI as sg
import helpers as h
import socket, sys, pickle, os


# Socket Variables
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
END_MESSAGE = 'END'
SIZE = 8192
ADDR = None


def transfer_win(client, addr):
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text(f'Connected to: IP: {addr[0]}  Port: {addr[1]}', font=('Helvetica', 10))],
              [sg.Text('File Destination: ', font=('Helvetica', 20)), sg.Push(), sg.Input('', font=('Helvetica', 20), key='dest'), sg.FolderBrowse(font=('Helvetica', 15))],
              [sg.ProgressBar(50, orientation='h', size=(92, 20), border_width=2, bar_color=('grey', 'lightgrey'), key='status')],
              [sg.Button('Exit', font=('Helvetica', 15)), sg.Push(), sg.Text('0/0', font=('Helvetica', 15), key='fraction')]]
    
    window = sg.Window('File Transfer (Client)', layout)
    write_file = None
    file_size = None
    count = None

    while True:
        event, values = window.read(timeout=1)
        msg = None
        try:
            client.send(h.pickle_msg('CONNECTED', SIZE))
            msg = client.recv(SIZE)
            while len(msg) < SIZE:
                msg += client.recv(SIZE-len(msg))
            msg = pickle.loads(msg)
        except socket.error as e:
            print(e)

        if msg == DISCONNECT_MESSAGE:
            window.close()
            client.close()
            break
        elif msg != 'OK':
            if write_file and file_size and count is not None:
                if msg == END_MESSAGE:
                    write_file.close()
                    write_file, file_size, count = None, None, None
                else:
                    if msg is None:
                        pass
                    else:
                        write_file.write(msg)
                        count += SIZE
                        if count > file_size:
                            count = file_size
                        window['status'].update(max=file_size, current_count=count)
                        window['fraction'].update(f'{h.convert_size(count)}/{h.convert_size(file_size)}')
            elif not os.path.isdir(values['dest']):
                client.send(h.pickle_msg('NO', SIZE))
                sg.popup_no_wait('Select Directory To Transfer To', keep_on_top=True)
            else:
                client.send(h.pickle_msg('OK', SIZE))
                client.send(h.pickle_msg('OK', SIZE))

                path = values['dest']
                write_file = open(f'{path}\\{msg}', 'wb')

                msg = client.recv(SIZE)
                while len(msg) < SIZE:
                    msg += client.recv(SIZE - len(msg))
                file_size = pickle.loads(msg)

                count = 0

        if event == sg.WIN_CLOSED or event == 'Exit':
            client.send(h.pickle_msg(DISCONNECT_MESSAGE, SIZE))
            window.close()
            client.close()
            sys.exit()

    start()


def start():
    global ADDR
    layout = [[sg.Text('Transfer Files', font=('Helvetica', 32))],
              [sg.Text('Server: ', font=('Helvetica', 20)), sg.Input('', font=('Helvetica', 20), key='server_in')],
              [sg.Text('Port: ', font=('Helvetica', 20)), sg.Push(), sg.Input('', font=('Helvetica', 20), key='port_in')],
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
                    ADDR = values['server_in'], int(values['port_in'])
                    client.connect(ADDR)
                    window.close()
                except:
                    sg.Popup('Check Server And Port Values And Check Server', keep_on_top=True)
                    client = None
            else:
                sg.Popup('Check Server And Port Values', keep_on_top=True)

        if client:
            transfer_win(client, ADDR)


start()
