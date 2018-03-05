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
import os

from bpy.props import (
    BoolProperty
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


class ImportGMDC(bpy.types.Operator):
    """Load a Sims 2 GMDC File"""
    bl_idname = "import_scene.gmdc"
    bl_label = "Import GMDC"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".gmdc"


