import tkinter
from tkinter import ttk, messagebox
import PIL
from PIL import ImageTk, Image, ImageDraw, ImageFont
import time
import threading

global username 
global password 
global cursor_sta
global window_sta

username = ""
password = ""
cursor_sta = 1
window_sta = 1

global amp_holder 
global vol_holder 
global power_holder 
global arm_status
global l_speed
global r_speed
global pixy_cam
global touch
global arm_change_time
global protocal_list


amp_holder = 0
vol_holder = 0
power_holder = []
arm_status = False
l_speed = 0
r_speed = 0
pixy_cam = {}
touch = False
protocal_list = []
arm_change_time = 0

pixy_cam["vaild"] = False
pixy_cam["x"] = 0
pixy_cam["y"] = 0
pixy_cam["SIG"] = ""

import mqtt_remote_method_calls as com


class dataUploader(object):

    def rcv_pwr_data(self, amp, vol):
        global amp_holder 
        global vol_holder
        amp_holder = int(amp)
        vol_holder = int(vol)
        power_holder.append(vol_holder/10000/100*amp_holder/10000/100)
        reDraw()
    
    def set_arm_up(self):
        global arm_status
        global arm_change_time
        arm_status = True
        arm_change_time = time.time()
        reDraw()
    
    def set_arm_down(self):
        global arm_status
        
        arm_status = False
        arm_change_time = time.time()
        reDraw()

    def rcv_speed(self, speedL, speedR):
        global l_speed
        global r_speed
        l_speed = int(speedL)
        r_speed = int(speedR)
        reDraw()

def reDraw():
    global arm_change_time

    pilImage_raw = Image.open("./lego_dashboard.gif")
    pilImage = Image.new("RGB", pilImage_raw.size)
    pilImage.paste(pilImage_raw)
    fnt = ImageFont.truetype('/Library/Fonts/Trebuchet MS.ttf', 15)

    d = ImageDraw.Draw(pilImage)

    cnt = 0
    for cnt_p in power_holder[-170:]:
        d.line((63+cnt, 300, 63+cnt, 300-10*cnt_p), fill=(220,220,220))
        cnt += 1

    d.text((250,199), "Voltage: " + str(int(vol_holder/10000)/100) + "V", font=fnt)
    d.text((250,235), "Current: " + str(int(amp_holder/10000)/100) + "A", font=fnt)
    d.text((250,269), "Power:   " + str(int(vol_holder/10000/100*amp_holder/10000)/100) + "W", font=fnt)

    cnt = 0
    protocal_list = mqtt_client.getMessage()
    for cnt_p in protocal_list[-8:]:
        d.text((67,424+15*cnt),  cnt_p[:41], font=fnt)
        cnt += 1

    if l_speed == 0:
        d.text((1008,415), "Status: Stop / Break", font=fnt)
    else:
        d.text((1008,415), "Status: Running", font=fnt)

    d.text((1008,444), "Speed: " + str(l_speed) + " °/s", font=fnt)

    if r_speed == 0:
        d.text((373,207), "Status: Stop / Break", font=fnt)
    else:
        d.text((373,207), "Status: Running", font=fnt)

    d.text((373,237), "Speed: " + str(r_speed) + " °/s", font=fnt)

    if time.time() - arm_change_time < 5:
        if arm_status:
            d.text((973,93), "Status: Rising", font=fnt)
            d.text((973,120), "Speed: 600 °/s", font=fnt)
            d.text((992,182), "Status: Inactive", font=fnt)
        else:
            d.text((973,93), "Status: Lowing", font=fnt)
            d.text((973,120), "Speed: -600 °/s", font=fnt)
            d.text((992,182), "Status: Inactive", font=fnt)
    else:
        if arm_status:
            d.text((973,93), "Status: Up", font=fnt)
            d.text((973,120), "Speed: 0 °/s", font=fnt)
            d.text((992,182), "Status: Active", font=fnt)
        else:
            d.text((973,93), "Status: Down", font=fnt)
            d.text((973,120), "Speed: 0 °/s", font=fnt)
            d.text((992,182), "Status: Inactive", font=fnt)
            

    d.text((373,413), "Deteted: Black", font=fnt)

    d.text((1005,248), "Target: SIG1 Setted", font=fnt)
    d.text((1005,280), "Status: Waiting", font=fnt)


    image = ImageTk.PhotoImage(pilImage)
    imglabel.configure(image=image)
    imglabel.grid(row=1, column=1)
    imglabel.image = image


