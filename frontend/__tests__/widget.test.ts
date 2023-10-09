/**
 * @jest-environment jsdom
 */

import { editable_check_progress } from "../src/widgets/check_progress";

afterEach(() => {
    jest.restoreAllMocks();
});

test("editable_check_progress", () => {
    let count = 0;
    const callback = jest.fn((value) => {
        count = value;
    });
    const progress_element = document.createElement("span");
    let checkboxes: HTMLInputElement[] = [];
    for (let i = 0; i < 5; i++) {
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.setAttribute("data-value", (i + 1).toString());
        checkboxes.push(checkbox);
        progress_element.appendChild(checkbox);
    }
    document.body.appendChild(progress_element);
    editable_check_progress(progress_element, callback);

    checkboxes[0].click();
    expect(callback).toHaveBeenCalled();
    expect(count).toBe(1);

    checkboxes[2].click();
    expect(callback).toHaveBeenCalled();
    expect(count).toBe(3);

    checkboxes[0].click();
    expect(callback).toHaveBeenCalled();
    expect(count).toBe(1);
});
