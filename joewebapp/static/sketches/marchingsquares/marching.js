let msqLookup = [
  [],
  [[0, 3]],
  [[0, 1]],
  [[1, 3]],
  [[3, 2]],
  [[0, 2]],
  [[0,3], [1, 2]],
  [[1, 2]],
  [[1, 2]],
  [[0,3], [1, 2]],
  [[0, 2]],
  [[3, 2]],
  [[1, 3]],
  [[0, 1]],
  [[0, 3]],
  [],
];

function linesToPoint(line){
  switch (line){
    case 0:
      return createVector(0.5, 0);
    case 1:
      return createVector(1, 0.5);
    case 2:
      return createVector(0.5, 1);
    case 3:
      return createVector(0, 0.5);
  }
}

function indexFromPoints(points, thresh = 0.5){
  let index = 0;
  for (let i = 0; i < 4; i++)
    if (points[i] < thresh)
      index += 1 << i;
  return index;
}

function drawSqaure(index, off, size = 1){
  msqLookup[index].forEach(function (lines){
    var pointa = linesToPoint(lines[0]).mult(size);
    var pointb = linesToPoint(lines[1]).mult(size);
    line(pointa.x+off.x, pointa.y+off.y, pointb.x+off.x, pointb.y+off.y);
  })
}