function sketchesCreateCanvas(width, height) {
    canvas = createCanvas(width, height);
    canvas.parent("sketch-holder");
    return canvas;
}

p5.Element.prototype.label = function(labelText) {
    label = createElement("label");
    span = createElement("span", labelText);
    span.parent(label);

    label.parent("input-holder");
    this.parent(label);
}