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

