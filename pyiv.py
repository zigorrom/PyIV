import PyCmdMessenger


arduino = PyCmdMessenger.ArduinoBoard("COM26",baud_rate = 115200,timeout=10.0)

commands = [["Watchdog","s"],
            ["Acknowledge","s"],
            ["SwitchChannel","i?"],#"i?"],
            ["Error","s"],
            ["MotorCommand","ii"]]#"ii"]]


c = PyCmdMessenger.CmdMessenger(arduino,commands)

print("start sending")

c.send("SwitchChannel",5,False)
msg = c.receive()
print(msg)
print("start sending")
c.send("MotorCommand",1,250)
msg = c.receive()
print(msg)





##c.send("kSwitchChannel",1,True)
##msg = c.receive()
##print(msg)




