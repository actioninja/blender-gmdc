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


__all__ = ['load_resource']

from struct import pack, unpack

from ._common import *
from ._node import _SGNode
from ._gmdc import GeometryDataContainer


########################################
#  Node classes
########################################

class ResourceNode(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cResourceNode'
        self.version = 0x07

    def read(self, f, log_level):
        s = f.read(18)
        if s != b'\x0dcResourceNode\x33\xc9\x19\xe5':
            error('Error! cResourceNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, 0x07): return False
        self.Res_unknown1 = f.read(1)
        if not self._read_csgresource(f) or not self._read_ccompositiontreenode(f): return False
        self.Res_unknown2 = f.read(5)
        return True

    def write(self, f):
        f.write(b'\x0dcResourceNode\x33\xc9\x19\xe5')
        self._write_version(f)
        f.write(self.Res_unknown1)
        self._write_csgresource(f)
        self._write_ccompositiontreenode(f)
        f.write(self.Res_unknown2)

    def __str__(self):
        s = 'cResourceNode\n'
        s += '--Unknown 1: ' + to_hex(self.Res_unknown1) + '\n'
        s += self._str_csgresource() + '\n' + self._str_ccompositiontreenode() + '\n'
        s += '--Unknown 2: ' + to_hex(self.Res_unknown2)
        return s


class ShapeRefNode(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cShapeRefNode'
        self.version = 0x14

    def read(self, f, log_level):
        s = f.read(18)
        if s != b'\x0dcShapeRefNode\x17\x55\x24\x65':
            error('Error! cShapeRefNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, (0x14, 0x15)) or not self._read_crenderablenode(f): return False
        # linked resource indices (?)
        i = unpack('<l', f.read(4))[0]
        s = f.read(i * 6)
        v = unpack('<' + 'BBl' * (len(s) // 6), s)
        self.SR_data1 = chunk(v, 3)
        # 4 bytes
        self.SR_unknown1 = f.read(4)
        # morphs (?)
        i = unpack('<l', f.read(4))[0]
        s = f.read(4 * i)
        self.SR_data2 = chunk(s, 4)
        if self.version >= 0x15:
            v = []
            while i:
                v.append(read_str(f))
                i -= 1
            self.SR_strings = v
        # unknown
        i = unpack('<l', f.read(4))[0]
        self.SR_unknown2 = f.read(i)
        self.SR_unknown3 = f.read(4)
        return True

    def write(self, f):
        f.write(b'\x0dcShapeRefNode\x17\x55\x24\x65')
        self._write_version(f)
        self._write_crenderablenode(f)
        f.write(pack('<l', len(self.SR_data1)))
        for t in self.SR_data1:
            f.write(pack('<BBl', *t))
        f.write(self.SR_unknown1)
        f.write(pack('<l', len(self.SR_data2)))
        for s in self.SR_data2:
            f.write(s)
        if self.version == 0x15:
            for s in self.SR_strings:
                write_str(f, s)
        f.write(pack('<l', len(self.SR_unknown2)))
        f.write(self.SR_unknown2)
        f.write(self.SR_unknown3)

    def __str__(self):
        s = 'cShapeRefNode (version: 0x%02X)\n' % self.version
        s += self._str_crenderablenode() + '\n'
        s += '--Unknown data (%i):\n' % len(self.SR_data1)
        s += "".join('  %02X %02X ( %i ) - linked resource index (?)\n' % t for t in self.SR_data1)
        s += '--Unknown 1: ' + to_hex(self.SR_unknown1) + '\n'
        s += '--Data related to morphs (?) (%i):\n' % len(self.SR_data2)
        s += "".join('\x20\x20%s\n' % to_hex(t) for t in self.SR_data2)
        if self.version == 0x15:
            s += '--Strings: ' + str(self.SR_strings) + '\n'
        s += '--Unknown 2: ' + to_hex(self.SR_unknown2) + '\n'
        s += '--Unknown 3: ' + to_hex(self.SR_unknown3)
        return s


class TransformNode(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cTransformNode'
        self.version = 0x07

    def read(self, f, log_level):
        return self._read_ctransformnode(f)

    def write(self, f):
        self._write_ctransformnode(f)

    def __str__(self):
        return self._str_ctransformnode()


class DataListExtension(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cDataListExtension'
        self.version = 0x01

    def read(self, f, log_level):
        s = f.read(23)
        if s != b'\x12cDataListExtension\x56\x6d\x83\x6a':
            error('Error! cDataListExtension header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        v = []
        if not self._read_check_version(f, 0x01) or not self._read_cextension_h(f) or not self._read_ext_data(f,
                                                                                                              v): return False
        assert len(v) == 1
        self.Ext_data = v[0]
        return True

    @staticmethod
    def _read_ext_data(f, data):
        i = unpack('B', f.read(1))[0]  # type
        s = read_str(f)  # name
        if i == 0x06:  # string (?)
            data.append((0x06, s, read_str(f)))
        elif i == 0x02:  # int (?)
            data.append((0x02, s, unpack('<l', f.read(4))[0]))
        elif i == 0x03:  # float (?)
            data.append((0x03, s, unpack('<f', f.read(4))[0]))
        elif i == 0x05:  # 3 floats (?)
            data.append((0x05, s, unpack('<3f', f.read(12))))
        elif i == 0x08:  # 4 floats (?)
            data.append((0x08, s, unpack('<4f', f.read(16))))
        elif i == 0x09:  # N bytes (?)
            i = unpack('<l', f.read(4))[0]
            data.append((0x09, s, f.read(i)))
        elif i == 0x07:  # list of data
            v = []
            for i in xrange(unpack('<l', f.read(4))[0]):
                if not DataListExtension._read_ext_data(f, v): return False
            data.append((0x07, s, v))
        else:
            error('Error! cDataListExtension. Unknown data type: %02X', i)
            error('%#x' % f.tell())
            return False
        return True

    def write(self, f):
        f.write(b'\x12cDataListExtension\x56\x6d\x83\x6a')
        self._write_version(f)
        self._write_cextension_h(f)
        self._write_ext_data(f, self.Ext_data)

    @staticmethod
    def _write_ext_data(f, data):
        i, s, v = data
        f.write(pack('B', i))
        write_str(f, s)
        if i == 0x06:
            write_str(f, v)
        elif i == 0x02:
            f.write(pack('<l', v))
        elif i == 0x03:
            f.write(pack('<f', v))
        elif i == 0x05:
            f.write(pack('<3f', *v))
        elif i == 0x08:
            f.write(pack('<4f', *v))
        elif i == 0x09:
            f.write(pack('<l', len(v)) + v)
        elif i == 0x07:
            f.write(pack('<l', len(v)))
            for x in v:
                DataListExtension._write_ext_data(f, x)
        else:
            raise AssertionError

    def __str__(self):
        s = 'cDataListExtension'
        if self.Ext_data[1] == 'footprint':
            s += '\x20(footprint)\n' + str_footprint(self.Ext_data[2])
        else:
            s += '\n' + self._str_ext_data(self.Ext_data)
        return s

    @staticmethod
    def _str_ext_data(data, indent=''):
        i, s, v = data
        if i == 0x06:
            s = indent + '--Property "%s": "%s"' % (s, v)
        elif i == 0x02:
            s = indent + '--Property "%s": %i' % (s, v)
        elif i == 0x03:
            s = indent + '--Property "%s": %f' % (s, v)
        elif i == 0x05:
            s = indent + '--Property "%s": ' % s + '(%f, %f, %f)' % v
        elif i == 0x08:
            s = indent + '--Property "%s": ' % s + '(%f, %f, %f, %f)' % v
        elif i == 0x09:
            s = indent + '--Property "%s" (%i bytes): %s' % (s, len(v), to_hex(v))
        elif i == 0x07:
            s = indent + '\n'.join(
                ['--Property list "%s" (%i):' % (s, len(v))] + [DataListExtension._str_ext_data(x, indent + '\x20\x20')
                                                                for x in v])
        else:
            raise AssertionError
        return s


class BoneDataExtension(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cBoneDataExtension'
        self.version = 0x04

    def read(self, f, log_level):
        s = f.read(23)
        if s != b'\x12cBoneDataExtension\xc5\x5b\x07\xe9':
            error('Error! cBoneDataExtension header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, (0x04, 0x05)) or not self._read_cextension_h(f): return False
        self.B_ext_unknown = f.read(12)
        self.B_ext_float = unpack('<f', f.read(4))[0]
        self.B_ext_quat = unpack('<4f', f.read(16))
        return True

    def write(self, f):
        f.write(b'\x12cBoneDataExtension\xc5\x5b\x07\xe9')
        self._write_version(f)
        self._write_cextension_h(f)
        f.write(self.B_ext_unknown)
        f.write(pack('<f', self.B_ext_float))
        f.write(pack('<4f', *self.B_ext_quat))

    def __str__(self):
        s = 'cBoneDataExtension (version: 0x%02X)\n' % self.version
        s += '--Unknown: ' + to_hex(self.B_ext_unknown) + '\n'
        s += '--Float: %f\n' % self.B_ext_float
        s += '--Quaternion (?): (%f %f %f %f)' % self.B_ext_quat
        return s


class LightRefNode(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cLightRefNode'
        self.version = 0x0a

    def read(self, f, log_level):
        s = f.read(18)
        if s != b'\x0dcLightRefNode\x18\x20\x3d\x25':
            error('Error! cLightRefNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, 0x0a) or not self._read_crenderablenode(f): return False
        self.L_index = unpack('<BBl', f.read(6))
        self.L_unknown = f.read(2)
        return True

    def write(self, f):
        f.write(b'\x0dcLightRefNode\x18\x20\x3d\x25')
        self._write_version(f)
        self._write_crenderablenode(f)
        f.write(pack('<BBl', *self.L_index))
        f.write(self.L_unknown)

    def __str__(self):
        s = 'cLightRefNode\n'
        s += self._str_crenderablenode() + '\n'
        s += '--Linked resource index (?): %02X %02X ( %i )\n' % self.L_index
        s += '--Unknown: ' + to_hex(self.L_unknown)
        return s


class ViewerRefNode(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cViewerRefNode'
        self.version = 0x0d

    def _read_cViewerRefNodeBase(self, f):
        s = f.read(27)
        if s != b'\x12cViewerRefNodeBase\x00\x00\x00\x00\x05\x00\x00\x00':
            error('Error! cViewerRefNodeBase header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        return self._read_crenderablenode(f)

    def _write_cViewerRefNodeBase(self, f):
        f.write(b'\x12cViewerRefNodeBase\x00\x00\x00\x00\x05\x00\x00\x00')
        self._write_crenderablenode(f)

    def _str_cViewerRefNodeBase(self):
        return self._str_crenderablenode()

    def read(self, f, log_level):
        s = f.read(19)
        if s != b'\x0ecViewerRefNode\xbb\x6d\xa7\xdc':
            error('Error! cViewerRefNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, (0x0d, 0x0e)) or not self._read_cViewerRefNodeBase(f): return False
        self.V_data = f.read(0x9c if self.version == 0x0E else 0x9b)
        return True

    def write(self, f):
        f.write(b'\x0ecViewerRefNode\xbb\x6d\xa7\xdc')
        self._write_version(f)
        self._write_cViewerRefNodeBase(f)
        f.write(self.V_data)

    def __str__(self):
        s = 'cViewerRefNode (version: 0x%02X)\n' % self.version
        s += self._str_cViewerRefNodeBase() + '\n'
        s += '--Data:\n'
        s += '\n'.join(to_hex(x) for x in chunk(self.V_data, 16))
        return s


class ViewerRefNodeRecursive(ViewerRefNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cViewerRefNodeRecursive'
        self.version = 0x01

    def read(self, f, log_level):
        s = f.read(28)
        if s != b'\x17cViewerRefNodeRecursive\x8e\x2b\x15\x0c':
            error('Error! cViewerRefNodeRecursive header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, 0x01) or not self._read_cViewerRefNodeBase(f): return False
        self.VR_unknown = f.read(1)
        self.VR_string = read_str(f)
        self.VR_data = f.read(0x40)
        return True

    def write(self, f):
        f.write(b'\x17cViewerRefNodeRecursive\x8e\x2b\x15\x0c')
        self._write_version(f)
        self._write_cViewerRefNodeBase(f)
        f.write(self.VR_unknown)
        write_str(f, self.VR_string)
        f.write(self.VR_data)

    def __str__(self):
        s = 'cViewerRefNodeRecursive\n'
        s += self._str_cViewerRefNodeBase() + '\n'
        s += '--Unknown: ' + to_hex(self.VR_unknown) + '\n'
        s += '--String: "%s"\n' % self.VR_string
        s += '--Data:\n'
        s += '\n'.join(to_hex(x) for x in chunk(self.VR_data, 16))
        return s


class GeometryNode(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cGeometryNode'
        self.version = 0x0c

    def read(self, f, log_level):
        s = f.read(18)
        if s != b'\x0dcGeometryNode\x8c\x83\xa3\x7b':
            error('Error! cGeometryNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, 0x0c) or not self._read_cobjectgraphnode(f) or not self._read_csgresource(
            f): return False
        self.G_unknown = f.read(7)
        return True

    def write(self, f):
        f.write(b'\x0dcGeometryNode\x8c\x83\xa3\x7b')
        self._write_version(f)
        self._write_cobjectgraphnode(f)
        self._write_csgresource(f)
        f.write(self.G_unknown)

    def __str__(self):
        s = 'cGeometryNode\n'
        s += self._str_cobjectgraphnode() + '\n' + self._str_csgresource() + '\n'
        s += '--Unknown: ' + to_hex(self.G_unknown)
        return s


class MaterialDefinition(_SGNode):

    def __init__(self, index):
        self.index = index
        self.type = 'cMaterialDefinition'
        self.version = 0x0b

    def read(self, f, log_level):
        s = f.read(24)
        if s != b'\x13cMaterialDefinition\x78\x69\x59\x49':
            error('Error! cGeometryNode header:', to_hex(s))
            error('%#x' % f.tell())
            return False
        if not self._read_check_version(f, 0x0b) or not self._read_csgresource(f): return False
        self.Mat_name = read_str(f)
        self.Mat_type = read_str(f)
        i = unpack('<l', f.read(4))[0]
        v = []
        while i:
            v.append((read_str(f), read_str(f)))
            i -= 1
        self.Mat_properties = v
        i = unpack('<l', f.read(4))[0]
        v = []
        while i:
            v.append(read_str(f))
            i -= 1
        self.Mat_references = v
        return True

    def write(self, f):
        f.write(b'\x13cMaterialDefinition\x78\x69\x59\x49')
        self._write_version(f)
        self._write_csgresource(f)
        write_str(f, self.Mat_name)
        write_str(f, self.Mat_type)
        f.write(pack('<l', len(self.Mat_properties)))
        for s1, s2 in self.Mat_properties:
            write_str(f, s1)
            write_str(f, s2)
        f.write(pack('<l', len(self.Mat_references)))
        for s1 in self.Mat_references:
            write_str(f, s1)

    def __str__(self):
        s = 'cMaterialDefinition\n'
        s += self._str_csgresource() + '\n'
        s += '--Name: "%s"\n' % self.Mat_name
        s += '--Type: "%s"\n' % self.Mat_type
        s += '--Properties (%i):\n'
        for s1, s2 in self.Mat_properties:
            s += '\x20\x20"%s": "%s"\n' % (s1, s2)
        s += '\n'.join(
            ['--References (%i):' % len(self.Mat_references)] + ['\x20\x20"%s"' % s1 for s1 in self.Mat_references])
        return s


# -------------------------------------------------------------------------------

class ResourceFile(object):

    def __init__(self, filename=None, log_level=1):
        self._clear()
        if filename != None: self.load(filename, log_level)

    def _clear(self):
        self.filename = None
        self.linked_resources = list()
        self.nodes = list()
        self.sg_resource_name = None

    def __str__(self):
        s = 'ResourceFile\n'
        if self.filename: s += '--Filename: "%s"\n' % self.filename
        if self.sg_resource_name: s += '--Resource name: "%s"\n' % self.sg_resource_name
        s += '--Linked resources (%i):\n' % len(self.linked_resources)
        for t in self.linked_resources:
            s += '\x20\x20%08X - %08X - %08X - %08X\n' % t
        s += '--Number of nodes: %i' % len(self.nodes)
        return s

    def __repr__(self):
        return self.__str__()

    # ---------------------------------------

    def load(self, filename, log_level=1):

        with open(filename, 'rb') as f:
            s = f.read(4)
            if s != b'\x01\x00\xff\xff':
                error('Error! Wrong file header:', to_hex(s))
                return False

            if not self._load_resource(f, log_level):
                self._clear()
                return False

        self.filename = filename

        try:
            self.sg_resource_name = self.nodes[0].sg_resource_name
        except:
            pass

        return True

    def _load_resource(self, f, log_level):

        # linked resources
        #
        k = unpack('<l', f.read(4))[0]
        s = chunk(f.read(k * 16), 16)
        self.linked_resources = map(lambda x: unpack('<4L', x), s)
        assert len(self.linked_resources) == k

        if log_level > 0:
            log('Linked resources (%i):' % k)
            for t in self.linked_resources:
                log('%08X - %08X - %08X - %08X' % t)

        # types of nodes
        #
        k = unpack('<l', f.read(4))[0]
        s = f.read(k * 4)
        node_types = chunk(s, 4)
        assert len(node_types) == k

        if log_level > 0: log('Number of nodes:', k)

        dd = {
            b'\x33\xc9\x19\xe5': ResourceNode,
            b'\x62\x64\x24\x65': TransformNode,
            b'\x17\x55\x24\x65': ShapeRefNode,
            b'\x56\x6d\x83\x6a': DataListExtension,
            b'\xc5\x5b\x07\xe9': BoneDataExtension,
            b'\x18\x20\x3d\x25': LightRefNode,
            b'\xbb\x6d\xa7\xdc': ViewerRefNode,
            b'\x8e\x2b\x15\x0c': ViewerRefNodeRecursive,
            b'\x8c\x83\xa3\x7b': GeometryNode,
            b'\x87\x86\x4F\xAC': GeometryDataContainer,
            b'\x78\x69\x59\x49': MaterialDefinition,
        }

        # nodes
        #
        Nodes = []
        for i, nt_id in enumerate(node_types):

            offset = f.tell()

            try:
                _class = dd[nt_id]
            except KeyError:
                error('Error! Unknown node.')
                error('%#x' % f.tell())
                return False

            node = _class(i)
            if not node.read(f, log_level): return False

            Nodes.append(node)

            if log_level > 0:
                log('>Node #%s (offset: %08x) - ' % (str(i).rjust(4, '_'), offset) + (
                    str(node) if log_level > 1 else node.type))

        self.nodes = Nodes

        return True

    # ---------------------------------------

    def save(self):

        with open(self.filename, 'wb') as f:
            self._write_resource_file(f)

    def save_as(self, filename):

        with open(filename, 'wb') as f:
            self._write_resource_file(f)

    def _write_resource_file(self, f):

        f.write(b'\x01\x00\xff\xff')

        f.write(pack('<l', len(self.linked_resources)))
        for t in self.linked_resources: f.write(pack('<4L', *t))

        dd = {
            'cResourceNode': b'\x33\xc9\x19\xe5',
            'cTransformNode': b'\x62\x64\x24\x65',
            'cShapeRefNode': b'\x17\x55\x24\x65',
            'cDataListExtension': b'\x56\x6d\x83\x6a',
            'cBoneDataExtension': b'\xc5\x5b\x07\xe9',
            'cLightRefNode': b'\x18\x20\x3d\x25',
            'cViewerRefNode': b'\xbb\x6d\xa7\xdc',
            'cViewerRefNodeRecursive': b'\x8e\x2b\x15\x0c',
            'cGeometryNode': b'\x8c\x83\xa3\x7b',
            'cGeometryDataContainer': b'\x87\x86\x4F\xAC',
            'cMaterialDefinition': b'\x78\x69\x59\x49',
        }

        f.write(pack('<l', len(self.nodes)))
        for node in self.nodes:
            f.write(dd[node.type])
        for node in self.nodes:
            node.write(f)


# <- /ResourceFile


def load_resource(filename, log_level=1):
    res = ResourceFile()
    return res if res.load(filename, log_level) else False


# -------------------------------------------------------------------------------

def str_footprint(footprint):
    def str_footprint_pattern(data):

        w = dict((s, v) for i, s, v in data)

        minx = w['minx']
        maxx = w['maxx']
        miny = w['miny']
        maxy = w['maxy']

        s = ''

        for y in xrange(maxy, miny - 1, -1):
            ss = [str()] * 16
            for x in xrange(minx, maxx + 1):
                key = '(%i,%i)' % (x, y)
                v = w[key]
                for i, j in zip(xrange(0, 32, 2), xrange(15, -1, -1)):
                    a = unpack('<H', v[i:i + 2])[0]
                    ss[j] += "".join(reversed(format(a, '016b').replace('0', '-').replace('1', 'X'))) + '\x20'
                s += key.ljust(16) + '\x20'
            s += '\n' + '\n'.join(ss) + ('\n' if y != miny else '')
        return s

    return '\n'.join('--Footprint pattern "%s":\n' % name + str_footprint_pattern(data) for i, name, data in footprint)
