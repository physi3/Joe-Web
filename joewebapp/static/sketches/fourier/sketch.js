let tSlide;
let fourier;

let axes;

let fourierJSON;

function setup() {
  sketchesCreateCanvas(800, 500);

  let fourierClasses = {
    "britain" : new FourierClass(Fourier.JSONCoef("britain"), 100, false),
    "ukraine" : new FourierClass(Fourier.JSONCoef("ukraine"), 100, false),
    "linear": new FourierClass(Fourier.LinearCoef, 100),
    "step": new FourierClass(Fourier.StepCoef, 100),
    "ellipse": new FourierClass(Fourier.EllipseCoef, 100),
    "fish": new FourierClass(Fourier.FishCoef, 100)
  };

  let currentFourierClass = fourierClasses["britain"];

  Fourier.scale = 200;
  let initalJ = 100;
  fourier = currentFourierClass.createFourier(initalJ);

  tSlide = createSlider(0, 1, 0, 0);
  tSlide.label("");
  tSlide.size(350);
  tSlide.id("tSlide");

  dropdown = createSelect();

  jInput = createInput(initalJ, "number");
  jInput.label("Number of coefficients:");

  dropdown.option("Britain", "britain");
  dropdown.option("Ukraine", "ukraine");
  dropdown.option("Linear", "linear");
  dropdown.option("Step", "step");
  
  dropdown.label("Function:")
  dropdown.changed(() => {
    currentFourierClass = fourierClasses[dropdown.value()];
    fourier = currentFourierClass.createFourier(parseInt(jInput.value()));
  });

  jInput.changed(() => {
    fourier = currentFourierClass.createFourier(parseInt(jInput.value()));
  });

  axes = new Axes(createVector(100, 250), 300);
}

class FourierClass {

  constructor(coefficientFunction, maxK, real = true) {
    this.coefficientFunction = coefficientFunction;
    this.maxK = maxK;
    this.real = real;
  }

  createFourier(K) {
    let last = this.real ? new RealFourierParent(-300, 300) : new ComplexFourierParent();

    for (let k = 0; k < K; k++) {
      for (let s = -1; s <= 1; s += 2) {
        let coeff = this.coefficientFunction(s * k);
        if (math.abs(coeff) < 0.00001)
          continue;
        last = new FourierComponent(coeff, s * k, last);

        if (k == 0)
          break;
      }
    }

    return last;
  }
}

function draw() {
  background(240);
  axes.draw();

  translate(width / 2, height / 2);
  rotate(-HALF_PI);

  noFill(0);
  stroke(0, 0, 0, 100);
  fourier.drawRecursive(tSlide.value());

  stroke(255, 0, 0);
  let end = fourier.end(tSlide.value());
  strokeWeight(10);
  point(end.x, end.y);

  strokeWeight(1);
  stroke(255, 0, 0);
  fourier.drawUpto(tSlide.value(), 1000);
}

class Axes {
  constructor(origin, scale) {
    this.origin = origin;
    this.scale = scale;
  }

  draw() {
    stroke(200);
    strokeWeight(1);
    line(this.origin.x, 0, this.origin.x, height);
    line(0, this.origin.y, width, this.origin.y);
  }
}

class Fourier{
  static scale = 1;

  static LinearCoef(k) {
    if (k == 0)
      return math.complex(0, 0);
    
    return math.complex(0, -2 * k * math.PI).inverse();
  }

  static StepCoef(k) {
    if (k % 2 == 0)
      return math.complex(0, 0);

    return math.complex(0, 1 / (math.PI * k));
  }

  static EllipseCoef(k) {
    switch (k) {
      case 1:
        return math.complex(2, 0);
      case -1:
        return math.complex(0.5, 0);
      default:
        return math.complex(0, 0);
    }
  }

  static FishCoef(k) {
    switch (k) {
      case 1:
        return math.complex(0, 1);
      case -1:
        return math.complex(0, 0.9);
      case 2:
        return math.complex(0, -0.5);
      default:
        return math.complex(0, 0);
    }
  }

  static JSONCoef(name) {
    function get_coefficient(k) {
      let coeffs = fourierJSON[name]['coefficients'];
      if (coeffs.hasOwnProperty(k)) {
        let [real, imag] = coeffs[k];
        return math.complex(imag, real);
      }
      return math.complex(0, 0);
    }
    return get_coefficient;
  }
}

class FourierComponent {
  constructor(coefficient, frequency, parent) {
    this.coefficient = math.multiply(coefficient, Fourier.scale);
    this.coefficentPolar = this.coefficient.toPolar();
    this.frequency = frequency;
    this.parent = parent;
    this.cache = {};
  }
  
  center(t) {
    return this.parent.end(t);
  }

  end(t) {
    if (this.cache.hasOwnProperty(t))
      return this.cache[t];

    let angle = this.coefficentPolar.phi + this.frequency * t * Math.PI * 2;
    let end = createVector(
      this.coefficentPolar.r * Math.cos(angle),
      this.coefficentPolar.r * Math.sin(angle)
    ).add(this.center(t));
    this.cache[t] = end;
    return end;
  }

  draw(t) {
    strokeWeight(1);
    let center = this.center(t);
    let end = this.end(t);

    circle(center.x, center.y, this.coefficentPolar.r * 2);
    line(center.x, center.y, end.x, end.y);

    strokeWeight(4);
    point(end.x, end.y);
  }

  drawRecursive(t) {
    this.draw(t);
    this.parent.drawRecursive(t);
  }

  drawUpto(t, n = 100) {
    let last = this.end(0);
    for (let i = 0; i < n * t; i++) {
      let newP = this.end(i / n);
      line(last.x, last.y, newP.x, newP.y);
      last = newP;
    }
    let finalP = this.end(t);
    line(last.x, last.y, finalP.x, finalP.y);
  }
}

class ComplexFourierParent {
  end(t) {
    return createVector(0, 0);
  }

  drawRecursive(t) {
    strokeWeight(4);
    point(0, 0);
  }
}

class RealFourierParent {
  constructor(min = -1, max = 1) {
    this.min = min;
    this.max = max;
  }

  end(t) {
    return createVector(0, map(t, 0, 1, this.min, this.max));
  }

  drawRecursive(t) {
    strokeWeight(4);
    point(this.end(t).x, this.end(t).y);
  }
}