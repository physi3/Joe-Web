let noiseSpace;

let step = 2;
let thresholdSlide;

let pointArr;

function setup() {
    createCanvas(600, 600).parent("sketch-holder");
    noiseSpace = new PerlinSpace(0.005);

    pointArr = createArray(noiseSpace);
    thresholdSlide = createSlider(0, 1, 0.5, 0.001);
    thresholdSlide.input(updateSquares);

    thresholdSlide.label("Threshold");

    updateSquares();
}

function createArray(noiseSpace) {
    let out = [];
    for (let x = 0; x <= width; x += step) {
        out.push([]);
        for (let y = 0; y <= height; y += step)
            out[x / step].push(noiseSpace.getNoise(x, y));
    }
    return out;
}

function updateSquares() {
    background(220);
    noiseSpace.fillCanvas();

    strokeWeight(5);

    for (let x = 0; x < pointArr.length - 1; x++)
        for (let y = 0; y < pointArr[x].length - 1; y++)
            drawSqaure(indexFromPoints([
                pointArr[x][y],
                pointArr[x + 1][y],
                pointArr[x][y + 1],
                pointArr[x + 1][y + 1]
            ], thresholdSlide.value()), createVector(x * step, y * step), step);

}