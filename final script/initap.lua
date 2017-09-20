if sv ~=nil then 
    sv:close()
end 
wifi.setmode(wifi.SOFTAP)

ip_Adrr =
{
   ip="192.168.100.100",
   netmask="255.255.255.0",
   gateway="192.168.1.1"
}
  
wifi.ap.setip(ip_Adrr)

cfg={}
cfg.ssid="iot_valve15"
cfg.pwd="elsi1234"  -- min. 8 char, factory set to macid

wifi.ap.config(cfg)


tmr.alarm(0, 1000, 1, function() 
    if wifi.ap.getip()== nil then
       print ('Connecting...please wait')
       
    else
        tmr.stop(0)
        print("Your ESP8266 IP is "..wifi.ap.getip())
    end
end)

sv=net.createServer(net.TCP)

sv:listen(80,function(conn)
  conn:on("receive", function(conn, payload)
      print(payload) -- Print data from browser to serial terminal
        
        i = 0;
		clgid_obtained = 'NULL'
        ssid_obtained = 'NULL';
        pass_obtained = 'NULL';
        submit = 'NULL'
		last = 'NULL'
        --configure gpio pins according to revised pin map
        pin14 = 5
        pin12 = 6
        pin13 = 7
        
        mc=wifi.sta.getmac()
        print(mc.."\n")
        for complete_word in string.gmatch(payload, "([^&]+)") 
            do 
               for word in string.gmatch(complete_word,"([^=]+)")
                   do   i = i+1;
                        print(word.."\n")
                        print(i.."\n")  
						if (word == "clgid") then
							i=1;
						elseif (word == "ssid") then
							i=3;
						elseif (word == "pass") then
							i=5;
						elseif (word == "submit") then
							i=7;
                        elseif (i == 2 and last == "clgid") then
                           clgid_obtained = word 
                           clgid_obtained = string.gsub(clgid_obtained,"(+)","% ")
                        elseif (i == 4 and last == "ssid") then
                           ssid_obtained = word 
                           ssid_obtained = string.gsub(ssid_obtained,"(+)","% ")
                           print(ssid_obtained.."\n")                
                        elseif (i == 6 and last == "pass") then
                            pass_obtained = word 
							pass_obtained = string.gsub(pass_obtained,"(+)","% ")
                        elseif (i == 8 and last == "submit") then
                            submit = word 
                        elseif (word == "close" and last == "close_valve") then
                            gpio.write(pin12,gpio.LOW)
                            gpio.write(pin14,gpio.HIGH)
                            gpio.write(pin13,gpio.HIGH)
                            print("closing valve\n")
                        elseif (word == "open" and last == "open_valve") then
                            gpio.write(pin12,gpio.HIGH)
                            gpio.write(pin14,gpio.LOW) 
                            gpio.write(pin13,gpio.HIGH)
                            print("opening valve\n")
                        end -- end of if
                        last = word
               end
        end


        print("Obtained CLGID is "..(clgid_obtained))
        print("Obtained SSID is "..(ssid_obtained))
        print("Obtained PASSWORD is "..(pass_obtained))

           if submit == "Submit" then 
            --  put ssid in file
              tf=0;
              tmr.alarm(2, 1000, 1, function() 
              --  ssid, password, bssid_set, bssid=wifi.sta.getconfig()
                if ssid_obtained == 'NULL' then
                    print ('Waiting for SSID...please wait')
       
                else
                    tmr.stop(2)
                    file.open("test.txt","w")
					file.writeline(tf)
					file.writeline(clgid_obtained)
					file.writeline(ssid_obtained)
					file.writeline(pass_obtained)
					file.close()
                    dofile('initsta.lua')
                end -- end of if

               end)
           end  -- end of if   
          
            
      -- CREATE WEBSITE --
        
        -- HTML Header Stuff
        conn:send('HTTP/1.1 200 OK\n\n') --print(word.."\n")
        conn:send('<!DOCTYPE HTML>\n')
        conn:send('<html>\n')
        conn:send('<head><meta  content="text/html; charset=utf-8">\n')
        conn:send('<title>IoT Valve Controller</title></head>\n')
        conn:send('<body><h1 style="text-align:center;">k-Yantra Relay Controller</h1>\n')

        -- Buttons 
        conn:send('<form action="" method="POST">\n')
        conn:send('<br><p style="text-align:center;"> Your ESP8266 MACID is <b>['..mc..']</b>.</p><br>')
        conn:send('<p style="text-align:center;"><input type="hidden" name="erts" value="lab"><br>')
        conn:send('<input type="hidden" name="urban" value="farming"><br>')
        conn:send('Your <b>College ID</b>: <input type="text" name="clgid" value=""><br><br>')
        conn:send('<b>SSID</b> of wifi router you want to connect to: <input type="text" name="ssid" value=""><br><br>')
        conn:send('<b>Password</b> of wifi router you want to connect to: <input type="text" name="pass" value=""><br><br>')
        conn:send('<input type="submit" name="submit" value="Submit"></p><br>')
		conn:send('<br><br><br><br>')
		conn:send('<h2 style="text-align:center;">Test your solenoid valve here:</h2>\n <br><br>')
        conn:send('<p style="text-align:center;">Click <b>open button</b> to open the solenoid valve. <input type="submit" name="open_valve" value="open"><br><br>')
        conn:send('Click <b>close button</b> to close the solenoid valve. <input type="submit" name="close_valve" value="close"></p><br><br>')
        conn:send('</body></html>\n')

        --conn:on("sent", function(conn) conn:close() end)

    end)
   end) -- end of listen

 
