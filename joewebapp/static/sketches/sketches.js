let canvases = [];

function sketchesCreateCanvas(width, height) {
    canvas = createCanvas(width, height);
    canvas.parent("sketch-holder");
    canvases.push([canvas, width, height]);
    resizeCanvases();
    return canvas;
}

p5.Element.prototype.label = function(labelText) {
    label = createElement("label");
    span = createElement("span", labelText);
    span.parent(label);

    label.parent("input-holder");
    this.parent(label);
}

function resizeCanvases() {
    for (ci in canvases){
        var canvas = canvases[ci][0]
        var canvasWidth = canvases[ci][1]
        var canvasElement = document.getElementById(canvas.id());

        console.log(canvasElement)
        if (canvasWidth + 20 > this.window.innerWidth){
            canvasElement.style.width = `${this.window.innerWidth - 20}px`;
        } else {
            canvasElement.style.width =  `${canvasWidth}px`;
        }
        canvasElement.style.height = "";
    }
}

window.addEventListener('resize', resizeCanvases, true);