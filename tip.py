import cadquery as cq

from open_cane import CaneJoint, CaneTip

if __name__ == "__main__":
    joint = CaneJoint()
    tip = CaneTip(joint.tube_radius, joint_length=10, ball_height=15)
    model = tip.get_shape()
    cq.exporters.export(model, "tip.stl")
