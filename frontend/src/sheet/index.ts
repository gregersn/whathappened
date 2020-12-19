import { make_element_editable, saveCheck, show_message } from "../common";
import { send_update, Datamap, Elementdata, Tabledata } from "../common";
import { editable_list, editable_table, Listdata } from "../common"

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
                make_element_editable(element, save, "area");
                break;
            case 'picture':
                break;
            default:
                make_element_editable(element, save);
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

function init_editable_lists() {
    console.log("Init editable lists");
    const lists = <HTMLUListElement[]>Array.from(document.getElementsByClassName("editable_list"))

    lists.forEach(list => {
        editable_list(list, (data: Listdata) => {
            const field = list.getAttribute('data-field');
            console.log("Saving list.\n"); console.log(data);
            send_update({field: field}, data)
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

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the basic character sheet.")
    init_popup();
    init_sharebutton();
    init_editable();
    init_editable_lists();
    init_editable_binaries();
    init_editable_tables();
})
