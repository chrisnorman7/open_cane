from open_cane import CaneHandle, CaneJoint

if __name__ == "__main__":
    joint = CaneJoint()
    handle = CaneHandle(joint.tube_radius, joint_length=joint.female_length)
    model = handle.get_shape()
    model.export("handle.step")
