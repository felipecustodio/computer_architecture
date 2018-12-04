// var xspacing = 1;    //  Full
var xspacing = 16;    // Distance between each horizontal location
var w;                // Width of entire wave
var theta = 0.5;      // Start angle at 0
var theta_speed = 0.01;
var amplitude = 75.0; // Height of wave
var period = 400.0;   // How many pixels before the wave repeats
var dx;               // Value for incrementing x
var yvalues;  // Using an array to store height values for the wave

function calcWave() {
    // Increment theta (try different values for 
    // 'angular velocity' here)
    theta += theta_speed;
    // For every x value, calculate a y value with sine function
    var x = theta;
    for (var i = 0; i < yvalues.length; i++) {
      yvalues[i] = sin(x)*amplitude;
      x+=dx;
    }

  }
  
  function renderWave() {
    // A simple way to draw the wave with an ellipse at each location
    for (var x = 0; x < yvalues.length; x++) {
      ellipse(x*xspacing, yvalues[x], 1, 10);
    }
  }