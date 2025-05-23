from pxr import Usd, Sdf, UsdGeom
import omni.usd
import omni.kit.viewport.utility
import omni.kit.notification_manager as nm


class Recording:
    def add_camera(camera_name: str):
        Recording.remove_camera(camera_name)
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        if stage:
            found_camcorders = [prim for prim in stage.Traverse() if "Camcorder_node" in prim.GetName()]
            if found_camcorders:
                camcorder_path = found_camcorders[0].GetPath()
                camera_path = Sdf.Path(str(camcorder_path) + "/" + camera_name)
                usd_camera: UsdGeom.Camera = UsdGeom.Camera.Define(stage, camera_path)
                usd_camera.CreateProjectionAttr().Set(UsdGeom.Tokens.perspective)

                # set some other common attributes on the camera
                usd_camera.CreateFocalLengthAttr().Set(15)
                usd_camera.CreateFocusDistanceAttr().Set(400)
                usd_camera.CreateHorizontalApertureAttr().Set(20.955)
                usd_camera.CreateVerticalApertureAttr().Set(15.2908)
                usd_camera.CreateClippingRangeAttr().Set((0.1, 100000))

                # Get the active viewport
                viewport = omni.kit.viewport.utility.get_active_viewport()
                if not viewport:
                    raise RuntimeError("No active Viewport")

                # Set the Viewport's active camera to the new camera path
                viewport.camera_path = camera_path

                nm.post_notification(
                    "New camera active.",
                    duration=5,
                    status=nm.NotificationStatus.INFO,
                )
            else:
                nm.post_notification(
                    "No camcorder found.",
                    duration=5,
                    status=nm.NotificationStatus.WARNING,
                )

    def remove_camera(camera_name: str):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        if stage:
            found_cameras = [prim for prim in stage.Traverse() if camera_name in prim.GetName()]
            if found_cameras:
                stage.RemovePrim(found_cameras[0].GetPath())
                nm.post_notification(
                    "Recording camera removed.",
                    duration=5,
                    status=nm.NotificationStatus.INFO,
                )
            return

    def flatten_layers():
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        if stage:
            stage.FlattenLayers()
            nm.post_notification(
                "Flattened layers.",
                duration=5,
                status=nm.NotificationStatus.INFO,
            )
        else:
            nm.post_notification(
                "No stage found.",
                duration=5,
                status=nm.NotificationStatus.WARNING,
            )
