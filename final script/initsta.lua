file.open("test.txt","r") 
ff = (file.readline())
cc = (file.readline())
ss = (file.readline())
pp = (file.readline())
file.close()
ss = string.gsub(ss, "\n", "")
pp = string.gsub(pp, "\n", "")
print(ss)
print(pp)

node.setcpufreq(node.CPU80MHZ) --reduce operating freq for power saving

wifi.setmode(wifi.STATION)
wifi.sta.config(ss,pp)

wifi.sta.connect()

--configure gpio pins according to revised pin map
pin14 = 5
pin12 = 6

gpio.mode(pin14,gpio.OUTPUT) --in1 as output
gpio.mode(pin12,gpio.OUTPUT) --in2 as output

gpio.write(pin12,gpio.LOW) --in1 for driver (sleep mode)
gpio.write(pin14,gpio.LOW) --in2 for driver (sleep mode)

                                  

wifiAvailable=0 --initialising the flag 
sleepTime=1000000*60*5    --5 min sleep
dofile('connect.lua')
