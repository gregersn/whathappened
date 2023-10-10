export type Datamap = {
    field: string;
    subfield?: string | undefined;
    type?:
        | "skillcheck"
        | "binary"
        | "area"
        | "table"
        | "occupationcheck"
        | undefined;
};

export type Elementdata = any;
export type Tabledata = any[];
export type Listdata = string[];
export type SaveFunction = (
    datamap: Datamap | DOMStringMap,
    data: Elementdata | Tabledata
) => void;

function saveElement(
    editfield: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement,
    element: HTMLElement,
    save: SaveFunction,
    editable_handler: (e: Event) => void
) {
    let value = null;
    if (
        editfield instanceof HTMLInputElement &&
        (editfield.type === "number" || editfield.type === "integer")
    ) {
        value = isNaN(editfield.valueAsNumber)
            ? element.getAttribute("data-blank")
            : editfield.valueAsNumber;
    } else {
        value = editfield.value;
    }
    const datafields: DOMStringMap = element.dataset;
    const data = Object.assign({}, datafields);

    const field = element.getAttribute("data-field");
    console.log(`Save changes to ${field}, new value ${value}`);
    element.innerHTML = value;
    element.addEventListener("click", editable_handler);
    save(data, value);
}

function parse_value(value: any, value_type: string) {
    console.log(`Converting ${value} to ${value_type}`);
    switch (value_type) {
        case "number":
        case "integer":
            return Number.parseInt(value);

        case "string":
            return String(value);

        case "boolean":
            return value == "True";
        case "":
            return value;

        default:
            throw new Error(`Unknown value type: ${value_type}`);
            break;
    }
}

export function list_to_obj(list: HTMLUListElement): Listdata {
    let data_rows = [];
    const lines: HTMLLIElement[] = Array.from(list.getElementsByTagName("li"));
    for (const line of lines) {
        data_rows.push(line.innerHTML);
    }
    return data_rows;
}

export const editable_list = (
    list: HTMLUListElement,
    save: (data: Listdata) => void
) => {
    console.log("Editable list...");
    const lines: HTMLLIElement[] = Array.from(list.getElementsByTagName("li"));

    const parent = list.parentElement;
    const button = document.createElement("button");
    button.innerHTML = "Add...";
    button.onclick = () => {
        console.log("Adding row to list");
        send_update(
            { field: `${list.getAttribute("data-field")}.-1` },
            "New item..."
        );
        const blank = "New item...";
        const field = `${list.getAttribute("data-field")}.${
            list.childElementCount
        }`;
        const type = list.getAttribute("data-type");
        const new_item: HTMLLIElement = create_editable(
            "li",
            type,
            field,
            blank
        ) as HTMLLIElement;
        list.appendChild(new_item);
    };
    parent.appendChild(button);
};

function editElement(
    element: HTMLElement,
    type: edit_type,
    save: SaveFunction,
    editable_handler: (e: Event) => void
) {
    console.log("Edit element");
    const value = element.innerHTML;
    let editfield: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement =
        null;

    let choices = element.getAttribute("data-choices");

    if (choices) {
        editfield = document.createElement("select");
        JSON.parse(choices).forEach((choice) => {
            const option = document.createElement("option");
            option.value = choice;
            option.innerHTML = choice;
            editfield.appendChild(option);
        });
    } else if (type === "string") {
        editfield = document.createElement("input");
    } else if (type === "number" || type === "integer") {
        editfield = document.createElement("input") as HTMLInputElement;
        editfield.type = "number";
        editfield.min = element.getAttribute("data-min");
        editfield.max = element.getAttribute("data-max");
        editfield.setAttribute(
            "data-blank",
            element.getAttribute("data-blank")
        );
    } else if (type === "area") {
        editfield = document.createElement("textarea");
    } else {
        editfield = document.createElement("input");
    }

    editfield.value = value;

    element.innerHTML = "";
    element.append(editfield);
    editfield.focus();

    editfield.addEventListener("focusout", (e) => {
        saveElement(editfield, element, save, editable_handler);
    });

    editfield.addEventListener("keypress", (e: KeyboardEvent) => {
        if (e.keyCode === 13 && e.shiftKey === false) {
            saveElement(editfield, element, save, editable_handler);
        }
    });

    element.removeEventListener("click", editable_handler);
}

