import omni.kit.window.filepicker as filepicker
import omni.usd
import omni.kit.commands as cmd
import omni.kit.viewport.utility
import omni.kit.notification_manager as nm
from pxr import Usd, UsdGeom, Sdf, Gf

from .utils import Utils

# model_layer: Sdf.Layer = None
conversion_scale = Gf.Vec3d(100, 100, 100)
search_list = [
    "Keyframe",
    "CycleController",
    "defaults",
    "Lens",
    "Light",
    "Default_View",
    "LoadDeleter",
    "LoadCreator",
    "Camcorder",
    "PeopleProgram",
    "pijl_transparant",
]


class Model:
    model_layer: Sdf.Layer = None

    def get_model_prim(stage: Usd.Stage) -> Usd.Prim:
        print("get_model_prim()")
        all_layers: list[Sdf.Layer] = stage.GetLayerStack()
        for layer in all_layers:
            if "Emulate3D" in str(layer):
                Model.model_layer = layer
                break

        if Model.model_layer:
            model_prim_path: str = "/" + Model.model_layer.defaultPrim
            if model_prim_path:
                model_prim = stage.GetPrimAtPath(model_prim_path)
                return model_prim
            else:
                nm.post_notification(
                    "No default prim in model found.",
                    duration=3,
                    status=nm.NotificationStatus.WARNING,
                )
        else:
            nm.post_notification(
                "Please import model first.",
                duration=3,
                status=nm.NotificationStatus.WARNING,
            )
        return None

    def fix_scale():
        print("fix_scale()")
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        if stage:
            e3d_model = Model.get_model_prim(stage)
            if e3d_model:
                # Get the base class of the prim to apply transform changes to.
                xformable = UsdGeom.Xformable(e3d_model)

                # Clear transforms
                xformable.SetXformOpOrder([])

                # Translate
                # xformable.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble).Set(translation)

                # Rotate
                # xformable.AddRotateXYZOp(UsdGeom.XformOp.PrecisionDouble).Set(rotation)

                # Scale
                xformable.AddScaleOp(UsdGeom.XformOp.PrecisionDouble).Set(conversion_scale)

                nm.post_notification(
                    "Scale fixed.",
                    duration=3,
                    status=nm.NotificationStatus.INFO,
                )
            else:
                print("fix_scale: no e3d_model found")
        else:
            print("fix_scale: no stage found")

    def hide_unwanted_objects():
        print("hide_unwanted_objects()")
        stage: Usd.Stage = omni.usd.get_context().get_stage()

        if stage:
            hidden_objects = []
            e3d_model = Model.get_model_prim(stage)
            if e3d_model:
                for item in search_list:
                    found_prims = [prim for prim in Usd.PrimRange(e3d_model) if item in prim.GetName()]
                    for prim in found_prims:
                        if prim.IsValid():
                            visibility_attr = prim.GetAttribute("visibility")
                            if not visibility_attr:
                                visibility_attr = prim.CreateAttribute("visibility", Sdf.ValueTypeNames.Token)
                            visibility_attr.Set("invisible")
                            hidden_objects.append(prim)
                # hide floor
                found_prims = [prim for prim in Usd.PrimRange(e3d_model) if "floor" in prim.GetName()]
                for prim in found_prims:
                    if prim.IsValid() and "defaults" in str(prim.GetPath()):
                        visibility_attr = prim.GetAttribute("visibility")
                        if not visibility_attr:
                            visibility_attr = prim.CreateAttribute("visibility", Sdf.ValueTypeNames.Token)
                        visibility_attr.Set("invisible")
                        hidden_objects.append(prim)

                nm.post_notification(
                    str(len(hidden_objects)) + " objects hidden.",
                    duration=3,
                    status=nm.NotificationStatus.INFO,
                )
            else:
                print("hide_unwanted_models: no e3d_model found")
        else:
            print("hide_unwanted_models: no stage found")

    def unhide_unwanted_objects():
        print("unhide_unwanted_objects()")
        stage: Usd.Stage = omni.usd.get_context().get_stage()

        if stage:
            hidden_objects = []
            e3d_model = Model.get_model_prim(stage)
            if e3d_model:
                for item in search_list:
                    found_prims = [prim for prim in Usd.PrimRange(e3d_model) if item in prim.GetName()]
                    for prim in found_prims:
                        if prim.IsValid():
                            visibility_attr = prim.GetAttribute("visibility")
                            if not visibility_attr:
                                visibility_attr = prim.CreateAttribute("visibility", Sdf.ValueTypeNames.Token)
                            visibility_attr.Set("inherited")
                            hidden_objects.append(prim)

                nm.post_notification(
                    str(len(hidden_objects)) + " objects unhidden.",
                    duration=3,
                    status=nm.NotificationStatus.INFO,
                )
            else:
                print("unhide_unwanted_models: no e3d_model found")
        else:
            print("unhide_unwanted_models: no stage found")

    def hide_sensor_beams():
        print("hide_sensor_beams()")
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        if stage:
            e3d_model = Model.get_model_prim(stage)
            found_prims = [
                prim
                for prim in Usd.PrimRange(e3d_model)
                if "beam" in prim.GetName() or "LASERLIGHT" in prim.GetName() or "CAMERAVIEW" in prim.GetName()
            ]
            for prim in found_prims:
                if prim.IsValid():
                    visibility_attr = prim.GetAttribute("visibility")
                    if not visibility_attr:
                        visibility_attr = prim.CreateAttribute("visibility", Sdf.ValueTypeNames.Token)
                    visibility_attr.Set("invisible")

    def show_sensor_beams():
        print("show_sensor_beams()")
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        if stage:
            e3d_model = Model.get_model_prim(stage)
            found_prims = [
                prim
                for prim in Usd.PrimRange(e3d_model)
                if "beam" in prim.GetName() or "LASERLIGHT" in prim.GetName() or "CAMERAVIEW" in prim.GetName()
            ]
            for prim in found_prims:
                if prim.IsValid():
                    visibility_attr = prim.GetAttribute("visibility")
                    if not visibility_attr:
                        visibility_attr = prim.CreateAttribute("visibility", Sdf.ValueTypeNames.Token)
                    visibility_attr.Set("inherited")

    def import_model(dialog: filepicker.FilePickerDialog):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        viewport = omni.kit.viewport.utility.get_active_viewport()

        Model.model_layer = Utils.add_sublayer(dialog.get_current_selections()[0], dialog)
        print(Model.model_layer)
        if Model.model_layer:
            # get top level prim from layer
            e3d_model: Usd.Prim = Model.get_model_prim(stage)
            if e3d_model:
                # do essential work to start with a usable model.
                Model.fix_scale()
                Model.hide_unwanted_objects()

                # frame camera around prim
                cmd.execute("SelectPrims", old_selected_paths=[], new_selected_paths=[str(e3d_model.GetPath())])
                omni.kit.viewport.utility.frame_viewport_selection()
                omni.usd.get_context().get_selection().clear_selected_prim_paths()

                nm.post_notification(
                    f"Model imported as {Model.model_layer.GetDisplayName()}",
                    duration=5,
                    status=nm.NotificationStatus.INFO,
                )
            else:
                nm.post_notification(
                    "Model not found.",
                    duration=3,
                    status=nm.NotificationStatus.WARNING,
                )
        else:
            nm.post_notification(
                "Failed to import model.",
                duration=3,
                status=nm.NotificationStatus.WARNING,
            )
