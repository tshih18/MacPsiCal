#!/usr/bin/python

import os
from Tkinter import *
from subprocess import *
import commands
import smbus
import time
import struct
import cv2
import camera
import ast
import pexpect

class Header_Frame(Frame):

    def __init__(self,parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.config(width=800, height = 80)

        self.Title = Label(self, text="PSI Calibration",font=("Helvetica",24))
        self.Title.grid(row=0, column=0, sticky=W)

class Center_Frame(Frame):

    def __init__(self, parent,CalFields=None, IpField=None):
        #Frame.__init__(self,parent,bg="BLUE")
        Frame.__init__(self, parent)
        self.parent = parent
        self.config(width=400, height=400)
        self.initNumberPad()
        self.CalFields = CalFields
        self.IpField = IpField

    def initNumberPad(self):
        #Init the Buttons
        self.One = Button(self, text='1',height = 4, width = 5, command= lambda: self.numClick('1'))
        self.Two = Button(self, text='2',height = 4, width = 5, command=lambda: self.numClick('2'))
        self.Three = Button(self, text='3',height = 4, width = 5, command=lambda: self.numClick('3'))
        self.Four = Button(self, text='4',height = 4, width = 5, command=lambda: self.numClick('4'))
        self.Five = Button(self, text='5',height = 4, width = 5, command=lambda: self.numClick('5'))
        self.Six = Button(self, text='6',height = 4, width = 5, command=lambda: self.numClick('6'))
        self.Seven = Button(self, text ='7',height = 4, width = 5, command=lambda: self.numClick('7'))
        self.Eight = Button(self, text='8',height = 4, width = 5, command=lambda: self.numClick('8'))
        self.Nine = Button(self, text='9',height = 4, width = 5, command=lambda: self.numClick('9'))
        self.Zero = Button(self, text='0',height = 4, width = 5, command=lambda: self.numClick('0'))
        self.Decimal = Button(self, text='.',height = 4, width = 5, command=lambda: self.numClick('.'))
        self.Backspace = Button(self, text='del',height = 4, width = 5,command=lambda: self.numClick('d'))

        #Space the Buttons
        xspace=0
        # Starting Row and Column
        i = 3
        j= 1
        # Spacers for looks
        self.Space1 = Label(self, text=".", font=("Ariel", 1))
        self.Space2 = Label(self, text=".", font=("Ariel", 1))
        self.Space3 = Label(self, text=".", font=("Ariel", 1))
        self.Space1.grid(row=0,column=0,columnspan=1,padx=40,sticky=W)
        self.Space1.grid(row=1,column=0,columnspan=1,padx=40,sticky=W)
        self.Space1.grid(row=2,column=0,columnspan=1,padx=40,sticky=W)

        #Place the Buttons
        self.One.grid(row=i, column=j, padx=xspace)
        self.Two.grid(row=i, column=j+1, padx=xspace)
        self.Three.grid(row=i, column=j+2, padx=xspace)
        self.Four.grid(row=i+1, column=j, padx=xspace)
        self.Five.grid(row=i+1, column=j+1, padx=xspace)
        self.Six.grid(row=i+1, column=j+2, padx=xspace)
        self.Seven.grid(row=i+2,column=j, padx=xspace)
        self.Eight.grid(row=i+2,column=j+1, padx=xspace)
        self.Nine.grid(row=i+2,column=j+2, padx=xspace)
        self.Zero.grid(row=i+3,column=j, padx=xspace)
        self.Decimal.grid(row=i+3,column=j+1, padx=xspace)
        self.Backspace.grid(row=i+3,column=j+2, padx=xspace)

    def numClick(self,c):

        if self.CalFields is not None:
            if self.parent.focus_get() == self.CalFields[0]:
                if c == 'd':
                    self.CalFields[0].delete(len(self.CalFields[0].get())-1,END)
                else:
                    self.CalFields[0].insert(END,c)

            elif self.parent.focus_get() == self.CalFields[1]:
                if c == 'd':
                    self.CalFields[1].delete(len(self.CalFields[1].get())-1,END)
                else:
                    self.CalFields[1].insert(END,c)

            elif self.parent.focus_get() == self.CalFields[2]:
                if c == 'd':
                    self.CalFields[2].delete(len(self.CalFields[2].get())-1,END)
                else:
                    self.CalFields[2].insert(END,c)

            elif self.parent.focus_get() == self.CalFields[3]:
                if c == 'd':
                    self.CalFields[3].delete(len(self.CalFields[3].get())-1,END)
                else:
                    self.CalFields[3].insert(END,c)
            elif self.parent.focus_get() == self.CalFields[4]:
                if c == 'd':
                    self.CalFields[4].delete(len(self.CalFields[4].get())-1,END)
                else:
                    self.CalFields[4].insert(END,c)

        if self.IpField is not None:
            if self.parent.focus_get() == self.IpField:
                if c == 'd':
                    self.IpField.delete(len(self.IpField.get())-1,END)
                else:
                    self.IpField.insert(END,c)


class Left_Frame(Frame):

    def __init__(self, parent):
        #Frame.__init__(self, parent,bg="GREEN")
        Frame.__init__(self, parent)
        self.parent = parent
        self.config(width=200, height=400)

        self.BarreltoCal = StringVar(self)
        self.ToggleClean = IntVar(self)
        self.ToggleProcess = IntVar(self)


        self.InitWidgets()
        self.PlaceWidgets()

    def InitWidgets(self):
        #Label/Menu for Choosing Barrel
        self.SelectBarrel = OptionMenu(self, self.BarreltoCal, "   1  ", "   2  ", "   3  ", "   4  ", "   5  ", "   6  ", "   7  ", "   8  ",command=self.populateFields)
        self.ChooseBarrel = Label(self, text="Choose Barrel:",font=("Helvetica",14))
        self.SelectBarrel.config(width=6,height=2)

        #Labels for fields
        self.Pressure_Label = Label(self, text="Pressure:")
        self.Speed_Label = Label(self, text="Speed:")
        self.Width_Label = Label(self, text="Width:")
        self.Error_Label = Label(self, text="Error:")
        self.RefWidth_Label = Label(self, text="Reference Object Width:")
        self.Clean_Label = Label(self, text="Enable Tip Cleaning:")
        self.Process_Label = Label(self, text="Process on Computer:")

        #Entry for fields
        self.Pressure_cal_field = Entry(self, width= 10, validate="focusin",validatecommand=self.donothing)
        self.Speed_cal_field = Entry(self, width= 10, validate="focusin",validatecommand=self.donothing)
        self.Width_cal_field = Entry(self, width =10, validate="focusin",validatecommand=self.donothing)
        self.Error_cal_field = Entry(self, width=10, validate="focusin",validatecommand=self.donothing)
        self.RefWidth_field = Entry(self, width=10,validate="focusin",validatecommand=self.donothing)
        self.Cal_field_list = [self.Pressure_cal_field, self.Speed_cal_field, self.Width_cal_field, self.Error_cal_field,self.RefWidth_field]

        #Option Boxes
        self.CleanBox = Checkbutton(self, variable=self.ToggleClean)
        self.ProcessBox = Checkbutton(self, variable=self.ToggleProcess)

        self.Process_Settings = Button(self, text="Settings", command=self.Process_Computer_Settings)


    def PlaceWidgets(self):
        #Label/Menu forChoosing Barrel
        self.SelectBarrel.grid(row=0, column=1,pady=10, sticky=NW)
        self.ChooseBarrel.grid(row=0, column=0,pady=15, sticky=NW)

        #Space the fields and entry by this yspace
        yspace = 15
        #Place fields
        self.Pressure_Label.grid(row=2, column=0,pady=yspace, sticky=E)
        self.Speed_Label.grid(row=3, column=0,pady=yspace, sticky=E)
        self.Width_Label.grid(row=4, column=0,pady=yspace, sticky=E)
        self.Error_Label.grid(row=5, column=0,pady=yspace, sticky=E)
        self.RefWidth_Label.grid(row=6, column=0,pady=yspace, sticky=E)
        self.Clean_Label.grid(row=7, column=0,pady=yspace, sticky=E)
        self.Process_Label.grid(row=8, column=0, pady=yspace, sticky=E)

        #Place Entries
        self.Pressure_cal_field.grid(row=2, column=1,pady=yspace, sticky=W)
        self.Speed_cal_field.grid(row=3, column=1,pady=yspace, sticky=W)
        self.Width_cal_field.grid(row=4, column=1,pady=yspace, sticky=W)
        self.Error_cal_field.grid(row=5, column=1,pady=yspace, sticky=W)
        self.RefWidth_field.grid(row=6, column=1,pady=yspace, sticky=W)

        #Place Option Boxes
        self.CleanBox.grid(row=7, column=1, sticky=W)
        self.ProcessBox.grid(row=8, column=1, sticky=W)

        self.Process_Settings.grid(row=8, column=1, padx=25, sticky=E)

    def getFloat(self,data, index):
        bytess = data[index*4:(index+1)*4]
        return struct.unpack('f',"".join(map(chr,bytess)))[0]

    def populateFields(self,Barrel_select):
        #Clear any previous values
        self.Pressure_cal_field.delete(0,END)
        self.Speed_cal_field.delete(0,END)
        self.Width_cal_field.delete(0,END)
        self.Error_cal_field.delete(0,END)
        self.RefWidth_field.delete(0,END)
        #Tell Marlin what Barrel we are using
        self.parent.bus.write_byte(self.parent.address, int(Barrel_select))
        #Read in the Defaults
        data = self.parent.bus.read_i2c_block_data(self.parent.address, int(Barrel_select));
        #data = self.parent.bus.read_i2c_block_data(self.parent.address);
        pressure = round(self.getFloat(data, 0), 1);
        width = round(self.getFloat(data, 1) , 3);
        speed = round(self.getFloat(data, 2), 1);
        #Update the Entry Fields
        self.Pressure_cal_field.insert(0,str(pressure))
        self.Width_cal_field.insert(0,str(width))
        self.Speed_cal_field.insert(0,str(speed))
        self.Error_cal_field.insert(0, '3.0')
        self.RefWidth_field.insert(0,'17.9')

        return

    def Process_Computer_Settings(self):
        # Initialize frames
        self.comp_process_settings = Toplevel(self)
        self.comp_process_settings.geometry("800x480")
        self.back_button = Button(self.comp_process_settings, text="Back", command=self.exit_settings)
        self.title = Label(self.comp_process_settings, text="Configure Pi's IP Address", height=2)
        self.title.config(font=("Helvetica", 15))
        self.message = Label(self.comp_process_settings, text="Enter the IP address displayed on your computer. The Pi will need to restart to configure it's IP address")
        self.IpFrame = Frame(self.comp_process_settings)
        self.IpLabel = Label(self.IpFrame, text="Computer IP:")
        self.IpField = Entry(self.IpFrame, width= 15, validate="focusin")
        self.SetIp = Button(self.IpFrame, text="Configure/Reboot", command=self.configure_ip)
        self.NumPad = Center_Frame(self.comp_process_settings, IpField=self.IpField)


        # Place frames
        self.back_button.grid(row=0, column=0, sticky=W, padx=15, pady=15)
        self.title.grid(row=0, column=0, sticky=E, padx=280)
        self.message.grid(row=1, column=0, padx=40)
        self.IpFrame.grid(row=2, column=0, padx=100)
        self.IpLabel.grid(row=2, column=0)
        self.IpField.grid(row=2, column=1)
        self.SetIp.grid(row=2, column=2)
        self.NumPad.grid(row=3, column=0, sticky=W+E+N+S, padx=210)

        # Check comp_ip.txt for ip and put that ip in entry field
        if os.path.isfile("comp_ip.txt"):
            with open("comp_ip.txt", "r") as comp_ip_file:
                for ip in comp_ip_file:
                    if ip != "":
                        self.IpField.insert(END, ip)


    # Saves the computer's ip address and sets a compatible static ip for the pi
    def configure_ip(self):
        comp_ip = self.IpField.get()

        # Save computer's ip to a text file
        with open("comp_ip.txt", "w") as comp_ip_file:
            comp_ip_file.write(comp_ip)
            comp_ip_file.close()

        # Configure pi's ip
        hasInterface = False
        lines = []
        with open("/etc/dhcpcd.conf", "r") as f:

            for line in f:
                if re.match(r"\binterface eth0\b", line):
                    hasInterface = True
                lines.append(line)
            f.close()

        begin_comp_ip = comp_ip.split(".")[:-1]
        begin_comp_ip = ".".join(begin_comp_ip)
        new_ip = begin_comp_ip + ".115"
        new_route = begin_comp_ip + ".1"

        # Find regex that matches the lines and delete them
        # Then append them to end of file
        '''
        with open("/etc/dhcpcd.conf", "w") as f:
            for line in lines:
                if re.match(r"interface eth0", line):
                    interface = "interface eth0\n"
                    continue
                if re.match(r"static ip_address", line):
                    static_ip = "static ip_address=" + new_ip + "/24\n"
                    continue
                elif re.match(r"static routers", line):
                    static_routers = "static routers=" + new_route + "\n"
                    continue
                elif re.match(r"static domain_name_servers", line):
                    static_domain = "static domain_name_servers=8.8.8.8 8.8.4.4\n"
                    continue
                f.write(line)

            f.write(interface + static_ip + static_routers + static_domain)
            f.close()
        '''


        # If the file does not have 'interface eth0' append everything to end
        if not hasInterface:
            with open("/etc/dhcpcd.conf", "a") as f:
                interface = "interface eth0"
                ip = "\nstatic ip_address=" + new_ip + "/24\n"
                route = "static routers=" + new_route + "\n"
                server = "static domain_name_server=8.8.8.8 8.8.4.4\n"
                f.write(interface + ip + route + server)
                f.close()
        # If file already has 'interface eth0' modify that line
        else:
            with open("/etc/dhcpcd.conf", "w") as f:
                for line in lines:
                    if re.match(r"\bstatic ip_address", line):
                        line = "static ip_address=" + new_ip + "/24\n"
                    elif re.match(r"\bstatic routers", line):
                        line = "static routers=" + new_route + "\n"
                    elif re.match(r"\bstatic domain_name_servers", line):
                        line = "static domain_name_servers=8.8.8.8 8.8.4.4\n"
                    f.write(line)
                f.close()

        # Reboot pi
        #child = pexpect.spawn("sudo reboot")
        #child.expect(pexpect.EOF)

    # Close window when back button is clicked
    def exit_settings(self):
        self.comp_process_settings.destroy()


    def donothing(self):
        return True


class Right_Frame(Frame):

    def __init__(self, parent, CalFields, ToggleClean):
        #Frame.__init__(self, parent,bg="RED")
        Frame.__init__(self, parent)
        self.parent = parent
        self.config(width=200, height=400)
        self.CalFields = CalFields
        self.ToggleClean = ToggleClean
        #Init Camera
        self.camera_port = 0
        for i in range(5):
            cap=cv2.VideoCapture(i)

            if cap.isOpened():
                self.camera_port = i
                cap.release()
                print("succesful port: " + str(self.camera_port))
                break

        self.ramp_frames = 5
        self.images_to_take = 1
        #Delete previous image
        if os.path.isfile("/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png"):
            os.remove("/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png")
        #Delete previous image
        if os.path.isfile("/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_junk1.png"):
            os.remove("/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_junk1.png")
        #self.Esaac = camera.CV_Camera(self.camera_port,self.ramp_frames)
        #self.SelectedVar = IntVar()
        self.initButtons()

    def initButtons(self):
        #Declare Buttons
        self.StartButton = Button(self, text="Start",bd=2, height=1, width=9, command=self.StartCal)
        self.ReprintButton = Button(self, text="Reprint",bd=2,state=DISABLED, height=1,width=9, command=self.Reprint)
        '''
        self.OffloadCheckButton = Checkbutton(self, text="Process on computer", variable=self.SelectedVar, command=self.OffloadCal)
        self.IpLabel = Label(self, text="Computer IP:")
        self.IpField = Entry(self, width= 15, state=DISABLED, validate="focusin")
        '''
        self.ContinueButton = Button(self, text="Continue",bd=2,state=DISABLED,height=1, width=9, command=self.ContinueCal)
        self.CancelButton = Button(self, text="Cancel",bd=2,state=DISABLED,height=1, width=9, command=self.CancelProcess)
        self.CloseButton = Button(self, text="Close to Home", height=1, width=11, command=self.parent.destroy)
        #Place Buttons
        self.StartButton.grid(row=0,column=0,padx=60,pady=10)
        self.ReprintButton.grid(row=1, column=0, padx=60,pady=10)
        '''
        self.OffloadCheckButton.grid(row=2, column=0, padx=60)
        self.IpLabel.grid(row=3, column=0)
        self.IpField.grid(row=4, column=0, columnspan=1)
        '''
        self.ContinueButton.grid(row=5,column=0,padx=60,pady=10)
        self.CancelButton.grid(row=6, column=0,padx=60,pady=10)
        self.CloseButton.grid(row=7,column=0,pady=40,sticky=S)
    def CancelProcess(self):
        self.StartButton.config(state=NORMAL)
        self.ContinueButton.config(state=DISABLED)
        self.ReprintButton.config(state=DISABLED)
        self.CloseButton.config(state=DISABLED)
        self.CancelButton.config(state=DISABLED)
        successfulWrite = 0
        while not successfulWrite:
            try:
                self.parent.bus.write_byte(self.parent.address, 27)
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
        successfulWrite = 0
        time.sleep(0.5)
        while not successfulWrite:
            try:
            #self.parent.bus.write_byte(self.parent.address, 21)
            #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                self.parent.bus.write_byte(self.parent.address, 25) #Send Success flag
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
        #self.parent.bus.write_byte(self.parent.address, 25) #Send Success flag
        successfulWrite = 0
        time.sleep(0.5)
        while not successfulWrite:
            try:
            #self.parent.bus.write_byte(self.parent.address, 21)
            #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                self.parent.bus.write_byte(self.parent.address, 21) #Send Success flag
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
        successfulWrite = 0
        time.sleep(0.5)
        while not successfulWrite:
            try:
            #self.parent.bus.write_byte(self.parent.address, 21)
            #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                self.parent.bus.write_byte(self.parent.address, 21) #Send Success flag
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
    def StartCal(self):
    #This is the function binded to the Start Button
        #Get Values from Fields
        self.pressure = float(self.CalFields[0].get())
        self.width = float(self.CalFields[2].get())
        self.speed = float(self.CalFields[1].get())
        self.error = float(self.CalFields[3].get())
        self.RefWidth = float(self.CalFields[4].get())

        with open("comp_ip.txt", "r") as f:
            for line in f:
                self.ip = line

        #Send Values and Start Command to Marlin
        i2c_buf = []
        i2c_buf.extend(bytearray(struct.pack('b',self.ToggleClean.get())))
        i2c_buf.extend(bytearray(struct.pack('f', self.pressure)))
        i2c_buf.extend(bytearray(struct.pack('f', self.width)))
        i2c_buf.extend(bytearray(struct.pack('f', self.speed)))
        i2c_buf.extend(bytearray(struct.pack('f', self.error)))

        self.parent.bus.write_i2c_block_data(self.parent.address, 15, i2c_buf)
        #Marlin should draw a line then move out the way waiting for dime
        #Place the dime then hit continue, however if line is bad, reprint
        self.ContinueButton.config(state=NORMAL)
        self.ReprintButton.config(state=NORMAL)
        self.CancelButton.config(state=NORMAL)
        self.StartButton.config(state=DISABLED)
        self.CloseButton.config(state=DISABLED)
    def Reprint(self):
##        if self.ToggleClean:
##            print(self.ToggleClean)
##            print("clean each cycle")
    #If first line was bad, reprint
        #Get Values from Fields
        self.pressure = float(self.CalFields[0].get())
        self.width = float(self.CalFields[2].get())
        self.speed = float(self.CalFields[1].get())
        self.error = float(self.CalFields[3].get())
        #Send Values and Start Command to Marlin
        i2c_buf = []
        i2c_buf.extend(bytearray(struct.pack('b',self.ToggleClean.get())))

        i2c_buf.extend(bytearray(struct.pack('f', self.pressure)))
        i2c_buf.extend(bytearray(struct.pack('f', self.width)))
        i2c_buf.extend(bytearray(struct.pack('f', self.speed)))
        i2c_buf.extend(bytearray(struct.pack('f', self.error)))

        self.parent.bus.write_i2c_block_data(self.parent.address, 15, i2c_buf)
        successfulWrite = 0
        while not successfulWrite:
            try:
                self.parent.bus.write_byte(self.parent.address, 21)
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
        #self.parent.bus.write_byte(self.parent.address,21)


    def ContinueCal(self):
    #This is the function binded to the Continue Button
        #Tell Marlin first line was good
        offset_list = []
        successfulWrite = 0
        while not successfulWrite:
            try:
                self.parent.bus.write_byte(self.parent.address, 27)
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
        #self.parent.bus.write_byte(self.parent.address,27)
        #Tell Marlin Dime is placed
        successfulWrite = 0
        while not successfulWrite:
            try:
                self.parent.bus.write_byte(self.parent.address, 21)
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
        #self.parent.bus.write_byte(self.parent.address,21)
        #Send 9 to ask Marlin if in position for picture
        takePicture = False
        while not takePicture:
            successfulWrite = 0
            while not successfulWrite:
                try:
                    self.parent.bus.write_byte(self.parent.address, 9)
                    successfulWrite = 1
                except Exception as e:
                    print('I2C bus was busy. Trying again.')
                    time.sleep(0.5)
            time.sleep(.1)
            #Return Marlins answer if it's ready
            successfulRead = 0
            while not successfulRead:
                try:
                    takePicture = self.parent.bus.read_byte(self.parent.address)
                    successfulRead = 1
                except Exception as e:
                    print('I2C bus was busy. Trying again.')
                    time.sleep(0.5)
            time.sleep(1)
        #Picture is ready to be taken
        #self.Esaac.camera = cv2.VideoCapture(self.camera_port)
        self.Esaac = camera.CV_Camera(self.camera_port,self.ramp_frames)
        while(not self.Esaac.get_ximages(self.images_to_take,"PSI")):
                self.Esaac.get_ximages(self.images_to_take,"PSI")
        #Process the picture. offset_list has four values, [bool,float,float,float] -> [success,new_pressure,pixeltomm,meas_Width]
        #offset_list = check_output(['python2' ,'mul_proc_measure_psi_cal_pi.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,'17.9' ,'--desiredwidth' ,str(self.width),'--spsi',str(self.pressure),'--ppmm', '0'])
        ##offset_list = check_output(['/home/pi/Desktop/Code/SPI_mar30/mul_proc_measure_psi_cal_pi','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,'17.9' ,'--desiredwidth' ,str(self.width),'--spsi',str(self.pressure)])
        '''
        offset_list = check_output(['python2' ,'saveme1.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,str(self.RefWidth) ,'--desiredwidth' ,str(self.width),'--spsi',str(self.pressure),'--ppmm', '0','--margin',str(self.error)])
        '''
        print "RUNNING CODE..."
        #offset_list = check_output(['python2', 'eth_client.py', '--image', '/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png', '--width', str(self.RefWidth), '--desiredwidth', str(self.width), '--spsi', str(self.pressure), '--ppmm', '0', '--margin', str(self.error)])

        if self.parent.Left.ToggleProcess.get() == 0:
            offset_list = check_output(['/home/pi/Desktop/Code/SPI_mar30/saveme1','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,str(self.RefWidth) ,'--desiredwidth' ,str(self.width),'--spsi',str(self.pressure),'--ppmm', '0','--margin',str(self.error)])
        else:
            offset_list = check_output(['python2' ,'eth_client.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,str(self.RefWidth) ,'--desiredwidth' ,str(self.width),'--spsi',str(self.pressure),'--ppmm', '0','--margin',str(self.error),'--ip',self.ip])
        #offset_list = check_output(['python2' ,'psi_cal.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,'17.9' ,'--desiredwidth' ,str(self.width)])
        offset_list = ast.literal_eval(offset_list)
        print("This is the first line measurement")
        print(offset_list)
        #Report back to Marlin new pressure
        i2c_buf = []
        i2c_buf.extend(bytearray(struct.pack('f', offset_list[1])))
        successfulWrite = 0
        while not successfulWrite:
            try:
                #self.parent.bus.write_byte(self.parent.address, 21)
                self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                successfulWrite = 1
            except Exception as e:
                print('I2C bus was busy. Trying again.')
                time.sleep(0.5)
        #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
        #Only enter the calibration loop if the initial measurement was off
        #self.parent.bus.write_byte(self.parent.address, 21)
        if offset_list[0]: #If true, send calibration complete
            successfulWrite = 0
            while not successfulWrite:
                try:
                #self.parent.bus.write_byte(self.parent.address, 21)
                #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                    self.parent.bus.write_byte(self.parent.address, 25) #Send Success flag
                    successfulWrite = 1
                except Exception as e:
                    print('I2C bus was busy. Trying again.')
                    time.sleep(0.5)
            #self.parent.bus.write_byte(self.parent.address, 25) #Send Success flag
            successfulWrite = 0
            while not successfulWrite:
                try:
                #self.parent.bus.write_byte(self.parent.address, 21)
                #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                    self.parent.bus.write_byte(self.parent.address, 21) #Send Success flag
                    successfulWrite = 1
                except Exception as e:
                    print('I2C bus was busy. Trying again.')
                    time.sleep(0.5)
            #self.parent.bus.write_byte(self.parent.address, 21) #Send Continue flag
        else: #Otherwise enter calibration loop

            successfulWrite = 0
            while not successfulWrite:
                try:
                #self.parent.bus.write_byte(self.parent.address, 21)
                #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                    self.parent.bus.write_byte(self.parent.address, 21) #Send Success flag
                    successfulWrite = 1
                except Exception as e:
                    print('I2C bus was busy. Trying again.')
                    time.sleep(0.5)
            #self.parent.bus.write_byte(self.parent.address, 21)
            correctWidth = False
            while not correctWidth:
                #check if we need to cleantip

                #delete image from folder
                if os.path.isfile("/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_junk1.png"):
                    os.remove("/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_junk1.png")
                os.remove("/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png")
                #Edits 10/24 adjut for new ref every time
                PixelToMM = offset_list[2]
                NewPressure = offset_list[1]
                #Send 9 to ask Marlin if in position for picture
                takePicture = False
                while not takePicture:
                    successfulWrite = 0
                    while not successfulWrite:
                        try:
                            self.parent.bus.write_byte(self.parent.address, 9)
                            successfulWrite = 1
                        except Exception as e:
                            print('I2C bus was busy. Trying again.')
                            time.sleep(0.5)
                    time.sleep(.1)
                    #Return Marlins answer if it's ready
                    successfulRead = 0
                    while not successfulRead:
                        try:
                            takePicture = self.parent.bus.read_byte(self.parent.address)
                            successfulRead = 1
                        except Exception as e:
                            print('I2C bus was busy. Trying again.')
                            time.sleep(0.5)
                    time.sleep(1)
                time.sleep(3)
                #Release Camera, then reinitialize
                #self.Esaac.camera.release() #release camera
                self.Esaac.get_ximages(1,"junk")
                time.sleep(.5)
                #removed profanity
                #self.Esaac.camera = cv2.VideoCapture(self.camera_port)
                #At this point, picture is ready to be taken, call Camera Object, take picture
                while(not self.Esaac.get_ximages(self.images_to_take,"PSI")):
                   self.Esaac.get_ximages(1,"PSI")

                #After picture call victors stuff here, expect to return "correctWidth"
                #Call Victor CV Script
                try:
                    '''
                    offset_list = check_output(['python2' ,'saveme1.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,str(self.RefWidth) ,'--desiredwidth' ,str(self.width),'--spsi',str(NewPressure),'--ppmm', str(PixelToMM),'--margin',str(self.error)])
                    '''
                    #offset_list = check_output(['python2', 'eth_client.py', '--image', '/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png', '--width', str(self.RefWidth), '--desiredwidth', str(self.width), '--spsi', str(self.pressure), '--ppmm', str(PixelToMM), '--margin', str(self.error)])

                    if self.parent.Left.ToggleProcess.get() == 0:
                        offset_list = check_output(['/home/pi/Desktop/Code/SPI_mar30/saveme1','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,str(self.RefWidth) ,'--desiredwidth' ,str(self.width),'--spsi',str(NewPressure),'--ppmm', str(PixelToMM),'--margin',str(self.error)])
                    else:
                        offset_list = check_output(['python2' ,'eth_client.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,str(self.RefWidth) ,'--desiredwidth' ,str(self.width),'--spsi',str(NewPressure),'--ppmm', str(PixelToMM),'--margin',str(self.error),'--ip',self.ip])

                    #offset_list = check_output(['python2' ,'mul_proc_measure_psi_cal_pi.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,'17.9' ,'--desiredwidth' ,str(self.width),'--spsi',str(NewPressure),'--ppmm',str(PixelToMM)])
                    ##offset_list = check_output(['/home/pi/Desktop/Code/SPI_mar30/mul_proc_measure_psi_cal_pi','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,'17.9' ,'--desiredwidth' ,str(self.width),'--spsi',str(self.pressure)])

                    #offset_list = check_output(['python2' ,'psi_cal.py','--image' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/image_PSI1.png' ,'--width' ,'17.9' ,'--desiredwidth' ,str(self.width)])
                    offset_list = ast.literal_eval(offset_list)
                    print(offset_list)
                    #It says Offset, but we are just using old code names, index 0 has bool, index 1 has pressure
                    correctWidth = offset_list[0]


                    i2c_buf = []
                    i2c_buf.extend(bytearray(struct.pack('f', offset_list[1])))
                    successfulWrite = 0
                    while not successfulWrite:
                        try:
                    #self.parent.bus.write_byte(self.parent.address, 21)
                            self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                    #self.parent.bus.write_byte(self.parent.address, 25) #Send Success flag
                            successfulWrite = 1
                        except Exception as e:
                            print('I2C bus was busy. Trying again.')
                            time.sleep(0.5)
                    #self.parent.bus.write_i2c_block_data(self.parent.address, 26, i2c_buf)
                    if offset_list[0] and offset_list[1] != 0: #If true, send calibration complete
                        successfulWrite = 0
                        while not successfulWrite:
                            try:
                                self.parent.bus.write_byte(self.parent.address, 25)
                                successfulWrite = 1
                            except Exception as e:
                                print('I2C bus was busy. Trying again.')
                                time.sleep(0.5)
                        #self.parent.bus.write_byte(self.parent.address, 25) #Send Success flag
                        self.CalFields[0].delete(0,END)
                        self.CalFields[0].insert(0,NewPressure)
                    elif (offset_list[0] and offset_list[1] == 0) or (offset_list[3] >= 2*float(self.width)):
                        successfulWrite = 0
                        while not successfulWrite:
                            try:
                                self.parent.bus.write_byte(self.parent.address, 12)
                                successfulWrite = 1
                            except Exception as e:
                                print('I2C bus was busy. Trying again.')
                                time.sleep(0.5)
                        #self.parent.bus.write_byte(self.parent.address, 12)
                        successfulWrite = 0
                        while not successfulWrite:
                            try:
                                self.parent.bus.write_byte(self.parent.address, 25)
                                successfulWrite = 1
                            except Exception as e:
                                print('I2C bus was busy. Trying again.')
                                time.sleep(0.5)
                        #self.parent.bus.write_byte(self.parent.address, 25)
                    successfulWrite = 0
                    while not successfulWrite:
                        try:
                            self.parent.bus.write_byte(self.parent.address, 21)
                            successfulWrite = 1
                        except Exception as e:
                            print('I2C bus was busy. Trying again.')
                            time.sleep(0.5)
                except Exception as e:
                    print("Algorithm Failed, Might be bad pic")
                    successfulWrite = 0
                    while not successfulWrite:
                        try:
                            self.parent.bus.write_byte(self.parent.address, 12)
                            successfulWrite = 1
                        except Exception as e:
                            print('I2C bus was busy. Trying again.')
                            time.sleep(0.5)
                    #self.parent.bus.write_byte(self.parent.address, 12)
                    successfulWrite = 0
                    while not successfulWrite:
                        try:
                            self.parent.bus.write_byte(self.parent.address, 25)
                            successfulWrite = 1
                        except Exception as e:
                            print('I2C bus was busy. Trying again.')
                            time.sleep(0.5)
                    #self.parent.bus.write_byte(self.parent.address, 25)
                    successfulWrite = 0
                    while not successfulWrite:
                        try:
                            self.parent.bus.write_byte(self.parent.address, 21)
                            successfulWrite = 1
                        except Exception as e:
                            print('I2C bus was busy. Trying again.')
                            time.sleep(0.5)
                    correctWidth = True
                #self.parent.bus.write_byte(self.parent.address, 21) #Send Continue flag
        #Get Values from Fields

        #self.width = float(self.CalFields[2].get())
        #self.speed = float(self.CalFields[1].get())
        #self.error = float(self.CalFields[3].get())
        #If it breaks our of above loop, width is success, send 25 to signal marlin done
        #self.parent.bus.write_byte(self.parent.address, 25)
        #self.parent.Left.populateFields(self.parent.Left.BarreltoCal)
        self.ContinueButton.config(state=DISABLED)
        self.ReprintButton.config(state=DISABLED)
        self.CancelButton.config(state=DISABLED)
        self.StartButton.config(state=NORMAL)
        self.CloseButton.config(state=NORMAL)
        self.Esaac.camera.release()

class MainW(Tk):

    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.parent = parent
        self.width = 800
        self.height = 480
        self.geometry(str(self.width) + "x" + str(self.height))
        self.wm_title("AETHER PSI CALIBRATION")

        self.bus = smbus.SMBus(1)
        self.address = 0x75
        self.InitFrames()
        self.PlaceFrames()

    def InitFrames(self):

        self.Head = Header_Frame(self)
        self.Left = Left_Frame(self)
        self.Right = Right_Frame(self,self.Left.Cal_field_list,self.Left.ToggleClean)
        self.Center = Center_Frame(self,CalFields=self.Left.Cal_field_list)

    def PlaceFrames(self):

        self.Head.grid(row=0, column=0,columnspan=3,sticky=W)
        self.Left.grid(row=1,column=0, sticky=NW)
        self.Center.grid(row=1, column=1,sticky=W)#SW
        self.Right.grid(row=1,column=2,sticky=S, pady=30)


if __name__ == "__main__":

    app = MainW(None)

    app.mainloop()
