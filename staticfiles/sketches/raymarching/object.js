class CastObject {
    constructor() {
        this.pos = createVector();
    }
    distance(p) { return null }
}

class Circle extends CastObject {
    constructor(pos, r) {
        super();
        this.radius = r;
        this.pos = pos;
    }
    distance(p) {
        return p.dist(this.pos) - this.radius;
    }
    show() {
        push();
        noStroke();
        fill(0);
        ellipse(this.pos.x, this.pos.y, this.radius * 2);
        pop();
    }
}

class Rectangle extends CastObject {
    constructor(pos, sizeX, sizeY) {
        super();
        this.pos = pos.copy();
        this.size = createVector(sizeX, sizeY);
    }
    distance(p) {
        let offset = vAbs(p5.Vector.sub(p, this.pos)).sub(this.size);
        return vMax(offset, 0).mag(); // Change to include negative
    }
    show() {
        push();
        rectMode(RADIUS);
        noStroke();
        fill(0);
        rect(this.pos.x, this.pos.y, this.size.x, this.size.y);
        pop();
    }
}

class LineSegment extends CastObject{
  constructor(a, b){
    super();
    this.a = a;
    this.b = b;
  }
  distance(p) {
      let l2 = p5.Vector.sub(this.a,this.b).magSq();
      if (l2 == 0) return dist2(p, v);
      var t = ((p.x - this.a.x) * (this.b.x - this.a.x) + (p.y - this.a.y) * (this.b.y - this.a.y)) / l2;
      t = Math.max(0, Math.min(1, t));
      return createVector(this.a.x + t * (this.b.x - this.a.x), this.a.y + t * (this.b.y - this.a.y)).sub(p).mag();
  }
  
  show(){
    push();
    strokeWeight(2);
    stroke(0);
    line(this.a.x, this.a.y, this.b.x, this.b.y)
    pop();
  }
}


function vAbs(v) {
    return createVector(abs(v.x), abs(v.y));
}

function vMax(v1, s) {
    return createVector(Math.max(v1.x, s), Math.max(v1.y, s));
}