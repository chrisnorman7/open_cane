from dataclasses import dataclass

import cadquery as cq

from open_cane.cane_joint import CaneJoint


@dataclass(frozen=True)
class CaneTip:
    """The tip of the cane."""

    joint_radius: float
    """The radius of the female joint."""

    joint_length: float = 40
    """The length of the female joint."""

    walls_thickness: float = 3
    """The thickness of the walls."""

    string_hole_radius: float = 5
    """The radius for the top hole which the string will pass through."""

    ball_height: float = 25
    """The height of the ball part."""

    ball_radius: float = 13
    """The radius of the ball."""

    ball_fillet: float = 4
    """The fillet to use for the top and bottom edges."""

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
        return self.joint_length / 1.5

    @property
    def stem(self) -> cq.Workplane:
        """The stem of the tip."""
        stem_length = self.stem_length
        return (
            cq.Workplane("XY")
            .cylinder(
                stem_length,
                self.joint_radius - self.string_hole_radius,
                centered=(True, True, False),
            )
            .cut(
                cq.Workplane("XY")
                .cylinder(self.joint_radius * 2, self.string_hole_radius)
                .rotate((0, 0, 0), (0, 1, 0), 90)
                .translate((0, 0, stem_length / 2))
            )
        )

    def get_shape(self) -> cq.Workplane:
        """Get the entire tip."""
        return self.ball.union(self.stem.translate((0, 0, self.ball_height)))


if __name__ == "__main__":
    joint = CaneJoint()
    tip = CaneTip(joint.tube_radius)
    model = tip.get_shape()
    cq.exporters.export(model, "tip.stl")
