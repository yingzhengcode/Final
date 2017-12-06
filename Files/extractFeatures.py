import sys
import cv2
import numpy as np
from skimage.feature import hog
from skimage import img_as_float

# a trained model for locating faces within an image
faceCascade = cv2.CascadeClassifier('Files/haarcascade_frontalface_alt.xml')

class FeatureExtraction():
    # ------------------------------------------------------------------------------
    # ----------------------------Viola-Jones Face Detection------------------------
    # ------------------------------------------------------------------------------
    def viola_jones(self, image):
		# set the height and width of face images
        height = 56
        width = 56
		
		# create an temporary 'image' of zeros
        scaled = np.zeros((height, width), dtype=np.float)
		
		# set the properties of the faceCascade
        faces = faceCascade.detectMultiScale(image, 1.3, 5)

		# set variables for finding the largest face in an image 
        max_size = 0  # w*h
        X = Y = W = H = 0
		
		# keeping track of x,y,w,h in order to find the biggest face
        for (x, y, w, h) in faces:  
            if max_size < w * h:
                max_size = w * h
                X = x
                Y = y
                W = w
                H = h
				
        # cater for when there are no faces in the image 'max_size = 0'
        if max_size != 0:
			# draw a rectangle identifying the location of the face in the image
            cv2.rectangle(image, (X, Y), (X + W, Y + H), (192, 192, 192), 2)
			
			# store the location with the face as our region of interest 'roi'
            roi = image[Y:Y + H, X:X + W]
			
			# convert the roi to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
			
			# resize the roi so that all the roi's are uniform
            scaled = cv2.resize(gray, (height, width))

        return scaled, image

    # ------------------------------------------------------------------------------
    # -----------------------------------My HOG-------------------------------------
    # ------------------------------------------------------------------------------
    # Note: gradients work only on grayscale images

	# calculate the gradient in the X direction (gx)
    def gx(self, scaled):
        y, x = scaled.shape
        scaled = np.lib.pad(scaled, 1, 'constant', constant_values=0)
        gx = np.zeros((x, y))
        # sobelX:
        # [1	,0	,-1]
        # [2	,0	,-2]
        # [1	,0	,-1]
        for i in range(y):
            a = np.convolve(scaled[i - 1, :], [1, 0, -1], 'valid')
            b = np.convolve(scaled[i, :], [2, 0, -2], 'valid')
            c = np.convolve(scaled[i + 1, :], [1, 0, -1], 'valid')
            gx[i, :] = np.sum([a, b, c], axis=0)
        return gx
		
	# calculate the gradient in the Y direction (gy)
    def gy(self, scaled):
        y, x = scaled.shape
        scaled = np.lib.pad(scaled, 1, 'constant', constant_values=0)
        gy = np.zeros((x, y))
        # sobelY:
        # [-1	,-2	,-1]
        # [0	,0	,0]
        # [1	,2	,1]
        for j in range(x):
            a = np.convolve(scaled[:, j - 1], [1, 0, -1], 'valid')
            b = np.convolve(scaled[:, j], [2, 0, -2], 'valid')
            c = np.convolve(scaled[:, j + 1], [1, 0, -1], 'valid')
            gy[:, j] = np.sum([a, b, c], axis=0)
        return gy

	# calculate magnitude of the gradient('intensity')
    def magnitude(self, gx, gy):
        magnitude = np.sqrt(gx ** 2 + gy ** 2)
        return magnitude

	# calculate orientation of the gradient('direction')
    def orientation(self, gx, gy):
        orientation = (np.arctan2(gy, gx) / np.pi) % 2 * np.pi  # same output as cv2.cartToPolar
        return orientation
	
	# calculate the HOG using an algorithm developed from my documentation
    def calculate_myhog(self, scaled):
		# gradients gx and gy
        gx = self.gx(scaled)
        gy = self.gy(scaled)

		# magnitude and orientation
        magnitude = self.magnitude(gx, gy)
        orientation = self.orientation(gx, gy)

		# orientation bins
        bin_n = 9
        bins = np.int32(bin_n * orientation / (2 * np.pi))

		# magnitude and orientation cells within a block
        bin_blocks = []
        mag_blocks = []
        epsilon = sys.float_info.epsilon

		# size of block
        blocksize = 3 
		
		# size of cell
        cellsize = 4

		# store the height and width of the face image(roi)
        width = scaled.shape[0]
        height = scaled.shape[1]

		# create the parameters for the block slider
        y = ((height - (cellsize * blocksize)) / cellsize) + 1
        x = ((width - (cellsize * blocksize)) / cellsize) + 1

		# stores all the histograms in an image
        histograms = []
		
		# loops through each block in a image(i,j)
		# using a block "slider" to capture all posible blocks 
        for i in range(0, y, 1):  
            for j in range(0, x, 1):
				# magnitude and orientation cells within a block
                bin_block = bins[i * cellsize: i * cellsize + blocksize * cellsize,
                            j * cellsize: j * cellsize + blocksize * cellsize]
                mag_block = magnitude[i * cellsize: i * cellsize + blocksize * cellsize,
                            j * cellsize: j * cellsize + blocksize * cellsize]
							
                tempHists = []
                sumHists = np.zeros((9,))
				
				 # loops through each cell in a block(m,n)
				 # this ensures that all the histograms in each cell are calculated
                for m in range(0, blocksize * cellsize, cellsize): 
                    for n in range(0, blocksize * cellsize, cellsize):
					
						# magnitude and orientation cells within a cell
                        cellBin = bin_block[m:m + cellsize, n:n + cellsize]
                        cellMag = mag_block[m:m + cellsize, n:n + cellsize]
						
						# temporarily store the histograms
                        tempHists.append(np.bincount(cellBin.ravel(), cellMag.ravel(), bin_n))
						
						# store the sum of the histograms within a block
						# this will be used for block normalization
                        sumHists = np.sum([sumHists, np.bincount(cellBin.ravel(), cellMag.ravel(), bin_n)], axis=0)
						
				# sum up all the bins
                sumHists = np.sum(sumHists)
				
				# normalize all the cell histograms in the block
                for hist in tempHists:
                    histograms.append(np.divide(hist, np.sqrt(np.add(np.square(sumHists), np.square(epsilon)))))

				# store the magnitude and orientation for the block
                bin_blocks.append(bin_block)
                mag_blocks.append(mag_block)
		# create the HOG feature vector
        hist = np.hstack(histograms)
        return hist

    # ------------------------------------------------------------------------------
    # ---------------------------------OpenCV HOG-----------------------------------
    # ------------------------------------------------------------------------------
	
	# HOG implementation from skimage, using prefered parameters
    def hog_opencv(self, image):
        image = img_as_float(image)  # convert unit8 tofloat64 ... dtype
        orientations = 9		# orientation bins
        cellSize = (4, 4)  		# pixels_per_cell
        blockSize = (3, 3)  	# cells_per_block
        blockNorm = 'L1-sqrt' 	# {'L1', 'L1-sqrt', 'L2', 'L2-Hys'}
        visualize = True  		# Also return an image of the HOG.
        transformSqrt = False
        featureVector = True
        fd, hog_image = hog(image, orientations, cellSize, blockSize, blockNorm, visualize, transformSqrt,
                            featureVector)
        return fd
		
	# testing features 
    def main(self):
        image = cv2.imread('Files/lense.png')
		scaled, image = self.viola_jones(image)
        print(self.calculate_myhog(scaled).shape)
		fd = self.hog_opencv(scaled)
		print(fd.shape)


if __name__ == '__main__': FeatureExtraction().main()