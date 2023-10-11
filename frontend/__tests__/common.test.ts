/**
 * @jest-environment jsdom
 */

import {
    ExportedForTesting,
    init_set_portrait,
    show_message,
    make_element_editable,
} from "../src/common";
const { saveElement, editElement } = ExportedForTesting;

afterEach(() => {
    // restore the spy created with spyOn
    jest.restoreAllMocks();
});

test("saveElement", () => {
    const input_element = document.createElement("input");
    input_element.value = "TestValue";

    const status_element = document.createElement("p");

    let status = "unsaved";

    saveElement(
        input_element,
        status_element,
        (data, value) => {
            status = value;
        },
        () => {}
    );

    expect(status).toEqual("TestValue");
    expect(status_element.innerHTML).toEqual("TestValue");
});

test("saveElement with number", () => {
    const input_element = document.createElement("input");
    input_element.type = "number";
    input_element.value = "2";

    const status_element = document.createElement("p");

    let status = "unsaved";

    saveElement(
        input_element,
        status_element,
        (data, value) => {
            status = value;
        },
        () => {}
    );

    expect(status).toEqual(2);
    expect(status_element.innerHTML).toEqual("2");
});

test("init_set_portrait", () => {
    const portrait_container = document.createElement("div");
    portrait_container.classList.add("portrait");
    portrait_container.classList.add("editable");
    document.body.appendChild(portrait_container);

    expect(portrait_container.children.length).toBe(0);
    init_set_portrait("test_field");
    expect(portrait_container.children.length).toBe(1);
});

test("show_message", () => {
    const message_box = document.createElement("div");
    message_box.id = "messagebox";
    document.body.appendChild(message_box);
    show_message("test message");

    expect(message_box.innerHTML).toBe("test message");
});

test("make_element_editable", () => {
    const editable_element = document.createElement("span");
    let value = "unedited";
    make_element_editable(editable_element, (a, b) => {});

    editable_element.click();
});

test("editElement", () => {
    const editable_element = document.createElement("span");
    editable_element.innerHTML = "test_value";
    let saved_value = "unsaved";
    editElement(
        editable_element,
        "string",
        (map, data) => {
            console.log(data);
            saved_value = data;
        },
        (event) => {
            console.log(event);
        }
    );

    const input_element = editable_element.children.item(0) as HTMLInputElement;
    const spy = jest.spyOn(input_element, "blur");

    expect(input_element.type).toBe("text");
    expect(input_element.value).toBe("test_value");
    input_element.blur();
    expect(spy).toHaveBeenCalled();
});
