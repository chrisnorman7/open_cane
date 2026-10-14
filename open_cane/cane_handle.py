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

    hole_radius: float = 1.5
    """The radius for the top hole which the string will pass through."""

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
        height = section.section_length - section.waist_length + self.top_thickness
        cross_section = self.walls_thickness + section.section_radius
        box_cross_section = cross_section * 2
        cylinder = cq.Workplane("XY").cylinder(
            height, cross_section, centered=(True, True, False)
        )
        box = cq.Workplane("XY").box(
            height, box_cross_section, box_cross_section, centered=False
        )
        box = box.rotate((0, 0, 0), (0, 1, 0), 270)
        cylinder = cylinder.union(box)
        cylinder = cylinder.edges(">Z").fillet(self.walls_thickness)
        braille = self.braille
        if braille is not None:
            bounds = braille.BoundingBox()
            if bounds.xlen > height or bounds.ylen > box_cross_section:
                raise RuntimeError(
                    f"Braille text ({bounds.xlen} x {bounds.ylen}) does not fit on the handle ({height} x {box_cross_section})."
                )
            center_x = (bounds.xmin + bounds.xmax) / 2
            center_y = (bounds.ymin + bounds.ymax) / 2
            braille = braille.translate(
                (
                    height / 2 - center_x,
                    cross_section - center_y,
                    box_cross_section - bounds.zmin,
                )
            ).rotate((0, 0, 0), (0, 1, 0), 270)
            cylinder = cylinder.union(braille)
        middle = (
            cq.Workplane("XY")
            .cylinder(
                height - self.top_thickness,
                section.section_radius + self.radius_overflow,
                centered=(True, True, False),
            )
            .union(
                cq.Workplane("XY").cylinder(
                    height, self.hole_radius, centered=(True, True, False)
                )
            )
        ).union(
            cq.Workplane("XY").sphere(section.interior_radius).translate((0, 0, height))
        )
        return cylinder.cut(middle)


if __name__ == "__main__":
    section = CaneSection()
    handle = CaneHandle(section=section)
    model = handle.get_shape()
    cq.exporters.export(model, "handle.stl")
