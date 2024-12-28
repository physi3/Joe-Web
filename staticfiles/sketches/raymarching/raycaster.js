class Raycaster {
    constructor(pos, definition, fov) {
        this.pos = pos.copy();
        this.def = definition;

        this.rotation = 0;
        this.fov = fov;
    }

    cast(c) {
        let m = []
        for (let a = this.rotation - this.fov / 2; a < this.rotation + this.fov / 2; a += this.def) {
            //let ray = new Ray();
            let dir = p5.Vector.fromAngle(a);

            m.push(castRay(this.pos, dir, c));
            //ray.draw(true);
        }
        return m;
    }
}