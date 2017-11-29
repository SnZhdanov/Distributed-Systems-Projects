import sys
import os
import socket
import threading
import getopt
import time
import struct
from threading import Thread

def usage( script_name):
    print( 'Usage: python3' + script_name + '<client listening port>' + 'connect server port>')






def ftpListener():
    #wait for ftp requests. creates a thread to handle sending files. The threads are necessary,
    #so that multiple sends can happen.
    #block on accept

    while True:
        try:
            sock,addr = sockFTP.accept()
            print(">file request accepted")
            thread_ftpTime = threading.Thread(target = ftpSender, args = [sock])
            thread_ftpTime.start()
        except:
            break
    os._exit()

def ftpSender(sock):
    #thread that gets created when a file is ready to be sent.
    fileName = sock.recv(1024)
    fileName = fileName.decode()
    print(">Filename received: " + str(fileName))

    try:
        file_stat = os.stat(fileName)
        if file_stat.st_size:
            print(">File has a size")
            file = open( fileName, 'rb')
            file_size_bytes = struct.pack( '!L', file_stat.st_size)
            sock.send(file_size_bytes)
            print(">>file name found, sent file size, ready to send file bytes")
            while True:
                file_bytes = file.read( 1024)
                if file_bytes:
                    sock.send( file_bytes)
                else:
                    break
            print(">>finished sending file bytes")
            file.close()

        else:
            print("couldn't find file")
    except OSError:
        print("couldn't find file")
        print(fileName)
                

def fileRecv(msg_bytes):
    msg_bytes = msg_bytes.decode()
    msg_bytes = msg_bytes.split(', ')
    fileName = msg_bytes[0]
    senderPort = msg_bytes[1]

    #connect to the other end's ftp socket
    sockRecvFTP = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sockRecvFTP.connect(("localhost", int(senderPort)))

    sockRecvFTP.send(fileName.encode())
    print(">filename sent to other client")
    file_size_bytes = sockRecvFTP.recv( 4 )
    print("file size has been recieved")
    fsize = 0

    if file_size_bytes:
        file_size = struct.unpack('!L', file_size_bytes[:4])[0]
        fsize = file_size
        if file_size:
            file = open( fileName, 'wb')
            print(">>ready to write bytes")
            while True:
                file_bytes = sockRecvFTP.recv(1024)

                fsize = fsize-1024

                if file_bytes:
                    file.write( file_bytes)
                else:
                    break
                if( fsize <=0):
                    print(">>Finished writing file")
                    break
            print(">>Close file")
            file.close()
        else:
            print(' file does not exist or is empty')
    else:
        print(' file does not exist or is empty')
    sockRecvFTP.close()
            

class reciever( threading.Thread):
    def __init__(self,sock):
        threading.Thread.__init__(self)
        self.sock = sock
        
    def run(self):
        msg_bytes = ''
        while True:
            try:
                msg_bytes = self.sock.recv(1024)
                if msg_bytes:
                    strCheck = str(msg_bytes)
                    strCheck = strCheck[2:-1]
                    if('FTPrecv' in strCheck):
                        print(">starting ftpReciever")
                        thread_ftprecv = threading.Thread(target = fileRecv, args = [msg_bytes])
                        thread_ftprecv.start()
                    else:
                        print( msg_bytes.decode(), end='')
                else:
                    pass
            
            except:
                pass

if __name__== "__main__":
    # 2 is for the client's ftp port, 4 is the client's port

    sockText = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sockText.connect(("localhost", int(sys.argv[4])))

    sockFTP = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sockFTP.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sockFTP.bind(('', int(sys.argv[2])))
    sockFTP.listen(6)

    listener = threading.Thread( target=ftpListener)
    listener.start()

    
    name = ""
    print("what is your name?")

    name = sys.stdin.readline()
    name = name.strip('\n')
    sys.stdout.flush()

    try:
        message = str(name)
        message = message + ", " + str(sys.argv[2])
        sockText.send(message.encode())
    except:
        os._exit(0)
    
    
    Crecv = reciever(sockText)
    Crecv.start()
    time.sleep(.50)
    while True:
        print(" Enter an option ('m', 'f', 'x'): ")
        print(" (M)essage (send)")
        print(" (F)ile (requrest)")
        print(" e(X)it")
        message = ""
        Userinput = ""
        Userinput = sys.stdin.readline()

        if('m' in Userinput):
            print("Enter your message: ")
            message = sys.stdin.readline()
            if not message:
                break
            try:
                message = str(name) + ": " + str(message)
                sockText.send(message.encode())
            except:
                os._exit(0)

        elif('f' in Userinput):
            #sends the name of the user, the file requested, and then sends the code word sendFTPcode
            #to trigger the server to start a file request. Server will make a thread, split the string, and
            # figure out by the name, who is the intended user with the file. Sends back the socket info of that user
            print("Who owns the file?")
            reqUser = sys.stdin.readline()
            reqUser = reqUser.strip('\n')
            print("which file do you want?")
            reqFile = sys.stdin.readline()
            reqFile = reqFile.strip('\n')

            message = (str(reqUser) + ', ' + str(reqFile) + ', ' + 'sendFTPcode')
            sockText.send(message.encode())
            
        elif('x' in Userinput):
            os._exit(0)

        else:
            print("Please use the options given")

    


