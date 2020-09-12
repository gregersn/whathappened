console.log("Cthulhu fhtagn!");

function init_skillchecks() {
    console.log("Init skillchecks");
    const checkboxes: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    checkboxes.forEach(element => {
        if(element.type == "checkbox") {
            element.onchange = () => {
                console.log(element.id, element.checked);
            }
        }
    });
}

function init_skillvalues() {
    console.log("Init skill values");
    const inputs: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    inputs.forEach(element => {
        if(element.type == "text") {
            element.onchange = () => {
                console.log(element.id, element.value);
            }
        }
    })
}

const editable_handler = function(e: Event) {
    e.preventDefault();
    editElement(this);
}

function send_update(key: string, value: any) {
    const xhr = new XMLHttpRequest()
    const url = document.location.href;
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = () => {
        console.log("Post done");
        console.log(url);
        console.log(xhr.status);
        console.log(xhr.statusText);
    }
    let data = {}
    data[key] = value;
    xhr.send(JSON.stringify(data));
}

function editElement(element: Element) {
    console.log("Edit element");
    const value = element.innerHTML;
    const editfield = document.createElement("input");
    editfield.value = value;

    element.innerHTML = "";
    element.append(editfield);
    editfield.focus();

    editfield.addEventListener("focusout", (e) => {
        saveElement(editfield, element);
    })

    editfield.addEventListener("keypress", (e) => {
        if(e.keyCode === 13 && e.ctrlKey === false) {
            saveElement(editfield, element);
        }
    })
    
    element.removeEventListener("click", editable_handler);
}

function saveElement(editfield: HTMLInputElement, element: Element) {
    const value = editfield.value;
    const field = element.getAttribute('data-field');
    console.log(`Save changes to ${field}, new value ${value}`);
    send_update(field, value);
    element.innerHTML = value;
    element.addEventListener("click", editable_handler);
}


function init_editable() {
    console.log("Init editable values");
    const editables: Element[] = Array.from(document.getElementsByClassName('editable'));
    editables.forEach(element => {
        element.addEventListener("click", editable_handler);
    })
}

document.addEventListener('DOMContentLoaded', function(event) {
    //the event occurred
    init_skillchecks();
    init_skillvalues();
    init_editable();
  })
