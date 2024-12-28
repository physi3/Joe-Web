class Complex {
  constructor(real, imaginary){
    this.real = real;
    this.imaginary = imaginary;
  }
  copy(){
    return new Complex(this.real, this.imaginary)
  }
  square(){
    return new Complex(this.real*this.real - this.imaginary*this.imaginary, 2*this.real*this.imaginary);
  }
  add(o){
    return new Complex(this.real+o.real, this.imaginary+o.imaginary)
  }
  sub(o){
    return new Complex(this.real-o.real, this.imaginary-o.imaginary)
  }
  isFinite(){
    return isFinite(this.real) && isFinite(this.imaginary);
  }
  static zero(){
    return new Complex(0, 0);
  }
}