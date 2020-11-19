 window.onload = function() {

    Chart.defaults.global.defaultFontFamily = 'Archivo';

    config = {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        fill: false,
                        data: [],
                        backgroundColor: 'rgba(235, 57, 70, 1)',
                        borderColor: 'rgba(235, 57, 70, 1)',
                        lineTension: 0,
                    }]
                },
                options: {
                  scales: {
                    xAxes: [ {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 0
                        },
                        display: true,
                        type: 'time',
                        time: {
                          parser: 'HH:mm',
                          tooltipFormat: 'll HH:mm',
                          unit: 'minute',
                          displayFormats: {
                            'minute': 'HH:mm'
                          }
                        }
                      }
                    ],
                    responsive: true,
                    maintainAspectRatio: true,
                    legend: {
                       display: false,
                    },
                    tooltips: {
                       enabled: false,
                    },
                  }
                },
             }

    // charts
    var tctx = document.getElementById('t-plot').getContext('2d');
    tconfig = JSON.parse(JSON.stringify(config));
    tconfig.data.datasets[0].label = "Temperature";
    var tChart = new Chart(tctx, tconfig);

    var uctx = document.getElementById('u-plot').getContext('2d');
    uconfig = JSON.parse(JSON.stringify(config));
    uconfig.data.datasets[0].label = "Relative humidity";
    uconfig.options.scales.xAxes[0].min = 0;
    uconfig.options.scales.xAxes[0].max = 100;
    var uChart = new Chart(uctx, uconfig);

    var pctx = document.getElementById('p-plot').getContext('2d');
    pconfig = JSON.parse(JSON.stringify(config));
    pconfig.data.datasets[0].label = "Pressure";
    var pChart = new Chart(pctx, pconfig);

    var socket = io.connect('http://localhost:4000'); //connect to server

    fetch("sensors.json")
    .then(response => {
        return response.json();
    })
    .then(data => {

        document.getElementById('temp-sensor').innerHTML = data["temp"]["sensorName"];
        document.getElementById('u-sensor').innerHTML = data["u"]["sensorName"];
        document.getElementById('p-sensor').innerHTML = data["pres"]["sensorName"];

        function addData(chart, label, val) {
            chart.data.labels.push(label);
            chart.data.datasets[0].data.push(val);         
            chart.update();   
        }

        function updateValue(weatherVar, chart, x, time) {
            wrapper = document.getElementById(weatherVar);
            wrapper.getElementsByClassName("var-value")[0].innerHTML = x['value'] + data[weatherVar]["units"];
            // It is not necessary to show the last updated time for all variables, 
            // since they are sent together
            wrapper.getElementsByClassName("var-time")[0].innerHTML = "Last updated: " + time;
            wrapper.getElementsByClassName("var-error")[0].innerHTML = '±' + data[weatherVar]["systError"] + data[weatherVar]["units"];
            addData(chart, time, x['value']);
        };

        socket.on('serial', function (s) {
            document.getElementById("is-listening").innerHTML = 'Listening to port';
            document.getElementById("data-source").innerHTML = s;
        });

        socket.on('newData', function (inp) {
            for (let i = 0; i < Object.keys(inp.data).length; i++) {
                v = Object.keys(inp.data)[i];

                switch (v) {
                    case 'T':
                        updateValue('temp', tChart, inp.data[v], inp.time);
                        break;
                    case 'P':      
                        updateValue('pres', pChart, inp.data[v], inp.time);
                        break;  
                    case 'U':              
                        updateValue('u', uChart, inp.data[v], inp.time);
                        break;                                               
                };

            }

        });

    });

}