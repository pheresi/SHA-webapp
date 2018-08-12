// Mike

var lat = [];
var lon = [];
var mag = [];
var earthquakes;

const mappa = new Mappa('Leaflet');
let trainMap;
let canvas;
let dataSource;

let data = [];

let currentColor;
let fiv3;
var minfiv3;
var maxfiv3;

const options = {
  lat: 37.237,
  lng: -122.08874,
  zoom: 9,
  style: "http://{s}.tile.osm.org/{z}/{x}/{y}.png"
  //style:"https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
}

function preload() {
  // youtubeData = loadTable('subscribers_geo.csv', 'header');
  //youtubeData = loadTable('watch_time_geo.csv', 'header');
  //countries = loadJSON('countries.json');
  // earthquakes3 = loadStrings('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv');
  // earthquakes1 = loadStrings('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.csv');
  // earthquakes2 = loadStrings('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.csv');
  // earthquakes = earthquakes1;
  // usgs =  loadStrings('https://earthquake.usgs.gov/ws/designmaps/asce7-16.json?latitude=37.4&longitude=-122.18&riskCategory=III&siteClass=C&title=Example')
  // Load the data
  fiv3 = loadTable('../hazard/hazard_map-rlz-000_1.csv', 'csv', 'header');
}

function setup() {
  pixelDensity(1);
  // canvas = createCanvas(windowWidth,windowHeight)
  canvas = createCanvas(windowWidth, 400);
  // background(200);
  trainMap = mappa.tileMap(options);
  trainMap.overlay(canvas);

  periodinput = select('#periodhazard'); // get the DOM element from the HTML
  periodinput.changed(drawfiv3); // assign callback

  hazardinput = select('#hazardlevel'); // get the DOM element from the HTML
  hazardinput.changed(drawfiv3);

  currentColor = color(255, 0, 200, 100); // default color
  // console.table(usgs)
  // processData();
  // Only redraw the meteorites when the map change and not every frame.

  trainMap.onChange(drawfiv3);

 // fill(70, 203,31);
 // stroke(1);

 // get min and max
 // fiv3minmax();
}

function points() {
  for (var i=0; i<lat.length; i++) {
    //console.log(lat[i], lon[i])
    if (lat[i]){
    const pix1 = trainMap.latLngToPixel(lat[i],lon[i]);
    fill(currentColor);
    mag1 = pow(10,mag[i]);
    mag1 = sqrt(mag1);
    var magmax = sqrt(pow(10,10));

    var d = map(mag1,0, magmax,0,500);
    const zoom = trainMap.zoom();
    const scl = pow(2, zoom) //sin(frameCount * 0.1);
    ellipse(pix1.x, pix1.y, d*scl);
  }
}
}

function draw() {
  // noLoop();
  // ploting();
  // clear();
  // newzoom = trainMap.zoom();

  // points();


  // for (let country of data) {
  //   console.log(country.lat, country.lon)
  //   const pix = trainMap.latLngToPixel(country.lat, country.lon);
  //   fill(currentColor);
  //   const zoom = trainMap.zoom();
  //   const scl = pow(2, zoom); // * sin(frameCount * 0.1);
  //   ellipse(pix.x, pix.y, country.diameter * scl);
  // }

}

function fiv3minmax(FIV3THZ){
     minfiv3 = [];
     maxfiv3 = [];
     minfiv3 = Number(fiv3.getString(0, FIV3THZ));
     maxfiv3 = Number(fiv3.getString(0, FIV3THZ));
  for (let i = 0; i < fiv3.getRowCount(); i++) {
      size = Number(fiv3.getString(i, FIV3THZ));
      if (size < minfiv3){
        minfiv3 = size;
      }
      if (size > maxfiv3){
        maxfiv3 = size;
      }
  }
}


function drawfiv3() {
  // Clear the canvas
  clear();

  //get input period!
  let typeT = periodinput.value();
  switch (typeT) {
  case 'T01':
    fiv3T = '0.1';
    console.log(fiv3T);
    break;
  case 'T1':
    fiv3T = '1.0';
    console.log(fiv3T);
    break;
  }

  //get hazard level!
  let typeHZ = hazardinput.value();
  switch (typeHZ) {
  case 'HL1050':
    fiv3HZ = '0.1';
    console.log(fiv3HZ);
    break;
  case 'HL250':
    fiv3HZ = '0.02';
    console.log(fiv3HZ);
    break;
  }

  // Call min-max based on the correct FIV3THZ
  FIV3THZ = 'FIV3('+fiv3T+')-'+fiv3HZ;
  fiv3minmax(FIV3THZ);
  console.log(FIV3THZ);

  // I can draw Intensity bar passing the min and maximum
  // drawIntBar(minfiv3,maxfiv3);

  for (let i = 0; i < fiv3.getRowCount(); i++) {
    // Get the lat/lng of each meteorite
    const latitude = Number(fiv3.getString(i, 'lat'));
    const longitude = Number(fiv3.getString(i, 'lon'));

    // Only draw them if the position is inside the current map bounds. We use a
    // Leaflet method to check if the lat and lng are contain inside the current
    // map. This way we draw just what we are going to see and not everything. See
    // getBounds() in http://leafletjs.com/reference-1.1.0.html
    if (trainMap.map.getBounds().contains({lat: latitude, lng: longitude})) {
      // Transform lat/lng to pixel position
      const pos = trainMap.latLngToPixel(latitude, longitude);
      // Get the size of the meteorite and map it. 60000000 is the mass of the largest
      // meteorite (https://en.wikipedia.org/wiki/Hoba_meteorite)
      let size = fiv3.getString(i,FIV3THZ);
      // size = map(size, 558, 60000000, 1, 25) + trainMap.zoom();
      fiv3col = map(size,minfiv3,maxfiv3,0,255);
      fill(255,255-fiv3col,100-fiv3col,80);
      //noStroke()
      stroke(255,255-fiv3col,100-fiv3col,80);
      strokeWeight(1);
      // console.log(fiv3col);
      rect(pos.x, pos.y, 6, 6);
    }
  }
  drawIntBar(minfiv3,maxfiv3);
  // console.log('here');
}

// This is clever! A function with a P5JS instance inside - not to bad!
// Has been working OK, keep implementing new pops-up like This
// Since it is simpler an more organised
function drawIntBar(minI, maxI) {
// Intensity bar as another P5JS instance instead of a function
var s1 = function( pib ) { // p could be any variable name
  // var fiv3bar;
  var j = 0;
  pib.setup = function() {
  pib.createCanvas(windowWidth/4, 20);
  pib.noLoop();
  };

  pib.draw = function() {
    // p.background(0);
    for (var i=0; i<=windowWidth/4; i++){
      fiv3bar = map(i,minI,maxI,0,255);
      pib.fill(255,255-fiv3bar,100-fiv3bar,255);
      pib.stroke(255,255-fiv3bar,100-fiv3bar,255);
      pib.rect(1*i,0,1,10);

    }
    pib.textSize(11);
    pib.noStroke();
    pib.fill(0,0,0);
    pib.text(str(nf(minI,2,0)),20,20);
    pib.text(str(nf(maxI,2,0)),windowWidth/4 - 20,20);
  }
};
// First clean the current bar by erasing all in the DIV element
document.getElementById('intensitybar1').innerHTML = "";
// redraw
var myp5IB = new p5(s1, 'intensitybar1');
}
