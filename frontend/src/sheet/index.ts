import { make_element_editable, saveCheck, show_message } from "../common";
import { send_update, Datamap, Elementdata, Tabledata } from "../common";
import { editable_list, editable_table, Listdata, EditType } from "../common"
import { editable_check_progress } from "../widgets/check_progress";
import { ListLineData } from "../common"

function init_sharebutton() {
    const button = document.getElementById('sharebtn')
    if(button) {
        button.onclick = (e: Event) => {
            e.preventDefault();
            console.log("Activate share to get link")
            const id = button.getAttribute('data-id')
            const url = `/api/character/${id}/share`;
            const xhr = new XMLHttpRequest()
            xhr.open('GET', url);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onload = () => {
                const share_data = JSON.parse(xhr.responseText)
                const message = share_data.html;
                show_message(message);
            }
            xhr.send();

        }
    }
}

function init_editable() {
    console.log("Init editable values");
    const editables: HTMLElement[] = <HTMLElement[]>Array.from(document.getElementsByClassName('editable'));
    
    const save = (datamap: Datamap | DOMStringMap, data: Elementdata|Tabledata) => {
        console.log("Save data");
        console.log(data);
        send_update(datamap, data);
    }

    editables.forEach(element => {
        const dataType = element.getAttribute('data-type');
        switch(dataType) {
            case 'area':
                make_element_editable(element, save, "text");
                break;
            case 'picture':
                break;
            default:
                make_element_editable(element, save, dataType as EditType);
                break;
        }
    })
}

function init_editable_binaries() {
    console.log("Init editable binaries");
    const checkboxes: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    checkboxes.forEach(element => {
        if(element.type === "checkbox" && element.getAttribute('data-type') === 'binary') {
            element.onchange = () => {
                //console.log(element.getAttribute('data-field'), element.checked);
                saveCheck(element);
            }
        }
    });
}

function save_list_element(element: HTMLInputElement, line: HTMLLIElement, index: number, handler: (e: Event) => void, save: (data: ListLineData) => void) {
    const value = element.value;
    line.innerHTML = value;
    line.addEventListener("click", handler);
    console.log(`Should save ${value}`);
    save({line: index, value: value})
}

function edit_list_item(index: number, line: HTMLLIElement, type: EditType, handler: (Event) => void, save: (data: ListLineData) => void) {
    const value = line.innerHTML;
    let editfield = null;

    if(type === "string") {
        editfield = document.createElement('input');
    } else {
        editfield = document.createElement('input');
    }

    editfield.value = value;

    line.innerHTML = "";
    line.append(editfield);
    editfield.focus();

    editfield.addEventListener('focusout', (e: Event) => {
        console.log("Save element");
        save_list_element(editfield, line, index, handler, save);
    })

    editfield.addEventListener('keypress', (e: KeyboardEvent) => {
        const key = e.key || e.keyCode;
        if(key === 13 && e.shiftKey === false) {
            console.log("Save element from keyboard");
            save_list_element(editfield, line, index, handler, save);
        }
    })

    line.removeEventListener("click", handler);
}

function make_list_item_editable(index: number, line: HTMLLIElement, save: (data: ListLineData) => void) {
    const handler = (e: Event) => {
        e.preventDefault();
        console.log("Clicked on list line");
        edit_list_item(index, line, "string", handler, save);
    }

    line.addEventListener('click', handler);
}

function make_list_editable(list: HTMLUListElement|HTMLOListElement, save: (data: ListLineData) => void) {
    const lines: HTMLLIElement[] = Array.from(list.getElementsByTagName('li'));

    lines.forEach((line, index) => {
        console.log(line);
        make_list_item_editable(index, line, save)
        console.log(line.innerHTML, index);
    })
}

function init_editable_lists() {
    console.log("Init editable lists");
    const lists = <HTMLUListElement[]>Array.from(document.getElementsByClassName("editable_list"))


    lists.forEach(list => {
        make_list_editable(list, (data: ListLineData) => {
            const field = list.getAttribute('data-field');
            console.log("Saving list.\n"); 
            console.log(field, data);
            send_update({field: `${field}.${data.line}`, type: "list"}, data.value)
        })

    })
}


let popup: HTMLDivElement = null;
function init_popup() {
    popup = document.createElement('div');
    popup.style.backgroundColor = "#ff0000";
    popup.style.width = "100px";
    popup.style.height = "50px";
    popup.style.position = "absolute";
    popup.style.top = "100px";
    popup.style.left = "100px";
    popup.hidden = true;
    document.body.appendChild(popup);
}

function show_popup(x: number, y: number, content: HTMLElement) {
    popup.style.left = x + "px";
    popup.style.top = y + "px";
    popup.hidden = false;
    popup.innerHTML = "";
    popup.appendChild(content);
}

function close_popup() {
    popup.hidden = true;
}


function init_editable_tables() {
    console.log("Init editable tables");
    const tables: HTMLTableElement[] = <HTMLTableElement[]>Array.from(document.getElementsByClassName('editableTable'));

    tables.forEach(table => {
        editable_table(table, (data: Tabledata) => {
            const field = table.getAttribute('data-field');
            console.log("Saving table.\n"); console.log(data)
            send_update({field: field}, data)
        } );
    });

}


function init_check_progress() {
    console.log("Init check progress");
    const bars: HTMLSpanElement[] = <HTMLSpanElement[]>Array.from(document.getElementsByClassName('editable_check_progress'));
    bars.forEach(bar => {
        editable_check_progress(bar, (value: number) => {
            const field = bar.getAttribute('data-field');
            console.log("Saving progress.\n"); console.log(value);
            send_update({field: field}, value);
        })
    })
}

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the basic character sheet.")
    init_popup();
    init_sharebutton();
    init_editable();
    init_editable_lists();
    init_editable_binaries();
    init_editable_tables();
    init_check_progress();
})
