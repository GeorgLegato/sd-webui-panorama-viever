from modules import script_callbacks, scripts, shared
import os
import html
import gradio as gr
import base64
import io
from PIL import Image

usefulDirs = scripts.basedir().split(os.sep)[-2:]
iframesrc = "file="+usefulDirs[0]+"/"+usefulDirs[1]+"/scripts/viewer.html"

# js 2 gradio messaging?! how to do better?
gallery_input_ondrop=None
txt2img_gallery_component=None

def data_url_to_image(data_url):
    comma_position = data_url.find(',')
    base64_data = data_url[comma_position + 1:]
    image_data = base64.b64decode(base64_data)
    image_stream = io.BytesIO(image_data)
    image = Image.open(image_stream)
    return image


def onPanModeChange(m):
     print ("mode changed to"+str(m))


def add_tab():
    with gr.Blocks(analytics_enabled=False) as ui:
        with gr.Column():
            selectedPanMode = gr.Dropdown(choices=["Equirectangular", "Cubemap: Polyhedron net"],value="Equirectangular",label="Select projection mode", elem_id="panoviewer_mode")
            gr.HTML(value=f"<iframe id=\"panoviewer-iframe\" class=\"border-2 border-gray-200\" src=\"{iframesrc}\" title='description'></iframe>")

            selectedPanMode.change(fn=onPanModeChange, inputs=[selectedPanMode],outputs=[], _js="panorama_change_mode(\""+selectedPanMode.value+"\")")
    # unless we have functionality in this tab. Gallery-Viewer should be sufficient if not easier.
#    return [(ui, "Panorama Viewer", "panorama-3dviewer")]
    return []


def dropHandleGallery(x):
    if (None != txt2img_gallery_component):
        list = txt2img_gallery_component.value
        img = data_url_to_image(x)
        list.append(img)
        return list


def after_component(component, **kwargs):
    global gallery_input_ondrop
    global txt2img_gallery_component
    
    # Add our buttons after each "send to extras" button
    if kwargs.get("elem_id") == "extras_tab":

#            with gr.Row(elem_id="pano_sendbox",variant="compact", css="justify-content: center; align-content: flex-end;"):

            # DISABLED until we get some functionality here, two button for Equi and Cubemap is currently enough
            #send2tab_button   = gr.Button ("Pano \U0001F440", elem_id=f"sendto_panorama_button")          # 👀
            #send2tab_button.click(None, [], None, _js="() => panorama_send_gallery('WebUI Resource')")
            #send2tab_button.__setattr__("class","gr-button")
            suffix = component.parent.elem_id

            if (suffix):
                print ("Panorama_Viewer: adding sendto button in parent_elem_id: "+suffix)
                view_gallery_button = gr.Button ("Pano \U0001F310", elem_id="sendto_panogallery_button_"+suffix)        # 🌐
                view_cube_button    = gr.Button ("Pano \U0001F9CA", elem_id="sendto_panogallery_cube_button_"+ suffix)   # 🧊
                gallery_input_ondrop = gr.Textbox(visible=False, elem_classes="gallery_input_ondrop", elem_id="gallery_input_ondrop_"+ suffix)
                gallery_input_ondrop.style(container=False)
                
                view_gallery_button.click (None, [],None, _js="panorama_here(\""+iframesrc+"\",\"\",\""+view_gallery_button.elem_id+"\")" )
                view_cube_button.click    (None, [],None, _js="panorama_here(\""+iframesrc+"\",\"cubemap\",\""+view_cube_button.elem_id+"\")" )

            if (gallery_input_ondrop and txt2img_gallery_component):
                gallery_input_ondrop.change(fn=dropHandleGallery, inputs=[gallery_input_ondrop], outputs=[txt2img_gallery_component]) 


    if kwargs.get("elem_id") == "txt2img_gallery":
        print ("Panorama Viewer: enable file-drag-and-drop into txt2img gallery...")

        txt2img_gallery_component = component

        if (gallery_input_ondrop and txt2img_gallery_component):
            gallery_input_ondrop.change(fn=dropHandleGallery, inputs=[gallery_input_ondrop], outputs=[txt2img_gallery_component]) 
    

script_callbacks.on_ui_tabs(add_tab)
script_callbacks.on_after_component(after_component)
