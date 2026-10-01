"""SF Symbols, read from CoreGlyphs.bundle through CoreUI, the private framework Finder draws them with."""

from __future__ import annotations

import ctypes
import functools
import plistlib
from dataclasses import dataclass
from pathlib import Path

CATALOG = Path("/System/Library/CoreServices/CoreGlyphs.bundle/Contents/Resources/Assets.car")
# Legacy symbol names mapped to the current ones, which are the only ones the catalog knows.
ALIASES = CATALOG.with_name("name_aliases.strings")
# CoreUI counts the weights 1 ultralight to 9 black and the scales 1 small to 3 large; 0 is unspecified and resolves to
# these two, Finder's defaults.
REGULAR = 4
MEDIUM = 2
POINT_SIZE = 100.0
# CUIRenderingMode: 1 monochrome, 3 hierarchical. NSImage draws a symbol in its preferred one unless told otherwise.
HIERARCHICAL = 3
# The opacity AppKit draws each hierarchy level with: primary, secondary, tertiary.
HIERARCHY = (1.0, 0.5, 0.3)

# CGPathElementType, and the points each kind carries.
MOVE, LINE, QUAD, CURVE, CLOSE = range(5)
POINTS = {MOVE: 1, LINE: 1, QUAD: 2, CURVE: 3, CLOSE: 0}
COMMANDS = {MOVE: "M", LINE: "L", QUAD: "Q", CURVE: "C", CLOSE: "Z"}

SYMBOL = "namedVectorGlyphWithName:scaleFactor:deviceIdiom:glyphSize:glyphWeight:glyphPointSize:appearanceName:"
UTF8 = 0x08000100


@dataclass(frozen=True)
class Layer:
    """One layer of a symbol: its path elements as (kind, points), its hierarchy level, and its own opacity.

    The level is 0 primary, 1 secondary, or 2 tertiary; every layer of a monochrome symbol is primary.
    """

    elements: list[tuple[int, list[tuple[float, float]]]]
    level: int = 0
    opacity: float = 1.0


@dataclass(frozen=True)
class Outline:
    """A symbol at POINT_SIZE in its preferred rendering mode: its layers in drawing order, and the bounds (x, y, width, height) of what they draw.

    What the symbol's eraser layers cut is already cut out of the layers before them. CoreUI draws y down, as SVG does:
    the top of the symbol has the smallest y.
    """

    layers: list[Layer]
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

    A legacy symbol name is followed to the current one first, as current() does.

    Raises RuntimeError if CoreUI opens no catalog at CATALOG.
    """
    return _catalog().outline(current(symbol_name))


def current(symbol_name: str) -> str:
    """Return the symbol's current name: the symbol name followed through ALIASES, or itself if it has no alias."""
    return resolve(symbol_name, _aliases())


def resolve(symbol_name: str, aliases: dict[str, str]) -> str:
    """Return the current name of the symbol: the symbol name followed through aliases until a name without one, or until a cycle."""
    seen = set()
    while symbol_name in aliases and symbol_name not in seen:
        seen.add(symbol_name)
        symbol_name = aliases[symbol_name]
    return symbol_name


