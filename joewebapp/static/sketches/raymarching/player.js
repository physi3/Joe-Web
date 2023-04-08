class Player extends Raycaster {
    constructor(width, fov) {
        super(createVector(200, 200), fov / width, fov);
        this.speed = 3;
        this.rotSpeed = 0.05;

        this.sight = [];

    }

    move(dist) {
        this.pos.add(p5.Vector.fromAngle(this.rotation).mult(dist));
    }

    update(c) {
        this.sight = player.cast(c);

        if (keyIsPressed) {
            if (keyIsDown(UP_ARROW) || keyIsDown(87)) {
                player.move(this.speed);
            } else if (keyIsDown(DOWN_ARROW) || keyIsDown(83)) {
                player.move(-this.speed);
            }
            if (keyIsDown(LEFT_ARROW) || keyIsDown(65)) {
                player.rotation -= this.rotSpeed;
            }
            if (keyIsDown(RIGHT_ARROW) || keyIsDown(68)) {
                player.rotation += this.rotSpeed;
            }
        }
    }
    draw() {
        push();
        strokeWeight(5);
        stroke(1);
        translate(this.pos);
        rotate(this.rotation - PI / 2);
        fill(255);
        stroke(255);
        triangle(0, 0, 5, 5, -5, 5);
        point(0, 0);
        pop();
    }
}