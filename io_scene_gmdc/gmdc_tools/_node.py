# -------------------------------------------------------------------------------
# Copyright (C) 2016  DjAlex88 (https://github.com/djalex88/)
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

from struct import pack, unpack
from ._common import *


########################################
#  Base node class
########################################

class _SGNode(object):
    # General properties:
    # - index
    # - type
    # - version
    # cResourceNode:
    # - Res_unknown1 (1 byte)
    # - Res_unknown2 (5 bytes)
    # cSGResource:
    # - sg_resource_name
    # cCompositionTreeNode:
    # - child_nodes
    # cObjectGraphNode:
    # - extensions
    # - obj_string
    # cRenderableNode:
    # - R_number (BBl)
    # - R_strings
    # - R_unknown (5 bytes)
    # cTransformNode:
    # - T_loc
    # - T_rot
    # - T_bone_index
    # cDataListExtension:
    # - Ext_data
    # cShapeRefNode:
    # - SR_data1
    # - SR_unknown1 (4 bytes)
    # - SR_data2
    # - SR_strings (version 0x15)
    # - SR_unknown2
    # - SR_unknown3 (4 bytes)
    # cLightRefNode:
    # - L_index (BBl)
    # - L_unknown (2 bytes)
    # cBoneDataExtension:
    # - B_ext_unknown (12 bytes)
    # - B_ext_float
    # - B_ext_quat
    # cViewerRefNode:
    # - V_data
    # cViewerRefNodeRecursive:
    # - VR_unknown (1 bytes)
    # - VR_string
    # - VR_data (64 bytes)
    # cGeometryNode:
    # - G_unknown (7 bytes)
    # cGeometryDataContainer
    # - geometry
    #

    def __init__(self, index):
        self.index = index
        self.type = None

    def __str__(self):
        return 'unknown'

    def __repr__(self):
        return self.__str__()

    def _read_check_version(self, f, supported):
        self.version = unpack('<l', f.read(4))[0]
        try:
            assert self.version == supported or self.version in supported
            b = True
        except:
            error('Error! %s version %i is not supported.' % (self.type, self.version))
            b = False
        return b

    def _write_version(self, f):
        f.write(pack('<l', self.version))

    # _read_-methods

    def _read_csgresource(self, f):
        s = f.read(20)
        if s != b'\x0bcSGResource\x00\x00\x00\x00\x02\x00\x00\x00':
            error('Error! cSGResource header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        self.sg_resource_name = read_str(f)
        return True

    def _read_ccompositiontreenode(self, f):
        s = f.read(29)
        if s != b'\x14cCompositionTreeNode\x00\x00\x00\x00\x0b\x00\x00\x00':
            error('Error! cCompositionTreeNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_cobjectgraphnode(f):
            return False
        i = unpack('<l', f.read(4))[0]
        s = f.read(i * 6)
        v = unpack('<' + 'BBl' * (len(s) // 6), s)
        self.child_nodes = chunk(v, 3)
        return True

    def _read_cobjectgraphnode(self, f):
        s = f.read(25)
        if s != b'\x10cObjectGraphNode\x00\x00\x00\x00\x04\x00\x00\x00':
            error('Error! cObjectGraphNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        i = unpack('<l', f.read(4))[0]
        s = f.read(i * 6)
        v = unpack('<' + 'BBl' * (len(s) // 6), s)
        self.extensions = chunk(v, 3)
        self.obj_string = read_str(f)
        return True

    def _read_crenderablenode(self, f):
        s = f.read(24)
        if s != b'\x0fcRenderableNode\x00\x00\x00\x00\x05\x00\x00\x00':
            error('Error! cRenderableNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_cboundednode(f):
            return False
        self.R_number = unpack('<BBl', f.read(6))
        j = self.R_number[2]
        v = []
        while j:
            v.append(read_str(f))  # such as 'Practical', 'Sims', etc.
            j -= 1
        self.R_strings = v
        self.R_unknown = f.read(5)
        return True

    def _read_cboundednode(self, f):
        s = f.read(21)
        if s != b'\x0ccBoundedNode\x00\x00\x00\x00\x05\x00\x00\x00':
            error('Error! cBoundedNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        return self._read_ctransformnode(f)

    def _read_ctransformnode(self, f):
        s = f.read(23)
        if s != b'\x0ecTransformNode\x62\x64\x24\x65\x07\x00\x00\x00':
            error('Error! cTransformNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_ccompositiontreenode(f):
            return False
        self.T_loc = unpack('<3f', f.read(12))
        self.T_rot = unpack('<4f', f.read(16))
        i = unpack('<l', f.read(4))[0]
        self.T_bone_index = i if i != 0x7fffffff else None
        return True

    def _read_cextension_h(self, f):
        s = f.read(19)
        if s != b'\x0acExtension\x00\x00\x00\x00\x03\x00\x00\x00':
            error('Error! cExtension header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        return True

    # write methods

    def _write_csgresource(self, f):
        f.write(b'\x0bcSGResource\x00\x00\x00\x00\x02\x00\x00\x00')
        write_str(f, self.sg_resource_name)

    def _write_ccompositiontreenode(self, f):
        f.write(b'\x14cCompositionTreeNode\x00\x00\x00\x00\x0b\x00\x00\x00')
        self._write_cobjectgraphnode(f)
        f.write(pack('<l', len(self.child_nodes)))
        for t in self.child_nodes:
            f.write(pack('<BBl', *t))

    def _write_cobjectgraphnode(self, f):
        f.write(b'\x10cObjectGraphNode\x00\x00\x00\x00\x04\x00\x00\x00')
        f.write(pack('<l', len(self.extensions)))
        for t in self.extensions:
            f.write(pack('<BBl', *t))
        write_str(f, self.obj_string)

    def _write_crenderablenode(self, f):
        f.write(b'\x0fcRenderableNode\x00\x00\x00\x00\x05\x00\x00\x00')
        self._write_cboundednode(f)
        f.write(pack('<BBl', *self.R_number))
        assert self.R_number[2] == len(self.R_strings)
        for s in self.R_strings:
            write_str(f, s)
        f.write(self.R_unknown)

    def _write_cboundednode(self, f):
        f.write(b'\x0ccBoundedNode\x00\x00\x00\x00\x05\x00\x00\x00')
        self._write_ctransformnode(f)

    def _write_ctransformnode(self, f):
        f.write(b'\x0ecTransformNode\x62\x64\x24\x65\x07\x00\x00\x00')
        self._write_ccompositiontreenode(f)
        f.write(pack('<3f', *self.T_loc) + pack('<4f', *self.T_rot))
        f.write(b'\xff\xff\xff\x7f' if self.T_bone_index is None else pack('<l', self.T_bone_index))

    def _write_cextension_h(self, f):
        f.write(b'\x0acExtension\x00\x00\x00\x00\x03\x00\x00\x00')

    # _str_-methods

    def _str_csgresource(self):
        return '--SGResource: "%s"' % self.sg_resource_name

    def _str_ccompositiontreenode(self):
        s = self._str_cobjectgraphnode()
        s += '\n'.join(
            ['\n--Child nodes (%i):' % len(self.child_nodes)] + ['\x20\x20(%i, %i, %i)' % t for t in self.child_nodes])
        return s

    def _str_cobjectgraphnode(self):
        s = '--Extensions (%i):\n' % len(self.extensions)
        s += "".join('\x20\x20(%i, %i, %i)\n' % t for t in self.extensions)
        s += '--String: "%s"' % self.obj_string
        return s

    def _str_crenderablenode(self):
        s = '_R{\n' + self._str_cboundednode() + '\n'
        s += '--Number: ' + str(self.R_number) + '\n'
        s += '--Strings: ' + str(self.R_strings) + '\n'
        s += '--Unknown: ' + to_hex(self.R_unknown) + '\n}R_'
        return s

    def _str_cboundednode(self):
        return '_B{\n' + self._str_ctransformnode() + '\n}B_'

    def _str_ctransformnode(self):
        s = 'cTransformNode\n' + self._str_ccompositiontreenode() + '\n'
        s += '--Transform: (%f, %f, %f) ' % self.T_loc + '(%f, %f, %f, %f)\n' % self.T_rot
        s += '--Bone index: ' + str(self.T_bone_index)
        return s

# <- /_SGNode
