from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

class MotorPair:
    def __init__(self, port1, port2):
        self.motor1 = Motor(port1)
        self.motor2 = Motor(port2)
        self.timer = StopWatch()
    def move_angle(self,amount,speed1,speed2, timeout = 1000):
        self.motor1.reset_angle(0)
        self.motor2.reset_angle(0)
        self.timer.reset()
        while abs(self.motor1.angle()) < amount or self.timer.time() < timeout:
            while abs(self.motor2.angle()) < amount or self.timer.time() < timeout:
                self.motor1.run(speed1)
                self.motor2.run(-(speed2))
        self.motor1.stop()
        self.motor2.stop()
        return "succeded"
    def move_tank(self,amount, speed1, speed2):    
        self.motor1.run(speed1)
        self.motor2.run(-(speed2))
        wait(amount)
        self.motor1.stop()
        self.motor2.stop()
    def start_tank(self, speed1, speed2):
        self.motor1.run(speed1)
        self.motor2.run(-(speed2))
    def stop_tank(self):
        self.motor1.run(0)
        self.motor2.run(0)


def updateLog():
    global logs
    global name
    global move_side
    global log 
    logs = [name,move_side,log]

def axis_correction(set_point_c = 40, set_point_s = 75 ):
    global corner
    global name
    global move_side
    global log
    if name != "axis correction **Corner**":
        corner = 0
    if corner == 3:
        motors.stop_tank()
        if sd.reflection() < set_point_s:
            while sd.reflection() < set_point_s:
                motors.start_tank(-150,0)
                move_side = 'right'
        if se.reflection() < set_point_s : 
            while se.reflection() < set_point_s:
                motors.start_tank(0,-150)
                move_side = 'left'
        corner = 0
        name = "axis correction **Suave**"
        log = 'succeded'
    else:
        if sd.reflection() > set_point_c:
            while sd.reflection() > set_point_c:
                motors.start_tank(300,-50)
                move_side = 'left'
            corner += 1
        else:
            while se.reflection() > set_point_c:
                motors.start_tank(-50,300)
                move_side = 'right'
            corner += 1
        name = "axis correction **Corner**"
        log = 'succeded'
    updateLog()
    return [name, move_side, log]
    
       


def proportionalAlign(errorE,errorD, kP):
    global name
    global move_side
    global log
    name ='proportionalAlign'
    move_side = ''
    log='failed'
    leftMotorSpd = 50 + errorE * kP * 4.7
    rightMotorSpd = 50 + errorD * kP * 4.7
    motors.start_tank(leftMotorSpd,rightMotorSpd)
    diff_l_r = leftMotorSpd - rightMotorSpd
    if diff_l_r > 0:
        move_side = 'right'
    else:
        move_side = 'left'
    log = 'succeded'
    updateLog()
    return [name, move_side, log]
# def intersectionSolver():

def checkGreen():
    ve = se.color() == Color.GREEN
    vd = sd.color() == Color.GREEN
    if ve or vd:
        return True
    # if ve and vd:
    #     motors.stop_tank()
    #     wait(100)
    #     return True
    # else:
    #     if ve:
    #         wait(150)
    #         motors.stop_tank()
    #         wait(700)
    #         print('verdeEsquerda')
    #         if se.color() == Color.GREEN:
    #             return True
    #     if vd:
    #         wait(150) 
    #         motors.stop_tank()
    #         wait(700)
    #         print('verdeDireita')
    #         if sd.color() == Color.GREEN:
    #             return True
    # return False



hub = PrimeHub()

setPoint = 50
darkest = ""

# defining motors
motors = MotorPair(Port.A,Port.B)

# defining sensors
u2 = UltrasonicSensor(Port.E)
sc = ColorSensor(Port.D)
sd = ColorSensor(Port.C)
se = ColorSensor(Port.F)

# defining the log list
name = 'Beginning run'
move_side = 'None'
log = 'succeded'
logs = [name,move_side,log]
corner = 0

if __name__ == "__main__":
    while 1:
        se_value = se.reflection()
        sd_value = sd.reflection()
        sc_value = sc.reflection()
        errord = se_value - setPoint
        errore = sd_value - setPoint
        if se_value > 50 and sd_value > 50 and sc_value < 45:
            print(sc_value)
            proportionalAlign(errore,errord,1.2)
        else:
            if checkGreen() == True:
                print('-------- Green founded --------')
            else:
                if se_value > 80 and sd_value > 80 and sc_value > 80:
                    if logs[0] == 'proportionalAlign':
                        print('------- Possible Gap ---------')
                    else:
                        print("xxxxxxxxx  Recovery  xxxxxxxxx")
                else:
                    motors.stop_tank()
                    if se_value > sd_value: 
                        darkest = "direita"
                    if sd_value > se_value:
                        darkest = "esquerda"
                    if se_value < 30 and sd_value < 30:
                        print("------ crossing line ------")
                        motors.move_tank(1000, 200, 200)
                        se_value = se.reflection()
                        sd_value = sd.reflection()
                        sc_value = sc.reflection()
                        errord = se_value - setPoint
                        errore = sd_value - setPoint
                        if se_value > 60 and sd_value > 60 and sc_value < 30:
                            proportionalAlign(errore,errord,0.8)
                        else:
                            print('back until see black')
                            motors.move_tank(2000, -200, -200)
                            print('Axis Correction')
                            axis_correction()
                    else:
                        if darkest == "esquerda":        
                            print('Axis Correction')
                            axis_correction()
                        if darkest == "direita":        
                            print('Axis Correction')
                            axis_correction()

        print(logs,corner)
        msg = str(se.reflection()) + ',' + str(sc.reflection()) + ',' + str(sd.reflection())
        print(msg)