export type edit_type = "input" | "area" | "string" | "number" | "integer";

const make_editable_handler = (
    element: HTMLElement,
    save: SaveFunction,
    type: edit_type = "input"
) => {
    const f = (e: Event) => {
        e.preventDefault();
        editElement(element, type, save, f);
    };

    return f;
};

export function make_element_editable(
    element: HTMLElement,
    save: SaveFunction,
    type: edit_type = "input"
) {
    const editable_handler = make_editable_handler(element, save, type);
    element.addEventListener("click", editable_handler);
    const label = document.getElementById(
        `${element.getAttribute("data-field")}-label`
    );
    if (label) {
        label.addEventListener("click", editable_handler);
    }
}

export function get_meta_tag(tagname: string): string | undefined {
    const metas = document.getElementsByTagName("meta");
    for (const meta of metas) {
        if (meta.name === tagname) return meta.content;
    }
    return undefined;
}

export function show_message(message: string | HTMLElement) {
    const message_box = document.getElementById("messagebox");
    message_box.innerHTML = "";
    if (message instanceof HTMLElement) {
        message_box.appendChild(message);
    } else {
        message_box.innerHTML = message;
    }
    message_box.style.display = "block";
}

export function send_update(datamap: Datamap | DOMStringMap, value: any) {
    const busy = document.getElementById("busy");
    const xhr = new XMLHttpRequest();
    const url = document.location.href + "update";
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", get_meta_tag("_token"));
    xhr.setRequestHeader("x-csrf-token", get_meta_tag("_token"));
    xhr.onload = () => {
        console.log(`Post done, got ${xhr.status} ${xhr.statusText}`);
        if (xhr.status === 200 && xhr.statusText === "OK") {
            busy.style.display = "none";
        }
    };

    datamap["value"] = value;

    console.log(`Sending: ${JSON.stringify(datamap)}`);
    // Disable due to interference with checkprogress
    // TODO: Find new solution
    //busy.style.display = "block";
    xhr.send(JSON.stringify([datamap]));
}

export function saveCheck(editfield: HTMLInputElement) {
    const value = editfield.checked;
    const datafields: DOMStringMap = editfield.dataset;
    const data = Object.assign({}, datafields);
    //console.log(data, value);
    send_update(data, value);
}

function table_to_obj(table: HTMLTableElement): Tabledata {
    let data_rows = [];

    //const tableName = table.getAttribute('data-field');
    const fields = Array.from(table.tHead.rows[0].cells)
        .map((element, index) => {
            return {
                property: element.getAttribute("data-property"),
                index: index,
                type: element.getAttribute("data-type"),
                blank: element.getAttribute("data-blank"),
            };
        })
        .filter((element, index) => {
            if (element["property"]) return true;
            return false;
        });

    const rows = Array.from(table.tBodies[0].rows);
    for (const row of rows) {
        const row_data = {};
        fields.forEach((field) => {
            if (field["type"] === "number" || field["type"] === "integer") {
                const value = Number.parseInt(
                    row.cells.item(field["index"]).innerHTML
                );
                row_data[field["property"]] = isNaN(value)
                    ? field["blank"]
                    : value;
            } else {
                row_data[field["property"]] = row.cells.item(
                    field["index"]
                ).innerHTML;
            }
        });

        data_rows.push(row_data);
    }
    /*data_rows.sort((a, b) => { 
        if( a['name'] < b['name'] ) return -1;
        if( a['name'] > b['name'] ) return 1;
        return 0;})*/

    return data_rows;
}

const create_editable = (
    tagname: keyof HTMLElementTagNameMap,
    data_type: string,
    data_field: string,
    data_blank: any
) => {
    const editable = document.createElement(tagname);
    editable.setAttribute("data-type", data_type);

    if (data_type == "boolean") {
        const new_input: HTMLInputElement = document.createElement("input");
        new_input.type = "checkbox";
        new_input.setAttribute("data-field", data_field);
        new_input.setAttribute("data-type", "binary");
        new_input.onchange = () => {
            saveCheck(new_input);
        };
        editable.append(new_input);
    } else {
        const new_span: HTMLSpanElement = document.createElement("span");
        new_span.setAttribute("data-field", data_field);
        new_span.setAttribute("data-type", data_type);
        new_span.innerText = data_blank;

        const save = (
            datamap: Datamap | DOMStringMap,
            data: Elementdata | Tabledata
        ) => {
            console.log("Save data");
            console.log(data);
            send_update(datamap, data);
        };
        editable.append(new_span);
        make_element_editable(new_span, save, data_type as edit_type);
    }

    return editable;
};

