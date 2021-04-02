var express = require('express');
var bodyparser = require('body-parser');

var app = express();
var server = app.listen(4000, () => {
    console.log("Listening to requests on port 4000...");
})

var io = require('socket.io')(server);

app.use(bodyparser.urlencoded({extended: true}));

app.use('/', express.static('public'));
app.use('/sonda', express.static('public/sonda.html'));
app.use('/css', express.static('css'));

app.post('/sonda', (req, res) => {

    if (req.body.serial) {
        var s = req.body.serial; // serial port
        console.log('Listening to serial in ' + s);

        const SerialPort = require('serialport'); 
        const Readline = SerialPort.parsers.Readline;
        const port = new SerialPort(path = s);
        const parser = port.pipe(new Readline({delimiter: '\n'}));

        parser.on('data', (data) => { 

            io.sockets.emit('serial', s);

            var re = /(\w{1}\d*\.?\d+)/g;
            var matches = data.match(re);

            var today = new Date(); // reception time, not measure time

            var data = {}; // dictionary containing all received data
            
            for (let i = 0; i < matches.length; i++){
                // Round to 0 or 1 decimals depending on the sensor's resolution

                x = matches[i];
                switch (x.charAt(0)) {
                    case "T":
                        data["T"] = {
                            value: parseFloat(x.substring(1)).toFixed(1),
                        };
                    case 'P':
                        data['P'] = {
                            value: parseFloat(x.substring(1)).toFixed(1),
                        };           
                    case 'U':
                        data['U'] = {
                            value: parseInt(x.substring(1)),
                        };
                };
            }

            io.sockets.emit('newData', {
                // saves time as hh:mm
                time: (today.getHours())+":"+((today.getMinutes() < 10 ? '0' : '') + today.getMinutes()),
                data: data
            });

        });
    }

    res.redirect('/sonda');

});