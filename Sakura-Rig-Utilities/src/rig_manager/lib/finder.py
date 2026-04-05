import os
import bpy

class RigFinder:
    def __init__(self, addon_dir: str):
        self.addon_dir = os.path.abspath(addon_dir)
        self.rig_data = [] # List of dicts: {"name": str, "filepath": str}
        self.sacr_dir = os.path.join(self.addon_dir, "sacr")

    def scan_for_rigs(self):
        self.rig_data = []
        
        # 1. Scan the root addon directory for .blend files
        if not os.path.isdir(self.addon_dir):
            return

        blend_files = [f for f in os.listdir(self.addon_dir) if f.endswith('.blend')]
        for blend_file in blend_files:
            blend_path = os.path.join(self.addon_dir, blend_file)
            self._process_blend_file(blend_path)
            
        # 2. Scan sacr/ subdirectory for versioned .blend files
        if os.path.isdir(self.sacr_dir):
            for version in os.listdir(self.sacr_dir):
                version_dir = os.path.join(self.sacr_dir, version)
                if not os.path.isdir(version_dir):
                    continue
                
                version_blends = [f for f in os.listdir(version_dir) if f.endswith('.blend')]
                for blend_file in version_blends:
                    blend_path = os.path.join(version_dir, blend_file)
                    self._process_blend_file(blend_path)

    def _process_blend_file(self, blend_path):
        asset_collections = self.get_rig_assets(blend_path)
        existing_names = [r["name"] for r in self.rig_data]
        for col_name in asset_collections:
            if "SACR" in col_name and col_name not in existing_names:
                self.rig_data.append({"name": col_name, "filepath": blend_path})

    @staticmethod
    def append_rig(rig_item):
        """Append the selected rig collection from its source file."""
        import os
        import bpy
        
        filepath = os.path.abspath(rig_item.filepath)
        rig_name = rig_item.name
        
        if not os.path.exists(filepath):
            # Try to see if it's a relative path from addon_dir
            from ...preferences import get_preferences
            prefs = get_preferences()
            alt_path = os.path.abspath(os.path.join(prefs.addon_directory, rig_item.filepath))
            if os.path.exists(alt_path):
                filepath = alt_path
            else:
                return False, f"Source file not found: {filepath}"

        # To append a collection, we use bpy.ops.wm.append or bpy.data.libraries.load
        # Using libraries.load allows more control, but wm.append is simpler for operators
        
        # We need the directory inside the blend file
        directory = os.path.join(filepath, "Collection")
        inner_filepath = os.path.join(directory, rig_name)
        
        try:
            bpy.ops.wm.append(
                filepath=inner_filepath,
                directory=directory,
                filename=rig_name
            )
            return True, f"Appended rig: {rig_name}"
        except Exception as e:
            return False, f"Failed to append: {str(e)}"

    def get_rig_assets(self, file):
        if file == bpy.data.filepath:
            return [c.name for c in bpy.data.collections if c.asset_data]

        # Only load names of data-blocks marked as assets
        with bpy.data.libraries.load(file, assets_only=True) as (data_from, _):
            return list(data_from.collections)

    def is_rig_asset(self, file, rig_name):
        """Check if a specific rig collection in a blend file is marked as an asset."""
        if file == bpy.data.filepath:
            col = bpy.data.collections.get(rig_name)
            return col is not None and col.asset_data is not None

        with bpy.data.libraries.load(file, assets_only=True) as (data_from, _):
            return rig_name in data_from.collections
