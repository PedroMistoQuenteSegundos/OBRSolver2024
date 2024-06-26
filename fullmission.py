from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub()#defining the actual hub object
display = hub.display#defining the display object
yaw = hub.imu#defining the angle object of the hub

#defining display's
def executionDisplay():
    display.off()
    display.pixel(0,1)
    display.pixel(0,2)
    display.pixel(0,3)
    display.pixel(1,1)
    display.pixel(2,1)
    display.pixel(2,2)
    display.pixel(2,3)
    display.pixel(3,1)
    display.pixel(4,1)
    display.pixel(4,2)
    display.pixel(4,3)
def calibrateLeftDisplay(brightness):
    display.pixel(0,0,brightness)
    display.pixel(0,1,brightness)
    display.pixel(1,0,brightness)
    display.pixel(1,1,brightness)
    display.pixel(2,0,brightness)
    display.pixel(2,1,brightness)
    display.pixel(3,0,brightness)
    display.pixel(3,1,brightness)
    display.pixel(4,0,brightness)
    display.pixel(4,1,brightness)
def calibrateRightDisplay(brightness):
    display.pixel(0,3,brightness)
    display.pixel(0,4,brightness)
    display.pixel(1,3,brightness)
    display.pixel(1,4,brightness)
    display.pixel(2,3,brightness)
    display.pixel(2,4,brightness)
    display.pixel(3,3,brightness)
    display.pixel(3,4,brightness)
    display.pixel(4,3,brightness)
    display.pixel(4,4,brightness)
def proportionalAlignDisplay():
    display.off()
    display.pixel(0,1)
    display.pixel(0,2)
    display.pixel(0,3)
    display.pixel(1,1)
    display.pixel(1,3)
    display.pixel(2,1)
    display.pixel(2,2)
    display.pixel(2,3)
    display.pixel(3,1)
    display.pixel(4,1)
def axisCorrectionDisplay():
    display.off()
    display.pixel(0,2)
    display.pixel(1,1)
    display.pixel(1,3)
    display.pixel(2,1)
    display.pixel(2,2)
    display.pixel(2,3)
    display.pixel(3,1)
    display.pixel(3,3)
    display.pixel(4,1)
    display.pixel(4,3)
def intersectionSolverDisplay():
    display.off()
    display.pixel(0,2)
    display.pixel(2,2)
    display.pixel(3,2)
    display.pixel(4,2)
def recoveryTaskDisplay():
    display.off()
    display.pixel(0,1)
    display.pixel(0,2)
    display.pixel(0,3)
    display.pixel(1,1)
    display.pixel(1,3)
    display.pixel(2,1)
    display.pixel(2,2)
    display.pixel(3,1)
    display.pixel(3,3)
    display.pixel(4,1)
    display.pixel(4,3)
def desviarObsDisplay():
    display.off()
    display.pixel(0,1)
    display.pixel(0,2)
    display.pixel(1,1)
    display.pixel(1,3)
    display.pixel(2,1)
    display.pixel(2,3)
    display.pixel(3,1)
    display.pixel(3,3)
    display.pixel(4,1)
    display.pixel(4,2)

#creating motor pair object
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
        self.motor1.hold()
        self.motor2.hold()

#creating update log function
def updateLog(log):
    global logs
    if len(log) != 3:
        return False
    if log != logs[-1]:
        logs.append(log)
        return True

#creating the axis correction function
def axis_correction(last_move, set_point_c = 40, set_point_s = 75):
    axisCorrectionDisplay()
    global corner
    name = ''
    move_side = ''
    log = ''
    if last_move != "axis correction **Corner**" and last_move != "axis correction **Suave**":
        corner = 0
    if corner >= 3:
        motors.stop_tank()
        if sd.reflection() < set_point_s:
            while sd.reflection() < set_point_s:
                motors.start_tank(-150,0)
                move_side = 'right'
        if se.reflection() < set_point_s : 
            while se.reflection() < set_point_s:
                motors.start_tank(0,-150)
                move_side = 'left'
        if corner == 5:
            corner == 0
        name = "axis correction **Suave**"
        log = 'succeded'
    else:
        if sd.reflection() > se.reflection():
            while sd.reflection() > set_point_c:
                motors.start_tank(300,-50)
                move_side = 'right'
            corner += 1
        else:
            while se.reflection() > set_point_c:
                motors.start_tank(-50,300)
                move_side = 'left'
            corner += 1
        name = "axis correction **Corner**"
        log = 'succeded'
    return [name, move_side, log]

