from pyb import UART,LED,Timer,Pin
#串口定义
QuadRotor_Uart = UART(3,921600)
Us100_Uart=UART(1,9600)
Us100_State,Us100_Data_List=0,[]
QuadRotor_State,QuadRotor_Data_List=0,[]
QuadRotor_Effective_Data_Len,QuadRotor_Total_Data_Len = 0,0


class Target_Class(object):
    Target_x,Target_y = 0,0
    Target_Pixel,Target_Flag = 0,0
    Target_State,Target_Angle = 0,0
    Target_Distance,Target_Apriltag_Id = 0,0
    Target_Img_Width,Target_Img_Height = 0,0
    Target_Reserved1,Target_Reserved2 = 0,0
    Target_Reserved3,Target_Reserved4 = 0,0
    Target_Fps = 0
    Target_Sensor1,Target_Sensor2 = 0,0
    Target_Sensor3,Target_Sensor4 = 0,0
    def Target_Reset_AllData(self):
        self.Target_Pixel,self.Target_Flag = 0,0
        self.Target_x,self.Target_y = 0,0
        self.Target_State,self.Target_Angle = 0,0
        self.Target_Distance,self.Target_Apriltag_Id = 0,0
        self.Target_Img_Width,self.Target_Img_Height = 0,0
        self.Target_Reserved3,self.Target_Reserved2=0,0

def QuadRotor_SendData(Us100_Distance_,Target,Mode):
    Us100_Distance_Send = int(Us100_Distance_*10.0)
    Target.Target_Sensor1 = Us100_Distance_Send
    Send_Data = bytearray([0xFF,0xFC,0xA0+Mode,0x00,
                       Target.Target_x>>8,Target.Target_x,
                       Target.Target_y>>8,Target.Target_y,
                       Target.Target_Pixel>>8,Target.Target_Pixel,
                       Target.Target_Flag,Target.Target_Flag,
                       Target.Target_Angle>>8,Target.Target_Angle,
                       Target.Target_Distance>>8,Target.Target_Distance,
                       Target.Target_Apriltag_Id>>8,Target.Target_Apriltag_Id,
                       Target.Target_Img_Width>>8,Target.Target_Img_Width,
                       Target.Target_Img_Height>>8,Target.Target_Img_Height,
                       Target.Target_Fps,Target.Target_Reserved1,
                       Target.Target_Reserved2,Target.Target_Reserved3,
                       Target.Target_Reserved4,
                       Target.Target_Sensor1>>8,Target.Target_Sensor1,
                       Target.Target_Sensor2>>8,Target.Target_Sensor2,
                       Target.Target_Sensor3>>8,Target.Target_Sensor3,
                       Target.Target_Sensor4>>8,Target.Target_Sensor4,
                       0x00])
    Send_Data[3] = len(Send_Data)-5
    Send_Data_Sum = 0
    for i in range(0,len(Send_Data)-1):
        Send_Data_Sum = Send_Data_Sum+Send_Data[i]
    Send_Data[len(Send_Data)-1] = Send_Data_Sum
    QuadRotor_Uart.write(Send_Data)
    return 0
def QuadRotor_Receive_Anl(QuadRotor_Data_List,Num):
    Sum = 0
    for i in range(Num-1):
        Sum+=QuadRotor_Data_List[i]
    Sum = Sum%256
    if Sum!=QuadRotor_Data_List[Num-1]:
        return
    if QuadRotor_Data_List[2]==0xA0:
        Mode = QuadRotor_Data_List[4]
        if(QuadRotor_Data_List[4] == 0x0B or QuadRotor_Data_List[4]==0x0D):
            Snap_Finish_=1
        print("setting work mode success:",Mode)
    return Mode

def QuadRotor_ReceiveData(Current_Mode):
    global QuadRotor_State,QuadRotor_Data_List
    Snap_Finish = 0
    Mode = Current_Mode
    QuadRotor_Data_Len = QuadRotor_Uart.any()
    for i in range(0,QuadRotor_Data_Len):
        QuadRotor_Data = QuadRotor_Uart.readchar()
        if QuadRotor_State==0 and QuadRotor_Data==0xFF:
            QuadRotor_State=1
            QuadRotor_Data_List.append(QuadRotor_Data)
        elif QuadRotor_State==1 and QuadRotor_Data==0xFE:
            QuadRotor_State=2
            QuadRotor_Data_List.append(QuadRotor_Data)
        elif QuadRotor_State==2 and QuadRotor_Data<0xFF:
            QuadRotor_State=3
            QuadRotor_Data_List.append(QuadRotor_Data)
        elif QuadRotor_State==3 and QuadRotor_Data<50:
            QuadRotor_State=4
            QuadRotor_Effective_Data_Len,QuadRotor_Total_Data_Len = QuadRotor_Data,QuadRotor_Data+5
            QuadRotor_Data_List.append(QuadRotor_Data)
        elif QuadRotor_State==4 and QuadRotor_Effective_Data_Len>0:
            QuadRotor_Effective_Data_Len-=1
            QuadRotor_Data_List.append(QuadRotor_Data)
            if(QuadRotor_Effective_Data_Len==0):
                QuadRotor_State = 5
        elif QuadRotor_State==5:
            QuadRotor_State = 0
            QuadRotor_Data_List.append(QuadRotor_Data)
            Mode = QuadRotor_Receive_Anl(QuadRotor_Data_List,QuadRotor_Data_List[3]+5)
            QuadRotor_Data_List = []
        else:
            QuadRotor_State = 0
            QuadRotor_Data_List = []
    return Mode

def Us100_ReceiveData():
    global Us100_State,Us100_Data_List
    Us100_Distance = 100.0
    Us100_Uart.writechar(0x55)
    Us100_Data_Len = Us100_Uart.any()
    for i in range(0, Us100_Data_Len):
        Us100_Data = Us100_Uart.readchar()
        if Us100_State==0 and Us100_Data>=0:
            Us100_Data_List.append(Us100_Data)
            Us100_State=1
        elif Us100_State==1 and Us100_Data>=0:
            Us100_Data_List.append(Us100_Data)
            Us100_State=2
        if(len(Us100_Data_List)==2):
            Us100_Distance =(Us100_Data_List[0]*256.0+Us100_Data_List[1])/10.0
        if Us100_State==2:
            Us100_State,Us100_Data_List=0,[]
    return Us100_Distance if Us100_Distance<100.0 else 100.0

def Set_Rgb(r,g,b):
    if(r):LED(1).on()
    if(g):LED(2).on()
    if(b):LED(3).on()

def Reset_Rgb(r,g,b):
    if(r):LED(1).off()
    if(g):LED(2).off()
    if(b):LED(3).off()
