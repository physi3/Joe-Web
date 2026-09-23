const mouseTracers = document.getElementsByClassName("mouse-tracer");

window.onpointermove = event => { 
    const { clientX, clientY } = event;
    
    for (let index = 0; index < mouseTracers.length; index++) {
        const mouseTracer = mouseTracers[index];
        const gradient = mouseTracer.getAttribute("gradient")
        const box = mouseTracer.getBoundingClientRect();
        
        console.log();

        mouseTracer.style.background = `radial-gradient(600px at ${clientX - box.left}px ${clientY - box.top}px, ${gradient})`
    }
    //mouseTracer.animate({
    //  left: `${clientX}px`,
    //  top: `${clientY}px`
    //}, { duration: 3000, fill: "forwards" });
  }