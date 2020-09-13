console.log("Cthulhu fhtagn!");

function init_skillchecks() {
    console.log("Init skillchecks");
    const checkboxes: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    checkboxes.forEach(element => {
        if(element.type === "checkbox" && element.getAttribute('data-type') === 'skillcheck') {
            element.onchange = () => {
                console.log(element.getAttribute('data-field'), element.checked);
                saveCheck(element);
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
    editElement(this, "input");
}

const editable_area_handler = function(e: Event) {
    e.preventDefault();
    editElement(this, "area");
}

function send_update(datamap: any, value: any) {
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
    datamap['value'] = value;

    console.log(JSON.stringify(datamap));
    xhr.send(JSON.stringify([datamap, ]));
}

function editElement(element: HTMLElement, type: "area" | "input") {
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
        saveElement(editfield, element);
    })

    editfield.addEventListener("keypress", (e) => {
        if(e.keyCode === 13 && e.ctrlKey === false) {
            saveElement(editfield, element);
        }
    })
    
    element.removeEventListener("click", editable_handler);
}

function saveElement(editfield: HTMLInputElement, element: HTMLElement) {
    const value = editfield.value;
    const datafields: DOMStringMap = element.dataset;
    const data = Object.assign({}, datafields);
    
    const field = element.getAttribute('data-field');
    console.log(`Save changes to ${field}, new value ${value}`);
    send_update(data, value);
    element.innerHTML = value;
    element.addEventListener("click", editable_handler);
}

function saveCheck(editfield: HTMLInputElement) {
    const value = editfield.checked;
    const datafields: DOMStringMap = editfield.dataset;
    const data = Object.assign({}, datafields);
    console.log(data, value);
    send_update(data, value);
}

function init_editable() {
    console.log("Init editable values");
    const editables: Element[] = Array.from(document.getElementsByClassName('editable'));
    editables.forEach(element => {
        if(element.getAttribute('data-type') == 'area') {
           element.addEventListener("click", editable_area_handler); 
        } else {
            element.addEventListener("click", editable_handler);
        }
    })
}

function init_editable_binaries() {
    const checkboxes: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    checkboxes.forEach(element => {
        if(element.type === "checkbox" && element.getAttribute('data-type') === 'binary') {
            element.onchange = () => {
                console.log(element.getAttribute('data-field'), element.checked);
                saveCheck(element);
            }
        }
    });
}




document.addEventListener('DOMContentLoaded', function(event) {
    //the event occurred
    init_skillchecks();
    // init_skillvalues();
    init_editable();
    init_editable_binaries();
  })
