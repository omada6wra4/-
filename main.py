from machine import Pin, PWM
import time

# --- Ορισμός Pin Αισθητήρων ---
sensor_center = Pin(0, Pin.IN)  # GP0
sensor_left = Pin(5, Pin.IN)    # GP5
sensor_right = Pin(26, Pin.IN)  # GP26

# --- Ορισμός Pin Κινητήρων (L298N) ---
ena = PWM(Pin(6)); in1 = Pin(1, Pin.OUT); in2 = Pin(2, Pin.OUT) # Αριστερός
enb = PWM(Pin(7)); in3 = Pin(3, Pin.OUT); in4 = Pin(4, Pin.OUT) # Δεξιός

ena.freq(1000); enb.freq(1000)
PWM_MAX = 65535

# --- Ορισμός Pin Κουμπιού Έναρξης (Maker Pi Pico User Button) ---
# GP20 είναι συνήθως ένα από τα user buttons στην Maker Pi Pico.
# Έχει ενσωματωμένο pull-up, οπότε είναι HIGH όταν δεν πατιέται, LOW όταν πατιέται.
start_button = Pin(20, Pin.IN, Pin.PULL_UP)

# --- Ορισμός Ταχυτήτων ---
STRAIGHT_SPEED = 55
CORRECTION_TURN_OUTER_SPEED = 35
CORRECTION_TURN_INNER_SPEED = 15
SMOOTH_TURN_OUTER_SPEED = 33
SMOOTH_TURN_INNER_SPEED = 18

# --- Βοηθητικές Συναρτήσεις Κινητήρων ---
def set_motor_speed(pwm_pin, percent):
    if percent < 0: percent = 0
    if percent > 100: percent = 100
    duty = int((percent / 100) * PWM_MAX)
    pwm_pin.duty_u16(duty)

def motor_left_forward(speed_percent):
    in1.low(); in2.high()
    set_motor_speed(ena, speed_percent)

def motor_left_backward(speed_percent):
    in1.high(); in2.low()
    set_motor_speed(ena, speed_percent)

def motor_left_stop():
    in1.low(); in2.low()
    set_motor_speed(ena, 0)

def motor_right_forward(speed_percent):
    in3.low(); in4.high()
    set_motor_speed(enb, speed_percent)

def motor_right_backward(speed_percent):
    in3.high(); in4.low()
    set_motor_speed(enb, speed_percent)

def motor_right_stop():
    in3.low(); in4.low()
    set_motor_speed(enb, 0)

# --- Συναρτήσεις Κίνησης Ρομπότ ---
def robot_go_straight():
    motor_left_forward(STRAIGHT_SPEED)
    motor_right_forward(STRAIGHT_SPEED)

def robot_turn_sharply_left():
    motor_right_forward(CORRECTION_TURN_OUTER_SPEED)
    motor_left_forward(CORRECTION_TURN_INNER_SPEED)

def robot_turn_sharply_right():
    motor_left_forward(CORRECTION_TURN_OUTER_SPEED)
    motor_right_forward(CORRECTION_TURN_INNER_SPEED)

def robot_turn_smoothly_left():
    motor_right_forward(SMOOTH_TURN_OUTER_SPEED)
    motor_left_forward(SMOOTH_TURN_INNER_SPEED)

def robot_turn_smoothly_right():
    motor_left_forward(SMOOTH_TURN_OUTER_SPEED)
    motor_right_forward(SMOOTH_TURN_INNER_SPEED)

def robot_stop_all():
    motor_left_stop()
    motor_right_stop()

# --- Κύρια Λογική Line Follower ---
try:
    print("Εκκίνηση Line Follower (με στοπ όταν όλοι οι αισθητήρες είναι 1)...")
    print(f"Λογική Αισθητήρων: 1 = Μαύρη Γραμμή, 0 = Άσπρη Επιφάνεια")
    print(f"Ταχύτητα Ευθείας: {STRAIGHT_SPEED}%")
    print(f"Ταχύτητα Απότομης Στροφής (Εξωτερικός/Εσωτερικός): {CORRECTION_TURN_OUTER_SPEED}% / {CORRECTION_TURN_INNER_SPEED}%")
    print("Power Bank και γεμάτες μπαταρίες ΑΑ!")
    print("Τοποθέτησε το ρομπότ στη γραμμή, με τον κεντρικό αισθητήρα πάνω της.")

    # --- ΑΝΑΜΟΝΗ ΓΙΑ ΠΑΤΗΜΑ ΚΟΥΜΠΙΟΥ ---
    print("\nΠάτησε το κουμπί RUN (GP20) στην Maker Pi Pico για να ξεκινήσει το ρομπότ.")
    while start_button.value() == 1:  # Περίμενε μέχρι το κουμπί να πατηθεί (να γίνει LOW)
        time.sleep(0.05) # Μικρή καθυστέρηση για να μην καταναλώνει πολλούς πόρους

    print("Κουμπί πατήθηκε! Το ρομπότ ξεκινά σε 1 δευτερόλεπτο...")
    time.sleep(1) # Δώσε χρόνο στον χρήστη να απομακρύνει το χέρι του

    while True:
        s_left = sensor_left.value()
        s_center = sensor_center.value()
        s_right = sensor_right.value()

        # print(f"L:{s_left} C:{s_center} R:{s_right} \r", end="") # Για debugging

        if s_left == 1 and s_center == 1 and s_right == 1:
            print(f"ΚΑΤΑΣΤΑΣΗ 111: L:{s_left} C:{s_center} R:{s_right} -> ΣΤΟΠ")
            robot_stop_all()
        elif s_center == 1:
            # print(f"L:{s_left} C:{s_center} R:{s_right} -> Ευθεία") # Debug
            robot_go_straight()
        elif s_left == 1 and s_center == 0:
            # print(f"L:{s_left} C:{s_center} R:{s_right} -> Δεξιά") # Debug
            robot_turn_sharply_right()
        elif s_right == 1 and s_center == 0:
            # print(f"L:{s_left} C:{s_center} R:{s_right} -> Αριστερά") # Debug
            robot_turn_sharply_left()
        # Πιθανές περιπτώσεις που δεν καλύπτονται άμεσα από την παραπάνω λογική για στροφή/ευθεία
        # και δεν είναι η τριπλή ενεργοποίηση για στοπ.
        # 000: Εκτός γραμμής -> Σταμάτα (αν και μπορεί να θες να ψάξει τη γραμμή)
        # 101: Κεντρικός εκτός, πλάγιοι εντός -> Σύγχυση, ίσως διασταύρωση; -> Σταμάτα για ασφάλεια
        # Άλλες (π.χ. 010, 001, 110 - αν και καλυπτεται η 110 απο την s_center==1 ) θα πρέπει να ελεγχθούν.
        # Η παρακάτω συνθήκη else καλύπτει ό,τι δεν καλύφθηκε, κυρίως το 000 και το 101
        else:
            print(f"Κατάσταση εκτός/άγνωστη: L:{s_left} C:{s_center} R:{s_right} -> Στοπ")
            robot_stop_all()

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nΔιακοπή από το χρήστη.")
finally:
    print("Σταμάτημα κινητήρων (finally block)...")
    robot_stop_all()
