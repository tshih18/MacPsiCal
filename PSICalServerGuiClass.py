from Tkinter import *
import socket
import base64
from subprocess import *
import os
import time
import sys

class MainW(Tk):
    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.parent = parent
        self.title("PSI Cal Server GUI")

        self.TCP_PORT = 5050
        self.BUFFER_SIZE = 1024

        # Initialize messages to display to user
        self.message = StringVar()
        self.message.set("Click to start server")

        # Initialize ip address variable
        self.display_mac_eth_ip = StringVar()
        self.mac_eth_ip = self.get_mac_ip()
        self.display_mac_eth_ip.set(self.mac_eth_ip)

        # Setup layout of GUI
        self.InitFrames()
        self.PlaceFrames()

        # Disable start button if no connection
        if self.mac_eth_ip == "N/A":
            self.message.set("Ethernet cable not connected to Pi")
            self.start_button.config(state=DISABLED)


    def InitFrames(self):
        self.instructions = Label(self, text="Please enter the IP address displayed below and click start before running PSI Calibration").pack()
        self.mac_ip = Label(self, textvariable=self.display_mac_eth_ip)
        self.button_frame = Frame(self, height=50, width=200)
        self.button_frame.pack_propagate(0) # don't shrink
        self.start_button = Button(self.button_frame, text="Start")
        self.start_button.config(command=self.run_script, anchor=W)
        self.reconnect_button = Button(self.button_frame, text="Reconnect")
        self.reconnect_button.config(command=lambda: self.get_mac_ip(True), anchor=E)
        self.feedback = Label(self, textvariable=self.message)

    def PlaceFrames(self):
        self.mac_ip.pack()
        self.button_frame.pack()
        self.start_button.pack()
        self.reconnect_button.pack()
        self.feedback.pack()

    # Becomes server and gets the parameters and ip from pi
    def read_from_pi(self, TCP_PORT, BUFFER_SIZE):
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

        # Organize data into variables
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

    # Run psi cal and get the values
    def psi_cal(self, width, desiredWidth, spsi, ppmm, margin):
        print("Running PSI Calibration Code...")
        start_time = time.time()
        offset_list = check_output(['python', 'saveme1.py', '--image', 'image_decode.png', '--width', width, '--desiredwidth', desiredWidth, '--spsi', spsi, '--ppmm', ppmm, '--margin', margin])
        print("PSI Calibration Code took", time.time() - start_time, "seconds")
        print("Output:", offset_list)
        return offset_list

    # Becomes client and sends the values back to the pi
    def send_to_pi(self, TCP_IP, TCP_PORT, offset_list):
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

    # Get mac's ethernet ip address
    def get_mac_ip(self, loaded=False):
        # Run command to list connected hardware ports
        self.output = check_output(['networksetup', '-listallhardwareports'])
        self.output = self.output[1:-1]
        self.output = self.output.split('\n\n')
        self.device = ""
        self.mac_eth_ip = ""

        # Grab the ethernet port number
        for port in self.output:
            port = port.split('\n')
            if "Ethernet" in port[0]:
                self.device = port[1].split(' ')[1]
                break

        try:
            # Get the ip address associated with the ethernet port number
            self.mac_eth_ip = check_output(['ipconfig', 'getifaddr', self.device])[:-1]
            self.message.set("Click to start server")
            print("Ethernet cable connected to Pi")

            # Display the ip and update GUI
            if loaded:
                self.display_mac_eth_ip.set(self.mac_eth_ip)
                self.start_button.config(state=NORMAL)
                self.update()

            return self.mac_eth_ip

        except Exception:
            print("Ethernet cable not connected to Pi")
            self.mac_eth_ip = "N/A"

            # Display N/A and update GUI
            if loaded:
                self.start_button.config(state=DISABLED)
                self.reconnect_button.config(state=NORMAL)
                self.display_mac_eth_ip.set(self.mac_eth_ip)
                self.message.set("Ethernet cable not connected to Pi")
                self.update()

            return self.mac_eth_ip

    # Runs the entire script when start is clicked
    def run_script(self):
        self.start_button.config(state=DISABLED)
        self.message.set("Server running... Now continue PSI calibration on the Pi")
        self.update()
        while True:
            (self.width, self.desiredWidth, self.spsi, self.ppmm, self.margin, self.pi_eth_ip) = self.read_from_pi(self.TCP_PORT, self.BUFFER_SIZE)
            self.offset_list = self.psi_cal(self.width, self.desiredWidth, self.spsi, self.ppmm, self.margin)
            self.send_to_pi(self.pi_eth_ip, self.TCP_PORT, self.offset_list)



if __name__ == "__main__":
    app = MainW(None)
    app.mainloop()
