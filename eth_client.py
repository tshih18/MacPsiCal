import socket
import cv2
import base64
import time
from tqdm import tqdm
from subprocess import check_output
import argparse
import re
import ast
import netifaces as ni

in_development = False

def send_to_computer(TCP_IP, TCP_PORT, pi_eth_ip, IMAGE_FILE, parameters):
    # Format and add endstop keyword
    parameters = parameters + ',' + pi_eth_ip + ',END'
    parameters = parameters.replace(" ", "")

    # Encode image in base64
    with open(IMAGE_FILE, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    # Create an INET, STREAMing socket and connect to TCP_IP on port TCP_PORT
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if in_development: print "Connecting to", TCP_IP, "at port", TCP_PORT
    clientSocket.connect((TCP_IP, TCP_PORT))

    # Handle sending data incrementally
    inc = 2048
    start = 0
    end = 2048
    intervals = (len(encoded_string)/inc)+1
    num_bytes = 0

    if in_development: print "Sending data to computer..."
    start_time = time.time()

    # send the image
    #num_bytes = clientSocket.send(encoded_string)
    for iters in tqdm(range(intervals)):
        num_bytes += clientSocket.send(encoded_string[start:end])
        start += inc
        end += inc
        if end > len(encoded_string):
            end = len(encoded_string)+1

    clientSocket.send(parameters)
    clientSocket.close()

    if in_development:
        print "Successfully sent data in", time.time() - start_time, "seconds"
        print "Image bytes sent:", num_bytes

def read_from_computer(TCP_PORT, BUFFER_SIZE):
    if in_development:
        host_ip = socket.gethostbyname(socket.gethostname())
        print "IP of hostname:", host_ip

    # Create an INET, STREAMing socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('', TCP_PORT))
    if in_development: print "Socket hostname:", socket.gethostname()
    serverSocket.listen(1)
    if in_development: print "Waiting for a connection..."
    (clientSocket, addr) = serverSocket.accept()
    if in_development: print "Connection Address:", addr

    # Read in data in chunks of BUFFER_SIZE
    data = ""
    while 1:
        data += clientSocket.recv(BUFFER_SIZE)
        if not data: break
        if data[-3:] == 'END': break

    clientSocket.close()
    if in_development: print "Data received:", data

    # Truncate endstop and format data
    data = data[:-3]
    data = "[" + data + "]"

    if in_development: print "Data passed back to GUI:", data
    if in_development: return data
    if not in_development: print data

# Get the pi's ethernet ip address
def get_pi_eth_ip():
    ni.ifaddresses('eth0')
    ip = str(ni.ifaddresses('eth0')[ni.AF_INET][0]['addr'])
    return ip

if __name__ == '__main__':
    start_time = time.time()

    # Parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True)
    ap.add_argument("-w", "--width", type=float, required=True)
    ap.add_argument("-dw", "--desiredwidth", type=float, required=True)
    ap.add_argument("-spsi", "--spsi", type=float, required=True)
    ap.add_argument("-p", "--ppmm", type=float, required=True)
    ap.add_argument("-m", "--margin", type=float, required=True)
    ap.add_argument("-ip", "--ip", required=True)
    args = vars(ap.parse_args())

    # Get/Set variables
    pi_eth_ip = get_pi_eth_ip()
    TCP_IP = args["ip"]
    TCP_PORT = 5050
    BUFFER_SIZE = 1024

    # Format parameters to send to computer
    parameters = "," + str(args["width"]) + "," + str(args["desiredwidth"]) + "," + str(args["spsi"]) + "," + str(args["ppmm"]) + "," + str(args["margin"])
    if in_development: print parameters

    # Becomes client and sends data to computer
    send_to_computer(TCP_IP, TCP_PORT, pi_eth_ip, args["image"], parameters)
    # Becomes server and listens for data back from computer
    read_from_computer(TCP_PORT, BUFFER_SIZE)

    if in_development: print "Runtime:", time.time() - start_time, "seconds"
