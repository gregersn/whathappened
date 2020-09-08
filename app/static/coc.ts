console.log("Hello, Coc!");

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

document.addEventListener('DOMContentLoaded', function(event) {
    //the event occurred
    init_skillchecks();
    init_skillvalues();
  })
