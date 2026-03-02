const express = require('express')
  , app = express()
  , bodyParser = require('body-parser')
  , config = require('./config/config')
  , db = require('./config/db')
  , cron = require("node-cron")
  , axios = require("axios");

app.set('views', __dirname + '/views');
app.engine('ejs', require('ejs').__express);
app.set('view engine', 'ejs');

app.use(express.static(__dirname + '/public'));
app.use('/css', express.static(__dirname + '/node_modules/bootstrap/dist/css'));
app.use('/css', express.static(__dirname + '/node_modules/bootstrap-datepicker/dist/css/'));
app.use('/js', express.static(__dirname + '/node_modules/axios/dist/'));
app.use('/js', express.static(__dirname + '/node_modules/jquery/dist/'));
app.use('/js', express.static(__dirname + '/node_modules/bootstrap-datepicker/dist/js/'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

/*    Get Routes of the apps */
app.use(require('./routes'));

cron.schedule("* * * * *", function() {

  axios.get('http://' + config.server.hostname + ':' + config.server.port + '/stations')
  .then(function (response) {
    if ( parseInt(response.data.length) < 20 ) {
      axios.get('http://' + config.server.hostname + ':' + config.server.port + '/stations/add');
      console.log("another Station was added!")
    } else {
      for (let i = 0; i < response.data.length; i++) {
        axios.get('http://' + config.server.hostname + ':' + config.server.port + '/stations/delete/' + response.data[i]);
      }
      axios.get('http://' + config.server.hostname + ':' + config.server.port + '/stations/add');
      console.log("all Stations were deleted!")
    }
  })
  .catch(function (error) {
    console.log(error);
  });
});

db.on('connected', () => {
  app.listen(config.server.port, config.server.hostname, function() {
    console.log('Listening on port ' + config.server.hostname + ":" + config.server.port)
  });
});

