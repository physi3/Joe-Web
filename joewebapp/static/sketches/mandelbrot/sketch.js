let field;
let theme;

let mouseStartX;
let mouseStartY;

let mouseDown = false;

function mandelSetup(start, end, w) {
    let size = end.sub(start);
    let h = floor(w * size.imaginary / size.real);

    resizeCanvas(w, h);
    for (let x = 0; x < width; x++)
        for (let y = 0; y < height; y++)
            set(x, y, color(256));
    updatePixels();
    field = new MandelField(start, end, w, h, theme);
}

function setup() {
    createCanvas(600, 600).parent("sketch-holder");
    rectMode(CORNERS);
    noFill();

    //theme = new MandelTheme(15, 0, 35); // White to black
    //theme = new MandelTheme(0, 0, 700); // Classic
    //theme = new MandelTheme(0, 0, 3); // Dark
    //theme = new MandelTheme(256, 1, 70); // Black to white
    //theme = new MandelTheme(256, 1, 700); // Inverse classic
    //theme = new MandelTheme(0, 1, 20); // High Contrast
    theme = new MandelTheme(256, 1, 500, 1); // Small Level

    mandelSetup(new Complex(-2, -1.5), new Complex(1, 1.5), 600)
}

function draw() {
    field.mandelIteration();

    if (mouseDown) {
        stroke(25, 200, 255);
        rect(mouseStartX, mouseStartY, mouseX, mouseY);
    }
}

function mousePressed(event) {
    if (event.button != 0 || event.target.id != "defaultCanvas0") return;

    mouseStartX = mouseX;
    mouseStartY = mouseY;

    mouseDown = true;
}

function mouseReleased(event) {
    if (event.button != 0 || event.target.id != "defaultCanvas0" || !mouseDown) return;

    let mouseEnd = field.indexToPoint(mouseX, mouseY);
    let mouseStart = field.indexToPoint(mouseStartX, mouseStartY);

    mouseDown = false;

    mandelSetup(mouseStart, mouseEnd, 600)
}