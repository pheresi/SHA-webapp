// lat = []; // always clear the array when picking a new type
// lon = [];
// mag = [];

// Minimum Variables
var lat;
var lng;
var riskcat;
var siteclass;
var marker;
var contenido;
let usgs;
var ss;

function preload() {
  // youtubeData = loadTable('subscribers_geo.csv', 'header');
  //youtubeData = loadTable('watch_time_geo.csv', 'header');
  //countries = loadJSON('countries.json');
  // earthquakes3 = loadStrings('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv');
  // earthquakes1 = loadStrings('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.csv');
  // earthquakes2 = loadStrings('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.csv');
  // earthquakes = earthquakes1;
//  usgs =  loadJSON('https://earthquake.usgs.gov/ws/designmaps/asce7-16.json?latitude=37.4&longitude=-122.18&riskCategory=III&siteClass=C&title=Example')
google.charts.load('current', {'packages':['corechart']});
}

var map;

function setup() {
  pixelDensity(1);
  noCanvas();
  map = L.map('mapid').setView([37.4249366, -122.187936], 10);

	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


  // L.geoJSON(usgsfaults,{
  //   // onEachFeature:
  // }).addTo(map);


marker = L.marker([37.4249366, -122.187936]).addTo(map);
latlongshown = select('#latlong0');
latlongshown.html('Latitude: '+ nf(37.4249366,1,3) + ', Longitude: ' + nf(-122.187936,1,3));

 //marker = L.marker([37.4249366, -122.187936]).addTo(mymap);
// L.circleMarker([37.4249366, -122.187936],{radius: 10}).addTo(map)
//     .bindPopup('S Flag')
//     .openPopup();

// buttons
// Risk Category
riskSource = select('#riskcategory'); // get the DOM element from the HTML
riskSource.changed(processRisk); // assign callback

// Soil Type
siteSource = select('#siteclass'); // get the DOM element from the HTML
siteSource.changed(processSite); // assign callback

// gofind = select('#findit'); // get the DOM element from the HTML
// gofind.onclick(processFind); // assign callback

// currentColor = color(255, 0, 200, 100); // default color
// console.table(usgs)
// processData();

// Picking lat and long from map!
map.on('click', function(e) {
    if(marker)
    map.removeLayer(marker);
    // console.log(e.latlng); // e is an event object (MouseEvent in this case)
    coordinates = e.latlng;
    lat = coordinates.lat;
    lng = coordinates.lng;
    console.log(lat,lng)
    // drawLatlong(lat,lng)
    latlongshown = select('#latlong0');
    latlongshown.html('Latitude: '+ nf(lat,1,3) + ', Longitude: ' + nf(lng,1,3));
    marker = L.marker(e.latlng).addTo(map);
});

}

function draw() {
    noLoop();
    // clear();
    // map.setView([37.4249366, -122.187936], 8);
}

function processRisk() {
  let type = riskSource.value();
  // console.log(type);
  switch (type) {
    case 'I':
      riskcat = 'I';
      break;
    case 'II':
      riskcat = 'II';
      break;
    case 'III':
      riskcat = 'III';
      break;
    case 'IV':
      riskcat = 'IV';
        console.log('IV');
        break;
  }
}

// Process site info from button selected
function processSite() {
  let type = siteSource.value();

  switch (type) {
    case 'A':
      siteclass = 'A';
      break;
    case 'B':
      siteclass = 'B';
      break;
    case 'C':
      siteclass = 'C';
      break;
    case 'D':
      siteclass = 'D';
      break;
    case 'E':
      siteclass = 'E';
      break;
  }
}


async function processFind(){
  SH  = createP('');
  usgs =  await loadJSON('https://earthquake.usgs.gov/ws/designmaps/asce7-16.json?latitude='+lat+'+&longitude='+lng+'&riskCategory='+riskcat+'&siteClass='+siteclass+'&title=Example',plotResults);
}

// function processFind(){
//   loadJSON('https://earthquake.usgs.gov/ws/designmaps/asce7-16.json?latitude='+lat+'+&longitude='+lng+'&riskCategory='+riskcat+'&siteClass='+siteclass+'&title=Example',plotResults);
// }

