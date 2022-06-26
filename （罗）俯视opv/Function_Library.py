import UartSet
import sensor,image,math,time
from image import SEARCH_EX, SEARCH_DS
clock = time.clock()
sensor.reset()

last_pixformat,last_framesize=10,15
last_windowing,last_auto_gain=10,10
last_auto_whitebal,last_auto_exposure=10,10
last_auto_exposure_us=10

def sensor_initial(pixformat=sensor.RGB565,framesize=sensor.QVGA,windowing = (0,0,320,240),auto_gain=0,auto_whitebal=0,auto_exposure=1,auto_exposure_us=5000):
    global last_pixformat,last_framesize,last_windowing,last_auto_gain,last_auto_whitebal,last_auto_exposure,last_auto_exposure_us
    if(last_pixformat!=pixformat):
        sensor.set_pixformat(pixformat)
    if(last_framesize!=framesize):
        sensor.set_framesize(framesize)
    if(last_windowing!=windowing):
        sensor.set_windowing(windowing)
    if(last_auto_gain!=auto_gain):
        sensor.set_auto_gain(auto_gain)
    if(last_auto_whitebal!=auto_whitebal):
        sensor.set_auto_whitebal(auto_whitebal)
    if(last_auto_exposure!=auto_exposure or last_auto_exposure_us!=auto_exposure_us):
        sensor.set_auto_exposure(auto_exposure,exposure_us=auto_exposure_us) # 设置自动曝光
    last_pixformat=pixformat
    last_framesize=framesize
    last_windowing=windowing
    last_auto_gain=auto_gain
    last_auto_whitebal=auto_whitebal
    last_auto_exposure=auto_exposure
    last_auto_exposure_us=auto_exposure_us

th_green=(37, 54, -26, 13, -13, 25)#(30, 100, -64, -8, -32, 32)#经典绿色阈值
roi_vertical=(299,0,20,480)
roi_vertical_up=(0,0,20,240)
roi_vertical_down=(0,239,20,240)
roi_horizontal=(0,199,640,20)
roi_horizontal_right=(319,0,320,20)
roi_horizontal_left=(0,0,320,20)

pixels_cnt_ver_up=0
pixels_cnt_ver_down=0
pixels_cnt_hor_lef=0
pixels_cnt_hor_right=0

percent_ver_up=0
percent_ver_down=0
percent_hor_left=0
percent_hor_right=0

def green_pixel_init():
    pixels_cnt_ver_up=0
    pixels_cnt_ver_down=0
    pixels_cnt_hor_lef=0
    pixels_cnt_hor_right=0

    percent_ver_up=0
    percent_ver_down=0
    percent_hor_left=0
    percent_hor_right=0

def find_green_pixel(point):
    if point==1 or point==2:
        left=0
        right=0
        sensor.set_windowing(roi_horizontal)
        img=sensor.snapshot()
        green_blobs_hor_left=img.find_blobs([th_green],roi=roi_horizontal_left)
        for blobs in green_blobs_hor_left:
            left+=blobs.pixels()

        green_blobs_hor_right=img.find_blobs([th_green],roi=roi_horizontal_right)
        for blobs in green_blobs_hor_right:
            right+=blobs.pixels()
        if point==1:
            return left
        if point==2:
            return right

    if point==3 or point==4:
        up=0
        down=0
        sensor.set_windowing(roi_vertical)
        img=sensor.snapshot()
        green_blobs_ver_up=img.find_blobs([th_green],roi=roi_vertical_up)
        for blobs in green_blobs_ver_up:
            up+=blobs.pixels()

        green_blobs_ver_down=img.find_blobs([th_green],roi=roi_vertical_down)
        for blobs in green_blobs_ver_down:
            down+=blobs.pixels()
        if point==3:
            return up
        if point==4:
            return down

def green_pixel_phrase(point):
    if point==1:
        percent_hor_left=pixels_cnt_hor_lef/6400
        percent_hor_right=pixels_cnt_hor_right/6400
    if point==2:
       percent_ver_up=pixels_cnt_ver_up/4800
       percent_ver_down=pixels_cnt_ver_down/4800

