export function editable_check_progress(bar: HTMLSpanElement | HTMLDivElement, save: (data: number) => void) {
    let current_value = Number.parseInt(bar.getAttribute('data-value'));
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
        box.onclick = (ev: Event) => {
            let value = Number.parseInt(box.getAttribute('data-value'));
            if (value == current_value) {
                value = current_value - 1;
            }
            save(value);
            current_value = value;
            set_count(value);
        }
        box.onmouseenter = () => {
            const value = Number.parseInt(box.getAttribute('data-value'));
            set_count(value);
        }
        box.onmouseout = () => {
            set_count(current_value);
        }
    })
}
