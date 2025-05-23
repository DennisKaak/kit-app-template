from anyio import Path
import omni.ui as ui
import omni.usd
from pxr import Usd, UsdShade, Sdf
import asyncio
import omni.kit.notification_manager as nm

from .utils import Utils
from .model import Model

rvs_material_path = "/World/Looks/RVS"
material_dict = {
    "frameplaat": "/World/Looks/RVS",
    "flenslager": "/World/Looks/Plastic_Kaak_Blauw",
    "H1141": "/World/Looks/Plastic_Geel",
    "custom_rvs": "/World/Looks/RVS",
    "custom_rubber": "/World/Looks/Rubber",
    "custom_plastic_wit": "/World/Looks/Plastic_Wit",
    "custom_plastic_donker_blauw": "/World/Looks/Plastic_Licht_Blauw",
    "custom_plastic_donker_blauw": "/World/Looks/Plastic_Donker_Blauw",
    "custom_plastic_bruin": "/World/Looks/Plastic_Bruin",
    "custom_plastic_rood": "/World/Looks/Plastic_Rood",
    "custom_plastic_groen": "/World/Looks/Plastic_Groen",
    "custom_plastic_geel": "/World/Looks/Plastic_Geel",
    "custom_plastic_kaak_blauw": "/World/Looks/Plastic_Kaak_Blauw",
}


async def wait_for_next_frame(frames=1):
    wait_time = frames / Utils.get_fps()
    await asyncio.sleep(wait_time)  # Yield control back to the event loop


async def async_assign_material_to_objects(
    stage: Usd.Stage,
    object_paths: list[Sdf.Path],
    material_path: Sdf.Path,
):
    material_prim = stage.GetPrimAtPath(material_path)
    Looks.create_progress_window(f"Changing materials of {len(object_paths)} objects to {material_prim.GetName()}")
    progress_part: float = 1.0 / float(len(object_paths))
    current_value = 0.0
    await wait_for_next_frame(1)
    for obj in object_paths:
        # Get the prims for the object and the material
        object_prim = stage.GetPrimAtPath(obj)
        material_prim = stage.GetPrimAtPath(material_path)

        # Ensure both prims exist
        if not object_prim or not material_prim:
            print("Invalid object or material path.")
            return

        # Create a MaterialBindingAPI for the object
        material_binding_api: UsdShade.MaterialBindingAPI = UsdShade.MaterialBindingAPI.Apply(object_prim)

        # Bind the material to the object
        material_binding_api.Bind(UsdShade.Material(material_prim))

        # print(f"Material {material_path} assigned to object {obj}.")
        # await wait_for_next_frame(1)
        current_value = current_value + progress_part
        if current_value > 1.0:
            current_value = 1.0
        # print(current_value)
        Looks.update_progress_bar(current_value)
        await wait_for_next_frame(1)
    Utils.close_window(Looks.progress_window)


def find_objects_bound_to_material(stage: Usd.Stage, material_path: Sdf.Path) -> list[Usd.Prim]:
    bound_prims = []
    for prim in stage.Traverse():
        direct_binding = UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterial()
        if direct_binding and direct_binding.GetPath() == material_path:
            bound_prims.append(prim.GetPath())
    return bound_prims