def Front_Find_Pole(Target,Front_Find_Pole_Threshold,Work_Mode):
    Target.Target_Reset_AllData()

    sensor_initial(pixformat=sensor.RGB565,framesize=sensor.VGA,
          windowing = (0,240,640,100),auto_gain=0,auto_whitebal=0,
          auto_exposure=1,auto_exposure_us=5000)
    Img_Source = sensor.snapshot()
    Target.Target_Img_Width = Img_Source.width()
    Target.Target_Img_Height = Img_Source.height()
    Pixel_Max = 0
    for Blob in Img_Source.find_blobs([Front_Find_Pole_Threshold],pixels_threshold=100,merge=True,margin=50):
        if Blob.pixels()>Pixel_Max:
            Pixel_Max =  Blob.pixels()
            Blob_Max = Blob
        Img_Source.draw_rectangle(Blob_Max[0:4])
        if(Work_Mode==0x0E):UartSet.Set_Rgb(1,1,0)
        elif(Work_Mode==0x0B):UartSet.Set_Rgb(1,0,0)
        Pixel_Max = Blob_Max.pixels()
        Target.Target_Pixel = Pixel_Max
        Target.Target_Flag = 1
        Target.Target_x = Blob_Max.cx()
        Target.Target_y = Blob_Max.cy()
        Target.Target_Distance = int(1200/Blob_Max.w())
    if(Target.Target_Flag):
        Img_Source.draw_circle(Target.Target_x,Target.Target_y,15,color=127)
        Img_Source.draw_cross(Target.Target_x,Target.Target_y,color=127,size=15)
    else:
        UartSet.Reset_Rgb(1,1,1)

def Front_Find_Blob(Target,Front_Find_Blob_Threshold,Work_Mode):
    Target.Target_Reset_AllData()
    sensor_initial(pixformat=sensor.RGB565,framesize=sensor.VGA,
            windowing = (0,0,640,480),auto_gain=0,auto_whitebal=0,
            auto_exposure=1,auto_exposure_us=5000)
    Img_Source = sensor.snapshot()
    Target.Target_Img_Width = Img_Source.width()
    Target.Target_Img_Height = Img_Source.height()
    Pixel_Max = 0
    for Blob in Img_Source.find_blobs([Front_Find_Blob_Threshold],pixels_threshold=100,merge=True,margin=50):
        if Blob.pixels()>Pixel_Max:
            Pixel_Max =  Blob.pixels()
            Blob_Max = Blob
        Img_Source.draw_rectangle(Blob_Max[0:4])
        UartSet.Set_Rgb(0,1,0)
        Pixel_Max = Blob_Max.pixels()
        Target.Target_Pixel = Pixel_Max
        Target.Target_Flag = 1
        Target.Target_x = Blob_Max.cx()
        Target.Target_y = Blob_Max.cy()
        Target.Target_Distance = int(1200/Blob_Max.w())
    if(Target.Target_Flag):
        Img_Source.draw_circle(Target.Target_x,Target.Target_y,15,color=127)
        Img_Source.draw_cross(Target.Target_x,Target.Target_y,color=127,size=15)
    else:
        UartSet.Reset_Rgb(1,1,1)

def Front_Find_Qrodes():
    Target.Target_Reset_AllData()

def Down_Find_Circle(Target,Work_Mode):
    Target.Target_Reset_AllData()
    sensor_initial(pixformat=sensor.GRAYSCALE,framesize=sensor.QQVGA,
            windowing = (0,0,160,120),auto_gain=0,auto_whitebal=0,
            auto_exposure=1,auto_exposure_us=5000)
    Img_Source = sensor.snapshot().lens_corr(1.8)
    Target.Target_Img_Width = Img_Source.width()
    Target.Target_Img_Height = Img_Source.height()
    #Pixel_Max = 0

    Kernel = [-1, -1, +1,\
              -1, +8, +1,\
              -1, -1, +1]
    Img_Source.morph(1, Kernel)
    #Img_Source.binary([(100, 255)])
    Img_Source.laplacian(3, sharpen=True)
    Img_Source.binary([(100, 55)])
    #Img_Source.binary([(80, 55)])
    for Circle in Img_Source.find_circles(threshold=5000,x_stride=2,y_stride=2,x_margin=10,\
                    y_margin=10,r_margin=10,r_min=5,r_max=100,r_step=2):
        Img_Source.draw_circle(Circle.x(),Circle.y(),Circle.r(),color=(255,0,0))
        Target.Target_x = Circle.x()
        Target.Target_y = Circle.y()
        Roi_Area = [Circle.x()-Circle.r(),Circle.y()-Circle.r(),2*Circle.r(),2*Circle.r()]

