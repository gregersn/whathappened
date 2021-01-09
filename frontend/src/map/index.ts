import { SVG, Element, Svg, G } from '@svgdotjs/svg.js';


//document.addEventListener('DOMContentLoaded', function(event) {
    //console.log("Hello, map")
//}

let svg: Svg | undefined = undefined;
let map_content: G;

type position = {
    x: number,
    y: number
};

function getMousePosition(evt) {
    const CTM = (svg as Svg).screenCTM();
    return {
        x: (evt.clientX - CTM.e) / CTM.a,
        y: (evt.clientY - CTM.f) / CTM.d

    };
}

function draw_grid(draw: Svg) {

}

let selectedElement: Element;
let offset: position;
let zoom_factor: number = 1.0;

function makeDraggable(element: Element) {
    element.mousedown((evt: MouseEvent) => {
        // Start drag
        selectedElement = SVG(evt.target);
        selectedElement.front();
        offset = getMousePosition(evt);
        offset.x -= selectedElement.x();
        offset.y -= selectedElement.y();

    })

    svg.mousemove((evt: MouseEvent) => {
        // Drag
        if(selectedElement) {
            evt.preventDefault();
            const coord = getMousePosition(evt);
            (selectedElement as Element).move(coord.x - offset.x, coord.y - offset.y);
        }
    })

    element.mouseup((evt: MouseEvent) => {
        // End drag
        selectedElement = null;
    })

}


function pan_and_zoom(group: G) {
    svg.on('wheel', (e: WheelEvent) => {
        e.preventDefault();    
        const zoom_dir = e.deltaY / Math.abs(e.deltaY)

        if(zoom_dir > 0 && zoom_factor < 5) {
            zoom_factor *= 1.5;
        }
        else if(zoom_dir < 0 && zoom_factor > 0.2) {
            zoom_factor /= 1.5;
        }

        group.transform({scale: zoom_factor});
    })
}

export function show_map(container: HTMLDivElement) {
    console.log("Look out!");

    svg = SVG().addTo(container).size('100%', '100%');
    map_content = svg.group();

    pan_and_zoom(map_content);
    const rect = map_content.rect(100, 100).attr({fill: '#f06'});
    const rect2 = map_content.rect(150, 150).attr({fill: '#60f'}).move(50, 50);
    const rect3 = map_content.rect(150, 150).attr({fill: '#6f0'}).move(100, 100);

    makeDraggable(rect);
    makeDraggable(rect2);
    makeDraggable(rect3);
}