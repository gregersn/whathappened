
document.addEventListener('DOMContentLoaded', function(event) {
    const image: HTMLImageElement = <HTMLImageElement>document.getElementById('source_picture');
    
    const canvas: HTMLCanvasElement = document.createElement('canvas');
    canvas.id="canvas";

    const borderWidth = 10;
    const size = Math.min(image.width, image.height) + borderWidth * 2;
    canvas.width = size;
    canvas.height = size;

    image.parentElement.appendChild(canvas);

    const ctx = canvas.getContext("2d");

    ctx.translate(size / 2, size / 2);
    ctx.fillStyle = "#0ff";
    ctx.beginPath();
    ctx.arc(0, 0, size / 2, 0, 2 * Math.PI, true);
    //ctx.fill();
    ctx.clip();
    ctx.drawImage(image, -image.width / 2, -image.height / 2);
    ctx.fillStyle = "#f0f";

    ctx.beginPath();
    ctx.arc(0, 0, size / 2 - borderWidth / 2.0, 0, 2 * Math.PI, false);
    ctx.lineWidth = borderWidth;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(0, 0, size / 2 - borderWidth, 0, 2 * Math.PI, false);
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2.0;
    ctx.stroke();
});
