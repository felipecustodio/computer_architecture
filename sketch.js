// palette
// https://colorhunt.co/palette/132222
const windchime = new Windchime();
// table render
var font, fontsize = 22
var cell_width = 100;
var cell_height = 50;

var num_instructions = 5;
var mPressed = false;
var clock = 0;

function preload() {
    font = loadFont('assets/bebas.otf');
}

function setup() {
	var cnv = createCanvas(windowWidth, windowHeight);
    cnv.style('display', 'block');
    
    textFont(font);
    textSize(fontsize);
    textAlign(CENTER, CENTER);

    w = width + 16;
    dx = (TWO_PI / period) * xspacing;
    yvalues = new Array(floor(400/xspacing));
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
    console.log("Resized!");
}

function draw() {

    background("#fbeed7");

    push();
    fill("#ff7657");
    stroke("#ff7657");
    translate(1200, -220);
    calcWave();
    renderWave();
    pop();

     // render clocks
     push();
     translate(1300, 50)
     var offset_x = 0;
     var offset_y = 0;
     fill("#ff7657");
     stroke("#ff7657");
     for (var i = 0; i < 3; i++) {
         for (var j = 0; j < 10; j++) {
             if (clock >= (i+1 + j+1)) {
                ellipse(offset_x, offset_y, 5, 5);
             }
             
             offset_x += 20;
         }
         offset_y += 20;
         offset_x = 0;
    }
    pop();

    // draw cycles table
    cell_width = 100;
    cell_height = 50;
    var text_x = 0;
    textAlign(LEFT);
    stroke("#665c84");
    fill("#665c84");
    text("Instruction", 100 + text_x, 80);
    text_x += cell_width + 105;
    text("ISSUE", 100 + text_x, 80);
    text_x += cell_width + 5;
    text("READ OP", 100 + text_x, 80);
    text_x += cell_width + 5;
    text("BEGIN", 100 + text_x, 80);
    text_x += cell_width + 5;
    text("END", 100 + text_x, 80);
    text_x += cell_width + 5;
    text("WRITE BACK", 100 + text_x, 80);
    text_x += cell_width + 5;
    
    var offset_x = 0;
    var offset_y = 0;
    for (var i = 0; i < num_instructions; i++) {
        for (var j = 0; j < 6; j++) {
            if (j == 0) {
                fill("#ffba5a");
                // noStroke()
                rect(100 + offset_x, 100 + offset_y, cell_width + 100, cell_height);
                offset_x += cell_width + 105;
            } else {
                fill("#ff7657");
                rect(100 + offset_x, 100 + offset_y, cell_width, cell_height);
                offset_x += cell_width + 5;
            }
            stroke("#665c84");
            fill("#665c84");
            if (j == 0) {
                textAlign(RIGHT);
                textSize(20);
                text("addi $2 $3 5", (40 + offset_x - 105 + cell_width/2), (100 + offset_y + cell_height/2));
            } else {
                textSize(fontsize);
                text("0", (100 + offset_x - 105 + cell_width/2), (100 + offset_y + cell_height/2));
            }
        }
        offset_y += cell_height + 5;
        offset_x = 0;
    }

    // draw results table
    cell_width = 100;
    cell_height = 50;
    var initial_x = 100 + (cell_width * 6) + (5 * 6) + 200;

    text_x = 0;
    textAlign(LEFT);
    text("Register", initial_x + text_x, 80);
    text_x += cell_width + 5;
    text("Unit", initial_x + text_x, 80);

    var offset_x = 0;
    var offset_y = 0;
    
    for (var i = 0; i < num_instructions; i++) {
        for (var j = 0; j < 2; j++) {
            if (j == 0) {
                fill("#ffba5a");
            } else {
                fill("#ff7657");
            }
            rect(initial_x + offset_x, 100 + offset_y, cell_width, cell_height);
            offset_x += cell_width + 5;

            stroke("#665c84");
            fill("#665c84");
            if (j == 0) {
                textAlign(CENTER);
                textSize(20);
                text("$" + str(i), initial_x + (cell_width / 2), 80 + offset_y + cell_height);
            } else {
                textSize(fontsize);
                text("-", initial_x + offset_x - cell_width / 2, 80 + offset_y + cell_height);
            }
        }
        offset_y += cell_height + 5;
        offset_x = 0;
    }

    // draw functional units
    cell_width = 99;
    var text_x = 0;
    textAlign(RIGHT);
    stroke("#665c84");
    fill("#665c84");
    text("FU", 100 + text_x + cell_width / 2, 480);
    text_x += cell_width + (cell_width/2) + 5;
    text("BUSY", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("OP", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("FI", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("FJ", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("FK", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("QJ", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("QK", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("RJ", 100 + text_x, 480);
    text_x += cell_width + 5;
    text("RK", 100 + text_x, 480);
    text_x += cell_width + 5;

    var offset_x = 0;
    var offset_y = 0;
    
    for (var i = 0; i < 4; i++) {
        for (var j = 0; j < 10; j++) {
            if (j == 0) {
                fill("#ffba5a");
            } else {
                fill("#ff7657");
            }
            rect(100 + offset_x, 500 + offset_y, cell_width, cell_height);
            
            stroke("#665c84");
            fill("#665c84");
            if (j == 0) {
                textAlign(CENTER);
                text("LDU", 100 + offset_x + cell_width / 2, 500 + offset_y + cell_height / 2);
            } else {
                text("-", 100 + offset_x + cell_width / 2, 500 + offset_y + cell_height / 2);
            }

            offset_x += cell_width + 5;
        }
        offset_y += cell_height + 5;
        offset_x = 0;
    }

//     if (mouseIsPressed) {
//         if (clock < 30) clock += 1;
//         theta_speed = map(clock, 0, 30, 0.01, 0.2);
//       }
}

function mouseClicked() {
    if (clock < 30) clock += 1;
    theta_speed = map(clock, 0, 30, 0.01, 0.2);
    windchime.soundNewUser();
    windchime.soundWikiChange();
}
