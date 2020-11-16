var express = require('express');

var app = express();
var server = app.listen(4000, () => { //Start the server, listening on port 4000.
    console.log("Listening to requests on port 4000...");
})

var io = require('socket.io')(server); //Bind socket.io to our express server.

app.use('/', express.static('public')); //Send index.html page on GET /
app.use('/css/', express.static('css'));

const SerialPort = require('serialport'); 
const Readline = SerialPort.parsers.Readline;
const port = new SerialPort('/dev/ttyUSB0'); //Connect serial port to port COM3. Because my Arduino Board is connected on port COM3. See yours on Arduino IDE -> Tools -> Port
const parser = port.pipe(new Readline({delimiter: '\n'})); //Read the line only when new line comes.
parser.on('data', (data) => { //Read data

    var re = /(\w{1}\d*\.?\d+)/g;
    var matches = data.match(re);

    console.log(data);

    var today = new Date();

    tempEmitted = false;

    for (let i = 0; i < matches.length; i++){
        x = matches[i];
        console.log(x);
        switch (x.charAt(0)) {
            case 'T':
                if (!tempEmitted) {
                    io.sockets.emit('temp', {time: (today.getHours())+":"+((today.getMinutes() < 10 ? '0' : '') + today.getMinutes()), data: x.substring(1),
                    units: ' ºC'});
                    tempEmitted = true;
                }
            case 'P': 
                io.sockets.emit('pres', {time: (today.getHours())+":"+((today.getMinutes() < 10 ? '0' : '') + today.getMinutes()), data: x.substring(1),
                units: ' hPa'});
            case 'U': 
                io.sockets.emit('u', {time: (today.getHours())+":"+((today.getMinutes() < 10 ? '0' : '') + today.getMinutes()), data: x.substring(1),
                units: '%'});
        }
    }

});

io.on('connection', (socket) => {
    console.log("Someone connected."); //show a log as a new client connects.
})