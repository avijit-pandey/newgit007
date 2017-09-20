var mqtt = require('mqtt')
var client  = mqtt.connect({host: 'localhost', port: 1883})

client.on('connect', function () {
  client.subscribe('esp/18:fe:34:a1:37:05')
  client.publish('esp/18:fe:34:a1:37:05', '2')
})

client.on('message', function (topic, message) {
  // message is Buffer
  console.log(message.toString())
  client.end()
})

