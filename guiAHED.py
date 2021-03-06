import sys
import cv2
import numpy as np
import pickle
from extractFeatures import FeatureExtraction
from PyQt4 import QtCore, QtGui, uic

qtCreatorFile = 'userinterface.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class Demo(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.capturing = False
        self.c = cv2.VideoCapture(0)

        self.features = FeatureExtraction()
        self.loaded_model = pickle.load(open('Files/finalized_model.sav', 'rb'))
        self.emojimaps, self.target_names = self.getpixmaps()

        self.startVideoButton.clicked.connect(self.startCapture)
        self.endVideoButton.clicked.connect(self.endCapture)
        self.quitVideoButton.clicked.connect(self.quitCapture)

        pixmap = QtGui.QPixmap('Files/lense.png')
        pixmap = pixmap.scaled(200, 200)
        self.emojiLabel.setPixmap(pixmap)

        pixmapVideo = QtGui.QPixmap('Files/lense.png')
        pixmapVideo = pixmapVideo.scaled(450, 450)
        self.videoLabel.setPixmap(pixmapVideo)

        self.videoLabel.show()
        self.emojiLabel.show()

    def getpixmaps(self):
        target_names = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise', 'blank']
        emojis = {1: 'Data/Emojis/angry.png', 2: 'Data/Emojis/disgust.png', 3: 'Data/Emojis/fear.png',
                  4: 'Data/Emojis/happy.png', 5: 'Data/Emojis/neutral.png', 6: 'Data/Emojis/sad.png',
                  7: 'Data/Emojis/surprise.png', 8: 'Data/Emojis/emoji_empty_r.png'}
        pixmaps = {}
        for key in emojis:
            pixmap = QtGui.QPixmap(emojis[key])
            pixmap = pixmap.scaled(200, 200)
            pixmaps[target_names[key - 1]] = pixmap

        return pixmaps, target_names

    def startCapture(self):
        print 'pressed start'
        self.capturing = True
        cap = self.c

        track = []
        while self.capturing:
            ret, camframe = cap.read()

            if ret:
                scaled, vframe = self.features.viola_jones(camframe)
                if np.sum(scaled) != 0:
                    hog = self.features.hog_opencv(scaled)
                    result = self.loaded_model.predict(np.array([hog]))

                    if len(track) == 1:
                        if track[0] != (result[0]):
                            del track[:]
                            track.append(result[0])
                        else:
                            track.append(result[0])
                    elif len(track) == 2:
                        if track[0] == result[0] and track[1] == result[0]:
                            del track[:]
                            self.emojiLabel.setPixmap(self.emojimaps[self.target_names[result[0] - 1]])
                            print(self.target_names[result[0] - 1])
                            result_proba = self.loaded_model.predict_proba(np.array([hog]))
                            probabilities = (result_proba[0]) * 100
                            probabilities.astype(np.int64)
                            self.lcd1.display(probabilities[0])
                            self.lcd2.display(probabilities[1])
                            self.lcd3.display(probabilities[2])
                            self.lcd4.display(probabilities[3])
                            self.lcd5.display(probabilities[4])
                            self.lcd6.display(probabilities[5])
                            self.lcd7.display(probabilities[6])
                        else:
                            del track[:]
                            track.append(result[0])
                    else:
                        track.append(result[0])
                frame = cv2.cvtColor(vframe, cv2.COLOR_BGR2RGB)
                img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
                pixmapVideo = QtGui.QPixmap.fromImage(img)
                self.videoLabel.setPixmap(pixmapVideo)
                QtGui.QApplication.processEvents()

    def endCapture(self):
        print 'pressed End'
        self.capturing = False

    def quitCapture(self):
        print 'pressed Quit'
        cap = self.c
        cap.release()
        QtCore.QCoreApplication.quit()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Demo()
    window.show()
    sys.exit(app.exec_())
