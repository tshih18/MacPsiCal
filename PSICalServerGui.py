from Tkinter import *
import socket
import base64
from subprocess import *
import os
import time
import sys

def read_from_pi(TCP_PORT, BUFFER_SIZE):
    print("Starting socket connection")
    # create an INET, STREAMing socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to host and a port.
    # '' means socket is reachable by any address the machine happens to have
    serverSocket.bind(('', TCP_PORT))
    print("Socket hostname:", socket.gethostname())
    # become a server socket
    serverSocket.listen(1)
    print("Waiting for a connection...")
    # accept connections from outside
    (clientsocket, addr) = serverSocket.accept()
    print('Connection address:', addr)
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
    print("Parameters:", (width, desiredWidth, spsi, ppmm, margin))

    decoded_data = base64.b64decode(image)
    #print "Decoded data:", decoded_data

    # create writable image and write the decoding result
    image_result = open('image_decode.png', 'wb')
    image_result.write(decoded_data)

    return (width, desiredWidth, spsi, ppmm, margin, pi_eth_ip)

def psi_cal(width, desiredWidth, spsi, ppmm, margin):
    print("Running PSI Calibration Code...")
    start_time = time.time()
    offset_list = check_output(['python', 'saveme1.py', '--image', 'image_decode.png', '--width', width, '--desiredwidth', desiredWidth, '--spsi', spsi, '--ppmm', ppmm, '--margin', margin])
    print("PSI Calibration Code took", time.time() - start_time, "seconds")
    print("Output:", offset_list)
    return offset_list

def send_to_pi(TCP_IP, TCP_PORT, offset_list):
    # format data to send to pi
    offset_list = offset_list[1:-2]
    offset_list += "END"
    print("Data to send:", offset_list)

    # creating socket connection to send data
    print("Sending data back to PI...")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((TCP_IP, TCP_PORT))
    start_time = time.time()
    clientSocket.send(offset_list)
    clientSocket.close()
    print("Successfully sent data in", time.time() - start_time, "seconds")

def get_mac_ip(loaded=False):
    output = check_output(['networksetup', '-listallhardwareports'])
    output = output[1:-1]
    output = output.split('\n\n')
    device = ""
    mac_eth_ip = ""

    for port in output:
        port = port.split('\n')
        if "Ethernet" in port[0]:
            device = port[1].split(' ')[1]
            break

    try:
        mac_eth_ip = check_output(['ipconfig', 'getifaddr', device])[:-1]
        message.set("Click to start server")
        print("Ethernet cable connected to Pi")

        if loaded:
            display_mac_eth_ip.set(mac_eth_ip)
            start_button.config(state=NORMAL)
            update()

        return mac_eth_ip

    except Exception:
        print("Ethernet cable not connected to Pi")
        mac_eth_ip = "N/A"

        if loaded:
            start_button.config(state=DISABLED)
            reconnect_button.config(state=NORMAL)
            display_mac_eth_ip.set(mac_eth_ip)
            message.set("Ethernet cable not connected to Pi")
            update()

        return mac_eth_ip

def run_script():
    start_button.config(state=DISABLED)
    message.set("Server running... Now continue PSI calibration on the Pi")
    update()
    while True:
        (width, desiredWidth, spsi, ppmm, margin, pi_eth_ip) = read_from_pi(TCP_PORT, BUFFER_SIZE)
        offset_list = psi_cal(width, desiredWidth, spsi, ppmm, margin)
        send_to_pi(pi_eth_ip, TCP_PORT, offset_list)

def update_message_label(mes):
    message.set(mes)
    mainloop()


TCP_PORT = 5050
BUFFER_SIZE = 1024

root = Tk()
root.title("PSI Cal Server GUI")

# user messages
message = StringVar(root)
message.set("Click to start server")

# StringVar to display the mac's ethernet ip address
display_mac_eth_ip = StringVar(root)

# initialize widgets
instructions = Label(root, text="Please enter the IP address displayed below and click start before running PSI Calibration").pack()
mac_ip = Label(root, textvariable=display_mac_eth_ip)
button_frame = Frame(root, height=50, width=200)
button_frame.pack_propagate(0) # don't shrink
start_button = Button(button_frame, text="Start")
start_button.config(command=run_script, anchor=W)
reconnect_button = Button(button_frame, text="Reconnect")
reconnect_button.config(command=lambda: get_mac_ip(True), anchor=E)
feedback = Label(root, textvariable=message)

# get the mac's ethernet ip address
mac_eth_ip = get_mac_ip()
display_mac_eth_ip.set(mac_eth_ip)

# handle disabling buttons
if mac_eth_ip == "N/A":
    message.set("Ethernet cable not connected to Pi")
    start_button.config(state=DISABLED)

# place widgets
mac_ip.pack()
button_frame.pack()
start_button.pack()
reconnect_button.pack()
feedback.pack()

mainloop()