function plotResults(){
  // console.log(usgs);
  // var ss = usgs.response.data.ss;
  // console.log(ss);
  contenido = {
    // formatted_address: formatted_address,
    // latlng: lat + ", " + lng,
    ss: usgs.response.data.ss,
    s1: usgs.response.data.s1,
    s1rt: usgs.response.data.s1rt,
    s1uh: usgs.response.data.s1uh,
    s1d: usgs.response.data.s1d,
    pgad: usgs.response.data.pgad,
    pga: usgs.response.data.pga,
    sds: usgs.response.data.sds,
    sd1: usgs.response.data.sd1,
    sms: usgs.response.data.sms,
    sm1: usgs.response.data.sm1,
    crs: usgs.response.data.crs,
	  cr1: usgs.response.data.cr1,
    sdc: usgs.response.data.sdc,
    fa: usgs.response.data.fa,
    fv: usgs.response.data.fv,
    fpga: usgs.response.data.fpga,
    pgam: usgs.response.data.pgam,
    ssrt: usgs.response.data.ssrt,
    tsubl: usgs.response.data['t-sub-l'],
    ssuh: usgs.response.data.ssuh,
    ssd: usgs.response.data.ssd
   }
   S0 = select('#s0');
   S0.html('Lat, Lon = '+ nf(lat,3,3) +', '+nf(lng,3,3));
   S1 = select('#s1');
   S1.html('S<sub>S</sub> = '+contenido.ss + ' - MCE<sub>R</sub> ground motion. (for 0.2 second period)')
   SP = select('#sp');
   SP.html('PGA = '+contenido.pga + ' - MCE<sub>G</sub> Peak ground acceleration')
   S2 = select('#s2');
   S2.html('S<sub>1</sub> = '+contenido.s1 + ' - MCE<sub>R</sub> ground motion. (for 1.0s period)');
   S3 = select('#s3');
   S3.html('S<sub>MS</sub> = '+contenido.sms + ' - Site-modified spectral acceleration value');
   S4 = select('#s4');
   S4.html('S<sub>M1</sub> = '+contenido.sm1 + ' - Site-modified spectral acceleration value');
   S5 = select('#s5');
   S5.html('S<sub>DS</sub> = '+contenido.sds + ' - Numeric seismic design value at 0.2 second SA');
   S6 = select('#s6');
   S6.html('S<sub>D1</sub> = '+contenido.sd1 + ' - Numeric seismic design value at 1.0 second SA');
}

// Google hazard Curveslet hcdata;
var hcdata;
var im;
var arraytogoogle = [];

async function drawHazardprep(){
  // usgs =  await loadJSON('https://earthquake.usgs.gov/ws/designmaps/asce7-16.json?latitude='+lat+'+&longitude='+lng+'&riskCategory='+riskcat+'&siteClass='+siteclass+'&title=Example',plotResults);
  hcdata = await loadTable('../hazard/HC_output1.csv', 'csv','header',drawHazard);
}

function drawHazard() {

for (var y = 0; y < hcdata.getRowCount(); y++) {
      arraytogoogle[y] = []; // create nested array
      for (var x = 0; x < hcdata.getColumnCount(); x++) {
          if (y==0) {
            arraytogoogle[0][0] = 'IM';
            arraytogoogle[0][1] = 'FIV3';
          } else{
          arraytogoogle[y][x] = Number(hcdata.getString(y,x));
        }
    }
}

console.table(arraytogoogle)

// var data = google.visualization.arrayToDataTable([
//   ['Year', 'Sales', 'Expenses'],
//   ['2004',  1000,      400],
//   ['2005',  1170,      460],
//   ['2006',  660,       1120],
//   ['2007',  1030,      540]
// ]);

var data = google.visualization.arrayToDataTable(arraytogoogle);

// console.table([
//   ['Year', 'Sales', 'Expenses'],
//   ['2004',  1000,      400],
//   ['2005',  1170,      460],
//   ['2006',  660,       1120],
//   ['2007',  1030,      540]
// ]);
// var data = google.visualization.arrayToDataTable(data);
var options = {
  title: 'Hazard curve',
  curveType: 'function',
  legend: { position: 'top', alignment: 'start' },
  vAxis:  {
    scaleType: 'log',
    title: 'MAF'
  },
  hAxis:  {
    scaleType: 'log',
    title: 'IM'
  },
  colors: ['#FF5733'],
  chartArea: {
      backgroundColor: {
          stroke: '#727272',
          strokeWidth: 1
      }
  }
};
var chart = new google.visualization.LineChart(document.getElementById('hazard_chart'));
chart.draw(data, options);
}

// Visualise Location: Lat:, Lon:
// function drawLatlong(lat0, lng0){
// // Intensity bar as another P5JS instance instead of a function
// var sl = function( pl ) { // p could be any variable name
//   // var fiv3bar;
//   pl.setup = function() {
//     clear();
//     pl.createCanvas(windowWidth/4, 10);
//     pl.latlongshown = createP('');
//     pl.latlongshown.html('Latitude = '+ nf(lat0,1,2) + ' Longitude = ' + nf(lng0,1,2));
//   };
//
//   pl.draw = function() {
//     noLoop();
//     }
//   }
// var myp5l = new p5(sl, 'latlong0');
// }
