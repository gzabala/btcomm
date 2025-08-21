import serial
import time
import threading

class Comm:
    def __init__(self):
        self.port = None
        self.MOT4 = 30  # Constant for motor 4 adjustment, can be tuned as needed

    def is_connected(self):
        return self.port != None and self.port.is_open
    
    def connect(self, port_name):
        if self.is_connected(): return False

        port = serial.Serial(port_name, baudrate=9600)
        if port.is_open:
            self.port = port
            # self.start_debug_thread()
            return True
        else:
            return False
        
    def disconnect(self):
        if self.is_connected():
            self.port.close()
            self.port = None

    def start_debug_thread(self):
        t = threading.Thread(target=lambda: self.debug_printout())
        t.start()

    def debug_printout(self):
        try:
            while self.is_connected():
                line = self.port.readline()
                print(line.decode("utf-8"))
        except Exception:
            print("ERROR reading! Bye...")
            self.disconnect()

    def set_motors(self, motor_1, motor_2, motor_3, motor_4):
        if not self.is_connected(): return

        directions = 0
        if motor_1 > 0: directions |= (1 << 0)
        if motor_2 > 0: directions |= (1 << 1)
        if motor_3 > 0: directions |= (1 << 2)
        if motor_4 > 0: directions |= (1 << 3)

        if motor_1 > 255: motor_1 = 255
        if motor_1 < -255: motor_1 = -255
        if motor_2 > 255: motor_2 = 255
        if motor_2 < -255: motor_2 = -255
        if motor_3 > 255: motor_3 = 255
        if motor_3 < -255: motor_3 = -255
        if motor_4 > 255: motor_4 = 255
        if motor_4 < -255: motor_4 = -255

        msg = bytes([1, directions, abs(motor_1), abs(motor_2), abs(motor_3), abs(motor_4)])
        self.port.write(msg)

    # def turn(self, speed):
    #     if not self.is_connected(): return

    #     is_clockwise = speed > 0

    #     msg = bytes([2, is_clockwise, abs(speed)])
    #     self.port.write(msg)

    def turn(self, speed):
        if not self.is_connected(): return

        is_clockwise = speed > 0

        if speed<0:
            speed4=speed-self.MOT4
        else:
            speed4=speed+self.MOT4

        self.set_motors(speed, speed, speed, speed4)

    def turn_left(self, speed=255):
        self.turn(-speed)

    def turn_right(self, speed=255):
        self.turn(speed)

    # def move_lr(self, speed):
    #     if not self.is_connected(): return

    #     is_left = speed < 0

    #     msg = bytes([3, is_left, abs(speed)])
    #     self.port.write(msg)
    
    
    def move_lr(self, speed):
        self.MOT4 = 0  # Adjust this constant as needed
        if not self.is_connected(): return

        is_left = speed < 0

        speed1=-speed
        speed2=speed
        speed3=-speed
        if speed<0:
            speed4=speed-self.MOT4
        elif speed>0:
            speed4=speed+self.MOT4
        else:
            speed4=0

        self.set_motors(speed1, speed2, speed3, speed4)

    def move_left(self, speed=255):
        self.move_lr(-speed)
    
    def move_right(self, speed=255):
        self.move_lr(speed)

    def move_fb(self, speed):
        self.MOT4 = 70  # Adjust this constant as needed
        if not self.is_connected(): return

        speed1 = speed
        speed2= -speed
        speed3= -speed
        speed4 = speed

        if speed<0:
            speed4=max(speed-self.MOT4,255)
        elif speed>0:
            speed4=min(speed+self.MOT4,255)
        else:
            speed4=0

        self.set_motors(speed1, speed2, speed3, speed4)

    def move_forward(self, speed=255):
        self.move_fb(speed)

    def move_backward(self, speed=255):
        self.move_fb(-speed)

    def stop(self):
        self.set_motors(0, 0, 0, 0)

    def readline(self):
        return self.port.readline() # TODO(Richo): Just for debugging...


## Example
comm = Comm()
# comm.connect("COM16") # USB
comm.connect("COM14") # Bluetooth

# comm.set_motors(0, 0, 0, 60)
# time.sleep(1)
# comm.stop()

comm.move_forward(200)
# comm.stop()

# comm.move_backward(150)
# comm.stop()

# comm.turn_left(90)
# # comm.turn_left(128)
# comm.stop()

# comm.turn_right(90)
# # comm.turn_right(128)
# comm.stop()

# comm.MOT4 = 50
# comm.move_left(150)
# comm.stop()

# comm.move_right(150)
# comm.stop()

time.sleep(2)
comm.stop()

comm.disconnect()



