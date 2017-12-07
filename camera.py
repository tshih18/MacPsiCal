import cv2
import os
# import ast
# import subprocess
 
class CV_Camera(object):
 
	def __init__(self, camera_port, ramp_frames):
		self.camera_port = camera_port
		self.ramp_frames = ramp_frames
		self.img_location = "/home/pi/Desktop/Code/SPI_mar30/FilesToSend/"
		self.camera = cv2.VideoCapture(self.camera_port)
		self.X_RES = 1920
		self.Y_RES = 1080


	def get_cap(self):
		self.camera = -1
		for i in range(100):
			self.camera = cv2.VideoCapture(i)

			if self.camera.isOpened():
				self.camera_port = i
				self.camera.set(3, self.X_RES)
				self.camera.set(4, self.Y_RES)
				break

		if (self.camera == -1):
			self.get_cap()
			print("Had to try again...")
 
	def get_image(self):
		self.retval, self.im = self.camera.read()

		if (not retval): # failed to take image

			count = 0
			while(count < 5):
				# Capture frame-by-frame
				ret, self.im = self.camera.read()

				if (ret):
					count += 1 # succeed in taking 5 photos consecutively
				else:
					count = 0
					self.camera.release()
					self.camera = get_cap()


		return self.im


	def get_ximages(self, no_of_images, type1):
##        X_RES = 4224
##        Y_RES = 3156
##        self.camera.set(3, X_RES)
##        self.camera.set(4, Y_RES)
		 
		#toss first few frames to adjust for lighting
##        for i in xrange(self.ramp_frames):
##        
##            temp = self.get_image()
		 
		 
		print("Taking image...")
		# Take the actual image designated amount of times
		for i in range(no_of_images):
			img_file_name = ''.join([self.img_location,"image_",str(type1),str(i+1),".png"])

			if (os.path.isfile(img_file_name)): # deletes previous img if exists
				os.remove(img_file_name)
			 
			camera_capture = self.get_image()
 
			camera_capture = cv2.cvtColor(camera_capture, cv2.IMREAD_COLOR)
 
			#save the image
			cv2.imwrite(img_file_name, camera_capture)
 
##            img_file_name = ''.join([self.img_location,"beta_test81.png"])
 
			return os.path.isfile(img_file_name) and os.path.getsize(img_file_name) > 0
			 
##        #del(self.camera)
##
##if __name__ == "__main__":
##   
##    camera_port = 0
##    ramp_frames = 5
##    images_to_take = 1
##
##    Esaac = CV_Camera(camera_port,ramp_frames)
##    val = Esaac.get_ximages(images_to_take,"ref")
##    print(val)
	#offset_list = subprocess.check_output(['python2' ,'offset_algorithm.py','--image1' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/beta_test82.png' ,'--image2' ,'/home/pi/Desktop/Code/SPI_mar30/FilesToSend/beta_test81.png' ,'--refwidth' ,'17.9' ,'--sdist','10','--jump','10'])
	#offset_list = ast.literal_eval(offset_list)
	#print("num tools: " + str(len(offset_list)) + "\n" + str(offset_list))