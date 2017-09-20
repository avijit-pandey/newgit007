var mqtt = require('mqtt')
var client = mqtt.connect({host: 'localhost', port: 1883})
 
//client = mqtt.createClient(1883, 'localhost');
 
client.subscribe('presence');
 
client.on('message', function(topic, message) {
  console.log(message.toString());
});
 
console.log('Client started...');
