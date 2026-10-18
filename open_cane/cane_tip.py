from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class CaneTip:
    """The tip of the cane."""

    joint_radius: float
    """The radius of the female joint."""

    joint_length: float = 40
    """The length of the female joint."""

    string_hole_radius: float = 2.5
    """The radius for the top hole which the string will pass through."""

    stem_difference: float = 2
    """How much to subtract from `joint_radius` when making the stem."""

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
            .cylinder(self.ball_height, self.ball_radius, centered=(True, True, False))
            .edges("<Z or >Z")
            .fillet(self.ball_fillet)
        )

    @property
    def stem(self) -> cq.Workplane:
        """The stem of the tip."""
        half = self.joint_length / 2
        top = (
            cq.Workplane("XY")
            .cylinder(
                half,
                self.joint_radius - self.stem_difference,
                centered=(True, True, False),
            )
            .cut(
                cq.Workplane("XY")
                .cylinder(self.joint_radius * 2, self.string_hole_radius)
                .rotate((0, 0, 0), (0, 1, 0), 90)
                .translate((0, 0, half / 2))
            )
        ).translate((0, 0, half))
        bottom = cq.Workplane("XY").cylinder(
            half, self.joint_radius, centered=(True, True, False)
        )
        return bottom.union(top)

    def get_shape(self) -> cq.Workplane:
        """Get the entire tip."""
        return self.ball.union(self.stem.translate((0, 0, self.ball_height)))
