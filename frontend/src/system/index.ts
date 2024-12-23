import {
    Datamap,
    Elementdata,
    get_meta_tag,
    make_element_editable,
    Tabledata,
} from "../common";

function update(datamap: Datamap | DOMStringMap, value: any) {
    const xhr = new XMLHttpRequest();
    const url = document.location.href;
    const field_name = datamap.field.split(".")[1];

    console.log(url);
    console.log(field_name);

    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", get_meta_tag("_token"));
    xhr.setRequestHeader("x-csrf-token", get_meta_tag("_token"));
    xhr.onload = () => {
        console.log(`Post done, got ${xhr.status} ${xhr.statusText}`);
        if (xhr.status === 200 && xhr.statusText === "OK") {
        }
    };

    const payload = { field_name: field_name, value: value };

    console.log(`Sending: ${JSON.stringify(payload)}`);
    xhr.send(JSON.stringify([payload]));
}

function init_editable() {
    const editables: HTMLElement[] = <HTMLElement[]>(
        Array.from(document.getElementsByClassName("editable"))
    );

    const save = (
        datamap: Datamap | DOMStringMap,
        data: Elementdata | Tabledata
    ) => {
        console.log(datamap.field);
        console.log(data);
        update(datamap, data);
    };

    editables.forEach((element) => {
        make_element_editable(element, save);
    });
}

document.addEventListener("DOMContentLoaded", function (event) {
    console.log("Initiate system functionality");
    init_editable();
});
