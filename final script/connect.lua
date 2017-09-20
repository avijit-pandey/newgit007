file.open("test.txt","r") 
ff = (file.readline())
collegid = (file.readline())
ssid = (file.readline())
psk = (file.readline())
file.close()
collegid = string.gsub(collegid, "\n", "")

mqtt_broker_ip='10.129.139.139'
mqtt_port = 1883
qos = 0

macid = wifi.sta.getmac()
--wait for WiFi connection 
wifi_available=0
broker_connect_tries=0
if wifi_available==0 then
	tmr.alarm(1,1000,1,function()
		if wifi.sta.getip()==nil then
			print("no wifi")
		else
		    print ('IP is '..wifi.sta.getip())
		    wifi_available=1
		    mqqt_connection()
	        end
	end)
end

function mqqt_connection()
	print ("in broker code")
	print (collegid)
	broker_connect_tries=broker_connect_tries + 1 
	dofile('mqttsetup_valve.lua') 

	m:connect(mqtt_broker_ip,mqtt_port,0,function(conn) 
		tmr.stop(1)
		tmr.unregister(1)
		topic = collegid..'/esp/'..macid                 -- topic to subscribe to 
                m:subscribe(topic,0,function(conn) end)
		print('mqtt connected')
	end)     
end	

tmr.alarm(0,60000,1,function()  --sleeps after being active for 60 seconds
	print("restarting")
	dofile("init.lua")
end)



