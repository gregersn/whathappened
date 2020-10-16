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

function init_handout_share() {
    const table: HTMLTableElement = <HTMLTableElement>document.getElementsByClassName('handoutshares')[0];
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

document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Initiate the campaign functions.");
    init_handout_share();
})
