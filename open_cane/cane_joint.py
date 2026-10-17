from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class CaneJoint:
    """A joint between two metal tubes."""

    tube_radius: float = 6.2
    """The radius of the metal tube, plus some.

    For example, with 13 mm tubes, the radius is `6.5`. Then add a little for wiggle room.

    This value will form the radius of the female join.
    """

    wall_thickness: float = 3
    """The thickness of the walls."""

    female_length: float = 30
    """The length of the female part of the joint."""

    string_hole_length: float = 5
    """The length of the part where the string passes through."""

    string_hole_radius: float = 5
    """The radius of the hole where the string will pass through."""

    male_join_length: float = 40
    """The length of the part which will clamp the tube."""

    male_offset: float = 0.1
    """The offset from `tube_radius` which will inform the radius of the part of the join which grips the tube."""

    @property
    def full_length(self) -> float:
        """The full length of the section."""
        return self.female_length + self.string_hole_length + self.male_join_length

    @property
    def full_radius(self) -> float:
        """Return the radius of the join."""
        return self.tube_radius + self.wall_thickness

    @property
    def female_section(self) -> cq.Workplane:
        """The female part of the join.

        This value should be cut away from the eventual solid."""
        return cq.Workplane("XY").cylinder(
            self.female_length, self.tube_radius, centered=(True, True, False)
        )

    @property
    def male_section(self) -> cq.Workplane:
        """The male part of the join.

        This section should be cut away from the eventual solid, and will be used to grip the inner metal tube.
        """
        return cq.Workplane("XY").cylinder(
            self.male_join_length,
            self.tube_radius - self.male_offset,
            centered=(True, True, False),
        )

    @property
    def string_hole(self) -> cq.Workplane:
        """The hole which the string will pass through.

        This model should be cut from the eventual solid.
        """
        return cq.Workplane("XY").cylinder(
            self.string_hole_length,
            self.string_hole_radius,
            centered=(True, True, False),
        )

    def get_shape(self) -> cq.Workplane:
        """Get the entire model."""
        cylinder = cq.Workplane("XY").cylinder(
            self.full_length, self.full_radius, centered=(True, True, False)
        )
        female_section = self.female_section
        cylinder = cylinder.cut(
            female_section.translate(
                (0, 0, self.male_join_length + self.string_hole_length)
            )
        )
        string_hole = self.string_hole
        cylinder = cylinder.cut(string_hole.translate((0, 0, self.male_join_length)))
        male_section = self.male_section
        cylinder = cylinder.cut(male_section)
        return cylinder


if __name__ == "__main__":
    joint = CaneJoint()
    joint.get_shape().export("joint.step")
