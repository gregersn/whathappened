import { get_meta_tag } from "../common"

function set_handout_state(player_id: number, campaign_id: number, handout_id: number, state: boolean) {
    const url = `/api/campaign/${campaign_id}/handout/${handout_id}/players`;
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', "application/json;charset=UTF-8");
    xhr.setRequestHeader("X-CSRFToken", get_meta_tag('_token'));
    xhr.setRequestHeader('x-csrf-token', get_meta_tag('_token'));

    xhr.send(JSON.stringify({"player_id": player_id, "state": state}));
}

function update_handouts(handouts, handout_list: HTMLUListElement) {
    console.log("Update handouts");
    const sha = handout_list.getAttribute('data-sha');
    if(sha === handouts['sha']) return;

    handout_list.innerHTML = "";
    handouts['handouts'].forEach(handout => {
        const li = document.createElement('li');
        li.innerHTML = `<a href=${handout['url']}>${handout['title']}</a>`;
        handout_list.appendChild(li);
    });
    handout_list.setAttribute('data-sha', handouts['sha']);
}

function get_handouts(campaign_id: number, handout_list: HTMLUListElement) {
    const url = `/api/campaign/${campaign_id}/handouts/`;

    const xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.setRequestHeader('Content-Type', "application/json;charset=UTF-8");
    xhr.onload = () => {
        if(xhr.status >= 200 && xhr.status < 300) {
            const handouts = JSON.parse(xhr.responseText)
            update_handouts(handouts, handout_list);
        }
    }
    xhr.send();
}

function init_handout_share() {
    const table: HTMLTableElement = <HTMLTableElement>document.getElementsByClassName('handoutshares')[0];
    if(!table) return;
    const checkboxes: HTMLInputElement[] = <HTMLInputElement[]>Array.from(table.getElementsByTagName('input'));

    checkboxes.forEach(cb => {
        cb.onchange = () => {
            const player_id = Number.parseInt(cb.getAttribute('data-player'));
            const campaign_id = Number.parseInt(cb.getAttribute('data-campaign'));
            const handout_id = Number.parseInt(cb.getAttribute('data-handout'));
            const state = cb.checked;

            set_handout_state(player_id, campaign_id, handout_id, state);
            console.log(player_id, campaign_id, handout_id, state);
        }
    });
}

const init_handout_watch = () => {
    console.log("Init handout watch")
    const handout_list = <HTMLUListElement>document.getElementsByClassName('player_handouts')[0];
    if(!handout_list) return false;
    const campaign_id = Number.parseInt(handout_list.getAttribute('data-campaign'), 10);
    const refresh_handouts = () => {
        get_handouts(campaign_id, handout_list);
        window.setTimeout(refresh_handouts, 10000);
    }
    refresh_handouts();
}

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the campaign functions.");
    init_handout_share();
    init_handout_watch();
})
