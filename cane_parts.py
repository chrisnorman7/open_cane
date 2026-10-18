from open_cane import CaneJoint, CaneParts

if __name__ == "__main__":
    parts = CaneParts(CaneJoint())
    model = parts.get_shape()
    model.export("cane_parts.step")