Find_A_Sensor_Flag = 0
def Down_Find_A_Template(Target,Work_Mode,Templates):
    global Find_A_Sensor_Flag
    Target.Target_Reset_AllData()
    sensor_initial(pixformat=sensor.GRAYSCALE,framesize=sensor.QQVGA,
            windowing = (0,0,160,120),auto_gain=1,auto_whitebal=0,
            auto_exposure=1,auto_exposure_us=5000)
    if (Find_A_Sensor_Flag==0):
        sensor.skip_frames(time =300)
        #sensor.set_contrast(1)
        #sensor.set_gainceiling(16)
        Find_A_Sensor_Flag = 1
    Img_Source = sensor.snapshot()#.lens_corr(1.8)
    Target.Target_Img_Width = Img_Source.width()
    Target.Target_Img_Height = Img_Source.height()
    Target_Detect=0
    for Template in Templates:
        #print(Template)
        #Template = image.Image(Template)
        Target_Detect = Img_Source.find_template(Template, 0.60, step=4, search=SEARCH_EX)
    if Target_Detect:
        UartSet.Set_Rgb(1,0,0)
        Img_Source.draw_rectangle(Target_Detect,(0,0,0))
        Target.Target_x = Target_Detect[0]
        Target.Target_y = Target_Detect[1]
        Target.Target_Flag = 1
        #print(Target.Target_x,Target.Target_y)
    else:
        UartSet.Reset_Rgb(1,1,1)
def Down_Find_Square(Target,Work_Mode):
    Target.Target_Reset_AllData()
    sensor_initial(pixformat=sensor.RGB565,framesize=sensor.QVGA,
            windowing = (0,0,320,240),auto_gain=0,auto_whitebal=0,
            auto_exposure=1,auto_exposure_us=5000)
    Min_Degree = 0
    Max_Degree = 179
    Img_Source = sensor.snapshot().lens_corr(1.8)
    Lines = Img_Source.find_lines(x_stride=2,y_stride=1,threshold=1000,theta_margin = 25, rho_margin = 25)
    Line_Num = len(Lines)
    Line_List,Theta_List = [],[]
    for i,Line in enumerate(Lines):
        if((Line.theta()>=Min_Degree) and (Line.theta()<=Max_Degree)):
            Line_Theta = Line.theta()
            for j in range(i+1,Line_Num):
                Theta_Diff = abs(Line_Theta-Lines[j].theta())
                if(80<Theta_Diff<110):
                    Line_List.append(Line)
                    Line_List.append(Lines[j])
                    Theta_List.append(abs(Theta_Diff-90))
    try:
        Min_Index = Theta_List.index(min(Theta_List))
        Img_Source.draw_line(Line_List[Min_Index].line(),color=(255,0,0))
        Img_Source.draw_line(Line_List[Min_Index+1].line(),color=(255,0,0))

    except:
        pass

Down_Find_Color_Flag=0
def Down_Find_Color(Target,Work_Mode):
    global Down_Find_Color_Flag
    Target.Target_Reset_AllData()
    sensor_initial(pixformat=sensor.RGB565,framesize=sensor.QVGA,
            windowing = (0,0,320,240),auto_gain=0,auto_whitebal=0,
            auto_exposure=1,auto_exposure_us=5000)
    if(Down_Find_Color_Flag==0):
        sensor.skip_frames(time=500)
        Down_Find_Color_Flag=1
    Img_Source = sensor.snapshot()
    Roi_Area = (130,90,60,60)
    Statistic = Img_Source.get_statistics(roi = Roi_Area)
    color_l=Statistic.l_mode()
    color_a=Statistic.a_mode()
    color_b=Statistic.b_mode()
    print(color_l,color_a,color_b)
    if(20<color_l<99 and -64<color_a<-10 and -32<color_b<80):
        print("this is green")
        #UartSet.Set_Rgb(0,0,0)
        Target.Target_Reserved2 = 1
    else:
        #print("i dont know")
        #UartSet.Reset_Rgb(1,1,1)
        Target.Target_Reserved2 = 0
    #Kernel = [-3, -0, +3,\
               #   -10, +0, +10,\
               #   -3, -0, +3]
    #Img_Source.morph(1, Kernel)
    #Img_Source.laplacian(1)
    #Img_Source.bilateral(3, color_sigma=0.1, space_sigma=1)
    #Img_Source.find_edges(image.EDGE_CANNY, threshold=(50, 80))
    for l in Img_Source.find_lines(threshold = 3000, x_stride=2,y_stride=2,theta_margin = 25, rho_margin = 25):
        #Img_Source.draw_line(l.line(),color = (0,255,0),thickness=3)
        #print("theta::::::::",l.theta())
        if((0 <= l.theta()) and (l.theta() <=179)):
            if(120<l.theta() or l.theta()<70):
                Img_Source.draw_line(l.line(), color = (255, 0,0),thickness=2)
                UartSet.Set_Rgb(0,0,1)
                Target.Target_Reserved3 = 1
                Target.Target_Flag=1
                Target.Target_x = int((l.x1()+l.x2())/2)
                Target.Target_y = int((l.y1()+l.y2())/2)
                Target.Target_Angle = int(l.theta())
                print("Target.Target_x",Target.Target_x,
                    "Target.Target_y",Target.Target_y,
                    "Target.Target_angle",Target.Target_Angle)
    if(Target.Target_Reserved3==0):UartSet.Reset_Rgb(1,1,1)

