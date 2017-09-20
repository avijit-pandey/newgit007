var mqtt = require('mqtt')
var client  = mqtt.connect({host: '10.129.139.139', port: 1883})

client.on('connect', function () {
  client.subscribe('collegeid/esp/5c:cf:7f:4c:28:64')
  client.publish('collegeid/esp/5c:cf:7f:4c:28:64', '1')
})

client.on('message', function (topic, message) {
  // message is Buffer
  console.log(message.toString())
  client.end()
})