#creating the proportional align function
def proportionalAlign(errorE,errorD, kP):
    proportionalAlignDisplay()
    name ='proportional align'
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
    return [name, move_side, log]

#creating intersection object
class Intersection:
    def __init__(self, se, sd, green_values):
        self.se = se
        self.sd = sd
    def intersectionSolver(self, valores):
        se = self.se
        sd = self.sd
        last_values = valores
        intersectionSolverDisplay()
        name = 'intersectionSolver'
        move_side = ''
        while valores[0] != False or valores[1] != False:
            if valores[0] == True and valores[1] == True:
                last_values = valores
                break
            motors.start_tank(100,100)
            wait(200)
            last_values = valores
            valores = self.checkGreen(green_values)
        valores = last_values
        motors.stop_tank()
        if valores[0] == True and valores[1] == True:
            print('dar voltinha')
            if se.reflection() > 50 or sd.reflection() > 50 :
                print('fake double')
                return [name,'','Failed']
            motors.move_tank(1000, 350, 350)
            while se.reflection() > 80 and sd.reflection() > 80 :
                motors.start_tank(350, -350)
            motors.stop_tank()
            wait(1000)
        else:
            if valores[0] == True:
                if se.reflection() > 50:
                    print('fake left')
                    return [name,'','Failed']
                print('esquerdinha')
                motors.stop_tank()
                wait(1000)
                motors.start_tank(300,0)
                wait(1000)
                motors.stop_tank()
                move_side = 'left'
            else:
                if sd.reflection() > 50 :
                    print('fake right')
                    return [name,'','Failed']
                print('direitinha')
                motors.stop_tank()
                motors.start_tank(0,300)
                wait(1000)
                while se.reflection() > 80 and sd.reflection() > 80 :
                    motors.start_tank(0,300)
                motors.stop_tank()
                wait(1000)
                move_side = 'right'
        name = 'intersectionSolver'
        log = 'succeded'
        return [name,move_side,log]
    def getGreenValues(self,side):
        hsv_min = [0,0,0]
        hsv_max = [0,0,0]
        hsv_med = [0,0,0]
        if side == 'left':
            sensor = self.se
        elif side == "right":
            sensor = self.sd
        for x in range(200):
            wait(10)
            if side == "right":
                calibrateRightDisplay(int((x+1)/2))
            if side == "left":
                calibrateLeftDisplay(int((x+1)/2))
            hsv_obj = sensor.hsv()
            hsv_med[0] += hsv_obj.h
            hsv_med[1] += hsv_obj.s
            hsv_med[2] += hsv_obj.v
            print(hsv_med)
        for i in range(3):
            hsv_med[i] = hsv_med[i]/200
            hsv_min[i] = hsv_med[i] - 20
            hsv_max[i] = hsv_med[i] + 20  
            # if hsv_obj.h < hsv_min[0] or hsv_min[0] == 0 :
            #     hsv_min[0] = hsv_obj.h
            # if hsv_obj.s < hsv_min[1] or hsv_min[1] == 0 :
            #     hsv_min[1] = hsv_obj.s
            # if hsv_obj.v < hsv_min[2] or hsv_min[2] == 0 :
            #     hsv_min[2] = hsv_obj.v
            # if hsv_obj.h > hsv_max[0]:
            #     hsv_max[0] = hsv_obj.h
            # if hsv_obj.s > hsv_max[1]:
            #     hsv_max[1] = hsv_obj.s
            # if hsv_obj.v > hsv_max[2]:
            #     hsv_max[2] = hsv_obj.v
            
            wait(50)
        hsv_values = [hsv_min, hsv_max]
        print(hsv_values)
        return hsv_values
    def checkGreen(self, valores):
        valuesE = valores[0]
        valuesD = valores[1]
        sensor_d = self.sd.hsv()
        sensor_e = self.se.hsv()
        direita = False
        esquerda = False
        # print(sensor)
        # if sensor.h < values[0][0] or sensor.h > values[1][0]:
        #     return False
        # if sensor.s < values[0][1] or sensor.s > values[1][1]:
        #     return False
        # if sensor.v < values[0][2] or sensor.v > values[1][2]:
        #     return False
        if sensor_d.h > valuesD[0][0] and sensor_d.h < valuesD[1][0]:
            if sensor_d.s > valuesD[0][1] and sensor_d.s < valuesD[1][1]:
                if sensor_d.v > valuesD[0][2] and sensor_d.v < valuesD[1][2]:
                    direita = True
        if sensor_e.h > valuesE[0][0] and sensor_e.h < valuesE[1][0]:
            if sensor_e.s > valuesE[0][1] and sensor_e.s < valuesE[1][1]:
                if sensor_e.v > valuesE[0][2] and sensor_e.v < valuesE[1][2]:
                    esquerda = True
        return [esquerda, direita]

