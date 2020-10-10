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

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the handout stuff.")
    init_tabs();
})
