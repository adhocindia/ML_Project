import cv2
import time
from PIL import Image
import numpy as np
import csv
import logistic
import mouthoriginal as m

# all mouth images will be resized to the same size
WIDTH, HEIGHT = 28, 10 

# dimension of feature vector
dim = WIDTH * HEIGHT 

#pop up an image showing the mouth with a blue rectangle
def show(area): 
    cv2.Rectangle(img,(area[0][0],area[0][1]),(area[0][0]+area[0][2],area[0][1]+area[0][3]),(255,0,0),2)
    cv2.NamedWindow('Face Detection', cv2.CV_WINDOW_NORMAL)
    cv2.ShowImage('Face Detection', img) 
    cv2.WaitKey()


#given an area to be cropped, crop() returns a cropped image
def crop(area): 
    crop= img[area[0][1]:area[0][1] + area[0][3], area[0][0]:area[0][0]+area[0][2]] 
    return crop

#given a jpg image, vectorize the grayscale pixels to a (width * height, 1) np array it is used to preprocess the data and transform it to feature space
def vectorize(filename):
    size = WIDTH, HEIGHT # (width, height)
    im = Image.open(filename)
    resized_im = im.resize(size, Image.ANTIALIAS) # resize image
    im_grey = resized_im.convert('L') # convert the image to *greyscale*
    im_array = np.array(im_grey) # convert to np array
    oned_array = im_array.reshape(1, size[0] * size[1]) # reshape the image
    return oned_array


if __name__ == '__main__':
    #load training data
    # create a list for filenames of smiles pictures
    smilefiles = []
    with open('smiles.csv', 'rt') as csvfile:
        for rec in csv.reader(csvfile, delimiter='	'):
            smilefiles += rec

    # create a list for filenames of neutral pictures
    neutralfiles = []
    with open('neutral.csv', 'rt') as csvfile:
        for rec in csv.reader(csvfile, delimiter='	'):
            neutralfiles += rec

    # N x dim matrix to store the vectorized data (aka feature space)       
    phi = np.zeros((len(smilefiles) + len(neutralfiles), dim))
    # 1 x N vector to store binary labels of the data: 1 for smile and 0 for neutral
    labels = []

    # load smile data
    PATH = "/home/samiksha/Desktop/emotion-detection-master/data/smile/"
    for idx, filename in enumerate(smilefiles):
        phi[idx] = vectorize(PATH + filename)
        labels.append(1)

    # load neutral data    
    PATH = "/home/samiksha/Desktop/emotion-detection-master/data/neutral/"
    offset = idx + 1
    for idx, filename in enumerate(neutralfiles):
        phi[idx + offset] = vectorize(PATH + filename)
        labels.append(0)

    #training the data with logistic regression
    lr = logistic.Logistic(dim)
    lr.train(phi, labels)
    
    #open webcam and capture image
    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)

    # try to get the first frame
    if vc.isOpened(): 
        rval, frame = vc.read()
    else:
        rval = False

    print ("\n\npress space to take picture; press ESC to exit")

    while rval:
        cv2.imshow("preview", frame)
        rval, frame = vc.read()
        key = cv2.waitKey(40)        
        if key == 27: # exit on ESC
            break
        if key == 32: # press space to save images
            cv2.imwrite("webcam.jpg",frame)
            img = cv2.imread("webcam.jpg") # input image
            mouth = m.findmouth(img)
            
            if mouth != 2: # did not return error
                mouthimg = crop((mouth))
                cv2.imwrite("webcam-m.jpg", mouthimg)
                # predict the captured emotion
                result = lr.predict((vectorize('webcam-m.jpg')))
                print (result)
                if result*100 >=50:
                    print ("you are smiling! :-) Seems like you are happy today")
                else:
                    print ("you are not smiling :-| hey..Is everything ok")
            else:
                print ("failed to detect mouth. Try hold your head straight and make sure there is only one face.")
    
    cv2.destroyWindow("preview")