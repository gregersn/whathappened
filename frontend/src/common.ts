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
    let value = null; 
    if(editfield.type === "number") {
        value = editfield.valueAsNumber;
    }
    else {
        value = editfield.value;
    }
    const datafields: DOMStringMap = element.dataset;
    const data = Object.assign({}, datafields);
    
    const field = element.getAttribute('data-field');
    console.log(`Save changes to ${field}, new value ${value}`);
    element.innerHTML = value;
    element.addEventListener("click", editable_handler);
    save(data, value);
}

function list_to_obj(list: HTMLUListElement): Listdata {
    let data_rows  = []
    const lines: HTMLLIElement[] = Array.from(list.getElementsByTagName('li'));
    for(const line of lines) {
        data_rows.push(line.innerHTML);
    }
    return data_rows;
}

export const editable_list = (list: HTMLUListElement, save: (data: Listdata) => void) => {
    console.log("Editable list...");
    const lines: HTMLLIElement[] = Array.from(list.getElementsByTagName('li'));
    for(const line of lines) {
        make_element_editable(line, (data: any) => {
            save(list_to_obj(list));
        })
    }

    const parent = list.parentElement;
    const button = document.createElement('button');
    button.innerHTML = "Add...";
    button.onclick = () => {
        const new_item = document.createElement('li');
        new_item.innerHTML = 'New item...';
        list.appendChild(new_item);
        make_element_editable(new_item, (data: any) => {
            save(list_to_obj(list));
        })
    }
    parent.appendChild(button);
}


function editElement(element: HTMLElement, type: edit_type, save: SaveFunction, editable_handler: (e: Event) => void) {
    console.log("Edit element");
    const value = element.innerHTML;
    let editfield = null;

    if(type === "string") {
        editfield = document.createElement("input");
    }
    else if(type === "number") {
        editfield = document.createElement("input");
        editfield.type = "number";
    }
    else if(type === "area") {
        editfield = document.createElement('textarea');
    }
    else {
        editfield = document.createElement("input");       
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


export type edit_type = "input" | "area" | "string" | "number";

const make_editable_handler = (element: HTMLElement, save: SaveFunction, type: edit_type = "input") => {
    const f = (e: Event) => {
        e.preventDefault();
        editElement(element, type, save, f);
    }

    return f;
}

export function make_element_editable(element: HTMLElement, save: SaveFunction, type: edit_type  = "input") {
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

function table_to_obj(table: HTMLTableElement): Tabledata {
    let data_rows = [];

    //const tableName = table.getAttribute('data-field');
    const fields = Array.from(table.tHead.rows[0].cells).map((element, index) => {
        return {'property': element.getAttribute('data-property'), 'index': index, 'type': element.getAttribute('data-type')};
    }).filter((element, index) => {
        if(element['property']) return true;
        return false;
    });

    const rows = Array.from(table.tBodies[0].rows);
    for(const row of rows) {
        const row_data = {}
        fields.forEach(field => {
            if(field['type'] === "number") {
                row_data[field['property']] = Number.parseInt(row.cells.item(field['index']).innerHTML);
            } else {
                row_data[field['property']] = row.cells.item(field['index']).innerHTML;
            }
        });

        data_rows.push(row_data);
    }
    /*data_rows.sort((a, b) => { 
        if( a['name'] < b['name'] ) return -1;
        if( a['name'] > b['name'] ) return 1;
        return 0;})*/

    return data_rows
}

export const editable_table = (table: HTMLTableElement, save: (data: Tabledata) => void) => {
    const make_cell_editable = (cell: HTMLTableCellElement) => {
        make_element_editable(cell, (data: any) => {
            save(table_to_obj(table));
        }, cell.getAttribute('data-type') as edit_type);
    }
    const make_row_editable = (row: HTMLTableRowElement, fields: any[]) => {
        const cells = Array.from(row.cells);
        //console.log(fields);
        cells.forEach((cell, index) => {
            if(fields.find(field => (field['index'] === index))) {
                make_cell_editable(cell);
            }
        })
    }

    const cells = Array.from(table.tHead.rows[0].cells);
    const fields = cells.map((element, index) => {
        return {'property': element.getAttribute('data-property'), 'index': index};
    }).filter((element, index) => {
        if(element['property']) return true;
        return false;
    });

    const rows =  Array.from(table.tBodies[0].rows);
    for(const row of rows) {
        make_row_editable(row, fields);
    }
    const parent = table.parentElement;
    const button = document.createElement('button');
    button.innerHTML = "Add row";

    button.onclick = () => {
        const new_row = table.insertRow(-1);
        new_row.innerHTML = "<td>-</td>".repeat(cells.length);
        make_row_editable(new_row, fields);
    }

    parent.appendChild(button);
}

export function init_set_portrait(field_name: string) {
    console.log("Init set portrait");
    const portraitbox: HTMLElement = <HTMLElement>document.getElementsByClassName('portrait')[0];
    if(portraitbox.classList.contains("editable")) {
        const uploadelement: HTMLInputElement = document.createElement('input');
        uploadelement.type = 'file';
        uploadelement.style.display = 'none';
        uploadelement.onchange = (e: Event) => {
            const reader = new FileReader();
            reader.readAsDataURL(uploadelement.files[0]);
            reader.onload = () => {
                send_update({field: field_name, type: 'portrait'}, reader.result);
            }
        }

        portraitbox.appendChild(uploadelement);
        portraitbox.onclick = (e: Event) => {
            uploadelement.click();
        }
    }
}
