let img;
let circles = [];
let points = [];

function setup() {
  sketchesCreateCanvas(img.width, img.height)
  
  for (let x = 0; x < img.width; x ++){
    for (let y = 0; y < img.height; y ++){
      if (img.get(x, y)[3] > 127){
        points.push(createVector(x, y));
      }
    }
  }
}

function draw() {
  background(19.2, 20, 22)
  
  for (let _ = 0; _ < 15; _ ++) {
    let rPoint = randomPoint(points, circles);
    if (rPoint != null)
      circles.push(new Circle(rPoint, img.get(rPoint.x, rPoint.y).slice(0, 3)))
  }
  
  for (let ci in circles){
    let c = circles[ci];
    c.grow(circles);
    c.display();
  }
  
}

function randomPoint(points, circles, maxAttempts = 5) {
  let selectedPoint;
  let attempts = 0;
  
  do {
    if (attempts >= maxAttempts)
      return null
    
    selectedPoint = random(points)
    attempts++;
  } while (isOccupied(selectedPoint, circles))
    
  return selectedPoint;
}

function isOccupied(p, circles){
  for (let ci in circles){
    let c = circles[ci];
    if (p5.Vector.sub(c.pos, p).magSq() <= (c.r * c.r)){
      return true;
    }
  }
  return false;
}

class Circle{
  constructor(pos, colour){
    this.pos = pos;
    this.colour = colour;
    
    this.r = 0;
    this.rv = 0.4;
    this.growing = true;
  }
  
  grow(otherCircles){
    if (!this.growing) return;
    
    this.r += this.rv;
    for (let ci in otherCircles){
      let c = otherCircles[ci];
      if (c != this && p5.Vector.sub(c.pos, this.pos).magSq() <= (c.r + this.r)*(c.r + this.r)){
        this.growing = false;
        c.growing = false;
      }
    }
  }
  
  display(){
    stroke(this.colour)
    noFill()
    circle(this.pos.x, this.pos.y, this.r * 2);
  }
}