#creating recovery task function
def recoveryTask():
    recoveryTaskDisplay()
    # global logs
    # global name 
    # global move_side
    # global log 
    # if logs[0] == "proportionalAlign":
    #     timeout = 0
    #     while se.reflection() > 20 and sc.reflection() > 20 and sd.reflection() > 20 and timeout < 3000 :
    #         motors.start_tank(-200,-200)
    #         wait(10)
    #         timeout += 10
    #     motors.stop_tank()
    #     if se.reflection() < 20 or sc.reflection() < 20 or sd.reflection() < 20:
    #         name = "recovery task"
    #         move_side = move_side
    #         log = "succeded"
    #         updateLog()
    #         return "succeded"
    #     else:
    #         name = "recovery task"
    #         move_side = move_side
    #         log = "failed"
    #         updateLog()
    #         return "succeded"
    # if logs[0] == "axis correction" or logs[0] == "intersection solver":
    #     if logs[0] == "intersection solver":
    #         if logs[1] == "right":
    #             logs[1] = "left"
    #         if logs[1] == "left":
    #             logs[1] = "right"
    #     yaw.reset_heading()
    #     if logs[1] == "right":
    #         motors.start_tank(-200,200)
    #         while yaw.heading() >= -90:
    #             if se.reflection() < 20 or sd.reflection() < 20:
    #                 name = "recovery task"
    #                 move_side = "left"
    #                 log = "succeded"
    #                 updateLog()
    #                 return "succeded"
    #             else:
    #                 timeout = 0
    #                 while se.reflection() > 20 and sc.reflection() > 20 and sd.reflection() > 20 and timeout < 3000 :
    #                     motors.start_tank(-200,-200)
    #                     wait(10)
    #                     timeout += 10
    #                 motors.stop_tank()
    #                 if se.reflection() < 20 or sc.reflection() < 20 or sd.reflection() < 20:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "succeded"
    #                     updateLog()
    #                     return "succeded"
    #                 else:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "failed"
    #                     updateLog()
    #                     return "succeded"
    #         yaw.reset_heading()
    #         motors.start_tank(200,-200)
    #         while yaw.heading() <= 90:
    #             if se.reflection() < 20 or sd.reflection() < 20:
    #                 name = "recovery task"
    #                 move_side = "right"
    #                 log = "succeded"
    #                 updateLog()
    #                 return "succeded"
    #             else:
    #                 timeout = 0
    #                 while se.reflection() > 20 and sc.reflection() > 20 and sd.reflection() > 20 and timeout < 3000 :
    #                     motors.start_tank(-200,-200)
    #                     wait(10)
    #                     timeout += 10
    #                 motors.stop_tank()
    #                 if se.reflection() < 20 or sc.reflection() < 20 or sd.reflection() < 20:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "succeded"
    #                     updateLog()
    #                     return "succeded"
    #                 else:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "failed"
    #                     updateLog()
    #                     return "succeded"
    #     if logs[1] == "left":
    #         motors.start_tank(200,-200)
    #         while yaw.heading() <= 90:
    #             if se.reflection() < 20 or sd.reflection() < 20:
    #                 name = "recovery task"
    #                 move_side = "right"
    #                 log = "succeded"
    #                 updateLog()
    #                 return "succeded"
    #             else:
    #                 timeout = 0
    #                 while se.reflection() > 20 and sc.reflection() > 20 and sd.reflection() > 20 and timeout < 3000 :
    #                     motors.start_tank(-200,-200)
    #                     wait(10)
    #                     timeout += 10
    #                 motors.stop_tank()
    #                 if se.reflection() < 20 or sc.reflection() < 20 or sd.reflection() < 20:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "succeded"
    #                     updateLog()
    #                     return "succeded"
    #                 else:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "failed"
    #                     updateLog()
    #                     return "succeded"
    #         yaw.reset_heading()
    #         motors.start_tank(-200,200)
    #         while yaw.heading() >= -90:
    #             if se.reflection() < 20 or sd.reflection() < 20:
    #                 name = "recovery task"
    #                 move_side = "left"
    #                 log = "succeded"
    #                 updateLog()
    #                 return "succeded"
    #             else:
    #                 timeout = 0
    #                 while se.reflection() > 20 and sc.reflection() > 20 and sd.reflection() > 20 and timeout < 3000 :
    #                     motors.start_tank(-200,-200)
    #                     wait(10)
    #                     timeout += 10
    #                 motors.stop_tank()
    #                 if se.reflection() < 20 or sc.reflection() < 20 or sd.reflection() < 20:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "succeded"
    #                     updateLog()
    #                     return "succeded"
    #                 else:
    #                     name = "recovery task"
    #                     move_side = move_side
    #                     log = "failed"
    #                     updateLog()
    #                     return "succeded"

