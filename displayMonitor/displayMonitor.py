from Adafruit_GPIO import I2C
from lib_oled96 import ssd1306
from time import sleep
from smbus import SMBus
from PIL import Image, ImageDraw, ImageFont
import socket

class Display:
    def __init__(self):
        self.lines = {
            '3B' : [],
            '13A' : [],
            '9B' : [],
            '13B' : [],
            '19B' : [],
            }
        
        self.host = '192.168.1.22'
        self.port = 5001
        self.client_socket = socket.socket()
        while 1:
            try:
                print('trying connecting to server')
                self.client_socket.connect((self.host, self.port))
                break
            except:
                sleep(3)
                
        print('server on')
        self.connection()
        # init disp connecting
        self.init_tca()
        sleep(5)
        self.oled.onoff(0)
        
        while 1:
            self.get_message()
            sleep(1)
            
    def tca_select(self, channel):
        if channel > 7:
            return
        self.tca.writeRaw8(1 << channel)
        
    def tca_set(self, mask):
        if mask > 0xff:
            return
        self.tca.writeRaw8(mask)

    def init_tca(self):
        self.tca = I2C.get_i2c_device(address=0x70)
        
        self.select_disp('all disps mobilize')
        self.texts(['2','connected'], 'inits')

    def select_disp(self, disp_num):
        if disp_num == 1:
            self.tca_select(0)
        elif disp_num == 2:
            self.tca_select(1)
        elif disp_num == 3:
            self.tca_select(2)
        elif disp_num == 4:
            self.tca_select(3)
        elif disp_num == 5:
            self.tca_select(4)
        else:
            self.tca_set(0b00011111)

    def connection(self):
        msg = '00'
        self.client_socket.send(msg.encode())

    def get_message(self):
        data = self.client_socket.recv(1024).decode()
        if not data:
            return
        
        data = data.split('/', 10)
        print(data)
        
        # disp 2
        
        # check validation and delete
        if data[0] == '':
            return False

#         elif data[0] == 'delete':
#             loop_end = False
#             for i in self.lines:
#                 for p, k in enumerate(self.lines[i]):
#                     if data[1] == k[1]:
#                         self.lines[i].pop(p)
#                         loop_end = True
#                         break
#                 if loop_end:
#                     break

        # let's delete number if there's already exist numberplate
        """
        Algorithm
        1. find number
        2_1. if exist number
            delete number
        2_2. if not exist number
            continue 
        """
        loop_end = False
        for i, k in enumerate(self.lines):
            for count, line in enumerate(self.lines[k]):
                if data[1] in line:
                    self.lines[k].pop(count)
                    loop_end = True
                    break
            if loop_end:
                break
        
        # setting datas - self.lines
        for i, k in enumerate(self.lines):
            if k == data[2]:
                loop_end = False
                for p in self.lines[k]:
                    if data[2] in p:
                        p[0] = data[0]
                        loop_end = True
                if loop_end:
                    break
                else:
                    self.lines[k].append(data)
        
        # send datas
        for i, k in enumerate(self.lines):
            self.select_disp(int(i) + 1)
            print('datas :', i, self.lines[k])
            if len(self.lines[k]) == 0:
                self.i2cbus2 = SMBus(1)
                self.oled = ssd1306(self.i2cbus2)
                self.oled.onoff(0)
            else:
                self.texts(self.lines[k])
        
    def texts(self, lines, inits = ''):
        self.i2cbus2 = SMBus(1)
        self.oled = ssd1306(self.i2cbus2)
        
        if inits == '':
            for i, line in enumerate(lines):
                direction1 = str(line[0])
                file_name = 'left_arr.png'
                if direction1 == '1':
                    file_name = 'left_arr.png'
                elif direction1 == '2':
                    file_name = 'up_arr.png'
                elif direction1 == '3':
                    file_name = 'right_arr.png'
                 
                file = '/home/pi/Desktop/python/nav_display/' + file_name
                img = Image.open(file)
                draw_text = str(line[1])
                font = ImageFont.truetype("/home/pi/Desktop/python/nav_display/Car_Num.ttf", 45)
                draw = ImageDraw.Draw(img)
                draw.text((64, 32 * i), draw_text, 'black', font)
            
                flip1 = img.transpose(Image.FLIP_LEFT_RIGHT)
                result = flip1.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            direction1 = lines[0]
            file_name = 'left_arr.png'
            if direction1 == '1':
                file_name = 'left_arr.png'
            elif direction1 == '2':
                file_name = 'up_arr.png'
            elif direction1 == '3':
                file_name = 'right_arr.png'
             
            file = '/home/pi/Desktop/python/nav_display/' + file_name
            img = Image.open(file)
            draw_text = str(lines[1])
            font = ImageFont.truetype("/home/pi/Desktop/python/nav_display/Car_Num.ttf", 45)
            draw = ImageDraw.Draw(img)
            draw.text((64, 0), draw_text, 'black', font)
        
            flip1 = img.transpose(Image.FLIP_LEFT_RIGHT)
            result = flip1.transpose(Image.FLIP_TOP_BOTTOM)
             
        displaying = result.resize((128,32)).convert('1')
        self.oled.canvas.bitmap((0,32), displaying, fill = 1)
        self.oled.display()
        
sleep(2)
display = Display()
