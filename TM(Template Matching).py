import numpy as np
import cv2
import math
vidcap = cv2.VideoCapture('movie.mov')
success, image = vidcap.read()
count = 0
frames = []
actual = []
actual2 = []
actual3 = []
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
global fps
fps = vidcap.get(cv2.CAP_PROP_FPS)

while success:
    actual.append(image)
    actual2.append(image)
    actual3.append(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.bitwise_not(image)
    image = (image * 0.0005)
    frames.append(image)
    success, image = vidcap.read()
    count += 1
ref = cv2.imread("reference.jpg", 0)
ref = cv2.bitwise_not(ref)
ref = ref*0.0005
print(ref.shape)
print(frames[0].shape)
print("no of frames = ", count)
global P
P = 50


def valid(img, i, j):
    return 0 <= i < len(img) and 0 <= j < len(img[0])

def exhaust(frames, ref, new_frames):
    ct = 0
    op_count = 0
    for fr in range(len(frames)):
        img = cv2.filter2D(frames[fr], -1, ref)
        if ct % 700 == 0:
            print(ct)
        val = 0
        global l, r, u, d, pos_x, pos_y
        l = 0
        r = len(img[0])
        u = 0
        d = len(img)
        if fr > 0:
            l = pos_y - P
            u = pos_x - P
            r = pos_y + P
            d = pos_x + P
        for i in range(u, d + 1):
            for j in range(l, r + 1):
                if not valid(img, i, j):
                    continue
                op_count += 1
                if img[i][j] >= val:
                    val = img[i][j]
                    pos_x = i
                    pos_y = j
        cv2.rectangle(new_frames[ct], (pos_y - len(ref[0]) // 2, pos_x - len(ref) // 2),
                      (pos_y + len(ref[0]) - len(ref[0]) // 2, pos_x + len(ref) - len(ref) // 2), color=(255, 255, 0),
                      thickness=2)
        ct += 1
    return new_frames, op_count/len(frames)


def log2dSearch(frames, ref, new_frames):
    ct = 0
    op_count = 0
    global sp
    for fr in range(len(frames)):
        img = cv2.filter2D(frames[fr], -1, ref)
        if ct % 700 == 0:
            print(ct)
        val = 0
        global l, r, u, d, pos_x, pos_y, dis
        l = 0
        r = len(img[0])
        u = 0
        d = len(img)
        if fr > 0:
            global dis
            sp = P
            dis = 2 ** int(math.ceil(math.log(sp, 2)) - 1)
            while dis > 1:
                l = pos_y - sp
                u = pos_x - sp
                r = pos_y + sp
                d = pos_x + sp
                val = 0
                for i in range(u, d + 1, dis):
                    for j in range(l, r + 1, dis):
                        if not valid(img, i, j):
                            continue
                        op_count += 1
                        if img[i][j] >= val:
                            val = img[i][j]
                            pos_x = i
                            pos_y = j
                sp = sp//2
                dis = 2 ** int(math.ceil(math.log(sp, 2)) - 1)
                #print(pos_x, pos_y)
            cv2.rectangle(new_frames[ct], (pos_y - len(ref[0]) // 2, pos_x - len(ref) // 2),
                          (pos_y + len(ref[0]) - len(ref[0]) // 2, pos_x + len(ref) - len(ref) // 2),
                          color=(255, 255, 0),
                          thickness=2)
        else:
            for i in range(u, d + 1):
                for j in range(l, r + 1):
                    if not valid(img, i, j):
                        continue
                    op_count += 1
                    if img[i][j] >= val:
                        val = img[i][j]
                        pos_x = i
                        pos_y = j
            cv2.rectangle(new_frames[ct], (pos_y - len(ref[0]) // 2, pos_x - len(ref) // 2),
                          (pos_y + len(ref[0]) - len(ref[0]) // 2, pos_x + len(ref) - len(ref) // 2), color=(255, 255, 0),
                          thickness=2)
        ct += 1
    return new_frames, op_count/len(frames)
def sample(img):
    pct = 0.5
    size = (int(img.shape[0] * pct), int(img.shape[1] * pct))
    return cv2.resize(img, size)

def search(img, l, r, u, d):
    val = 0
    cntt = 0
    for i in range(u, d + 1):
        for j in range(l, r + 1):
            if not valid(img, i, j):
                continue
            cntt += 1
            if img[i][j] >= val:
                val = img[i][j]
                best_x = i
                best_y = j
    return best_x, best_y, cntt

def hierarchy(frames, ref, new_frames):
    ct = 0
    op_count = 0
    global sp
    global l, r, u, d, pos_x, pos_y, dis
    for fr in range(len(frames)):
        img = cv2.filter2D(frames[fr], -1, ref)
        if ct % 700 == 0:
            print(ct)
        if fr == 0:
            l = 0
            r = len(img[0])
            u = 0
            d = len(img)
            val = 0
            for i in range(u, d + 1):
                for j in range(l, r + 1):
                    if not valid(img, i, j):
                        continue
                    op_count += 1
                    if img[i][j] >= val:
                        val = img[i][j]
                        pos_x = i
                        pos_y = j
            cv2.rectangle(new_frames[ct], (pos_y - len(ref[0]) // 2, pos_x - len(ref) // 2),
                          (pos_y + len(ref[0]) - len(ref[0]) // 2, pos_x + len(ref) - len(ref) // 2), color=(255, 255, 0),
                          thickness=2)
        else:
            img2 = frames[fr]
            x = pos_x
            y = pos_y
            level1img = sample(cv2.GaussianBlur(img2, (5, 5), 0))
            level1ref = sample(cv2.GaussianBlur(ref, (5, 5), 0))
            level2img = sample(cv2.GaussianBlur(level1img, (5, 5), 0))
            level2ref = sample(cv2.GaussianBlur(level1ref, (5, 5), 0))
            l = pos_y//4 - P//4
            u = pos_x//4 - P//4
            r = pos_y//4 + P//4
            d = pos_x//4 + P//4
            best_x, best_y, cnt = search(cv2.filter2D(level2img, -1, level2ref), l, r, u, d)
            x1 = best_x-x//4
            y1 = best_y-y//4
            pos_x = x//2+2*x1
            pos_y = y//2+2*y1
            l = pos_y - 1
            u = pos_x - 1
            r = pos_y + 1
            d = pos_x + 1
            best_x, best_y, cnt2 = search(cv2.filter2D(level1img, -1, level1ref), l, r, u, d)
            x2 = best_x-x//2
            y2 = best_y-y//2
            pos_x = x + 2 * x2
            pos_y = y + 2 * y2
            l = pos_y - 1
            u = pos_x - 1
            r = pos_y + 1
            d = pos_x + 1
            pos_x, pos_y, cnt3 = search(cv2.filter2D(img2, -1, ref), l, r, u, d)
            cv2.rectangle(new_frames[ct], (pos_y - len(ref[0]) // 2, pos_x - len(ref) // 2),
                          (pos_y + len(ref[0]) - len(ref[0]) // 2, pos_x + len(ref) - len(ref) // 2),
                          color=(255, 255, 0),
                          thickness=2)
            # print(cnt, cnt2, cnt3)
            op_count += cnt+cnt2+cnt3
        ct += 1
    return new_frames, op_count/len(frames)

ps = [10, 20, 30, 50, 100,150, 200,250,  300,350 , 400, 500]
'''
for i in ps:
    P = i
    frames1, cnt1 = exhaust(frames, ref,actual)
    frames1, cnt2 = log2dSearch(frames, ref,actual2)
    frames1, cnt3 = hierarchy(frames, ref, actual3)
    print("P = ", P,"exhaust-", cnt1,"log2d-", cnt2,"hierarchy-", cnt3)
'''

frames1, cnt3 = hierarchy(frames, ref, actual3)
#frames1, cnt1 = exhaust(frames, ref,actual)
#frames1, cnt2 = log2dSearch(frames, ref,actual2)
#print(cnt1, cnt2, cnt3)
#print(cnt2)
'''
for i in range(len(conv)):
    for j in range(len(conv[0])):
        if(conv[i][j]>0):
            print(i, j, conv[i][j])
cv2.imshow('co',frames[0])
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

height, width, layers = frames1[0].shape
output = cv2.VideoWriter('output.mov', fourcc, fps, (width, height))
for frame in frames1:
    output.write(frame)
output.release()

# (98, 54)
'''
def conv(img, ref, l, r, u, d):
    max_val = 0
    ret_x = l
    ret_y = r

    for i in range(r-l-len(ref)+1):
        print("line29")
        for j in range(d-u-len(ref[0])+1):
            sum = 0
            #print("line31")
            global ret_x, ret_y
            if not valid(img, i+l, j+u):
                continue
            for m in range(len(ref)):
                for n in range(len(ref[0])):
                    sum += img[i+l][j+u]*ref[m][n]
            if sum>max_val:
                ret_x = i+l
                ret_y = j+u
    return ret_x, ret_y
'''
'''
P =  10 exhaust- 675.7210526315789 log2d- 253.27763157894736 hierarchy- 278.2447368421053
P =  20 exhaust- 1914.0894736842106 log2d- 262.2657894736842 hierarchy- 374.11842105263156
P =  30 exhaust- 3951.4052631578948 log2d- 299.2171052631579 hierarchy- 477.9815789473684
P =  50 exhaust- 10422.878947368421 log2d- 315.19605263157894 hierarchy- 877.4552631578947
P =  100 exhaust- 39218.45789473684 log2d- 329.51184210526316 hierarchy- 2752.680263157895
P =  150 exhaust- 76299.69210526315 log2d- 303.18684210526317 hierarchy- 4976.259210526316
P =  200 exhaust- 113726.75921052632 log2d- 336.37368421052633 hierarchy- 7392.772368421052
P =  250 exhaust- 147228.73289473684 log2d- 338.5921052631579 hierarchy- 9391.7
P =  300 exhaust- 169955.46842105262 log2d- 303.7934210526316 hierarchy- 10856.535526315789
P =  350 exhaust- 178186.67631578946 log2d- 288.1144736842105 hierarchy- 11327.268421052631
P =  400 exhaust- 178829.0 log2d- 339.7907894736842 hierarchy- 11362.640789473684
P =  500 exhaust- 178829.0 log2d- 340.4526315789474 hierarchy- 11362.640789473684
'''