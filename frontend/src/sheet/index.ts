import { make_element_editable, saveCheck, show_message } from "../common";
import { send_update, Datamap, Elementdata, Tabledata } from "../common";

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



document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the basic character sheet.")
    init_sharebutton();
    init_editable();
    init_editable_binaries();
})
