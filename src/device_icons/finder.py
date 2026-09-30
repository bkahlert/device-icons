"""Folder icons, set through AppKit as pasting an image into Finder's Get Info does."""

from __future__ import annotations

import subprocess
from pathlib import Path

# JavaScript for Automation. Sidebar icons are black template images, so each is tinted grey first to show in the
# dark and the light appearance alike.
SET_FOLDER_ICONS = r"""
ObjC.import('AppKit');
function tinted(path) {
  const image = $.NSImage.alloc.initWithContentsOfFile(path);
  const size = image.size;
  const rep = $.NSBitmapImageRep.alloc
    .initWithBitmapDataPlanesPixelsWidePixelsHighBitsPerSampleSamplesPerPixelHasAlphaIsPlanarColorSpaceNameBytesPerRowBitsPerPixel(
      null, size.width, size.height, 8, 4, true, false, $.NSCalibratedRGBColorSpace, 0, 0);
  const rect = $.NSMakeRect(0, 0, size.width, size.height);
  $.NSGraphicsContext.saveGraphicsState;
  $.NSGraphicsContext.setCurrentContext($.NSGraphicsContext.graphicsContextWithBitmapImageRep(rep));
  image.drawInRectFromRectOperationFraction(rect, $.NSZeroRect, $.NSCompositingOperationSourceOver, 1.0);
  $.NSColor.systemGrayColor.set;
  $.NSRectFillUsingOperation(rect, $.NSCompositingOperationSourceIn);
  $.NSGraphicsContext.restoreGraphicsState;
  const result = $.NSImage.alloc.initWithSize(size);
  result.addRepresentation(rep);
  return result;
}
function run(argv) {
  const workspace = $.NSWorkspace.sharedWorkspace;
  return argv.map(job => {
    const [image, folder] = job.split('\t');
    const ok = workspace.setIconForFileOptions(tinted(image), folder, 0);
    return (ok ? 'ok' : 'failed') + '\t' + folder;
  }).join('\n');
}
"""


def set_folder_icons(icons: dict[Path, Path]) -> list[Path]:
    """Give each folder the image as its icon; return the folders that could not be decorated.

    Finder keeps the icon in a hidden file inside the folder, named Icon plus a carriage return.
    """
    if not icons:
        return []
    jobs = [f"{image.resolve()}\t{folder.resolve()}" for folder, image in icons.items()]
    out = subprocess.run(["osascript", "-l", "JavaScript", "-e", SET_FOLDER_ICONS, *jobs], check=True, capture_output=True, text=True).stdout
    failed = {line.split("\t")[1] for line in out.splitlines() if line.startswith("failed")}
    return [folder for folder in icons if str(folder.resolve()) in failed]
