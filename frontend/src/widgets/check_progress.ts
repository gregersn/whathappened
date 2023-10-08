export function editable_check_progress(bar: HTMLSpanElement | HTMLDivElement, save: (data: number) => void) {
    let current_value = Number.parseInt(bar.getAttribute('data-value'));
    console.log(current_value);
    const checkboxes: HTMLInputElement[] = Array.from(bar.getElementsByTagName('input'));
    const count_check_marks = () => {
        let value: number = 0;
        checkboxes.forEach(box => {
            if (box.checked) {
                value += 1;
            }
        })
        return value;
    }

    const set_count = (value: number) => {
        for (let i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = i < value;
        }
    }

    checkboxes.forEach(box => {
        /*box.onchange = (ev: Event) => {
            ev.preventDefault();
        }*/
        box.onclick = (ev: Event) => {
            //ev.preventDefault();
            //const value = count_check_marks();
            let value = Number.parseInt(box.getAttribute('data-value'));
            console.log(value, current_value);
            if (value == current_value) {
                value = current_value - 1;
            }
            save(value);
            current_value = value;
            set_count(value);
        }
        box.onmouseenter = () => {
            console.log("Mouse enter");
            const value = Number.parseInt(box.getAttribute('data-value'));
            set_count(value);
        }
        box.onmouseout = () => {
            console.log("Mouse leave");
            set_count(current_value);
        }
    })
}