class Looks:
    progress_window: ui.Window = None
    progress_bar: ui.ProgressBar = None

    def create_progress_window(title: str):
        Looks.progress_window = ui.Window(title, width=400, height=100, noTabBar=False)
        with Looks.progress_window.frame:
            with ui.VStack():
                Looks.progress_bar = ui.ProgressBar()
                Looks.progress_bar.style = {
                    "background-color": "lightgray",  # Background color of the progress bar
                    "color": "blue",  # Color of the progress indicator
                }
                Looks.progress_bar.model.set_value(0.0)

    def update_progress_bar(new_value: float):
        Looks.progress_bar.model.set_value(new_value)

    def replace_selected_material_from_dict(dict_key: str):
        def on_ok(window, material_path):
            print("OK button clicked")
            Utils.close_window(window)
            Looks.replace_material(material_path)

        def on_cancel(window):
            print("Cancel button clicked")
            Utils.close_window(window)

        # Create the popup dialog
        replace_material_window = ui.Window("Are you sure?", width=300, height=130)
        with replace_material_window.frame:
            with ui.VStack():
                ui.Label(
                    "Warning: Cannot be undone.",
                    spacing=ui.Alignment.CENTER,
                    word_wrap=True,
                )
                with ui.HStack(spacing=40):
                    ui.Button(
                        "OK",
                        clicked_fn=lambda: on_ok(replace_material_window, material_dict.get(dict_key)),
                        width=120,
                        height=40,
                    )
                    ui.Button(
                        "Cancel",
                        clicked_fn=lambda: on_cancel(replace_material_window),
                        width=120,
                        height=40,
                    )

    def replace_material(new_material_path: Sdf.Path, auto_search=False):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        ctx = omni.usd.get_context()
        material_path = ""

        if auto_search:
            e3d_model = Model.get_model_prim(stage)
            if e3d_model:
                found_prims = [prim for prim in Usd.PrimRange(e3d_model) if "rvs" in prim.GetName()]
                deepest_prim = Utils.get_deepest_child(found_prims[0])
                binding_api = UsdShade.MaterialBindingAPI(deepest_prim)
                material_path = binding_api.GetDirectBinding().GetMaterial().GetPath()
            else:
                print("replace_material: e3d_model not found")
        else:
            # returns a list of prim path strings
            selection = ctx.get_selection().get_selected_prim_paths()

            if len(selection) == 1:  # is 1 object selected
                prim = stage.GetPrimAtPath(selection[0])
                deepest_prim = Utils.get_deepest_child(prim)
                binding_api = UsdShade.MaterialBindingAPI(deepest_prim)
                material_path = binding_api.GetDirectBinding().GetMaterial().GetPath()
            else:
                print("Please select 1 mesh of the model.")

        if material_path:
            bound_objects = find_objects_bound_to_material(stage, material_path)
            if bound_objects:
                print(f"Objects bound to the material: {len(bound_objects)}")
                if new_material_path:
                    asyncio.ensure_future(async_assign_material_to_objects(stage, bound_objects, new_material_path))
                else:
                    print(f"New material path not valid. {new_material_path}")
            else:
                print("No objects bound to the material.")
        else:
            print("No material found.")

    async def replace_material_by_name(name: str, new_material_path: Sdf.Path):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        ctx = omni.usd.get_context()
        material_path = ""
        selected_prims: list[Usd.Prim] = []

        if new_material_path:
            e3d_model = Model.get_model_prim(stage)
            if e3d_model:
                found_prims = [prim for prim in Usd.PrimRange(e3d_model) if name in prim.GetName()]
                # # This method finds the material of the first object found with the name.
                # # Then gets all object bound to that material and replaces their material with the new material.
                for prim in found_prims:
                    deepest_prim = Utils.get_deepest_child(prim)
                    if deepest_prim:
                        binding_api = UsdShade.MaterialBindingAPI(deepest_prim)
                        material_path = binding_api.GetDirectBinding().GetMaterial().GetPath()
                        if material_path and material_path != new_material_path:
                            bound_objects = find_objects_bound_to_material(stage, material_path)
                            if bound_objects:
                                for obj in bound_objects:
                                    if not obj in selected_prims:
                                        selected_prims.append(obj)
                                print(f"Current objects found with method 1: {len(selected_prims)}")
                                break
                            else:
                                print("No objects bound to the material.")
                        else:
                            print("No material found.")

                # This method find all objects that contain the name and replaces their material.
                for prim in found_prims:
                    deepest_prim = Utils.get_deepest_child(prim)
                    current_material = (
                        UsdShade.MaterialBindingAPI(deepest_prim).GetDirectBinding().GetMaterial().GetPath()
                    )
                    if deepest_prim and current_material != new_material_path:
                        selected_prims.append(deepest_prim.GetPath())
                print(f"Total objects found: {len(selected_prims)}")
                if selected_prims:
                    await async_assign_material_to_objects(stage, selected_prims, new_material_path)

                nm.post_notification(
                    f"Completed {stage.GetPrimAtPath(new_material_path).GetName()} material assignment.",
                    duration=3,
                    status=nm.NotificationStatus.INFO,
                )
            else:
                print("replace_material: e3d_model not found")
        else:
            print("New material path not valid.")

    async def auto_replace_materials():
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        for key, value in material_dict.items():
            material = stage.GetPrimAtPath(value)
            if material and "custom" not in key:
                await Looks.replace_material_by_name(key, value)
            else:
                print(f"No material found at {value}")

    def hide_objects_with_same_material():
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        ctx = omni.usd.get_context()
        selection = ctx.get_selection().get_selected_prim_paths()

        for prim_path in selection:
            prim = stage.GetPrimAtPath(prim_path)
            deepest_prim = Utils.get_deepest_child(prim)
            binding_api = UsdShade.MaterialBindingAPI(deepest_prim)
            material_path = binding_api.GetDirectBinding().GetMaterial().GetPath()
            if material_path:
                bound_objects = find_objects_bound_to_material(stage, material_path)
                for obj in bound_objects:
                    mesh = stage.GetPrimAtPath(obj).GetParent()
                    visibility_attr = mesh.GetAttribute("visibility")
                    if not visibility_attr:
                        visibility_attr = mesh.CreateAttribute("visibility", Sdf.ValueTypeNames.Token)
                    visibility_attr.Set("invisible")

        omni.usd.get_context().get_selection().clear_selected_prim_paths()