export const editable_table_2 = (table: HTMLTableElement) => {
    const parent = table.parentElement;

    const button = document.createElement("button");
    button.innerHTML = "Add row";

    const table_body = table.getElementsByTagName("tbody")[0];
    const table_header = table.getElementsByTagName("thead")[0];
    button.onclick = () => {
        // Set data-row on tr (length + 1)
        console.log("Adding row to table");
        console.log(`${table.getAttribute("data-field")}.-1`);
        console.log("Default values");
        const default_values = {};
        for (const cell of table_header.rows[0].cells) {
            default_values[cell.getAttribute("data-property")] = parse_value(
                cell.getAttribute("data-blank"),
                cell.getAttribute("data-type")
            );
        }
        send_update(
            { field: `${table.getAttribute("data-field")}.-1` },
            default_values
        );
        console.log(default_values);
        const new_row = table_body.insertRow(-1);
        new_row.setAttribute("data-row", new_row.rowIndex.toString());
        // set data-type on each row, with data-blank
        for (const cell of table_header.rows[0].cells) {
            const type = cell.getAttribute("data-type");
            const field = `${table.getAttribute("data-field")}.${
                new_row.rowIndex - 1
            }.${cell.getAttribute("data-property")}`;
            const blank = cell.getAttribute("data-blank");

            const new_cell: HTMLTableCellElement = create_editable(
                "td",
                type,
                field,
                blank
            ) as HTMLTableCellElement;
            new_row.appendChild(new_cell);
            //console.log(cell);
        }
    };

    parent.appendChild(button);
};

export const editable_table = (
    table: HTMLTableElement,
    save: (data: Tabledata) => void
) => {
    const make_cell_editable = (cell: HTMLTableCellElement) => {
        make_element_editable(
            cell,
            (data: any) => {
                save(table_to_obj(table));
            },
            cell.getAttribute("data-type") as edit_type
        );
    };
    const make_row_editable = (row: HTMLTableRowElement, fields: any[]) => {
        const cells = Array.from(row.cells);
        //console.log(fields);
        cells.forEach((cell, index) => {
            if (fields.find((field) => field["index"] === index)) {
                make_cell_editable(cell);
            }
        });
    };

    const cells = Array.from(table.tHead.rows[0].cells);
    const fields = cells
        .map((element, index) => {
            return {
                property: element.getAttribute("data-property"),
                index: index,
            };
        })
        .filter((element, index) => {
            if (element["property"]) return true;
            return false;
        });

    const rows = Array.from(table.tBodies[0].rows);
    for (const row of rows) {
        make_row_editable(row, fields);
    }
    const parent = table.parentElement;
    const button = document.createElement("button");
    button.innerHTML = "Add row";

    const table_body = table.getElementsByTagName("tbody")[0];
    button.onclick = () => {
        const new_row = table_body.insertRow(-1);
        new_row.innerHTML = "<td>-</td>".repeat(cells.length);
        make_row_editable(new_row, fields);
    };

    parent.appendChild(button);
};

export function init_set_portrait(field_name: string) {
    console.log("Init set portrait");
    const portraitbox: HTMLElement = <HTMLElement>(
        document.getElementsByClassName("portrait")[0]
    );
    if (portraitbox.classList.contains("editable")) {
        const uploadelement: HTMLInputElement = document.createElement("input");
        uploadelement.type = "file";
        uploadelement.style.display = "none";
        uploadelement.onchange = (e: Event) => {
            const reader = new FileReader();
            reader.readAsDataURL(uploadelement.files[0]);
            reader.onload = () => {
                send_update(
                    { field: field_name, type: "portrait" },
                    reader.result
                );
            };
        };

        portraitbox.appendChild(uploadelement);
        portraitbox.onclick = (e: Event) => {
            uploadelement.click();
        };
    }
}

export async function http<T>(request: RequestInfo): Promise<T> {
    const response = await fetch(request);
    const body = await response.json();
    return body;
}

export const ExportedForTesting = {
    saveElement,
    editElement,
};
