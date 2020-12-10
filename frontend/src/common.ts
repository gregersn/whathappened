export type Datamap = {
    field: string,
    subfield?: string | undefined,
    type?: "skillcheck" | "binary" | "area" | "table" | "occupationcheck" | undefined
}

export type Elementdata = any;
export type Tabledata = any[];
export type Listdata = string[];
export type SaveFunction = (datamap: Datamap | DOMStringMap, data: Elementdata | Tabledata) => void

function saveElement(editfield: HTMLInputElement, element: HTMLElement, save: SaveFunction, editable_handler: (e: Event) => void) {
    const value = editfield.value;
    const datafields: DOMStringMap = element.dataset;
    const data = Object.assign({}, datafields);
    
    const field = element.getAttribute('data-field');
    console.log(`Save changes to ${field}, new value ${value}`);
    element.innerHTML = value;
    element.addEventListener("click", editable_handler);
    save(data, value);
}




function editElement(element: HTMLElement, type: "area" | "input", save: SaveFunction, editable_handler: (e: Event) => void) {
    console.log("Edit element");
    const value = element.innerHTML;
    let editfield = null;

    if(type === "input") {
        editfield = document.createElement("input");
    }
    else if(type == "area") {
        editfield = document.createElement('textarea');
    }

    editfield.value = value;

    element.innerHTML = "";
    element.append(editfield);
    editfield.focus();

    editfield.addEventListener("focusout", (e) => {
        saveElement(editfield, element, save, editable_handler);
    })

    editfield.addEventListener("keypress", (e) => {
        if(e.keyCode === 13 && e.shiftKey === false) {
            saveElement(editfield, element, save, editable_handler);
        }
    })
    
    element.removeEventListener("click", editable_handler);
}


const make_editable_handler = (element: HTMLElement, save: SaveFunction, type: "input" | "area" = "input") => {
    const f = (e: Event) => {
        e.preventDefault();
        editElement(element, type, save, f);
    }

    return f;
}

export function make_element_editable(element: HTMLElement, save: SaveFunction, type: "input" | "area"  = "input") {
    const editable_handler = make_editable_handler(element, save, type);
    element.addEventListener("click", editable_handler);
}



export function get_meta_tag(tagname: string): string|undefined {
    const metas = document.getElementsByTagName('meta');
    for(const meta of metas) {
        if(meta.name === tagname)
            return meta.content;
    }
    return undefined;
}

export function show_message(message: string|HTMLElement) {
    const message_box = document.getElementById('messagebox');
    message_box.innerHTML = "";
    if(message instanceof HTMLElement) {
        message_box.appendChild(message);
    } else {
        message_box.innerHTML = message;
    }
    message_box.style.display = 'block';
}


export function send_update(datamap: Datamap|DOMStringMap, value: any) {
    const busy = document.getElementById("busy");
    const xhr = new XMLHttpRequest()
    const url = document.location.href + 'update';
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("X-CSRFToken", get_meta_tag('_token'));
    xhr.setRequestHeader('x-csrf-token', get_meta_tag('_token'));
    xhr.onload = () => {
        console.log(`Post done, got ${xhr.status} ${xhr.statusText}`);
        if(xhr.status === 200 && xhr.statusText === 'OK') {
            busy.style.display = 'none';
        }
    }

    datamap['value'] = value;

    console.log(`Sending: ${JSON.stringify(datamap)}`);
    busy.style.display = 'block';
    xhr.send(JSON.stringify([datamap, ]));
}


export function saveCheck(editfield: HTMLInputElement) {
    const value = editfield.checked;
    const datafields: DOMStringMap = editfield.dataset;
    const data = Object.assign({}, datafields);
    //console.log(data, value);
    send_update(data, value);
}
