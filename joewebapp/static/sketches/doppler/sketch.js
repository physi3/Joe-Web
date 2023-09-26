let wfs = [];
let timeSinceStart = 0;
let timeOfLast = -10000;

let frequency; // Per Second
let waveSpeed; // Pixels per Second

let sourcePos;

/*
let cursorSpeed = 40; // Pixels per Second
let cursorPos = 0;
*/

function setup() {
    sketchesCreateCanvas(400, 400);
    noFill();
    sourcePos = createVector(0, 0);

    frequencySlider = createSlider(0, 60, 5);
    waveSpeedSlider = createSlider(0, 400, 80);

    frequencySlider.label("Frequency");
    waveSpeedSlider.label("Wavespeed")
}

function draw() {
    background(220);
    timeSinceStart += deltaTime / 1000;

    frequency = frequencySlider.value();
    waveSpeed = waveSpeedSlider.value();

    //cursorPos += cursorSpeed * deltaTime / 1000;
    let sourceDelta = createVector(mouseX, mouseY).sub(sourcePos);
    sourceDelta.limit(waveSpeed * deltaTime / 1000)
    sourcePos.add(sourceDelta);

    if (timeSinceStart - timeOfLast > 1 / frequency) {
        append(wfs, new Wavefront(sourcePos.x, sourcePos.y, waveSpeed));
        timeOfLast = timeSinceStart;
    }

    for (let i = 0; i < wfs.length; i++) {
        wfs[i].update();
        if (wfs[i].r > 300) {
            wfs.splice(i, 1);
            i--;
        }
    }
}

class Wavefront {
    constructor(x, y, c) {
        this.x = x;
        this.y = y;
        this.c = c;
        this.r = 0;
    }

    update() {
        stroke(0, 300 - this.r);
        circle(this.x, this.y, this.r * 2);
        this.r += this.c * deltaTime / 1000;
    }
}