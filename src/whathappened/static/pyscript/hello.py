import sys
from typing import cast

from pyscript import display, window, document

console = window.console


def init_set_portrait(field_name: str):
    console.log("Init set portrait")
    portraitbox = document.getElementsByClassName("portrait")[0]
    console.log(portraitbox)
    if "editable" in portraitbox.classList:
        console.log("Editable portrait")
        uploadelement = cast(document.HTMLInputElement, document.createElement("input"))
        uploadelement.type = "file"
        uploadelement.style.display = "none"

        def on_change_cb(e):
            console.log("Changed")

            reader = window.FileReader.new()

            def onload_cb(e):
                console.log(field_name)
                """
                send_update(
                    { field: field_name, type: "portrait" },
                    reader.result
                );
                """

            reader.readAsDataURL(uploadelement.files[0])
            reader.onload = onload_cb

        uploadelement.onchange = on_change_cb

        def on_click_cb(e):
            uploadelement.click()

        portraitbox.appendChild(uploadelement)
        portraitbox.onclick = on_click_cb


display(sys.version)
display(window.location.hostname)

console.log("Hello")
init_set_portrait("personalia.Portrait")
