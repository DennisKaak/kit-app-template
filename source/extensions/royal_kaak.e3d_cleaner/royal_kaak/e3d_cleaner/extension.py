# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import omni.ext
import omni.usd
import omni.ui as ui
import omni.ui.scene
import omni.kit
import omni.kit.app
from omni.kit.menu.utils import MenuItemDescription
import omni.kit.window.filepicker
import omni.kit.viewport.utility
import omni.kit.actions.core
import omni.kit.stage_templates
import asyncio

from .utils import Utils
from .recording import Recording
from .model import Model
from .scene import Scene
from .looks import Looks

# path to environment
warehouse_path = (
    "//domain.kaak/kaak/Afdelingen/Engineering/Simulatiemodellen/_test/Omniverse/template_warehouse_small_01.usd"
)
rvs_material_path = "/World/Looks/RVS"
material_dict = {"rvs": "/World/Looks/RVS"}
conveyor_albedo_name = "t0.png"
camera_name = "E3D_Camera"
# Set the start and end time of the timeline in seconds
start_time = 1.0  # Set your desired start time here
end_time = 60.0  # Set your desired end time here


# Functions and vars are available to other extensions as usual in python: `royal_kaak.e3d_cleaner.some_public_function(x)`
# Function to check if the selected object in the top level E3D object.


def create_import_model_window():
    dialog = omni.kit.window.filepicker.FilePickerDialog(
        "Select USD File",
        apply_button_label="Import",
        file_extension_filter=["usd", "usda", "usdc", "usdz"],
        enable_filename_input=False,
    )
    dialog.set_click_apply_handler(lambda file_path, dir_path: Model.import_model(dialog))
    dialog.show()


def prepare_scene():
    Scene.add_environment(warehouse_path)
    Utils.setup_timeline(start_time, end_time)


def improve_model_looks():
    asyncio.ensure_future(Looks.auto_replace_materials())
    # TODO fix pivot location
    # TODO hide conveyor arrow meshes


def prepare_for_recording():
    Recording.add_camera(camera_name)

    # clear selection
    omni.usd.get_context().get_selection().clear_selected_prim_paths()


def undo_recording_prep():
    Recording.remove_camera(camera_name)


def replace_material_rvs():
    Looks.replace_selected_material_from_dict("custom_rvs")


def replace_material_rubber():
    Looks.replace_selected_material_from_dict("custom_rubber")


def replace_material_plastic_kaak_blauw():
    Looks.replace_selected_material_from_dict("custom_plastic_kaak_blauw")


def replace_material_plastic_geel():
    Looks.replace_selected_material_from_dict("custom_plastic_geel")


def replace_material_plastic_wit():
    Looks.replace_selected_material_from_dict("custom_plastic_wit")

def replace_material_plastic_licht_blauw():
    Looks.replace_selected_material_from_dict("custom_plastic_licht_blauw")

def replace_material_plastic_donker_blauw():
    Looks.replace_selected_material_from_dict("custom_plastic_donker_blauw")


def replace_material_plastic_groen():
    Looks.replace_selected_material_from_dict("custom_plastic_groen")


def replace_material_plastic_rood():
    Looks.replace_selected_material_from_dict("custom_plastic_rood")


def replace_material_plastic_bruin():
    Looks.replace_selected_material_from_dict("custom_plastic_bruin")


# Any class derived from `omni.ext.IExt` in the top level module (defined in `python.modules` of `extension.toml`) will
# be instantiated when the extension gets enabled, and `on_startup(ext_id)` will be called.
# Later when the extension gets disabled on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is the current extension id. It can be used with the extension manager to query additional information,
    # like where this extension is located on the filesystem.

    def create_wait_window(self, text: str):
        self._window = ui.Window(
            "Please Wait",
            width=300,
            height=100,
            noTabBar=True,
            auto_resieze=True,
        )
        with self._window.frame:
            ui.Label(text, alignment=ui.Alignment.CENTER)

    def on_startup(self, ext_id):
        print("[royal_kaak.e3d_cleaner] Extension startup")

        self._menu_list = [
            MenuItemDescription(
                name="1. Import Warehouse",
                onclick_fn=prepare_scene,
            ),
            MenuItemDescription(
                name="2. Import Model",
                onclick_fn=create_import_model_window,
            ),
            MenuItemDescription(
                name="3. Improve Model Looks",
                onclick_fn=improve_model_looks,
            ),
            MenuItemDescription(
                name="4. Prepare for Recording",
                onclick_fn=prepare_for_recording,
            ),
            # MenuItemDescription(
            #     name="Fix Transform",
            #     onclick_fn=Model.fix_scale,
            # ),
            MenuItemDescription(
                name="Visibility",
                sub_menu=[
                    MenuItemDescription(
                        name="Hide objects with same material",
                        onclick_fn=Looks.hide_objects_with_same_material,
                    ),
                    MenuItemDescription(
                        name="Hide Sensor Beams",
                        onclick_fn=Model.hide_sensor_beams,
                    ),
                    MenuItemDescription(
                        name="Show Sensor Beams",
                        onclick_fn=Model.show_sensor_beams,
                    ),
                    MenuItemDescription(
                        name="Hide Unwanted Objects",
                        onclick_fn=Model.hide_unwanted_objects,
                    ),
                    MenuItemDescription(
                        name="Show Unwanted Objects",
                        onclick_fn=Model.unhide_unwanted_objects,
                    ),
                ],
            ),
            MenuItemDescription(
                name="Replace Material with",
                sub_menu=[
                    MenuItemDescription(
                        name="RVS",
                        onclick_fn=(replace_material_rvs),
                    ),
                    MenuItemDescription(
                        name="Rubber",
                        onclick_fn=(replace_material_rubber),
                    ),
                    MenuItemDescription(
                        name="Plastic - Kaak Blauw",
                        onclick_fn=(replace_material_plastic_kaak_blauw),
                    ),
                    MenuItemDescription(
                        name="Plastic - Licht Blauw",
                        onclick_fn=(replace_material_plastic_licht_blauw),
                    ),
                    MenuItemDescription(
                        name="Plastic - Donker Blauw",
                        onclick_fn=(replace_material_plastic_donker_blauw),
                    ),
                    MenuItemDescription(
                        name="Plastic - Geel",
                        onclick_fn=(replace_material_plastic_geel),
                    ),
                    MenuItemDescription(
                        name="Plastic - Rood",
                        onclick_fn=(replace_material_plastic_rood),
                    ),
                    MenuItemDescription(
                        name="Plastic - Groen",
                        onclick_fn=(replace_material_plastic_groen),
                    ),
                    MenuItemDescription(
                        name="Plastic - Bruin",
                        onclick_fn=(replace_material_plastic_bruin),
                    ),
                    MenuItemDescription(
                        name="Plastic - Wit",
                        onclick_fn=(replace_material_plastic_wit),
                    ),
                ],
            ),
            MenuItemDescription(
                name="Recording",
                sub_menu=[
                    MenuItemDescription(
                        name="Remove Recording Camera",
                        onclick_fn=undo_recording_prep,
                    ),
                ],
            ),
        ]

        omni.kit.menu.utils.add_menu_items(self._menu_list, "Emulate3D")

    def on_shutdown(self):
        print("[royal_kaak.e3d_cleaner] Extension shutdown")
        omni.kit.menu.utils.remove_menu_items(self._menu_list, "Emulate3D")
