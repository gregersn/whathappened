import { get_meta_tag, http } from "../common";

function set_handout_state(
    player_id: number,
    campaign_id: number,
    handout_id: number,
    state: boolean,
) {
    const url = `/api/campaign/${campaign_id}/handout/${handout_id}/players`;
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.setRequestHeader("X-CSRFToken", get_meta_tag("_token"));
    xhr.setRequestHeader("x-csrf-token", get_meta_tag("_token"));

    xhr.send(JSON.stringify({ player_id: player_id, state: state }));
}

function set_npc_visibility(
    npc_id: number,
    campaign_id: number,
    state: boolean,
) {
    const url = `/api/campaign/${campaign_id}/npc/${npc_id}`;
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.setRequestHeader("X-CSRFToken", get_meta_tag("_token"));
    xhr.setRequestHeader("x-csrf-token", get_meta_tag("_token"));

    xhr.send(JSON.stringify({ npc_id: npc_id, visibility: state }));
}

function update_handouts(handouts, handout_list: HTMLUListElement) {
    console.log("Update handouts");
    const sha = handout_list.getAttribute("data-sha");
    if (sha === handouts["sha"]) return;

    handout_list.innerHTML = "";
    handouts["handouts"].forEach((handout) => {
        const li = document.createElement("li");
        li.innerHTML = `<a href=${handout["url"]}>${handout["title"]}</a>`;
        handout_list.appendChild(li);
    });
    handout_list.setAttribute("data-sha", handouts["sha"]);
}

function update_npcs(npcs, npc_container: HTMLElement) {
    console.log("Update NPCs");
    const list = document.getElementById("npc_list");

    const npcs_elements = npcs.npcs.map((npc) => {
        const div = document.createElement("div");
        div.classList.add("characterinfo");
        div.classList.add("splitcontainer");

        div.innerHTML =
            '<div class="personalia npc">' +
            `${npc.name} (${npc.age})<br />${npc.description}` +
            "</div>" +
            '<div class="portrait">' +
            `<img src="${npc.portrait}" />` +
            "</div>";

        return div;
    });

    list.innerHTML = "";
    npcs_elements.forEach((el) => list.appendChild(el));
}

function get_handouts(campaign_id: number, handout_list: HTMLUListElement) {
    console.log("Getting handouts");
    const url = `/api/campaign/${campaign_id}/handouts/`;

    const xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            const handouts = JSON.parse(xhr.responseText);
            update_handouts(handouts, handout_list);
        }
    };
    xhr.send();
}

function update_messages(messages: Message[], message_table: HTMLTableElement) {
    messages.forEach((element) => {
        const r = document.createElement("tr");
        const t = element.timestamp;

        r.innerHTML =
            `<td>${t.toLocaleString()}</td>` +
            `<td>${element.sender_name}</td>` +
            `<td>${element.to_name}</td>` +
            `<td>${element.message}</td>`;
        message_table.appendChild(r);
    });
}

interface Message {
    id: number;
    timestamp: string;
    message: string;
    sender_name: string;
    to_name: string;
}

async function get_messages(
    campaign_id: number,
    last_message: number,
    message_table: HTMLTableElement,
) {
    const url = `/api/campaign/${campaign_id}/messages?after=${last_message}`;
    const messages = await http<Message[]>(url);
    update_messages(messages, message_table);
    if (messages.length > 0) {
        last_message = Math.floor(
            new Date(messages[messages.length - 1].timestamp).getTime() /
                1000.0,
        );
    }
    return last_message;
}

function get_npcs(campaign_id: number, npc_container: HTMLElement) {
    console.log("Get NPCs");
    const url = `/api/campaign/${campaign_id}/npcs/`;
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            const npcs = JSON.parse(xhr.responseText);
            update_npcs(npcs, npc_container);
        }
    };
    xhr.send();
}

function init_handout_share() {
    const table: HTMLTableElement = <HTMLTableElement>(
        document.getElementsByClassName("handoutshares")[0]
    );
    if (!table) return;
    const checkboxes: HTMLInputElement[] = <HTMLInputElement[]>(
        Array.from(table.getElementsByTagName("input"))
    );

    checkboxes.forEach((cb) => {
        cb.onchange = () => {
            const player_id = Number.parseInt(cb.getAttribute("data-player"));
            const campaign_id = Number.parseInt(
                cb.getAttribute("data-campaign"),
            );
            const handout_id = Number.parseInt(cb.getAttribute("data-handout"));
            const state = cb.checked;

            set_handout_state(player_id, campaign_id, handout_id, state);
            console.log(player_id, campaign_id, handout_id, state);
        };
    });
}

const init_handout_watch = () => {
    console.log("Init handout watch");
    const handout_list = <HTMLUListElement>(
        document.getElementsByClassName("player_handouts")[0]
    );
    if (!handout_list) return false;
    const campaign_id = Number.parseInt(
        handout_list.getAttribute("data-campaign"),
        10,
    );
    const handout_section = document.getElementById("handout_section");
    handout_section.getElementsByTagName("h3")[0].onclick = () =>
        get_handouts(campaign_id, handout_list);
    /*const refresh_handouts = () => {
        get_handouts(campaign_id, handout_list);
        window.setTimeout(refresh_handouts, 10000);
    }
        refresh_handouts();*/
};

function init_npc_control() {
    const npcs: HTMLDivElement[] = <HTMLDivElement[]>(
        Array.from(document.getElementsByClassName("npc"))
    );

    npcs.forEach((npc) => {
        const visibility: HTMLInputElement = <HTMLInputElement>(
            npc.getElementsByClassName("visibility")[0]
        );
        if (visibility)
            visibility.onchange = () => {
                const npc_id = Number.parseInt(
                    visibility.getAttribute("data-npc"),
                );
                const campaign_id = Number.parseInt(
                    visibility.getAttribute("data-campaign"),
                );
                const state = visibility.checked;
                console.log(`Visibility toggled on ${npc_id} to ${state}`);
                set_npc_visibility(npc_id, campaign_id, state);
            };
    });
}

function init_npc_refresh() {
    console.log("Init NPC refresh");
    const npc_container: HTMLElement = document.getElementById("npc_section");
    if (!npc_container || npc_container.classList.contains("editable")) return;
    const campaign_id = Number.parseInt(
        npc_container.getAttribute("data-campaign"),
    );
    npc_container.getElementsByTagName("h3")[0].onclick = () =>
        get_npcs(campaign_id, npc_container);
}

function init_message_refresh(campaign_id: number) {
    console.log("Init message refresh");
    const message_table: HTMLTableElement = <HTMLTableElement>(
        document.getElementById("campaign_messages")
    );
    if (message_table) {
        let last_message = 0;
        const refresh_messages = async () => {
            last_message = await get_messages(
                campaign_id,
                last_message,
                message_table,
            );
            window.setTimeout(refresh_messages, 5000);
        };
        refresh_messages();
    }
}

declare global {
    interface Window {
        wh_campaign: any;
    }
}

window.wh_campaign = window.wh_campaign || {};

document.addEventListener("DOMContentLoaded", function (event) {
    console.log("Initiate the campaign functions.");
    init_handout_share();
    init_handout_watch();
    init_npc_control();
    init_npc_refresh();
    init_message_refresh(window.wh_campaign.id);
    console.log("Done");
});