#creating a function to avoid the obstacle            
def desviarObs(lado = 'right'):
    desviarObsDisplay()
    if lado == 'right':
        if name == 'axis correction **Corner**':
            motors.move_tank(800, -400, 400)
            motors.stop_tank()  
            motors.move_tank(1400, 500, 200)
            motors.move_tank(700, 200, 200)
            motors.move_tank(1400, 500, 130)
            motors.move_tank(300, 100, 100)
        elif name == 'proportional align':
            motors.move_tank(800, -400, 400)
            motors.stop_tank()  
            motors.move_tank(1850, 500, 200)
            motors.move_tank(700, 200, 200)
            motors.move_tank(1850, 500, 180)
        while se.reflection() > 80 and sd.reflection() > 80 :
            motors.start_tank(350, 150)
        motors.stop_tank()
        wait(1000)
        return [name, lado, 'succeded']
    elif lado == 'left':
        motors.move_tank(1300, 400, -400)
        motors.stop_tank()
        while se.reflection() > 80 or sd.reflection() > 80 :
            motors.start_tank(150, 350)
        motors.stop_tank()
        wait(1000)
        return [name, lado, 'succeded']
    return [name, lado, 'failed']       

#creating a function to detect if the robot is in the rescue zone
def checarResgate(u_value):
    if u_value > 900 and u_value < 930:
        motors.stop_tank()
        hub.speaker.beep()
        motors.move_tank(3000,250,250)
        motors.move_tank(1500,-250,250)
        motors.move_tank(1000,250,250)
        wait(2000)
        u_value = u2.distance()
        print(u_value)
        #Mover motor esquerdo para frente fazendo com q o robo gire 90 graus
        if u_value > 500 and u_value < 800:
            hub.speaker.beep()
            hub.display.pixel(4,4)
            print("resgate!!!!")
            return True
        else:
            motors.move_tank(1000,-250,-250)
            motors.move_tank(1500,250,-250)
            motors.move_tank(2250,-250,-250)
    elif u_value < 100:
        hub.speaker.beep()
        motors.stop_tank()
        move_side = 'right'
        desviarObs()
    return False

#defining the general comparation value to the sensors and creating the darkest variable to use it later
setPoint = 50
darkest = ""

# defining motors
motors = MotorPair(Port.A,Port.B)

# defining sensors
green_values = [[[144.18, 59.945, 52.26], [184.18, 99.945, 92.26]], [[146.77, 56.265, 53.105], [186.77, 96.265, 93.105]]]
u2 = UltrasonicSensor(Port.E)
sc = ColorSensor(Port.D)
sd = ColorSensor(Port.C)
se = ColorSensor(Port.F)
i = Intersection(se, sd, green_values)

#creating the log list and the corner variable
name = 'Beginning run'
move_side = 'None'
log = 'succeded'
logs = [name,move_side,log]
corner = 0

