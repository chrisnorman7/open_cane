from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class CaneSection:
    """A section of a cane."""

    section_length: float = 210
    """The length of the section, minus `join_length`."""

    section_radius: float = 7
    """The radius of the main section."""

    waist_length: float = 15
    """The length of the outer waist."""

    waist_radius: float = 8
    """The radius of the flared part of the female join."""

    join_length: float = 40
    """The length of each join."""

    male_wide_radius: float = 6
    """The radius of the wider part of the male joint."""

    male_narrow_radius: float = 4
    """The radius of the narrower part of the male joint."""

    female_offset: float = 0.5
    """The difference between the male and female joins."""

    interior_radius: float = 3
    """The radius of the interior shaft."""

    @property
    def total_length(self) -> float:
        """The entire length of the section."""
        return self.join_length + self.section_length

    @property
    def total_radius(self) -> float:
        """The total radius of the section"""
        return self.section_radius + self.waist_radius

    @property
    def male_join(self) -> cq.Workplane:
        """The male join.

        This join must be translated to be above the main section.
        """
        return (
            cq.Workplane("XY")
            .circle(self.male_wide_radius)
            .workplane(offset=self.join_length)
            .circle(self.male_narrow_radius)
            .loft()
        )

    @property
    def section(self) -> cq.Workplane:
        """The main section."""
        return cq.Workplane("XY").cylinder(
            self.section_length, self.section_radius, centered=(True, True, False)
        )

    @property
    def interior(self) -> cq.Workplane:
        """The central shaft.

        The interior should be cut from the section.
        """
        return cq.Workplane("XY").cylinder(
            self.total_length, self.interior_radius, centered=(True, True, False)
        )

    @property
    def female_join(self) -> cq.Workplane:
        """The female join.

        This join should be cut from the base of the section.
        """
        return (
            cq.Workplane("XY")
            .circle(self.male_wide_radius + self.female_offset)
            .workplane(offset=self.join_length)
            .circle(self.male_narrow_radius + self.female_offset)
            .loft()
        )

    @property
    def waist(self) -> cq.Workplane:
        """The waist ring."""
        return cq.Workplane("XY").cylinder(
            self.waist_length, self.waist_radius, centered=(True, True, False)
        )

    def get_shape(self) -> cq.Workplane:
        """Get the section shape."""
        section = self.section.union(
            self.male_join.translate((0, 0, self.section_length))
        ).union(self.waist)
        section = section.cut(self.interior).cut(self.female_join)
        return section


if __name__ == "__main__":
    section = CaneSection()
    model = section.get_shape()
    cq.exporters.export(model, "cane_section.stl")
