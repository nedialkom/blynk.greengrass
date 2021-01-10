import blynklib
import sensors

target = 400
old_target = 400
auto = False
irrigation = False

auth = 'goIBUGtXu2lArmBHBXJUhudtSCCCMSx7'

# initialize blynk
blynk = blynklib.Blynk(auth, server='35.156.189.43', port=80, ssl_cert=None, heartbeat=10, rcv_buffer=1024, log=print)

""" If server s not working - error 111
sudo iptables - t nat - A PREROUTING - p tcp - -dport 80 - j REDIRECT - -to - port 8080
sudo iptables - t nat - A PREROUTING - p tcp - -dport 443 - j REDIRECT - -to - port 9443
"""

@blynk.handle_event("connect")
def connect_handler():
    global auto, irrigation, target
    blynk.virtual_write(12, int(auto))
    blynk.virtual_write(13, int(irrigation))
    blynk.virtual_write(4, int(target))
    blynk.virtual_sync('*')


# register handler for virtual pin V* write event
@blynk.handle_event('write V*')
def write_virtual_pin_handler(pin, value):
    print('Write pin {}, value {}'.format(pin, value))
    global target, old_target
    global irrigation, auto
    if pin == 4:  # slider
        old_target = target
        target = int(float(value[0]))
        print('New target: {}'.format(target))
    elif pin == 12:  # auto/manual button
        print('Mode changed to {}'.format(bool(int(value[0]))))
        auto = bool(int(value[0]))
    elif pin == 13:  # irrigation button
        if auto:
            print('Auto mode, can not change irrigation manually')
            blynk.notify('Auto is on')
            # roll back the state
            if value[0] == '0':
                blynk.virtual_write(13, 1)
            else:
                blynk.virtual_write(13, 0)
        else:
            print('Irrigation changed to {}'.format(bool(int(value[0]))))
            irrigation = bool(int(value[0]))
        if irrigation:
            sensors.relay('on')
        else:
            sensors.relay('off')


# register handler for virtual pin V* reading
@blynk.handle_event('read V*')
def read_virtual_pin_handler(pin):
    print('Read pin {}'.format(pin))
    global target, old_target
    if target != old_target:
        blynk.virtual_write(4, target)


if __name__ == "__main__":
    while True:
        blynk.run()
        data = sensors.get_data()
        data['target'] = target
        data['auto mode'] = auto
        if auto:
            if data['target'] > data['moisture']:  # change relay status, button status and irrigation value
                if irrigation is False:
                    irrigation = True
                    blynk.virtual_write(13, 1)
                    sensors.relay('on')
            else:
                if irrigation:
                    irrigation = False
                    blynk.virtual_write(13, 0)
                    sensors.relay('off')
        data['irrigation'] = irrigation
        print('data: {}'.format(data))
        blynk.virtual_write(10, data['moisture'])
        blynk.virtual_write(11, data['target'])
        blynk.virtual_write(0, data['temperature'])
        blynk.virtual_write(1, data['humidity'])
        blynk.virtual_write(2, data['light'])
        blynk.virtual_write(3, data['sound'])
