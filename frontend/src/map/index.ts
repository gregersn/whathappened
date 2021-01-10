import { SVG, Element, Svg, G } from '@svgdotjs/svg.js';

let svg: Svg | undefined = undefined;
let map_content: G;

type position = {
    x: number,
    y: number
};

function getMousePosition(evt) {
    const CTM = map_content.screenCTM();
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
let panning: boolean = false;

function makeDraggable(element: Element) {
    element.mousedown((evt: MouseEvent) => {
        // Start drag
        selectedElement = SVG(evt.target);
        selectedElement.front();
        offset = getMousePosition(evt);
        offset.x -= selectedElement.x();
        offset.y -= selectedElement.y();
    })
}


function mouse_controls(group: G) {
    svg.on('wheel', (e: WheelEvent) => {
        e.preventDefault();    
        const zoom_dir = e.deltaY / Math.abs(e.deltaY)

        if(zoom_dir < 0 && zoom_factor < 5) {
            zoom_factor *= 1.5;
        }
        else if(zoom_dir > 0 && zoom_factor > 0.2) {
            zoom_factor /= 1.5;
        }

        const matrix = group.transform();
        group.transform({scale: zoom_factor});
    })

    svg.mousedown((e: MouseEvent) => {
        if(e.button == 0 && e.shiftKey) {
            panning = true;
            e.preventDefault();
            offset = getMousePosition(e);
            offset.x -= map_content.x();
            offset.y -= map_content.y();
    
        }
    });

    svg.mousemove((evt: MouseEvent) => {
        // Drag
        if(selectedElement && !panning) {
            evt.preventDefault();
            const coord = getMousePosition(evt);
            (selectedElement as Element).move(coord.x - offset.x, coord.y - offset.y);
        }

        if(panning) {
            evt.preventDefault();
            const coord = getMousePosition(evt);
            map_content.move(coord.x - offset.x, coord.y - offset.y);
        }
    })

    svg.mouseup((evt: MouseEvent) => {
        // End drag
        selectedElement = null;
        panning = false;
    })


}

function add_background(src: string, group: G) {
    const background = group.image(src);
    background.attr({'pointer-events': 'none'});
}

function add_token(group: G) {

}

type Token = {
    position: {
        x: number,
        y: number
    },
    color: string
}

type MapData = {
    background: {
        src: string
    },
    tokens: Token[]
}

const map_data: MapData = {
    background: {
        src: 'https://mk0a2minutetabl7hq7i.kinstacdn.com/wp-content/uploads/2018/10/Haunted-Garden-RPG-battle-map-square-grid-1.jpg'
    },
    tokens: [
        {
            position: {x: 0, y: 0},
            color: "#f06"
        },
        {
            position: {x: 70, y: 105},
            color: "#60f"
        },
        {
            position: {x: 442, y: 170},
            color: "#6f0"
        }
    ]
}

export function show_map(container: HTMLDivElement) {
    svg = SVG().addTo(container).size('100%', '100%');
    map_content = svg.group();

    mouse_controls(map_content);

    add_background(map_data.background.src, map_content);
    map_data.tokens.forEach(token => {
        const t = map_content.rect(34, 34).attr({fill: token.color}).move(token.position.x, token.position.y)
        makeDraggable(t);
    })
}
