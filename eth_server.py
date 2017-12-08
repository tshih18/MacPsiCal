import socket
import base64
from subprocess import *
import os
import time
import sys

def read_from_pi(TCP_PORT, BUFFER_SIZE):
    print "Starting socket connection"
    # create an INET, STREAMing socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to host and a port.
    # '' means socket is reachable by any address the machine happens to have
    serverSocket.bind(('', TCP_PORT))
    print "Socket hostname:", socket.gethostname()
    # become a server socket
    serverSocket.listen(1)
    print "Waiting for a connection..."
    # accept connections from outside
    (clientsocket, addr) = serverSocket.accept()
    print 'Connection address:', addr
    data = ""

    while 1:
        data += clientsocket.recv(BUFFER_SIZE)
        if not data: break
        if data[-3:] == 'END': break

    clientsocket.close()
    # print "Data:", data

    parameters = data.split(',')
    image = parameters[0]
    width = parameters[1]
    desiredWidth = parameters[2]
    spsi = parameters[3]
    ppmm = parameters[4]
    margin = parameters[5]
    pi_eth_ip = parameters[6]
    print "Parameters:", (width, desiredWidth, spsi, ppmm, margin)

    decoded_data = base64.b64decode(image)
    #print "Decoded data:", decoded_data

    # create writable image and write the decoding result
    image_result = open('image_decode.png', 'wb')
    image_result.write(decoded_data)

    return (width, desiredWidth, spsi, ppmm, margin, pi_eth_ip)

def psi_cal(width, desiredWidth, spsi, ppmm, margin):
    print "Running PSI Calibration Code..."
    start_time = time.time()
    offset_list = check_output(['python', 'saveme1.py', '--image', 'image_decode.png', '--width', width, '--desiredwidth', desiredWidth, '--spsi', spsi, '--ppmm', ppmm, '--margin', margin])
    print "PSI Calibration Code took", time.time() - start_time, "seconds"
    print "Output:", offset_list
    return offset_list

def send_to_pi(TCP_IP, TCP_PORT, offset_list):
    # format data to send to pi
    offset_list = offset_list[1:-2]
    offset_list += "END"
    print "Data to send:", offset_list

    # creating socket connection to send data
    print "Sending data back to PI..."
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Connecting to", TCP_IP, "at port", TCP_PORT
    clientSocket.connect((TCP_IP, TCP_PORT))
    start_time = time.time()
    clientSocket.send(offset_list)
    clientSocket.close()
    print "Successfully sent data in", time.time() - start_time, "seconds"

if __name__ == '__main__':
    TCP_PORT = 5050
    BUFFER_SIZE = 1024

    # Becomes server and gets the parameters and ip from pi
    (width, desiredWidth, spsi, ppmm, margin, pi_eth_ip) = read_from_pi(TCP_PORT, BUFFER_SIZE)
    # Run psi cal and get the values
    offset_list = psi_cal(width, desiredWidth, spsi, ppmm, margin)
    # Becomes client and sends the values back to the pi
    send_to_pi(pi_eth_ip, TCP_PORT, offset_list)
