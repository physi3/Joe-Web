const min = 0.1;
const max = 500;

function castRay(pos, direction, objects, out = null) {
    let p = pos.copy(),
        r;
    if (out) { out.begin(pos, direction); }

    do {
        r = Infinity;
        for (let object of objects) {
            let d = object.distance(p);
            if (d < r) r = d;
        }
        if (r > max) break;
        if (out) { out.addStep(p, r); }
        p.add(p5.Vector.mult(direction, r));
    } while (r > min);
    if (out) { out.finish(p); }
    return p.sub(pos).mag();
}

class Ray {
    constructor() {
        this.start = createVector();

        this.steps = [];
        this.end = createVector();
        this.vector = createVector();
        this.length = 0;
    }

    begin(pos) {
        this.start = pos.copy();
    }

    addStep(pos, r) {
        this.steps.push([pos.copy(), r]);
    }

    finish(endPoint) {
        this.end = endPoint.copy();
        this.vector = p5.Vector.sub(endPoint, this.pos)
        this.length = this.vector.mag();
    }

    draw(drawSteps = true) {
        push();

        stroke(255, 255, 255, 100);
        strokeWeight(2);
        line(this.start.x, this.start.y, this.end.x, this.end.y);

        if (drawSteps) {
            strokeWeight(1);
            fill(255, 255, 255, 50);
            for (let step of this.steps) {
                ellipse(step[0].x, step[0].y, step[1] * 2);
            }
        }

        stroke(200);
        strokeWeight(8);
        point(this.start);

        pop();
    }

}