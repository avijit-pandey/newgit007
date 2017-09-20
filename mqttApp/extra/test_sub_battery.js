var mqtt = require('mqtt')
var client = mqtt.connect({host: '192.168.1.117', port: 1883})
 
//client = mqtt.createClient(1883, 'localhost');
 
client.subscribe('esp/18:fe:34:a1:37:05/battery');
 
client.on('message', function(topic, message) {
  console.log(message.toString());
});
 
console.log('Client started...');
