import sys
import os
import socket
import threading
import time
clientList = []


def usage( script_name ):
    print( 'Usage python3 ' + script_name + '< listening port number>')


def listener():
    while True:
        try:
            sock,addr = serversocket.accept()
            mes = sock.recv(1024).decode()
            mes = mes.split(', ')
            name = mes[0]
            cFTP = mes[1]
            clientList.append((sock,name,cFTP))
            thread_client = threading.Thread(target = sender, args = [sock])
            thread_client.start()
        except:
            break
    serversocket.close()
    os._exit(0)


def sender(sock):

    while True:
        try:
            msg_bytes = sock.recv(1024)
            print(msg_bytes.decode())
            
            if msg_bytes:
                strCheck = str(msg_bytes)
                strCheck = strCheck[2:-1]
                if('sendFTPcode' in strCheck):
                    ## start a new threat to handle file transfer request.
                    print(">: starting a file transfer")
                    thread_ftp = threading.Thread(target = fileTransfer, args = [msg_bytes, sock])
                    thread_ftp.start()

                    
                else:
                    for x in clientList:
                        if( x[0] != sock):
                            x[0].send(msg_bytes)
                            
            if not msg_bytes:
                for x in clientList:
                    if(x[0] == sock):
                        print("Client disconnected : " + x[1])
                        clientList.remove(x)
                break
        except:
            break
    

def fileTransfer(msg,sock):
    #thread that handles file transfer
    #when a message is sent over the main channel, it will signal a file transfer
    #this thread will start. It will then send the one that will send the packets
    #they will connect with the given port, the one recieving, will block on accept.
    #once the accept happens, it will create a thread on the recieving end to recieve packets.
    #The sender will then also create a thread to handle sending, it will wait for the accept.
    #this way, multiple file transfers can happen simultaniously.
    msg = msg.decode()
    msg = msg.split(', ')
    user = msg[0]
    fileName = msg[1]
    message = ''
    print(">:->I'm looking for the recipent's ftpPort : " + str(user))

    #figure out what the FTP port the user sending has.
    for x in clientList:
        print(x[1] + " = " + user)
        if(x[1] == user):
            #we found the port of the user. Now send that port number back through the requester's port
            senderPort = x[2]
            print(">:->:->:Found the recipent's ftpPort, sending ftpPort back")
            message = (str(fileName) + ', ' + senderPort + ', ' + 'FTPrecv')
            sock.send(message.encode())
            break
            
if __name__ == "__main__":
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    serversocket.bind(('', int(sys.argv[1])))

    serversocket.listen(6)

    listener = threading.Thread( target= listener)
    listener.start()

    
