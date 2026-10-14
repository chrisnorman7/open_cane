from dataclasses import dataclass

import cadquery as cq
from cane_section import CaneSection


@dataclass(frozen=True)
class CaneTip:
    """The tip of the cane."""

    section: CaneSection
    """The section to size the tip to."""

    ball_height: float = 25
    """The height of the ball part."""

    ball_radius: float = 13
    """The radius of the ball."""

    ball_fillet: float = 4
    """The fillet to use for the top and bottom edges."""

    interior_offset: float = 0.1
    """The difference between the interior radius of the section and the stem of the tip."""

    @property
    def ball(self) -> cq.Workplane:
        """The ball part of the cane."""
        return (
            cq.Workplane("XY")
            .cylinder(self.ball_height, self.ball_radius)
            .edges("Z")
            .fillet(self.ball_fillet)
        )

    @property
    def stem_length(self) -> float:
        """The length of the tip stem."""
        return self.section.join_length / 1.5

    @property
    def stem(self) -> cq.Workplane:
        """The stem of the tip."""
        section = self.section
        middle_cutter = cq.Workplane("XY").box(
            section.section_radius * 2,
            section.interior_radius,
            section.join_length,
            centered=(True, True, False),
        )
        loop = (
            cq.Workplane("XY")
            .box(
                section.interior_radius,
                section.interior_radius,
                self.stem_length,
                centered=(True, True, False),
            )
            .cut(
                cq.Workplane("XY")
                .cylinder(section.section_length, section.interior_radius)
                .rotate((0, 0, 0), (0, 1, 0), 90)
            )
        )
        return (
            cq.Workplane("XY")
            .cylinder(
                self.stem_length,
                section.female_radius - self.interior_offset,
                centered=(True, True, False),
            )
            .cut(middle_cutter)
        ).union(loop)

    def get_shape(self) -> cq.Workplane:
        """Get the entire tip."""
        section = self.section
        difference = self.ball_radius - self.ball_fillet
        cutter = (
            cq.Workplane("XY")
            .cylinder(
                section.section_length,
                section.section_radius * 2,
                centered=(True, True, False),
            )
            .cut(
                cq.Workplane("XY").cylinder(
                    section.section_length, section.female_radius - self.interior_offset
                )
            )
            .edges("<Z")
            .fillet(difference)
        )
        ring = (
            cq.Workplane("XY")
            .cylinder(difference, difference, centered=(True, True, False))
            .cut(cutter)
        )
        return ring.union(
            self.ball.union(self.stem.translate((0, 0, self.ball_height)))
        )


if __name__ == "__main__":
    section = CaneSection()
    tip = CaneTip(section)
    model = tip.get_shape()
    cq.exporters.export(model, "tip.stl")
