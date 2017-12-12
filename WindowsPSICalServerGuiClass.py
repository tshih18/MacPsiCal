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

        # Initialize messages and ip to display
        self.message = StringVar()
        self.display_win_eth_ip = StringVar()

        # Setup layout of GUI
        self.InitFrames()
        self.PlaceFrames()

        # Get ip address and update GUI with connection status
        self.get_win_ip()

    def InitFrames(self):
        self.instructions = Label(self, text="Please enter the IP address displayed below and click start before running PSI Calibration")
        self.win_ip = Label(self, textvariable=self.display_win_eth_ip)

        self.set_ip_frame = Frame(self, height=50, width=200)
        self.set_win_ip_label = Label(self.set_ip_frame, text="Set Static IP:")
        self.enter_win_ip = Entry(self.set_ip_frame, width=12, validate="focusin")
        self.set_win_ip_button = Button(self.set_ip_frame, text="Set", command=self.set_win_ip)

        self.start_button = Button(self, text="Start")
        self.start_button.config(command=self.run_script, anchor=W)
        self.reconnect_button = Button(self, text="Reconnect")
        self.reconnect_button.config(command=lambda: self.get_win_ip(), anchor=E)
        self.feedback = Label(self, textvariable=self.message)

    def PlaceFrames(self):
        self.instructions.grid(row=0, column=0)
        self.win_ip.grid(row=1, column=0)

        self.set_ip_frame.grid(row=2, column=0)
        self.set_win_ip_label.grid(row=2, column=0)
        self.enter_win_ip.grid(row=2, column=1)
        self.set_win_ip_button.grid(row=2, column=3)

        self.start_button.grid(row=3, column=0)
        self.reconnect_button.grid(row=4, column=0)
        self.feedback.grid(row=5, column=0)

    # Becomes server and gets the parameters and ip from pi
    def read_from_pi(self, TCP_PORT, BUFFER_SIZE):
        print("Starting socket connection")
        # Create an INET, STREAMing socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to host and a port.
        # '' means socket is reachable by any address the machine happens to have
        serverSocket.bind(('', TCP_PORT))
        print("Socket hostname:", socket.gethostname())
        # Become a server socket
        serverSocket.listen(1)
        print("Waiting for a connection...")
        # Accept connections from outside
        (clientsocket, addr) = serverSocket.accept()
        print('Connection address:', addr)
        data = ""

        # Continue to read data until endstop is reached
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
        offset_list = offset_list[1:-3]
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

    def set_win_ip(self):
        return

    # Get windows's ethernet ip address
    def get_win_ip(self):
        output = check_output(['ipconfig'])
        output = output.split('\r\n')
        self.win_eth_ip = ""

        for (i,x) in enumerate(output):
            if 'Ethernet' in x:
                # i+2 to skip the '' and go to next index
                for (j,y) in enumerate(output[i+2:]):
                    if y == "": break
                    if "IPv4" in y:
                        y = y.split(": ")
                        self.win_eth_ip = y[1]

        # Successful Connection
        if self.win_eth_ip != "":
            # Update the message and button, and display the ip
            print("Ethernet cable connected to Pi")
            self.message.set("Click to start server")
            self.start_button.config(state=NORMAL)
            self.display_win_eth_ip.set(self.win_eth_ip)
            self.update()

        # Unsuccessful Connection
        else:
            print("Ethernet cable not connected to Pi")
            self.win_eth_ip = "N/A"
            self.message.set("Ethernet cable not connected to Pi")
            self.start_button.config(state=DISABLED)
            self.reconnect_button.config(state=NORMAL)
            self.display_win_eth_ip.set(self.win_eth_ip)

        return self.win_eth_ip

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
