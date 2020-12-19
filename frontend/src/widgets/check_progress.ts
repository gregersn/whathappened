export function editable_check_progress(bar: HTMLSpanElement | HTMLDivElement, save: (data: number) => void) {
    const count_check_marks = (bar: HTMLSpanElement | HTMLDivElement, save: (data: number) => void) => {
        const checkboxes: HTMLInputElement[] = Array.from(bar.getElementsByTagName('input'));
        let value: number = 0;
        checkboxes.forEach(box => {
            if(box.checked) {
                value += 1;
            }
        })
        save(value);
    }

   const checkboxes: HTMLInputElement[] = Array.from(bar.getElementsByTagName('input'));
   checkboxes.forEach(box => {
       box.onchange = () => count_check_marks(bar, save);
   })
}