#creating the mode variable to use it later to choose the robot mode between calibrate mode and execution mode 
mode = ""

#main loop
if __name__ == "__main__":
    while True:
        if hub.buttons.pressed() == {Button.LEFT}: #if the left button were pressed, start the execution mode
            mode = "execution"
        if hub.buttons.pressed() == {Button.RIGHT}: #if the right button were pressed, start the calibrate mode
            mode = "calibrate"
        if mode == "calibrate": #if the actual mode is calibrate, then:
            print("------calibrando------") #debug
            leftValues = i.getGreenValues("left") #set the variable leftValues with the function getGreenValues(Correct placement of the robot is necessary to get correct values for the left sensor)
            rightValues = i.getGreenValues("right") #set the variable rightValues with the function getGreenValues(Correct placement of the robot is necessary to get correct values for the right sensor)
            green_values = [leftValues, rightValues] #update the green_values array to the new values got with the intersection object 
            print(green_values)#debug
            display.off()#turn off the display to show that the mode has restarted
            mode = ""#set the mode to blank after the calibrate is done
        if mode == "execution": #if the actual mode is execution, then:
            executionDisplay() #set the display to show an "E"
            u_value = u2.distance() # constantly get the distance value
            while checarResgate(u_value) == False: #while the robot isn't in rescue zone, then:
                print(logs[-1],corner) #debug for showing the logs every second 
                u_value = u2.distance() #constantly get the distance value
                se_value = se.reflection() #constantly get the left sensor value
                sd_value = sd.reflection() #constantly get the right sensor value 
                sc_value = sc.reflection() #constantly get the middle sensor value
                errord = se_value - setPoint #constantly get the difference between the right value and the setPoint
                errore = sd_value - setPoint #constantly get the difference between the left value and the setPoint
                if se_value > 50 and sd_value > 50 and sc_value < 55: #if right-left sensors values are bigger then 50(if they are seeing white), and middle value is smaller then 55(if its seeing black), then(if the robot is in line):
                    updateLog(proportionalAlign(errore,errord,1.2)) #do proportional align to correct little route errors
                else: #else(if the robot isn't in line), then:
                    valores_verdes = i.checkGreen(green_values) #constantly use the checkGreen function from the Intersection object to return if any of the right-left sensors are seeig green
                    if valores_verdes[0] != False or valores_verdes[1] != False: #if any of the right-left sensors is seeing green, then:
                        updateLog(i.intersectionSolver(valores_verdes))# do intersection solver
                    if se_value > 80 and sd_value > 80 and sc_value > 80: #if every sensor is seeing white, then:
                        if logs[-1][0] == 'proportional align': #if the last task was proportional align(if the robot were in line before seeing all white), then:
                            
                            updateLog(["gap", 'None', "succeded"]) #it's a gap(uptade the log to a gap case)
                        else: #if the last task wasn't proportional align(something is wrong), then:
                            recoveryTask() #shit, lets try recovery task
                    else: #else, if the robot isn't in line and isn't seeing everything white, then:
                        motors.stop_tank() #stop the motors from moving
                        if se_value < 30 and sd_value < 30: #if both right-left sensors are seeing black, then:
                            motors.move_tank(2000, 200, 200) #move tank during 2000 milliseconds
                            se_value = se.reflection() #update the left sensor value
                            sd_value = sd.reflection() #update the right sensor value
                            sc_value = sc.reflection() #update the middle sensor value
                            errord = se_value - setPoint #update the errorD
                            errore = sd_value - setPoint #update the errorE
                            if se_value > 60 and sd_value > 60 and sc_value < 45: #if the robot is in line, then:
                                updateLog(proportionalAlign(errore,errord,0.8)) #do proportional align 
                            else: #if the robot isn't in line, then:
                                print('back until see black') #debug
                                motors.move_tank(2000, -200, -200) #go back until see black
                                updateLog(axis_correction(logs[-1][0])) # do axis correction after it returns
                        else: #else, if both left-right are seeing a value higher then 30, then:
                            print('axis correction no branco')
                            updateLog(axis_correction(logs[-1][0])) #do axis correction 
                msg = str(se.reflection()) + ',' + str(sc.reflection()) + ',' + str(sd.reflection())
                print(msg)