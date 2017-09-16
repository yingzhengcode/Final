import cv2
import os
import shutil
from myFeatures import FeatureExtraction
import sys
import csv
import xlsxwriter
import numpy as np

class MineData():
    def load_images_from_folder(self, folder):
        print("Load images from CK+")
        images = []
        for filename in os.listdir(folder):
            if filename.endswith(".png"):
                img = cv2.imread(os.path.join(folder, filename))
                if img is not None:
                    images.append(img)
        return images

    def main(self):
        self.ahed = FeatureExtraction()

        #create paths
        pathAngry = os.path.abspath('Data/Angry')
        pathDisgust = os.path.abspath('Data/Disgust')
        pathFear = os.path.abspath('Data/Fear')
        pathHappy = os.path.abspath('Data/Happy')
        pathNeutral = os.path.abspath('Data/Neutral')  # or path
        pathSad = os.path.abspath('Data/Sad')
        pathSurprise = os.path.abspath('Data/Surprise')

        Angry = self.load_images_from_folder(pathAngry)
        Disgust = self.load_images_from_folder(pathDisgust)
        Fear = self.load_images_from_folder(pathFear)
        Happy = self.load_images_from_folder(pathHappy)
        Neutral = self.load_images_from_folder(pathNeutral)
        Sad = self.load_images_from_folder(pathSad)
        Surprise = self.load_images_from_folder(pathSurprise)

	#-------------------Uncomment below for results of Viola-Jones(as Images):-------------------
        current_directory = os.getcwd()
        print(current_directory)
        shutil.rmtree(current_directory + '/Data/Viola')

        if not os.path.exists(os.path.join(current_directory, r'Data/Viola/angViola')):
            os.makedirs(os.path.join(current_directory, r'Data/Viola/angViola'))
        if not os.path.exists(os.path.join(current_directory, r'Data/Viola/disViola')):
            os.makedirs(os.path.join(current_directory, r'Data/Viola/disViola'))
        if not os.path.exists(os.path.join(current_directory, r'Data/Viola/fearViola')):
            os.makedirs(os.path.join(current_directory, r'Data/Viola/fearViola'))
        if not os.path.exists(os.path.join(current_directory, r'Data/Viola/hapViola')):
            os.makedirs(os.path.join(current_directory, r'Data/Viola/hapViola'))
        if not os.path.exists(os.path.join(current_directory, r'Data/Viola/neuViola')):
            os.makedirs(os.path.join(current_directory, r'Data/Viola/neuViola'))
        if not os.path.exists(os.path.join(current_directory, r'Data/Viola/sadViola')):
            os.makedirs(os.path.join(current_directory, r'Data/Viola/sadViola'))
        if not os.path.exists(os.path.join(current_directory, r'Data/Viola/surViola')):
            os.makedirs(os.path.join(current_directory, r'Data/Viola/surViola'))

	
        print("Running Viola Jones on Images")
        angViola, disViola, fearViola, hapViola, neuViola, sadViola, surViola = [], [], [], [], [], [], []
        for i in range(0, 84):  # change
            if i < len(Angry):
                v1, image = self.ahed.viola_jones(Angry[i])
                angViola.append(v1)
                cv2.imwrite(current_directory + "/Data/Viola/angViola/angry" + str(i) + ".png", v1)
            if i < len(Disgust):
                v2, image = self.ahed.viola_jones(Disgust[i])
                disViola.append(v2)
                cv2.imwrite(current_directory + "/Data/Viola/disViola/disgust" + str(i) + ".png", v2)
            if i < len(Fear):
                v3, image = self.ahed.viola_jones(Fear[i])
                fearViola.append(v3)
                cv2.imwrite(current_directory + "/Data/Viola/fearViola/fear" + str(i) + ".png", v3)
            if i < len(Happy):
                v4, image = self.ahed.viola_jones(Happy[i])
                hapViola.append(v4)
                cv2.imwrite(current_directory + "/Data/Viola/hapViola/happy" + str(i) + ".png", v4)
            if i < len(Neutral):
                v5, image = self.ahed.viola_jones(Neutral[i])
                neuViola.append(v5)
                cv2.imwrite(current_directory + "/Data/Viola/neuViola/neutral" + str(i) + ".png", v5)
            if i < len(Sad):
                v6, image = self.ahed.viola_jones(Sad[i])
                sadViola.append(v6)
                cv2.imwrite(current_directory + "/Data/Viola/sadViola/sad" + str(i) + ".png", v6)
            if i < len(Surprise):
		#if(i == 53):
		 #   cv2.imwrite("wtf.png",Surprise[i])
                v7, image = self.ahed.viola_jones(Surprise[i])
                surViola.append(v7)
                cv2.imwrite(current_directory + "/Data/Viola/surViola/surprise" + str(i) + ".png", v7)
	#-----------------------------------end of Viola-Jones-------------------------------------------
        print("Running Hog on Viola Images")
        featureVectors = []
        for i in range(0, 84):
            if i < len(angViola):
                angVector = self.ahed.hog_opencv(angViola[i])
                angVector = angVector.tolist()
                angVector.insert(0, 1)
                featureVectors.append(angVector)
            if i < len(disViola):
                disVector = self.ahed.hog_opencv(disViola[i])
                disVector = disVector.tolist()
                disVector.insert(0, 2)
                featureVectors.append(disVector)
            if i < len(fearViola):
                fearVector = self.ahed.hog_opencv(fearViola[i])
                fearVector = fearVector.tolist()
                fearVector.insert(0, 3)
                featureVectors.append(fearVector)
            if i < len(hapViola):
                hapVector = self.ahed.hog_opencv(hapViola[i])
                hapVector = hapVector.tolist()
                hapVector.insert(0, 4)
                featureVectors.append(hapVector)
            if i < len(neuViola):
                neuVector = self.ahed.hog_opencv(neuViola[i])
                neuVector = neuVector.tolist()
                neuVector.insert(0, 5)
                featureVectors.append(neuVector)
            if i < len(sadViola):
                sadVector = self.ahed.hog_opencv(sadViola[i])
                sadVector = sadVector.tolist()
                sadVector.insert(0, 6)
                featureVectors.append(sadVector)
            if i < len(surViola):
                surVector = self.ahed.hog_opencv(surViola[i])
                surVector = surVector.tolist()
                surVector.insert(0, 7)
                featureVectors.append(surVector)
        with open("dataCsv.csv", "wb+") as f:
            writer = csv.writer(f)
            writer.writerows(featureVectors)
        # if we read f.csv we will write f.xlsx
        workbook = xlsxwriter.Workbook('dataExcel.xlsx')
        worksheet = workbook.add_worksheet()
        row = 0
        for row, vector in enumerate(featureVectors):
            for col, value in enumerate(vector):
                worksheet.write(row, col, value)
        workbook.close()

	print("Running My Hog on Viola Images")
        featureVectors = []
        for i in range(0, 84):
            if i < len(angViola):
                angVector = self.ahed.calculate_myhog(angViola[i])
                angVector = angVector.tolist()
                angVector.insert(0, 1)
                featureVectors.append(angVector)
            if i < len(disViola):
                disVector = self.ahed.calculate_myhog(disViola[i])
                disVector = disVector.tolist()
                disVector.insert(0, 2)
                featureVectors.append(disVector)
            if i < len(fearViola):
                fearVector = self.ahed.calculate_myhog(fearViola[i])
                fearVector = fearVector.tolist()
                fearVector.insert(0, 3)
                featureVectors.append(fearVector)
            if i < len(hapViola):
                hapVector = self.ahed.calculate_myhog(hapViola[i])
                hapVector = hapVector.tolist()
                hapVector.insert(0, 4)
                featureVectors.append(hapVector)
            if i < len(neuViola):
                neuVector = self.ahed.calculate_myhog(neuViola[i])
                neuVector = neuVector.tolist()
                neuVector.insert(0, 5)
                featureVectors.append(neuVector)
            if i < len(sadViola):
                sadVector = self.ahed.calculate_myhog(sadViola[i])
                sadVector = sadVector.tolist()
                sadVector.insert(0, 6)
                featureVectors.append(sadVector)
            if i < len(surViola):
                surVector = self.ahed.calculate_myhog(surViola[i])
                surVector = surVector.tolist()
                surVector.insert(0, 7)
                featureVectors.append(surVector)
        with open("myHogdDataCsv.csv", "wb+") as f:
            writer = csv.writer(f)
            writer.writerows(featureVectors)
       
        workbook = xlsxwriter.Workbook('myHogdDataExcel.xlsx')
        worksheet = workbook.add_worksheet()
        row = 0
        for row, vector in enumerate(featureVectors):
            for col, value in enumerate(vector):
                worksheet.write(row, col, value)
        workbook.close()

if __name__ == '__main__': MineData().main()
