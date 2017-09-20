//var mqtt = require('mqtt')
//var client = mqtt.connect('localhost')
 
//client = mqtt.createClient(1883, 'localhost');
 
//client.subscribe('presence');
 
//console.log('Client publishing.. ');
//client.publish('presence', 'Client 1 is alive.. Test Ping! ' + Date());
 
//client.end();
var mqtt = require('mqtt')
var client  = mqtt.connect({host: 'localhost', port: 1883})

client.on('connect', function () {
  client.subscribe('presence')
  client.publish('presence', 'Client 1 is alive.. curious pandey!' + Date())
})

client.on('message', function (topic, message) {
  // message is Buffer
  console.log(message.toString())
  client.end()
})
