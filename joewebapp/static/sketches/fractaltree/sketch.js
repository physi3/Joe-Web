let newRandomSeed;
let waveTime = 0;

function setup() {
  sketchesCreateCanvas(1000, 700);
  angleMode(DEGREES); // Set angle mode to degrees
  newRandomSeed = random(0, 2000)
}

function draw() {
  background(230);
  randomSeed(newRandomSeed);
  translate(width / 2, height); // Move to bottom center
  stroke(0); // Set stroke color to black
  branch(150); // Start drawing the tree
  waveTime += deltaTime / 50;
}

function branch(len) {
  // Base case: if the branch is too short, stop drawing
  if (len < 8) {
    return;
  }

  // Draw the branch
  strokeWeight(map(len, 10, 150, 1, 15));
  line(0, 0, 0, -len);

  // Move to the end of the branch
  translate(0, -len);

  // Create two new branches, rotating randomly
  push();
  rotate(random(15, 45) + 3 * cos(waveTime));
  branch(len * random(0.6, 0.8));
  pop();

  push();
  rotate(-random(15, 45) + 2 * cos(waveTime * 1.1));
  branch(len * random(0.6, 0.8));
  pop();
}
