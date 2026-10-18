from dataclasses import dataclass

import cadquery as cq

from .cane_handle import CaneHandle
from .cane_joint import CaneJoint
from .cane_tip import CaneTip


@dataclass(frozen=True)
class CaneParts:
    """A class for nesting cane parts."""

    joint: CaneJoint
    """The joint to base all dimensions around."""

    joint_count: int = 4
    """The number of joints to print."""

    def get_shape(self) -> cq.Workplane:
        """Get the shape."""
        joint = self.joint.get_shape()
        tip = CaneTip(self.joint.tube_radius)
        tip_shape = tip.get_shape()
        handle = CaneHandle(self.joint.tube_radius)
        handle_shape = handle.get_shape()
        model = joint
        modifier = (self.joint.full_radius * 2) + 1
        for n in range(self.joint_count - 1):
            x = (n + 1) * modifier
            coordinates = (x, 0, 0)
            print(f"Joint #{n + 1}: {coordinates}")
            model = model.union(joint.translate(coordinates))
        handle_width = (handle.walls_thickness + handle.joint_radius) * 2
        model = model.union(handle_shape.translate((0, modifier + handle_width, 0)))
        tip_width = max(tip.ball_radius, tip.joint_radius) * 2
        model = model.union(
            tip_shape.translate((0, modifier + handle_width + tip_width, 0))
        )
        return model
