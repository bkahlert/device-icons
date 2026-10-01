"""SF Symbols, read from CoreGlyphs.bundle through CoreUI, the private framework Finder draws them with."""

from __future__ import annotations

import ctypes
import functools
from dataclasses import dataclass
from pathlib import Path

CATALOG = Path("/System/Library/CoreServices/CoreGlyphs.bundle/Contents/Resources/Assets.car")
# CoreUI's glyph weight runs 1 ultralight to 9 black, its glyph size 1 small to 3 large; 0 is unspecified and resolves
# to these two, Finder's defaults.
REGULAR = 4
MEDIUM = 2
POINT_SIZE = 100.0

# CGPathElementType, and the points each kind carries.
MOVE, LINE, QUAD, CURVE, CLOSE = range(5)
POINTS = {MOVE: 1, LINE: 1, QUAD: 2, CURVE: 3, CLOSE: 0}
COMMANDS = {MOVE: "M", LINE: "L", QUAD: "Q", CURVE: "C", CLOSE: "Z"}

GLYPH = "namedVectorGlyphWithName:scaleFactor:deviceIdiom:glyphSize:glyphWeight:glyphPointSize:appearanceName:"
UTF8 = 0x08000100


@dataclass(frozen=True)
class Outline:
    """A symbol's path at POINT_SIZE: its elements as (kind, points), and its bounds as (x, y, width, height), y up."""

    elements: list[tuple[int, list[tuple[float, float]]]]
    bounds: tuple[float, float, float, float]


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


class Size(ctypes.Structure):
    _fields_ = [("width", ctypes.c_double), ("height", ctypes.c_double)]


class Rect(ctypes.Structure):
    _fields_ = [("origin", Point), ("size", Size)]


class PathElement(ctypes.Structure):
    _fields_ = [("type", ctypes.c_int), ("points", ctypes.POINTER(Point))]


def outline(symbol_name: str) -> Outline | None:
    """Return the symbol's outline at regular weight and medium scale, or None if CoreGlyphs.bundle has no such symbol.

    Raises RuntimeError if CoreUI opens no catalog at CATALOG.
    """
    return _catalog().outline(symbol_name)


def svg(outline: Outline) -> str:
    """Return the outline as an SVG document: a tight viewBox, one path filled with currentColor, y pointing down.

    Coordinates are rounded to two decimals.
    """
    x, y, width, height = outline.bounds
    top = y + height
    d = "".join(COMMANDS[kind] + " ".join(f"{_number(px - x)} {_number(top - py)}" for px, py in points) for kind, points in outline.elements)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_number(width)} {_number(height)}"><path fill="currentColor" d="{d}"/></svg>\n'


def _number(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


class _Catalog:
    """The CUICatalog of an asset catalog, driven through the Objective-C runtime."""

    def __init__(self, car: Path) -> None:
        self.objc = ctypes.CDLL("/usr/lib/libobjc.A.dylib")
        self.foundation = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        self.graphics = ctypes.CDLL("/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics")
        ctypes.CDLL("/System/Library/PrivateFrameworks/CoreUI.framework/CoreUI")
        self.objc.objc_getClass.restype = ctypes.c_void_p
        self.objc.objc_getClass.argtypes = [ctypes.c_char_p]
        self.objc.sel_registerName.restype = ctypes.c_void_p
        self.objc.sel_registerName.argtypes = [ctypes.c_char_p]
        self.objc.objc_autoreleasePoolPush.restype = ctypes.c_void_p
        self.objc.objc_autoreleasePoolPop.argtypes = [ctypes.c_void_p]
        self.foundation.CFStringCreateWithCString.restype = ctypes.c_void_p
        self.foundation.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
        self.foundation.CFURLCreateWithFileSystemPath.restype = ctypes.c_void_p
        self.foundation.CFURLCreateWithFileSystemPath.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_bool]
        self.graphics.CGPathGetPathBoundingBox.restype = Rect
        self.graphics.CGPathGetPathBoundingBox.argtypes = [ctypes.c_void_p]
        self.graphics.CGPathApply.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.glyph = self._send(
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_void_p
        )
        self.path = self._send(ctypes.c_void_p)
        url = self.foundation.CFURLCreateWithFileSystemPath(None, self._string(str(car)), 0, False)
        allocated = self._send(ctypes.c_void_p)(self.objc.objc_getClass(b"CUICatalog"), self._selector("alloc"))
        self.catalog = self._send(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(allocated, self._selector("initWithURL:error:"), url, None)
        if not self.catalog:
            raise RuntimeError(f"CoreUI opens no asset catalog at {car}")

    def outline(self, symbol_name: str) -> Outline | None:
        pool = self.objc.objc_autoreleasePoolPush()
        try:
            glyph = self.glyph(self.catalog, self._selector(GLYPH), self._string(symbol_name), 1.0, 0, MEDIUM, REGULAR, POINT_SIZE, None)
            if not glyph:
                return None
            path = self.path(glyph, self._selector("CGPath"))
            elements: list[tuple[int, list[tuple[float, float]]]] = []

            @ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(PathElement))
            def visit(_, element):
                kind, points = element.contents.type, element.contents.points
                elements.append((kind, [(points[index].x, points[index].y) for index in range(POINTS[kind])]))

            self.graphics.CGPathApply(path, None, visit)
            box = self.graphics.CGPathGetPathBoundingBox(path)
            return Outline(elements, (box.origin.x, box.origin.y, box.size.width, box.size.height))
        finally:
            self.objc.objc_autoreleasePoolPop(pool)

    def _send(self, restype, *argtypes):
        return ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(restype, ctypes.c_void_p, ctypes.c_void_p, *argtypes))

    def _selector(self, name: str) -> int:
        return self.objc.sel_registerName(name.encode())

    def _string(self, text: str) -> int:
        return self.foundation.CFStringCreateWithCString(None, text.encode(), UTF8)


@functools.cache
def _catalog() -> _Catalog:
    return _Catalog(CATALOG)
