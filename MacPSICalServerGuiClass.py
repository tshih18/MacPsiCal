#!/usr/bin/env python
from Tkinter import *
import socket
import base64
from subprocess import *
import time
import pexpect
import Pmw
import threading

class MainW(Tk):
    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.parent = parent
        self.title("PSI Calibration")
        self.geometry("400x130")
        self.TCP_PORT = 5050
        self.BUFFER_SIZE = 1024

        # Initialize messages to display to user
        self.message = StringVar()
        #self.message.set("Program is ready to start")

        # Initialize ip address variable
        self.display_mac_eth_ip = StringVar()

        # Setup layout of GUI
        self.InitFrames()
        self.PlaceFrames()

        # Get ip address and update GUI with connection status
        self.get_ip()

        # enable internet sharing on ethernet thunderbolt
        #'networksetup -setnetworkserviceenabled Thunderbolt\ Ethernet on'

        # Modify argument's mode
        child = pexpect.spawn('chmod a+x MacPSICalServerGuiClass.py')
        child.expect(pexpect.EOF)

    def InitFrames(self):
        # Initialize popup balloons
        self.balloon = Pmw.Balloon(self)

        # Help popop box
        self.help = Label(self, text="Help")
        help_title = "Setup Instructions\n"
        help_1 = "1. Connect ethernet cable to the computer and raspberry pi and click connect.\n"
        help_2 = "2. If this is your first time setting up or if you are switching to another computer, set a custom ip address.\n"
        help_3 = "3. On the raspberry pi, check the box to process on computer.\n"
        help_4 = "4. On the raspberry pi, go to the settings page and enter the ip address displayed on the computer.\n"
        help_5 = "5. Click start before running PSI Calibration on the raspberry pi.\n"
        help_6 = "6. After calibration is complete, click stop to stop the program."
        help_messages = help_title + help_1 + help_2 + help_3 + help_4 + help_5 + help_6
        self.balloon.bind(self.help, help_messages)

        # Display ip address
        self.ip = Label(self, textvariable=self.display_mac_eth_ip)

        # Set ip address
        self.set_ip_frame = Frame(self, height=50, width=200)
        self.set_ip_label = Label(self.set_ip_frame, text="Set Custom IP:")
        self.enter_ip = Entry(self.set_ip_frame, width=12, validate="focusin")
        self.set_ip_button = Button(self.set_ip_frame, text="Set", command=self.set_ip)

        # Buttons
        self.button_frame = Frame(self, height=50, width=200)
        self.connect_button = Button(self, text="Connect", width=7)
        self.connect_button.config(command=lambda: self.get_ip())
        self.start_button = Button(self.button_frame, text="Start")
        self.start_button.config(command=self.run_script, width=5)
        self.stop_button = Button(self.button_frame, text="Stop", state=DISABLED)
        self.stop_button.config(command=self.stop_script, width=5)

        self.feedback = Label(self, textvariable=self.message)

    def PlaceFrames(self):
        self.help.grid(row=0, column=0, sticky=E, padx=10)
        self.ip.grid(row=0, column=0)

        self.set_ip_frame.grid(row=1, column=0, padx=67)
        self.set_ip_label.grid(row=1, column=0)
        self.enter_ip.grid(row=1, column=1)
        self.set_ip_button.grid(row=1, column=2)

        self.connect_button.grid(row=2, column=0)
        self.button_frame.grid(row=3, column=0)
        self.start_button.grid(row=3, column=0)
        self.stop_button.grid(row=3, column=1)

        self.feedback.grid(row=4, column=0, padx=20)

    # Becomes server and gets the parameters and ip from pi
    def read_from_pi(self, TCP_PORT, BUFFER_SIZE):
        print("Starting socket connection")
        # Create an INET, STREAMing socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow the socket to use same PORT address
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set timeout for 3 seconds
        serverSocket.settimeout(3)
        # Bind the socket to host and a port.
        # '' means socket is reachable by any address the machine happens to have
        serverSocket.bind(('', TCP_PORT))
        print("Socket hostname:", socket.gethostname())

        # Stay in this loop while the thread attribute is true
        while self.thread.do_run:
            try:
                # Become a server socket
                serverSocket.listen(1)
                print("Waiting for a connection...")
                # Accept connections from outside
                (clientsocket, addr) = serverSocket.accept()
                print('Connection address:', addr)

                # When connection has been established and data is transferring, disable stop button
                self.stop_button.config(state=DISABLED)

                data = ""
                while 1:
                    # Put in try/except block to wait for resource to free up
                    try:
                        data += clientsocket.recv(BUFFER_SIZE)
                        if not data: break
                        if data[-3:] == 'END': break
                    except socket.error, e:
                        if str(e) == "[Errno 35] Resource temporarily unavailable":
                            time.sleep(0.1)
                        elif "[Errno 10035]" in str(e):
                            time.sleep(0.1)
                        else:
                            raise e

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

                # Create writable image and write the decoding result
                image_result = open('image_decode.png', 'wb')
                image_result.write(decoded_data)

                return (width, desiredWidth, spsi, ppmm, margin, pi_eth_ip)
            except socket.error, e:
                print "Error:", e


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
        # Format data to send to pi
        offset_list = offset_list[1:-2]
        offset_list += "END"
        print("Data to send:", offset_list)

        # Creating socket connection to send data
        print("Sending data back to PI...")
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Connecting to", TCP_IP, "at port", TCP_PORT
        clientSocket.connect((TCP_IP, TCP_PORT))
        start_time = time.time()
        clientSocket.send(offset_list)
        clientSocket.close()
        print("Successfully sent data in", time.time() - start_time, "seconds")

    # Get mac's ethernet ip address
    def get_ip(self):
        # Run command to list connected hardware ports
        self.output = check_output(['networksetup', '-listallhardwareports'])
        self.output = self.output[1:-1]
        self.output = self.output.split('\n\n')
        self.device = ""
        self.interfaceName = ""
        self.mac_eth_ip = ""

        # Grab the ethernet port number
        for port in self.output:
            port = port.split('\n')
            # Let it check for thunderbolt or usb connection
            if "Thunderbolt Ethernet" in port[0] or " LAN" in port[0]:
                self.interfaceName = port[0].split(': ')[1]
                self.device = port[1].split(' ')[1]
                break

        # Successful Connection
        try:
            # Get the ip address associated with the ethernet port number
            self.mac_eth_ip = check_output(['ipconfig', 'getifaddr', self.device])[:-1]
            print("Ethernet cable connected to Pi")

            # Update message and button, and display the ip
            self.message.set("Program is ready to start")
            self.start_button.config(state=NORMAL)
            self.set_ip_button.config(state=NORMAL)
            self.enter_ip.config(state=NORMAL)
            self.display_mac_eth_ip.set("My IP: " + self.mac_eth_ip)
            self.update()

            return self.mac_eth_ip

        # Unsuccessful Connection
        except Exception:
            print("Ethernet cable not connected to Pi")
            self.mac_eth_ip = "N/A"

            # Update message and buttons, and display N/A ip
            self.message.set("Ethernet cable not connected to Pi")
            self.start_button.config(state=DISABLED)
            self.set_ip_button.config(state=DISABLED)
            self.enter_ip.config(state=DISABLED)
            self.connect_button.config(state=NORMAL)
            self.display_mac_eth_ip.set("My IP: " + self.mac_eth_ip)
            self.update()

            return self.mac_eth_ip


    # Manually set the ip address
    def set_ip(self):
        self.interfaceName = self.interfaceName.replace(' ', '\ ')
        cmd = 'networksetup -setmanual ' + self.interfaceName + ' ' + self.enter_ip.get() + ' 255.255.255.0 8.8.8.8'
        child = pexpect.spawn(cmd)
        child.expect(pexpect.EOF)
        print "Set ip address to", self.enter_ip.get()
        self.interfaceName = self.interfaceName.replace('\ ', '')

        # Display new ip address
        self.set_ip_button.config(state=DISABLED)
        start_time = time.time()
        while self.get_ip() == "N/A":
            if time.time() - start_time > 3:
                self.message.set("Unable to set Ip, make sure Ethernet cable is connected")
                self.update()
                break
            self.get_ip()
        self.set_ip_button.config(state=NORMAL)

    # Runs the entire script when start is clicked
    def run_script(self):
        self.start_button.config(state=DISABLED)
        self.enter_ip.config(state=DISABLED)
        self.set_ip_button.config(state=DISABLED)
        self.connect_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.message.set("Program running... continue PSI calibration on the Pi")
        self.update()

        # Use a thread to run process in background to prevent Tkinter gui from freezing
        self.thread = threading.Thread(name="Read", target=self.run)
        # Set thread as daemon so thread is terminated when main thread ends
        self.thread.daemon = True
        self.thread.start()
        self.thread.do_run = True

    # Thread that runs server
    def run(self):
        self.currThread = threading.currentThread()
        while getattr(self.currThread, "do_run", True):
            try:
                (self.width, self.desiredWidth, self.spsi, self.ppmm, self.margin, self.pi_eth_ip) = self.read_from_pi(self.TCP_PORT, self.BUFFER_SIZE)
            except TypeError, e:
                print "Error:", e
                break
            self.offset_list = self.psi_cal(self.width, self.desiredWidth, self.spsi, self.ppmm, self.margin)
            self.send_to_pi(self.pi_eth_ip, self.TCP_PORT , self.offset_list)

            self.stop_button.config(state=NORMAL)

    # Stops the thread process when stop is clicked
    def stop_script(self):
        self.message.set("Stopping server...")
        self.update()
        # Toggle the buttons
        self.stop_button.config(state=DISABLED)
        self.connect_button.config(state=NORMAL)
        # Set the thread attribute to False to signal stop
        self.thread.do_run = False
        # Join thread with main thread to end thread
        threading.Thread.join(self.thread, 1)
        self.message.set("Stopped server")
        self.update()



if __name__ == "__main__":
    app = MainW(None)
    app.mainloop()
