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

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the basic character sheet.")
    init_sharebutton();
})
