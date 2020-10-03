function show_message(message: string|HTMLElement) {
    const message_box = document.getElementById('messagebox');
    message_box.innerHTML = "";
    if(message instanceof HTMLElement) {
        message_box.appendChild(message);
    } else {
        message_box.innerHTML = message;
    }
    message_box.style.display = 'block';
}

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
                const share_url = JSON.parse(xhr.responseText)
                const message = document.createElement('span');
                message.innerHTML = "Sharable link: ";
                const link = document.createElement('a');
                link.href = share_url;
                link.innerText = share_url;
                message.appendChild(link)
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
