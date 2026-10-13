from dataclasses import dataclass

import cadquery as cq
from cane_section import CaneSection

from open_cane.braille import BrailleSettings


@dataclass(frozen=True)
class CaneHandle:
    """The handle of the cane."""

    section: CaneSection
    """The section this handle will be attached to.

    The section settings are used to work out the length and radius of the handle.
    """

    radius_overflow: float = 0.2
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
        cross_section = section.section_radius + self.walls_thickness
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
        box = (
            box.cut(middle_cutter)
            .edges("|Z and >X and <Y")
            .fillet(section.section_radius)
        )
        top_cutter = (
            (
                cq.Workplane("XY")
                .box(
                    cross_section,
                    cross_section,
                    self.top_thickness,
                    centered=(True, True, False),
                )
                .cut(cq.Workplane("XY").sphere(cross_section))
            ).union(
                cq.Workplane("XY").cylinder(
                    self.top_thickness,
                    section.interior_radius,
                    centered=(True, True, False),
                )
            )
        ).translate((0, 0, height))
        return box.cut(top_cutter)
