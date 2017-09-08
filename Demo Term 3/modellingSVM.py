import cv2
import numpy as np
import pandas as pd
import seaborn as sb
import os
import shutil
from myFeatures import FeatureExtraction
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, average_precision_score
import pickle

from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
#MENTION LABELS NB NB
class Tester():

    def main(self):
        self.ahed = FeatureExtraction()
        path = 'dataCsv.csv'
        dataset = pd.read_csv(path)
        #dataset.head()
        #sb.countplot(x='diagnosis',data=dataset, palette='hls')
        #dataset.isnull().sum()
        X = dataset.ix[:,1:].values
        y = dataset.ix[:,0].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.30, stratify = y, random_state=40)
        # BEFORE SVM TRAINING & GRID SEARCH:
        param_grid = [
        	{'C': [1, 10, 100, 1000], 'kernel': ['linear']},
        	{'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
        	 ]
        #C_range = np.logspace(-5, 15,num=21,base = 10.0)#, 6)
        #print(C_range)
        #gamma_range = np.logspace(-15, 3, num=19,base = 10.0)#, 6)
        #print(gamma_range)
        #param_grid = [
        #   {'C': C_range.tolist(), 'kernel': ['linear']},
        #   {'C': C_range.tolist(), 'gamma': gamma_range.tolist(), 'kernel': ['rbf']},
        #]
        svc = svm.SVC(probability=True)  # verbose=1)# I will also advice using verbose to see behavior of your svm and grid search
        print("SVM Grid Search")#easy.p & grid.py ??
        clf = GridSearchCV(svc, param_grid)  # ,verbose=1)
        clf = clf.fit(X_train, y_train)

        print("SVM Train")

        filename = 'finalized_model.sav'
        pickle.dump(clf, open(filename, 'wb'))

        #AFTER SVM TRAINING:
        #clf = pickle.load(open('finalized_model.sav', 'rb'))
        print("SVM Predict:")
        y_pred = clf.predict(X_test)
        print("SVM Best Estimator:")
        print(clf.best_estimator_)
        print("SVM Grid Scores:")
        print(clf.cv_results_)
        print("SVM Classification Report:")
        print(classification_report(y_test, y_pred, target_names=["Angry","Happy", "Neutral","Surprise"]))#target_names=["Angry", "Disgust", "Fear", "Happy", "Neutral", "Sad", "Surprise"]))
        print("SVM Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred, labels=[1,4,5,7]))
        print("SVM Accuracy Score:")
        print(accuracy_score(y_test, y_pred, normalize=True)) #normalize=False))



if __name__ == '__main__': Tester().main()