import { saveCheck } from "../common";
import { send_update, init_set_portrait } from "../common";

function init_skillchecks() {
    console.log("Init skillchecks");
    const checkboxes: HTMLInputElement[] = Array.from(
        document.getElementsByTagName("input")
    );
    checkboxes.forEach((element) => {
        if (
            element.type === "checkbox" &&
            element.getAttribute("data-type") === "skillcheck"
        ) {
            element.onchange = () => {
                //console.log(element.getAttribute('data-field'), element.checked);
                saveCheck(element);
            };
        }
    });
}

function show_subskillform(x: number, y: number, parent: string) {
    const formcontainer: HTMLDivElement = <HTMLDivElement>(
        document.getElementById("subskillform")
    );
    formcontainer.style.left = x + "px";
    formcontainer.style.top = y + "px";
    formcontainer.hidden = false;

    const parentfield: HTMLInputElement = <HTMLInputElement>(
        document.getElementById("subskillform-parent")
    );
    parentfield.value = parent;
}

function init_skill_edits() {
    console.log("Init skill edits");
    const skillnames: HTMLElement[] = <HTMLElement[]>(
        Array.from(document.getElementsByClassName("skillname"))
    );
    skillnames.forEach((element) => {
        const occupation_field = element.getAttribute("data-field");
        const occupation_subfield = element.getAttribute("data-subfield");
        const occupation_checker = document.createElement("input");

        occupation_checker.type = "checkbox";
        occupation_checker.hidden = true;

        if (element.classList.contains("occupation")) {
            occupation_checker.checked = true;
        }

        occupation_checker.onchange = () => {
            console.log("Changed occupation on skill", occupation_field);
            if (occupation_checker.checked) {
                element.classList.add("occupation");
            } else {
                element.classList.remove("occupation");
            }
            occupation_checker.hidden = true;
            send_update(
                {
                    field: occupation_field,
                    subfield: occupation_subfield,
                    type: "occupationcheck",
                },
                occupation_checker.checked
            );
        };

        element.parentElement.appendChild(occupation_checker);

        let btn_add_subskill: null | HTMLButtonElement = null;
        if (element.getAttribute("data-specializations")) {
            btn_add_subskill = document.createElement("button");
            btn_add_subskill.hidden = true;
            btn_add_subskill.innerHTML = "Add subskill";
            btn_add_subskill.onclick = (e: MouseEvent) => {
                show_subskillform(
                    e.pageX,
                    e.pageY,
                    element.getAttribute("data-field")
                );
            };
            element.parentElement.appendChild(btn_add_subskill);
        }

        // Add subt functions
        element.onclick = (e: Event) => {
            occupation_checker.hidden = !occupation_checker.hidden;
            if (element.getAttribute("data-specializations")) {
                btn_add_subskill.hidden = !btn_add_subskill.hidden;
            }
        };
    });
}

document.addEventListener("DOMContentLoaded", function (event) {
    console.log("Cthulhu fhtagn!");
    init_skillchecks();
    init_skill_edits();
    //init_set_portrait("personalia.Portrait");
});
