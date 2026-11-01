from pathlib import Path
from pxr import Usd, UsdGeom, Gf

# Locate project directory
project_dir = Path(__file__).resolve().parent

# Folder containing converted USD files
input_folder = project_dir / "USD_Pushbuttons"

# Supported USD formats
extensions = {".usd", ".usda", ".usdc"}

# Find files that haven't been centered
usd_files = sorted(
    file for file in input_folder.iterdir()
    if file.is_file()
    and file.suffix.lower() in extensions
    and not file.stem.endswith("_centered")
)

print(f"Found {len(usd_files)} USD files.")

for usd_file in usd_files:

    print(f"\nProcessing: {usd_file.name}")

    try:
        # Open USD stage
        stage = Usd.Stage.Open(str(usd_file))

        if stage is None:
            raise RuntimeError("Could not open USD stage.")

        # Identify assembly root
        root = stage.GetDefaultPrim()

        if not root.IsValid():
            raise RuntimeError("No valid default prim.")

        # Calculate assembly bounding box
        bbox_cache = UsdGeom.BBoxCache(
            Usd.TimeCode.Default(),
            ["default", "render", "proxy"]
        )

        bbox = bbox_cache.ComputeWorldBound(root)
        bounds = bbox.ComputeAlignedRange()

        if bounds.IsEmpty():
            raise RuntimeError("Assembly has no visible geometry.")

        # Get geometric center
        minimum = bounds.GetMin()
        maximum = bounds.GetMax()

        center = (minimum + maximum) / 2.0

        print(f"Original center: {center}")

        # Calculate translation to origin
        translation = Gf.Vec3d(
            -center[0],
            -center[1],
            -center[2]
        )

        # Access existing assembly transforms
        xform = UsdGeom.Xformable(root)

        if not xform:
            raise RuntimeError("Assembly root is not transformable.")

        existing_ops = xform.GetOrderedXformOps()
        reset_stack = xform.GetResetXformStack()

        # Add an independent translation
        translate_op = xform.AddTranslateOp(
            precision=UsdGeom.XformOp.PrecisionDouble,
            opSuffix="alignOrigin"
        )

        translate_op.Set(translation)

        # Apply translation outside the existing transforms
        xform.SetXformOpOrder(
            [translate_op] + existing_ops,
            reset_stack
        )

        # Save a new file
        output_file = usd_file.with_name(
            f"{usd_file.stem}_centered{usd_file.suffix}"
        )

        if not stage.GetRootLayer().Export(str(output_file)):
            raise RuntimeError("Failed to export centered USD.")

        # Verify new geometric center
        check_stage = Usd.Stage.Open(str(output_file))
        check_root = check_stage.GetDefaultPrim()

        check_cache = UsdGeom.BBoxCache(
            Usd.TimeCode.Default(),
            ["default", "render", "proxy"]
        )

        new_bounds = check_cache.ComputeWorldBound(
            check_root
        ).ComputeAlignedRange()

        new_center = (
            new_bounds.GetMin() + new_bounds.GetMax()
        ) / 2.0

        print(f"New center: {new_center}")
        print(f"SUCCESS: {output_file.name}")

    except Exception as error:
        print(f"FAILED: {usd_file.name}")
        print(error)

print("\nCentering complete!")