/**
 * @jest-environment jsdom
 */

import { list_to_obj } from "../src/common";

test('list_to_obj', () => {
    const list = document.createElement('ul');
    list.innerHTML = '<li>A</li><li>B</li>';

    const obj = list_to_obj(list);
    expect(obj.length).toEqual(2);
    expect(obj).toEqual(['A', 'B']);
});
