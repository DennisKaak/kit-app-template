from pxr import Usd, Sdf
import omni.timeline
import omni.ui as ui
import omni.kit.window.filepicker as filepicker
from omni.kit.usd.layers import LayerUtils
import asyncio


async def async_close_window(window: ui.Window):
    await asyncio.sleep(0)
    window.visible = False
    window.destroy()


class Utils:
    def get_deepest_child(prim: Usd.Prim) -> Usd.Prim:
        children = prim.GetChildren()
        if not children:
            return prim
        deepest_child = None
        max_depth = -1
        for child in children:
            current_child = Utils.get_deepest_child(child)
            current_depth = len(current_child.GetPath().GetPrefixes())
            if current_depth > max_depth:
                deepest_child = current_child
                max_depth = current_depth
        return deepest_child

    def setup_timeline(start: float, end: float):
        # set the timeline to useable values
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_start_time(start)
        timeline.set_end_time(end)

    def get_fps() -> float:
        timeline = omni.timeline.get_timeline_interface()
        fps = timeline.get_time_codes_per_seconds()
        return fps

    def close_window(window: ui.Window):
        asyncio.ensure_future(async_close_window(window))

    def add_sublayer(
        file_path: Sdf.Path,
        picker: filepicker.FilePickerDialog = None,
        anonymous=False,
        layer_name="",
    ) -> Sdf.Layer:
        if file_path:
            stage = omni.usd.get_context().get_stage()
            root_layer = stage.GetRootLayer()
            try:
                if anonymous:
                    sublayer: Sdf.Layer = Sdf.Layer.OpenAsAnonymous(file_path)
                else:
                    sublayer: Sdf.Layer = Sdf.Layer.FindOrOpen(file_path)

                if sublayer:
                    root_layer.subLayerPaths.append(sublayer.identifier)
                    if layer_name:
                        LayerUtils.set_custom_layer_name(sublayer, layer_name)
                    if picker:
                        picker.hide()
                    return sublayer
                else:
                    print(f"Failed to open layer: {file_path}")
            except Exception as e:
                print(f"Error opening layer: {e}")
                print(f"Failed to open layer: {file_path}")
        else:
            print("File path incorrect.")

        if picker:
            picker.hide()

        return None
