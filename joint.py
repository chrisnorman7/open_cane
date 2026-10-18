from open_cane import CaneJoint

if __name__ == "__main__":
    joint = CaneJoint()
    joint.get_shape().export("joint.step")
