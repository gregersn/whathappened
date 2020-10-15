function switch_tab(tab_id: string, tab_content: string, tabset: HTMLElement) {
    const tabs: HTMLElement[] = <HTMLElement[]>Array.from(tabset.getElementsByClassName('tab-content'));
    tabs.forEach(tab => {
        tab.style.display = 'none';
    });

    document.getElementById(tab_content).style.display = 'block';
    // TODO: Highlight selected tab
}

function init_tabs() {
    console.log("Init tabs");
    const tabsets: HTMLElement[] = <HTMLElement[]>Array.from(document.getElementsByClassName('tabs'));
    tabsets.forEach(tabset => {
        const tabs: HTMLElement[] = <HTMLElement[]>Array.from(tabset.getElementsByClassName('tab-content'));
        if(tabs.length < 2) return;
        const menucontainer =  document.createElement('div');
        const tabmenu = document.createElement('ul');
        tabmenu.classList.add('tab-menu');
        tabs.forEach((tab, idx) => {
            const menuitem = document.createElement('li');
            const menutrigger = document.createElement('a');

            menutrigger.href = ""
            menutrigger.innerHTML = tab.getAttribute('data-name');
            menutrigger.onclick = (e: Event) => {e.preventDefault(); switch_tab("", tab.id, tabset); }
            menuitem.appendChild(menutrigger);
            tabmenu.appendChild(menuitem);

            if(idx > 0)
                tab.style.display = 'none';
        })
        menucontainer.appendChild(tabmenu);
        tabset.prepend(menucontainer);
    })
}


function create_button(label: string, func: (e: Event) => void): HTMLElement {
    const btn = document.createElement('button');
    btn.classList.add("editor-button");
    btn.onclick = (e: Event) => {
        e.preventDefault();
        func(e);
    }
    btn.innerHTML = label;
    return btn;
}

function insertAtCursor(input: HTMLInputElement|HTMLTextAreaElement, text: string) {
    const isSuccess = document.execCommand('insertText', false, text);
    
    if(!isSuccess && typeof input.setRangeText === "function") {
        const start = input.selectionStart;
        input.setRangeText(text);
        input.selectionStart = input.selectionEnd = start + text.length;

        const e = document.createEvent("UIEvent");
        e.initEvent("input", true, false);
        input.dispatchEvent(e);
    }
}

function selected_asset_url(): string {
    const selector: HTMLSelectElement = <HTMLSelectElement>document.getElementsByClassName('asset-selector')[0];
    return selector.value;
}

function setup_editor(element: HTMLTextAreaElement) {
    const toolbar = document.createElement('div');
    const container = document.createElement('div');

    element.parentElement.replaceChild(container, element);
    container.appendChild(toolbar);
    container.appendChild(element);

    toolbar.appendChild(create_button("I", async () => {
        const url = await selected_asset_url();
        insertAtCursor(element, `![image](${url})\n`)
    }))
}

function init_editor() {
    console.log("Init editor");
    const editor: HTMLTextAreaElement[] =  <HTMLTextAreaElement[]>Array.from(document.getElementsByClassName('markdown-editor'));
    editor.forEach(el => {
        setup_editor(el);
    })
}

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the handout stuff.")
    init_tabs();
    init_editor();
})
