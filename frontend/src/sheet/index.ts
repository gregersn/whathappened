import { show_message } from "../common";


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

function init_valueadjusters() {
    const adjusters: HTMLDivElement[] = <HTMLDivElement[]>Array.from(document.getElementsByClassName('value_adjuster'));
    adjusters.forEach(adjuster => {
        console.log("Setting up adjuster");
        const datafield = adjuster.getAttribute('data-field');
        console.log("For field " + datafield);

        const input = <HTMLInputElement>adjuster.getElementsByTagName('input')[0];
        const button_add = <HTMLButtonElement>adjuster.getElementsByClassName('add')[0];
        const button_subtract = <HTMLButtonElement>adjuster.getElementsByClassName('subtract')[0];

        button_add.onclick = () => {
            if(!input.valueAsNumber) return;
            console.log(`Add ${input.valueAsNumber}`);
            input.value = '';
        }
        
        button_subtract.onclick = () => {
            if(!input.valueAsNumber) return;
            console.log(`Subtract ${input.valueAsNumber}`);
            input.value = '';
        }
    });
}

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the basic character sheet.")
    init_sharebutton();
    init_valueadjusters();
})
