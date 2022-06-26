import UartSet
import Function_Library
import image
import sensor
Detect_Target = UartSet.Target_Class()
Work_Mode = 0x03
#thresholds = [(30, 100, 15, 127, 15, 127), # generic_red_thresholds
             # (30, 100, -64, -8, -32, 32), # generic_green_thresholds
              #(0, 15, 0, 40, -80, -20)] # generic_blue_thresholds



Front_Find_Pole_Threshold = (27, 49, 65, 14, 41, 10)
Front_Find_Blob_Threshold = (0, 26, -40, -11, -8, 43)


if __name__ == "__main__":
    Templates = ["./photos/1.pgm","./photos/2.pgm","./photos/3.pgm","./photos/4.pgm","./photos/5.pgm","./photos/6.pgm","./photos/7.pgm","./photos/8.pgm"]
    Template_List = []
    for i in range(len(Templates)):
        Template_List.append(image.Image(Templates[i]))
    while True:
        #UartSet.Reset_Rgb(0,0,1)
        Function_Library.clock.tick()
        #Us100_Distance_Get = UartSet.Us100_ReceiveData()
        #print("THE US100_Distance_Send IS:",Us100_Distance_Get)
        #print("THE CURRENT MODE IS:",Work_Mode)
        Us100_Distance_Get = 200
        if(Work_Mode==0x00):
            Function_Library.sensor_initial(pixformat=sensor.RGB565,framesize=sensor.QVGA,
            windowing = (0,0,640,480),auto_gain=0,auto_whitebal=0,
            auto_exposure=0,auto_exposure_us=6000)
            sensor.set_auto_whitebal(False, rgb_gain_db = (0.0, 0.0, 0.0))
            sensor.set_auto_gain(True, gain_db_ceiling = 2.0)
            img=sensor.snapshot()
            UartSet.Set_Rgb(0,0,1)

        elif(Work_Mode==0x0D):
            Function_Library.Down_Find_Circle(Detect_Target,Work_Mode)
        elif(Work_Mode==0x07 or Work_Mode==0x08):
            Function_Library.Down_Find_Color(Detect_Target,Work_Mode)
        elif(Work_Mode==0x05):
            Function_Library.Down_Find_A_Template(Detect_Target,Work_Mode,Template_List)
        elif(Work_Mode==0x06):
            UartSet.Reset_Rgb(1,1,1)
        elif(Work_Mode==0x02):
            Function_Library.sensor_initial(pixformat=sensor.RGB565,framesize=sensor.QVGA,
            windowing = (0,0,640,480),auto_gain=0,auto_whitebal=0,
            auto_exposure=0,auto_exposure_us=6000)
            sensor.set_auto_whitebal(False, rgb_gain_db = (-4, -6, -3))
            sensor.set_auto_gain(True, gain_db_ceiling = 4.0)

            Function_Library.green_pixel_init()
            Function_Library.pixels_cnt_hor_left=Function_Library.find_green_pixel(1)
            Function_Library.pixels_cnt_hor_right=Function_Library.find_green_pixel(2)
            Function_Library.green_pixel_phrase(1)
            Function_Library.percent_hor_left=Function_Library.pixels_cnt_hor_lef/6400
            Function_Library.percent_hor_right=Function_Library.pixels_cnt_hor_right/6400
            Detect_Target.Target_Reserved1=int(250*Function_Library.percent_hor_left)
            Detect_Target.Target_Reserved2=int(250*Function_Library.percent_hor_right)

        elif(Work_Mode==0x03):
            Function_Library.sensor_initial(pixformat=sensor.RGB565,framesize=sensor.QVGA,
            windowing = (0,0,640,480),auto_gain=0,auto_whitebal=0,
            auto_exposure=0,auto_exposure_us=6000)
            sensor.set_auto_whitebal(False, rgb_gain_db = (-4, -6, -3))
            sensor.set_auto_gain(True, gain_db_ceiling = 4.0)

            Function_Library.green_pixel_init()
            Function_Library.pixels_cnt_ver_up=Function_Library.find_green_pixel(3)
            Function_Library.pixels_cnt_ver_down=Function_Library.find_green_pixel(4)
            #Function_Library.green_pixel_phrase(2)
            Function_Library.percent_ver_up=Function_Library.pixels_cnt_ver_up/4800
            Function_Library.percent_ver_down=Function_Library.pixels_cnt_ver_down/4800
            Detect_Target.Target_Reserved3=int(250*Function_Library.percent_ver_up)
            Detect_Target.Target_Reserved4=int(250*Function_Library.percent_ver_down)

        UartSet.QuadRotor_SendData(Us100_Distance_Get,Detect_Target,Work_Mode)
        Work_Mode= UartSet.QuadRotor_ReceiveData(Work_Mode)
        #print(Function_Library.percent_hor_left,Function_Library.percent_hor_right,Function_Library.percent_ver_up,Function_Library.percent_ver_down)
        #print(sensor.get_rgb_gain_db(),sensor.get_gain_db())
        #print(percent_hor_left,percent_hor_right,percent_ver_up,percent_ver_down)
        #print(Detect_Target.Target_Reserved3)
        #print("FPS %f" % Function_Library.clock.fps())
