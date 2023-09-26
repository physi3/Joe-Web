class PerlinSpace{
  constructor(scale, xoff = null, yoff = null){
    this.scale = scale;
    
    this.xoff = xoff ? xoff : random(100, 1000);
    this.yoff = yoff ? xoff : random(100, 1000);
  }
  getNoise(x, y){
    return noise(this.xoff + x*this.scale, this.yoff + y*this.scale);
  }
  fillCanvas(){
    for (let x = 0; x < width; x++)
      for(let y = 0; y < height; y++)
        set(x, y, this.getNoise(x, y)*255);
    updatePixels();
  }
}