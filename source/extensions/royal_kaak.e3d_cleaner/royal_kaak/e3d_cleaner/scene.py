import omni.kit.actions
import omni.kit.actions.core
from pxr import Usd, Sdf, UsdGeom
import omni.usd
import omni.kit.app
import omni.kit.notification_manager as nm
import asyncio

from .utils import Utils


async def load_warehouse(stage: Usd.Stage, path: Sdf.Path):
    # wait some time for the loading message to show
    for _ in range(100):
        await omni.kit.app.get_app().next_update_async()

    Utils.add_sublayer(path, anonymous=True, layer_name="Warehouse")

    nm.post_notification(
        "Warehouse Loaded.",
        duration=5,
        status=nm.NotificationStatus.INFO,
    )


class Scene:
    def add_environment(warehouse_path: Sdf.Path):
        stage: Usd.Stage = omni.usd.get_context().get_stage()
        default_prim = UsdGeom.Xform.Define(stage, Sdf.Path("/World")).GetPrim()

        if stage:
            # remove the empty environmetn folder
            found_prims = [prim for prim in stage.Traverse() if "Environment" in prim.GetName()]
            for prim in found_prims:
                # Check if the selected prim is the top level object, not the default prim(world), and the correct type.
                path_length = str(prim).count("/")
                if path_length == 1 and prim != default_prim and prim.GetTypeName() == "Xform":
                    stage.RemovePrim(prim.GetPath())

            # enable stage lights to show sky
            action_registry = omni.kit.actions.core.get_action_registry()
            action: omni.kit.actions.core.Action = action_registry.get_action(
                "omni.kit.viewport.menubar.lighting",
                "set_lighting_mode_stage",
            )
            action.execute()

            # import sublayer
            asyncio.ensure_future(load_warehouse(stage, warehouse_path))

            # show notifaction to keep user informed
            nm.post_notification(
                "Loading scene...",
                duration=1,
                status=nm.NotificationStatus.INFO,
            )
