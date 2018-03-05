# -------------------------------------------------------------------------------
# Copyright (C) 2018  actioninja
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -------------------------------------------------------------------------------


import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
)
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        )

bl_info = {
    "name": "Sims 2 GMDC Tools",
    "author": "djalex88 (actioninja for blender 2.5+ port)",
    "version": (1, 0, 0),
    "blender": (2, 79),
    "category": "Import-Export",
    "location": "File > Import/Export > Sims 2 GMDC (*.gmdc)",
    "description": "Importer and Exporter for Sims 2 format GMDC files."
}


class ImportGMDC(bpy.types.Operator, ImportHelper):
    """Load a Sims 2 GMDC File"""
    bl_idname = "import_scene.gmdc"
    bl_label = "Import GMDC"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".gmdc"
    filter_glob = StringProperty(
        default="*.gmdc",
        options={'HIDDEN'},
    )

    import_bmesh = BoolProperty(
        name="Import BMesh",
        description="Import bounding geometry",
        default=True,
    )
    remove_doubles = BoolProperty(
        name="Remove Doubles",
        description="Remove double verticies when importing mesh (can remove seams)",
        default=False,
    )
    import_all_bones = BoolProperty(
        name="Import All Bones",
        description="Import all bones/transforms; otherwise, used bones only",
        default=False,
    )

    def execute(self, context):
        from . import import_gmdc

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "import_bmesh")
        row.prop(self, "remove_doubles")
        row.prop(self, "import_all_bones")


class ExportGMDC(bpy.types.Operator, ExportHelper):
    """Save a Sims 2 GMDC File"""
    bl_idname = "export_scene.gmdc"
    bl_label = "Export GMDC"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".gmdc"
    filter_glob = StringProperty(
        default="*.gmdc",
        options={'HIDDEN'},
    )


def menu_func_import(self, context):
    self.layout.operator(ImportGMDC.bl_idname, text="Sims 2 GMDC (.gmdc)")


def menu_func_export(self, context):
    self.layout.operator(ExportGMDC.bl_idname, text="Sims 2 GMDC (.gmdc)")


classes = (
    ImportGMDC,
    ExportGMDC
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def register():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
