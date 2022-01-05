from face_recognition import FaceRecognition

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_curve, precision_recall_curve, roc_auc_score, accuracy_score

import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
import random
import numpy as np
import cv2
import base64
from tqdm import tqdm
import requests
from pprint import pprint

ROOT_Train = "C:/Users/Tapac/Desktop/AFDB_face_dataset2/"
ROOT_Test = "C:/Users/Tapac/Desktop/AFDB_masked_face_dataset2/"

train = []
for path in glob.iglob(os.path.join(ROOT_Train, "**", "*.jpg")):
    person = path.split("\\")[-2]
    train.append({"person": person, "path": path})

train = pd.DataFrame(train)
train = train.groupby("person").filter(lambda x: len(x) > 5)
train.head(10)

train.groupby("person").count()[:50].plot(kind='bar', figsize=(20,5))

print("number of person in train dataset : %s" %(len(train.groupby("person"))))
print("number of image in train dataset : %s" %(len(train)))

trainx, valid = train_test_split(train, test_size=0.1, random_state=42, shuffle=True)

#trainx, valid = train_test_split(train, test_size=0.5, random_state=2, shuffle=True)

print("number of person in train dataset : %s" %(len(trainx.groupby("person"))))
print("number of image in train dataset : %s" %(len(trainx)))
print("number of person in validation dataset : %s" %(len(valid.groupby("person"))))
print("number of image in validation dataset : %s" %(len(valid)))

plt.figure(figsize=(20,10))
for i in range(10):
    idx = random.randint(0, len(train))
    img = plt.imread(train.path.iloc[idx])
    plt.subplot(4, 5, i+1)
    plt.imshow(img)
    plt.title(train.person.iloc[idx])
    plt.xticks([])
    plt.yticks([])
plt.tight_layout()
plt.show()

test = []
for path in glob.iglob(os.path.join(ROOT_Test, "**", "*.jpg")):
    person = path.split("\\")[-2]
    test.append({"person":person, "path": path})
test = pd.DataFrame(test)
test = test.groupby("person").filter(lambda x: len(x) > 0)
test.head(10)

len(test.groupby("person"))

test.groupby("person").count()[:50].plot(kind='bar', figsize=(20,5))

plt.figure(figsize=(20,10))
for i in range(10):
    idx = random.randint(0, len(test))
    img = plt.imread(test.path.iloc[idx])
    plt.subplot(4, 5, i+1)
    plt.imshow(img)
    plt.title(test.person.iloc[idx])
    plt.xticks([])
    plt.yticks([])
plt.tight_layout()
plt.show()

print("Train:",len(train))
print("Test:",len(test))


fr = FaceRecognition()
fr.fit_from_dataframe(trainx)

fr.save('masked_unmasked_model.pkl')

valid_test, valid_pred, valid_scores = [],[],[]
for idx in tqdm(range(len(valid))):
    path = valid.path.iloc[idx]
    result = fr.predict(path)
    for prediction in result["predictions"]:
        valid_pred.append(prediction["person"])
        valid_scores.append(prediction["confidence"])
        valid_test.append(valid.person.iloc[idx])

y_test, y_pred, y_scores = [],[],[]
for idx in tqdm(range(len(test))):
    path = test.path.iloc[idx]
    result = fr.predict(path)
    for prediction in result["predictions"]:
        y_pred.append(prediction["person"])
        y_scores.append(prediction["confidence"])
        y_test.append(test.person.iloc[idx])

print(classification_report(y_test, y_pred))

print("Train Accuracy: %f" % accuracy_score(valid_test, valid_pred))

print("Accuracy: %f" % accuracy_score(y_test, y_pred))

person = "aidai" #"guojunchen"
path = test[test.person==person]["path"].iloc[0]
img = cv2.imread(path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

result = fr.predict(path)
file_bytes = np.fromstring(base64.b64decode(result["frame"]), np.uint8)
output = cv2.imdecode(file_bytes,1)

plt.figure(figsize=(10,5))
plt.subplot(1, 2, 1)
plt.imshow(img)
plt.title(person)
plt.subplot(1, 2, 2)
plt.imshow(output)
print(result["predictions"][0]["confidence"])
plt.title("%s (%f)" % (result["predictions"][0]["person"], result["predictions"][0]["confidence"]))
plt.tight_layout()
plt.show()
