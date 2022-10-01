import cv2
import time
import threading as th
import random as rand
import serial

class Item:
    def __init__(self, x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.shown = False

def isIn(a,b,c,d,x,y,w,h):
    if a>x and a+c<x+w and b>y and b+d<y+h:
        return True
    else :
        return False

cnt = 0
isspawn = False
item = Item(0,0,0,0)
complete = False
send = False

def findFace(img,ser,face_cascade):
    global cnt
    global isspawn
    global complete
    global send
    # Load the cascade
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    imgw, imgh = img.shape[1],img.shape[0]
    smallimgw,smallimgh = int(imgw/1.2),int(imgh/1.2)
    offsetxs,offsetys = int((imgw-smallimgw)/2),int((imgh-smallimgh)/2)
    cv2.rectangle(img,(offsetxs,offsetys),(offsetxs+smallimgw,offsetys+smallimgh),(255,255,255))
    dumimg = gray[offsetys:offsetys+smallimgh,offsetxs:offsetxs+smallimgw ]
    #cv2.imshow("dum",dumimg)
    faces = face_cascade.detectMultiScale(dumimg, 1.1, 5)
    tmp = []
    for (x, y, w, h) in faces:
        tmp.append((offsetxs+x,offsetys+y,w,h))

    faceareas = dict()

    if len(tmp)!=0:

        for (x, y, w, h) in tmp:
            faceareas[(x,y,w,h)] = w*h

        faceareas = dict(sorted(faceareas.items(), key=lambda item:item[1], reverse=True))
        maxarea = list(faceareas)[0]
        facex,facey,facew,faceh = maxarea[0], maxarea[1], maxarea[2], maxarea[3]
        if facew*faceh > 30000:
            #print(facew*faceh)
            cv2.rectangle(img, (facex, facey), (facex+facew, facey+faceh), (255, 0, 0), 2)
            if complete == False:
                send = False
                if isspawn == False:
                    (x,y) = randomlocate(offsetxs,offsetys,smallimgw,smallimgh)
                    while isIn(x,y,50,50,facex,facey,facew,faceh):
                        (x,y) = randomlocate(offsetxs,offsetys,smallimgw,smallimgh)
                    #t = th.Timer(1.5,spawnitem,[x,y])
                    #t.start()
                    spawnitem(x,y)
                    #print(str(x) + " " + str(y))
                else:
                    draw(img)

                if isIn(item.x,item.y,item.w,item.h,facex,facey,facew,faceh):
                    if cnt < 100:
                        cnt += 50
                    despawn()

                
                if cnt == 50:
                    filter(img,maxarea[0],maxarea[1],int(maxarea[2]/2),int(maxarea[3]/10))
                elif cnt == 100:
                    filter(img,maxarea[0],maxarea[1],int(maxarea[2]),int(maxarea[3]/10))
                    isspawn = False
                    t = th.Timer(1.5,isComplete,[])
                    t.start()
                

               
                ##hard mode
                #if cnt != 100:
                #    filter(img,maxarea[0],maxarea[1],int(maxarea[2]*cnt/100),int(maxarea[3]/10))
                #else:
                #    filter(img,maxarea[0],maxarea[1],int(maxarea[2]),int(maxarea[3]/10))
                #    isspawn = False
                #    t = th.Timer(1.5,isComplete,[])
                #    t.start()
                
            else:
                drawcomplete(img,facex,facey,facew,faceh)
                if send == False:
                    send = True
                    senddata(ser)
                    t = th.Timer(15.0,isnotComplete,[])
                    t.start()
        else:
            cnt = 0
            despawn()

    else:
        #timethread.cancel()
        cnt = 0
        despawn()

def senddata(ser):
    ser.write(b'\n1')


def randomlocate(x,y,w,h):
    offset_x = rand.randint(x+50,x+w-50)
    offset_y = rand.randint(y+50,y+h-50)
    return (offset_x, offset_y)

def despawn():
    global item
    global isspawn
    item.x = 0
    item.y = 0
    item.w = 0
    item.h = 0
    isspawn = False

def spawnitem(x,y):
    global item
    global isspawn
    item.x = x
    item.y = y
    item.w = 50
    item.h = 50
    isspawn = True

def draw(img):
    it = cv2.imread("icon.jpg")
    re_item = cv2.resize(it,(50,50))
    if isspawn == True:
        img[item.y:item.y+re_item.shape[1], item.x:item.x+re_item.shape[0]] = re_item

def filter(img,x,y,w,h):
    bar = cv2.imread("loadingbar.png")
    progress = cv2.resize(bar,(w,h))
    x_offset = x
    y_offset = y - h - 5 if y - h - 5 > 0 else y + h + 5
    img[y_offset:y_offset+progress.shape[0], x_offset:x_offset+progress.shape[1]] = progress
    
def progressbar(i):
    global cnt
    cnt = i

def isComplete():
    global complete
    complete = True

def isnotComplete():
    global complete
    global cnt
    cnt = 0
    complete = False
    
#def loadingbar():
    #if cnt == 0 and not timethread.is_alive():
        #    timethread = th.Timer(0.05,progressbar,[cnt+2])
        #    timethread.start()
        #elif cnt == 100 :
        #    filter(img,facex,facey,int(facew),int(faceh/10))
        #else:
        #    if not timethread.is_alive():
        #        filter(img,facex,facey,int(facew*cnt/100),int(faceh/10))
        #        timethread = th.Timer(0.05,progressbar,[cnt+2])
        #        timethread.start()

def drawcomplete(img,x,y,w,h):
    icon = cv2.imread("complete.png")
    icon = cv2.resize(icon,(int(w/2),int(w/2)))
    offsetx = int(x+w/4)
    offsety = int(y-30-w/2) if y-30-w/2 > 0 else int(y+h+30)
    img[offsety:offsety + int(w/2), offsetx:offsetx + int(w/2)] = icon

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    name = "window"
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow(name,1920,0)
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    ser = serial.Serial('COM7', 115200)
    #ser = 0
    while True:
        # Read the frame
        _, img = cap.read()
        findFace(img,ser,face_cascade)
        #print(img.shape)
        cv2.imshow(name,img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

