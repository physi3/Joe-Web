let c = [];
let centre;
let points = [];

let player;

let sceneX = 400;
let sceneW = 400;
let sceneH = 400;

let drawingRectangle = false;

function setup() {
    sketchesCreateCanvas(800, 400);

    c = [
        new Circle(createVector(100, 150), 20),
        new Circle(createVector(300, 125), 30),
        new Rectangle(createVector(200, 50), 50, 40),
        new Rectangle(createVector(20, 200), 20, 100),

        new LineSegment(createVector(0, 0), createVector(0, 400)),
        new LineSegment(createVector(0, 400), createVector(400, 400)),
        new LineSegment(createVector(400, 400), createVector(400, 0)),
        new LineSegment(createVector(400, 0), createVector(0, 0)),
    ];
    player = new Player(sceneW, radians(60));


}

function draw() {
    background(25);

    for (let ci of c)
        ci.show();

    player.update(c);
    player.draw();

    drawScene();

    if (drawingRectangle) {
        var rect = c[c.length - 1];
        var newSize = createVector(Math.abs(rect.pos.x - mouseX), Math.abs(rect.pos.y - mouseY));
        console.log(newSize);
        rect.size = newSize;
    }
}

function drawScene() {
    push();
    noStroke();
    fill(0);
    rect(sceneX, 0, width, height);
    rectMode(CENTER);
    const increment = sceneW / player.sight.length;
    let o = 0;
    for (let d of player.sight) {
        fill(map(d, 0, 400, 255, 0));
        let h = map(400 / d, 1, 10, 0, sceneH)
        rect(sceneX + o, sceneH / 2, increment, h);
        o += increment;
    }
    pop();
}

function mousePressed() {
    c.push(new Rectangle(createVector(mouseX, mouseY), 0, 0))
    drawingRectangle = true;
}

function mouseReleased() {
    drawingRectangle = false;
}