def svg(outline: Outline, hierarchy: tuple[float, float, float] = HIERARCHY) -> str:
    """Return the symbol as an SVG document: a tight viewBox with the layers moved to its origin, a path filled with currentColor per layer.

    hierarchy gives the opacity of a primary, secondary, and tertiary layer. A layer's opacity is its own times its
    level's; below 1, it is the path's fill-opacity. Coordinates are rounded to two decimals.
    """
    x, y, width, height = outline.bounds
    paths = ""
    for layer in outline.layers:
        d = "".join(COMMANDS[kind] + " ".join(f"{_number(px - x)} {_number(py - y)}" for px, py in points) for kind, points in layer.elements)
        opacity = layer.opacity * hierarchy[layer.level]
        attribute = f' fill-opacity="{_number(opacity)}"' if opacity < 1 else ""
        paths += f'<path fill="currentColor"{attribute} d="{d}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_number(width)} {_number(height)}">{paths}</svg>\n'


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
        self.graphics.CGPathCreateCopyBySubtractingPath.restype = ctypes.c_void_p
        self.graphics.CGPathCreateCopyBySubtractingPath.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        self.symbol = self._send(
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_double, ctypes.c_void_p
        )
        self.object = self._send(ctypes.c_void_p)
        self.item = self._send(ctypes.c_void_p, ctypes.c_ulong)
        self.unsigned = self._send(ctypes.c_ulong)
        self.signed = self._send(ctypes.c_long)
        self.double = self._send(ctypes.c_double)
        self.flag = self._send(ctypes.c_bool)
        url = self.foundation.CFURLCreateWithFileSystemPath(None, self._string(str(car)), 0, False)
        allocated = self.object(self.objc.objc_getClass(b"CUICatalog"), self._selector("alloc"))
        self.catalog = self._send(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(allocated, self._selector("initWithURL:error:"), url, None)
        if not self.catalog:
            raise RuntimeError(f"CoreUI opens no asset catalog at {car}")

    def outline(self, symbol_name: str) -> Outline | None:
        pool = self.objc.objc_autoreleasePoolPush()
        try:
            symbol = self.symbol(self.catalog, self._selector(SYMBOL), self._string(symbol_name), 1.0, 0, MEDIUM, REGULAR, POINT_SIZE, None)
            if not symbol:
                return None
            hierarchical = self.signed(symbol, self._selector("preferredRenderingMode")) == HIERARCHICAL
            group = self.object(symbol, self._selector("hierarchicalLayers" if hierarchical else "monochromeLayers"))
            shapes: list[tuple[int, int, float]] = []
            for index in range(self.unsigned(group, self._selector("count"))):
                layer = self.item(group, self._selector("objectAtIndex:"), index)
                shape = self.object(layer, self._selector("shape"))
                if self.flag(layer, self._selector("isEraserLayer")):
                    subtract = self.graphics.CGPathCreateCopyBySubtractingPath
                    shapes = [(subtract(path, shape, False), level, opacity) for path, level, opacity in shapes]
                else:
                    level = self.unsigned(layer, self._selector("hierarchyLevel")) if hierarchical else 0
                    shapes.append((shape, level, self.double(layer, self._selector("opacity"))))
            boxes = [self.graphics.CGPathGetPathBoundingBox(path) for path, _, _ in shapes]
            left, top = min(box.origin.x for box in boxes), min(box.origin.y for box in boxes)
            right, bottom = max(box.origin.x + box.size.width for box in boxes), max(box.origin.y + box.size.height for box in boxes)
            return Outline([Layer(self._elements(path), level, opacity) for path, level, opacity in shapes], (left, top, right - left, bottom - top))
        finally:
            self.objc.objc_autoreleasePoolPop(pool)

    def _elements(self, path: int) -> list[tuple[int, list[tuple[float, float]]]]:
        elements: list[tuple[int, list[tuple[float, float]]]] = []

        @ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(PathElement))
        def visit(_, element):
            kind, points = element.contents.type, element.contents.points
            elements.append((kind, [(points[index].x, points[index].y) for index in range(POINTS[kind])]))

        self.graphics.CGPathApply(path, None, visit)
        return elements

    def _send(self, restype, *argtypes):
        return ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(restype, ctypes.c_void_p, ctypes.c_void_p, *argtypes))

    def _selector(self, name: str) -> int:
        return self.objc.sel_registerName(name.encode())

    def _string(self, text: str) -> int:
        return self.foundation.CFStringCreateWithCString(None, text.encode(), UTF8)


@functools.cache
def _catalog() -> _Catalog:
    return _Catalog(CATALOG)


@functools.cache
def _aliases() -> dict[str, str]:
    with ALIASES.open("rb") as file:
        return plistlib.load(file)
