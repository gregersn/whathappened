import { get_meta_tag, Listdata, make_element_editable, saveCheck, SaveFunction, Tabledata } from "../common"
import { send_update, Datamap } from "../common"


function init_skillchecks() {
    console.log("Init skillchecks");
    const checkboxes: HTMLInputElement[] = Array.from(document.getElementsByTagName('input'));
    checkboxes.forEach(element => {
        if(element.type === "checkbox" && element.getAttribute('data-type') === 'skillcheck') {
            element.onchange = () => {
                //console.log(element.getAttribute('data-field'), element.checked);
                saveCheck(element);
            }
        }
    });
}


let popup: HTMLDivElement = null;
function init_popup() {
    popup = document.createElement('div');
    popup.style.backgroundColor = "#ff0000";
    popup.style.width = "100px";
    popup.style.height = "50px";
    popup.style.position = "absolute";
    popup.style.top = "100px";
    popup.style.left = "100px";
    popup.hidden = true;
    document.body.appendChild(popup);
}

function show_popup(x: number, y: number, content: HTMLElement) {
    popup.style.left = x + "px";
    popup.style.top = y + "px";
    popup.hidden = false;
    popup.innerHTML = "";
    popup.appendChild(content);
}

function close_popup() {
    popup.hidden = true;
}

function show_subskillform(x: number, y: number, parent: string) {
    const formcontainer: HTMLDivElement = <HTMLDivElement>document.getElementById("subskillform");
    formcontainer.style.left = x + "px";
    formcontainer.style.top = y + "px";
    formcontainer.hidden = false;

    const parentfield: HTMLInputElement = <HTMLInputElement>document.getElementById('subskillform-parent');
    parentfield.value = parent;
}

function init_skill_edits() {
    console.log("Init skill edits");
    const skillnames: HTMLElement[] = <HTMLElement[]>Array.from(document.getElementsByClassName('skillname'));
    skillnames.forEach(element => {
        const occupation_field = element.getAttribute('data-field');
        const occupation_subfield = element.getAttribute('data-subfield');
        
        const occupation_checker = document.createElement('input');
        occupation_checker.type = "checkbox";
        occupation_checker.hidden = true;
        if(element.classList.contains('occupation')) {
            occupation_checker.checked = true;
        }
        occupation_checker.onchange = () => {
            console.log("Changed occupation on skill", occupation_field);
            if(occupation_checker.checked) {
                element.classList.add('occupation');
            } else {
                element.classList.remove('occupation');
            }
            occupation_checker.hidden = true;
            send_update({field: occupation_field, subfield: occupation_subfield, type: "occupationcheck"}, occupation_checker.checked);
        }
        element.parentElement.appendChild(occupation_checker);

        let btn_add_subskill: null | HTMLButtonElement = null;
        if(element.getAttribute('data-specializations')) {
            btn_add_subskill = document.createElement('button');
            btn_add_subskill.hidden  = true;
            btn_add_subskill.innerHTML = "Add subskill";
            btn_add_subskill.onclick = (e: MouseEvent) => {
                show_subskillform(e.pageX, e.pageY, element.getAttribute('data-field'));
                
            }
            element.parentElement.appendChild(btn_add_subskill);

        }

        element.onclick = (e: Event) => {
            occupation_checker.hidden = !occupation_checker.hidden;
            if(element.getAttribute('data-specializations')) {
                btn_add_subskill.hidden = !btn_add_subskill.hidden;
            }
        }


    })
}

function table_to_obj(table: HTMLTableElement): Tabledata {
    let data_rows = [];

    //const tableName = table.getAttribute('data-field');
    const fields = Array.from(table.tHead.rows[0].cells).map((element, index) => {
        return {'property': element.getAttribute('data-property'), 'index': index};
    }).filter((element, index) => {
        if(element['property']) return true;
        return false;
    });

    const rows = Array.from(table.tBodies[0].rows);
    for(const row of rows) {
        const row_data = {}
        fields.forEach(field => {
            row_data[field['property']] = row.cells.item(field['index']).innerHTML;
        });

        data_rows.push(row_data);
    }
    /*data_rows.sort((a, b) => { 
        if( a['name'] < b['name'] ) return -1;
        if( a['name'] > b['name'] ) return 1;
        return 0;})*/

    return data_rows
}