def Down_Find_A(Target,Work_Mode):
    global Find_A_Sensor_Flag
    Target.Target_Reset_AllData()
    sensor_initial(pixformat=sensor.RGB565,framesize=sensor.QQVGA,
            windowing = (0,0,160,120),auto_gain=0,auto_whitebal=0,
            auto_exposure=1,auto_exposure_us=5000)
    if not(Find_A_Sensor_Flag):
        sensor.skip_frames(time = 2000)
        Find_A_Sensor_Flag = 1
    Img_Source = sensor.snapshot()#.lens_corr(1.8)
    #Img_Source.binary([(97, 223)])
    #Img_Source.histeq()
    Img_Source.laplacian(1, sharpen=True)
    Target.Target_Img_Width = Img_Source.width()
    Target.Target_Img_Height = Img_Source.height()
    Lines_Detect = Img_Source.find_line_segments(merge_distance = 0, max_theta_diff = 10)
    Lines=[]
    for line in Lines_Detect:
        if((line.x1()-line.x2())**2+((line.y1()-line.y2())**2)<1000):
            Lines.append(line)
            Img_Source.draw_line(line.line(),(255,0,0))
    lines_num = len(Lines)
    point=[]
    for i in range(0,lines_num):
        for j in range(i+1,lines_num):
            for k in range(j+1,lines_num):
                theta1 = Lines[i].theta()
                theta2 = Lines[j].theta()
                theta3 = Lines[k].theta()
                theta_sum = theta1+theta2+theta3
                a1x = (Lines[i].x1()+Lines[i].x2())/2
                a1y = (Lines[i].y1()+Lines[i].y2())/2
                a2x = (Lines[j].x1()+Lines[j].x2())/2
                a2y = (Lines[j].y1()+Lines[j].y2())/2
                a3x = (Lines[k].x1()+Lines[k].x2())/2
                a3y = (Lines[k].y1()+Lines[k].y2())/2
                if(90<theta_sum<=180 and ((a1x-a2x)**2+(a1y-a2y)**2)<150 \
                    and((a1x-a3x)**2+(a1y-a3y)**2)<150 \
                    and ((a3x-a2x)**2+(a3y-a2y)**2)<150):
                    point.append(i)
                    point.append(j)
                    point.append(k)
    if len(point)>=3:
        i = point[0]
        j= point[1]
        k=point[2]
        po_x=(Lines[i].x1()+Lines[j].x1()+Lines[k].x1()+Lines[i].x2()+Lines[j].x2()+Lines[k].x2())/6
        po_y = (Lines[i].y1()+Lines[j].y1()+Lines[k].y1()+Lines[i].y1()+Lines[j].y2()+Lines[k].y2())/6
        if(Img_Source.get_pixel(po_x,po_y)[0]>10,Img_Source.get_pixel(po_x,po_y)[1]>10):
            Target.Target_x = int(po_x)*1000
            Target.Target_y = int(po_y)*1000
            #print("detect r",po_x,po_y)
            UartSet.Set_Rgb(1,0,0)
            Img_Source.draw_circle(int(po_x),int(po_y),20,(255,255,255))
    else:
        UartSet.Reset_Rgb(1,1,1)











sensor_initial()

