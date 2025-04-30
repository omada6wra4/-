from gpiozero import Motor, LineSensor
from signal import pause

left_motor = Motor(forward=4, backward=14)
right_motor = Motor(forward=17, backward=18)

left_sensor = LineSensor(27)
right_sensor = LineSensor(22)

def on_line_left():
    print("Left sensor: line detected")
    right_motor.forward()
    left_motor.stop()

def on_line_right():
    print("Right sensor: line detected")
    left_motor.forward()
    right_motor.stop()

def both_on_line():
    print("Both sensors: line detected")
    left_motor.forward()
    right_motor.forward()

def both_off_line():
    print("No line detected")
    left_motor.stop()
    right_motor.stop()

left_sensor.when_line = on_line_left
left_sensor.when_no_line = both_off_line
right_sensor.when_line = on_line_right
right_sensor.when_no_line = both_off_line

pause()
