file.open("test.txt","r") 
f = (file.readline())
c = (file.readline())
s = (file.readline())
p = (file.readline())
file.close()
f = string.gsub(f, "\n", "")
print("flag"..f)
switch_pin = 3      -- 3= gpio0

--configure gpio pins according to revised pin map
pin14 = 5
pin12 = 6

gpio.mode(pin14,gpio.OUTPUT) --in1 as output
gpio.mode(pin12,gpio.OUTPUT) --in2 as output

gpio.write(pin12,gpio.LOW) --in1 for driver (sleep mode)
gpio.write(pin14,gpio.LOW) --in2 for driver (sleep mode)


gpio.mode(switch_pin, gpio.INPUT,gpio.PULLUP)    
tmr.alarm(1, 2000, 1, function()
	switch_status = gpio.read(switch_pin)
        print ("sw="..switch_status)
        print ("f="..f)
	if (switch_status == 0) then
		f="1"
    end    
    if (f == "1" or f == nil) then  
	    tmr.stop(1)
        print ("Entering Configuration Mode ..")
        dofile('initap.lua')
	elseif (f == "0") then
	    tmr.stop(1)
		print ("Using Previous settings ..")
		dofile('initsta.lua')
    end
end)

