class ComplexField {
  constructor(start, end, resX, resY) {
    this.start = start;
    this.end = end;
    this.resX = resX;
    this.resY = resY;
    
    this.field = new Array(resX);
    for (let r = 0; r <= resX; r++){
      this.field[r] = new Array(resY);
      for (let i = 0; i <= resY; i++){
        this.field[r][i] = new FieldPoint(this.indexToPoint(r, i));
      }
    }
    console.log(this.field[0].length);
  }
  
  stepSize(){
    let step = {};
    let size = this.end.sub(this.start);
    step.x = size.real/this.resX;
    step.y = size.imaginary/this.resY;
    return step;
  }
  
  indexToPoint(x, y){
    let step = this.stepSize();
    let unOff = new Complex(x*step.x, y*step.y);
    return unOff.add(this.start);
  }
  
}

class FieldPoint {
  constructor(pos){
    this.pos = pos;
    this.data = {};
  }
}

class MandelField extends ComplexField {
  constructor(start, end, resX, resY, theme){
    super(start, end, resX, resY);
    this.theme = theme;

    for (let r = 0; r <= resX; r++){
      for (let i = 0; i <= resY; i++){
        this.field[r][i].data.mandelTotal = Complex.zero();
        this.field[r][i].data.finite = true;
        set(r, i, color(this.theme.mandelShade));
      }
    }

    updatePixels();
    this.iters = 0;
  }
  
  mandelIteration() {
    for (let r = 0; r <= this.resX; r++){
      for (let i = 0; i <= this.resY; i++){
        let fieldPoint = this.field[r][i];
        if (fieldPoint.data.finite){
          fieldPoint.data.mandelTotal = fieldPoint.data.mandelTotal.square().add(fieldPoint.pos);
          fieldPoint.data.finite = fieldPoint.data.mandelTotal.isFinite();
          
          if (!fieldPoint.data.finite)
            set(r, i, this.itersToColour());
          if (!fieldPoint.data.finite && this.iters == 0 && this.theme.relative)
            this.iters = 1;
        }
      }
    }
    updatePixels();
    if (!this.theme.relative || this.iters != 0)
      this.iters ++;
  }
  itersToColour(){
    let f = this.iters/(this.theme.decayRate+this.iters)
    return 256*(1-this.theme.decayToWhite+(2*this.theme.decayToWhite-1)*f);
  }
  
}

class MandelTheme{
  constructor(mandelShade, decayToWhite, decayRate, relative = 0){
    this.mandelShade = mandelShade;
    this.decayToWhite = decayToWhite;
    this.decayRate = decayRate;
    this.relative = relative;
  }
}