function list_to_obj(list: HTMLUListElement): Listdata {
    let data_rows  = []
    const lines: HTMLLIElement[] = Array.from(list.getElementsByTagName('li'));
    for(const line of lines) {
        data_rows.push(line.innerHTML);
    }
    return data_rows;
}

const editable_list = (list: HTMLUListElement, save: (data: Listdata) => void) => {
    console.log("Editable list...");
    const lines: HTMLLIElement[] = Array.from(list.getElementsByTagName('li'));
    for(const line of lines) {
        make_element_editable(line, (data: any) => {
            save(list_to_obj(list));
        })
    }

    const parent = list.parentElement;
    const button = document.createElement('button');
    button.innerHTML = "Add item";
    button.onclick = () => {
        const new_item = document.createElement('li');
        new_item.innerHTML = 'New item...';
        list.appendChild(new_item);
        make_element_editable(new_item, (data: any) => {
            save(list_to_obj(list));
        })
    }
    parent.appendChild(button);
}

const editable_table = (table: HTMLTableElement, save: (data: Tabledata) => void) => {
    const make_cell_editable = (cell: HTMLTableCellElement) => {
        make_element_editable(cell, (data: any) => {
            save(table_to_obj(table));
        });
    }
    const make_row_editable = (row: HTMLTableRowElement, fields: any[]) => {
        const cells = Array.from(row.cells);
        //console.log(fields);
        cells.forEach((cell, index) => {
            if(fields.find(field => (field['index'] === index))) {
                make_cell_editable(cell);
            }
        })
    }

    const cells = Array.from(table.tHead.rows[0].cells);
    const fields = cells.map((element, index) => {
        return {'property': element.getAttribute('data-property'), 'index': index};
    }).filter((element, index) => {
        if(element['property']) return true;
        return false;
    });

    const rows =  Array.from(table.tBodies[0].rows);
    for(const row of rows) {
        make_row_editable(row, fields);
    }
    const parent = table.parentElement;
    const button = document.createElement('button');
    button.innerHTML = "Add row";

    button.onclick = () => {
        const new_row = table.insertRow(-1);
        new_row.innerHTML = "<td>-</td>".repeat(cells.length);
        make_row_editable(new_row, fields);
    }

    parent.appendChild(button);
}



function init_editable_tables() {
    console.log("Init editable tables");
    const tables: HTMLTableElement[] = <HTMLTableElement[]>Array.from(document.getElementsByClassName('editableTable'));

    tables.forEach(table => {
        editable_table(table, (data: Tabledata) => {
            const field = table.getAttribute('data-field');
            console.log("Saving table.\n"); console.log(data)
            send_update({field: field}, data)
        } );
    });

}

function init_editable_lists() {
    console.log("Init editable lists");
    const lists = <HTMLUListElement[]>Array.from(document.getElementsByClassName("editable_list"))

    lists.forEach(list => {
        editable_list(list, (data: Listdata) => {
            const field = list.getAttribute('data-field');
            console.log("Saving list.\n"); console.log(data);
            send_update({field: field}, data)
        })
    })
}

function init_set_portrait() {
    console.log("Init set portrait");
    const portraitbox: HTMLElement = <HTMLElement>document.getElementsByClassName('portrait')[0];
    if(portraitbox.classList.contains("editable")) {
        const uploadelement: HTMLInputElement = document.createElement('input');
        uploadelement.type = 'file';
        uploadelement.style.display = 'none';
        uploadelement.onchange = (e: Event) => {
            const reader = new FileReader();
            reader.readAsDataURL(uploadelement.files[0]);
            reader.onload = () => {
                send_update({field: 'personalia.Portrait', type: 'portrait'}, reader.result);
            }
        }

        portraitbox.appendChild(uploadelement);
        portraitbox.onclick = (e: Event) => {
            uploadelement.click();
        }
    }
}


document.addEventListener('DOMContentLoaded', function(event) {
    console.log("Cthulhu fhtagn!");

    init_popup();
    init_skillchecks();
    init_editable_tables();
    init_editable_lists();
    init_skill_edits();
    init_set_portrait();
  })
