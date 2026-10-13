from dataclasses import dataclass

import cadquery as cq
from braille import BrailleSettings
from cane_section import CaneSection


@dataclass(frozen=True)
class CaneHandle:
    """The handle of the cane."""

    section: CaneSection
    """The section this handle will be attached to.

    The section settings are used to work out the length and radius of the handle.
    """

    radius_overflow: float = 0.1
    """How much space should be left between the outside of the section and the handle."""

    top_thickness: float = 20
    """How much material will make up the top of the handle."""

    walls_thickness: float = 3
    """The thickness of the walls."""

    braille_text: str | None = "⠠⠕⠏⠢⠀⠠⠉⠁⠝⠑"
    """The braille to render on the handle."""

    @property
    def braille(self) -> cq.Compound | None:
        """The braille to add to the handle."""
        text = self.braille_text
        if text is None:
            return None
        return BrailleSettings.standard.braille_line(dots=8, line=text)

    def get_shape(self) -> cq.Workplane:
        """Get the shape of the handle."""
        section = self.section
        height = section.section_length - section.waist_length
        cross_section = (self.walls_thickness + section.section_radius) * 2
        box = cq.Workplane("XY").box(
            cross_section,
            cross_section,
            height + self.top_thickness,
            centered=(True, True, False),
        )
        middle_cutter = (
            cq.Workplane("XY")
            .circle(section.section_radius + self.radius_overflow)
            .workplane(offset=height)
            .circle(section.section_radius - self.radius_overflow)
            .loft()
        )
        box = box.cut(middle_cutter).edges("|Z and >X").fillet(section.section_radius)
        box = (
            box.edges(">Z")
            .fillet(cross_section / 2 - 0.1)
            .cut(
                cq.Workplane("XY")
                .cylinder(
                    self.top_thickness + 2,
                    section.interior_radius,
                    centered=(True, True, False),
                )
                .translate((0, 0, height - 1))
            )
        )
        braille = self.braille
        if braille is not None:
            bounds = braille.BoundingBox()
            if bounds.xlen > height or bounds.ylen > cross_section:
                raise RuntimeError(
                    f"Braille text ({bounds.xlen} x {bounds.ylen}) does not fit on the handle ({height} x {cross_section})."
                )
            braille = braille.translate(
                (
                    -bounds.xmin - bounds.xlen / 2 - height / 2,
                    -bounds.ymin - bounds.ylen / 2,
                    -bounds.zmin + cross_section / 2 - 0.05,
                )
            )
            box = (box.rotate((0, 0, 0), (0, 1, 0), 270).union(braille)).rotate(
                (0, 0, 0), (0, 1, 0), 90
            )
        return box


if __name__ == "__main__":
    section = CaneSection()
    handle = CaneHandle(section=section)
    model = handle.get_shape()
    cq.exporters.export(model, "handle.stl")
