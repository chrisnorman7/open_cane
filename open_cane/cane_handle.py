from dataclasses import dataclass

import cadquery as cq
from braille import BrailleLine

from open_cane.cane_joint import CaneJoint


@dataclass(frozen=True)
class CaneHandle:
    """The handle of the cane."""

    joint_radius: float
    """The radius of the female joint."""

    joint_length: float = 40
    """The length of the female join."""
    handle_length: float = 190
    """The length of the handle."""

    top_thickness: float = 20
    """How much material will make up the top of the handle."""

    walls_thickness: float = 3
    """The thickness of the walls."""

    string_hole_radius: float = 5
    """The radius for the top hole which the string will pass through."""

    braille_text: str | None = "⠠⠕⠏⠢⠀⠠⠉⠁⠝⠑"
    """The braille to render on the handle."""

    @property
    def braille(self) -> cq.Compound | None:
        """The braille to add to the handle."""
        text = self.braille_text
        if text is None:
            return None
        return BrailleLine(line=text).get_shape()

    def get_shape(self) -> cq.Workplane:
        """Get the shape of the handle."""
        height = self.handle_length + self.joint_length + self.top_thickness
        cross_section = self.walls_thickness + self.joint_radius
        box_y = cross_section * 2
        cylinder = cq.Workplane("XY").cylinder(
            height, cross_section, centered=(True, True, False)
        )
        box = cq.Workplane("XY").box(
            height, box_y, cross_section, centered=(False, True, False)
        )
        box = box.rotate((0, 0, 0), (0, 1, 0), 270)
        cylinder = cylinder.union(box)
        # An exact-radius fillet degenerates at the top face.
        cylinder = cylinder.edges(">Z").fillet(cross_section * 0.999)
        braille = self.braille
        if braille is not None:
            bounds = braille.BoundingBox()
            if bounds.xlen > height or bounds.ylen > box_y:
                raise RuntimeError(
                    f"Braille text ({bounds.xlen} x {bounds.ylen}) does not fit on the handle ({height} x {box_y})."
                )
            center_x = (bounds.xmin + bounds.xmax) / 2
            center_y = (bounds.ymin + bounds.ymax) / 2
            braille = braille.rotate((0, 0, 0), (0, 1, 0), 270)
            rotated_bounds = braille.BoundingBox()
            braille = braille.translate(
                (
                    -cross_section - rotated_bounds.xmax,
                    -center_y,
                    height / 2 - center_x,
                )
            )
            cylinder = cylinder.union(braille)
        middle = (
            cq.Workplane("XY")
            .cylinder(
                self.joint_length,
                self.joint_length,
                centered=(True, True, False),
            )
            .union(
                cq.Workplane("XY").cylinder(
                    height, self.string_hole_radius, centered=(True, True, False)
                )
            )
        )
        return cylinder.cut(middle)


if __name__ == "__main__":
    joint = CaneJoint()
    handle = CaneHandle(joint.tube_radius, joint_length=joint.female_length)
    model = handle.get_shape()
    cq.exporters.export(model, "handle.stl")