def mouse_press_main(event):
    print(event.x, event.y)
    if event.x > 373 and event.x < 973 and event.y > 318 and event.y < 428:
        print("RUNNING FORWARD, SPEED: ", (673-event.x)/300*600)
        mqtt_client.send_message("constant_moving", [int((673-event.x)/300*600), int((673-event.x)/300*600)])
        return

    if event.x > 662 and event.x < 802 and event.y > 90 and event.y < 269:
        print("RUNNING RIGHT")
        mqtt_client.send_message("constant_moving", [300,-300])
        return

    if event.x > 617 and event.x < 846 and event.y > 472 and event.y < 584:
        print("RUNNING LEFT")
        mqtt_client.send_message("constant_moving", [-300,300])
        return
        
    
    if event.x > 779 and event.x < 912 and event.y > 45 and event.y < 155:
        if arm_status == True:
            print("ARM Down")
            mqtt_client.send_message("arm_down", [])
            return
        else:
            print("ARM UP")
            mqtt_client.send_message("arm_up", [])
            return
    mqtt_client.send_message("stop",[])
    


def key_press_main(event):
    print(event.char)

def key_input(event):
    global username 
    global password 
    global cursor_sta 
    print ("pressed", repr(event.char))
    if event.char == '\x7f':
        if cursor_sta == 1 and len(username) > 0:
            username = username[:-1]
        else:
            if len(password) > 0:
                password = password[:-1]
    else:
    
        if event.char == '\t' or event.char == '\r':
            if cursor_sta == 1:
                cursor_sta = 2
            else:
                if event.char == '\r':
                    event.x = 205
                    event.y = 441
                    mouse_press(event)
                    return
                cursor_sta = 1
        else:
            if cursor_sta == 1 and len(username) < 16:
                username += event.char
            if cursor_sta == 2 and len(password) < 16:
                password += event.char


    pilImage_raw = Image.open("./lego_login.gif")
    pilImage = Image.new("RGB", pilImage_raw.size)
    pilImage.paste(pilImage_raw)

    # get a font
    fnt = ImageFont.truetype('/Library/Fonts/Trebuchet MS.ttf', 30)
    # get a drawing context
    d = ImageDraw.Draw(pilImage)

    # draw text, full opacity
    d.text((79,260), username, font=fnt)
    d.text((79,320), "*" * len(password), font=fnt)

    if cursor_sta == 2:
        d.line((45, 303, 365, 303), fill=(121,121,121))
        d.line((45, 304, 365, 304), fill=(121,121,121))

        d.line((45, 366, 365, 366), fill=(0,144,255))
        d.line((45, 367, 365, 367), fill=(0,144,255))
    else:
        d.line((45, 303, 365, 303), fill=(0,144,255))
        d.line((45, 304, 365, 304), fill=(0,144,255))

        d.line((45, 366, 365, 366), fill=(121,121,121))
        d.line((45, 367, 365, 367), fill=(121,121,121))



    image = ImageTk.PhotoImage(pilImage)
    imglabel.configure(image=image)
    imglabel.grid(row=1, column=1)
    imglabel.image = image

def update_req():
    mqtt_client.send_message("getPower", [])
    t = threading.Timer(0.5, update_req)
    t.start()



def mouse_press(event):
    global cursor_sta
    global username 
    global password
    print(event.x ,event.y)
    if event.x > 45 and event.x < 364 and event.y > 423 and event.y < 470:
        print("Button Click")
        if username != "lego04":
            messagebox.showerror("Error", "Unauthorized Username")
            username = ""
            password = ""
            event.char = ""
            key_input(event)
            return
        
        if password != "csse120":
            messagebox.showerror("Error", "Invaild Username or Password")
            username = ""
            password = ""
            event.char = ""
            key_input(event)
            return
        
        pilImage_raw = Image.open("./lego_dashboard.gif")
        pilImage = Image.new("RGB", pilImage_raw.size)
        pilImage.paste(pilImage_raw)
        image = ImageTk.PhotoImage(pilImage)
        imglabel.configure(image=image)
        imglabel.grid(row=1, column=1)
        imglabel.image = image
        root.bind("<Button-1>", mouse_press_main)
        root.bind("<Key>", key_press_main)

        _dataUploader = dataUploader()
        

        global mqtt_client
        mqtt_client = com.MqttClient(_dataUploader)
        mqtt_client.connect_to_ev3()

        t = threading.Timer(1.0, update_req)
        t.start()
        return
        
        
    if event.x > 68 and event.x < 361 and event.y > 248 and event.y < 296:
        cursor_sta = 1
        print("Switch to", cursor_sta)
    if event.x > 66 and event.x < 361 and event.y > 310 and event.y < 356:
        cursor_sta = 2
        print("Switch to", cursor_sta)
    event.char = ""
    key_input(event)
    
    
    

    


root = tkinter.Tk()

    # The values from the Pixy range from 0 to 319 for the x and 0 to 199 for the y.
    
pilImage = Image.open("./lego_login.gif")
    

    # get a font
fnt = ImageFont.truetype('/Library/Fonts/Trebuchet MS.ttf', 30)
    # get a drawing context
d = ImageDraw.Draw(pilImage)

    # draw text, full opacity

image = ImageTk.PhotoImage(pilImage)
global imglabel 
imglabel = ttk.Label(root, image=image)
imglabel.grid(row=1, column=1)

event = tkinter.Event()
event.char = ""
key_input(event)
    
root.bind("<Key>", key_input)
root.bind("<Button-1>", mouse_press)
root.mainloop()





