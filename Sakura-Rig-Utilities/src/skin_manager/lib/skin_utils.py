from base64 import b64decode
import json
from urllib import request, error
from pathlib import Path
from .utils import lookup_name, is_packed, file_exists
from ...preferences import get_preferences
import bpy

class SkinUtils:
    def __init__(self, name: str):
        self.name = name
        self.prefs = get_preferences()
        self.moj_api = {
            "api": "https://api.mojang.com/users/profiles/minecraft/",
            "profile": "https://sessionserver.mojang.com/session/minecraft/profile/",
            "textures": "https://textures.minecraft.net/texture/",
        }

    def _get_uuid(self):
        name = self.name

        try:
            url = self.moj_api["api"] + name
            return json.loads(request.urlopen(url).read())["id"]
        except (request.HTTPError, error.URLError):
            return "http_error"

    def _is_cached(self):
        return file_exists(f"{self.prefs.addon_directory}/skins/{self.name}/{self.name}.json")

    def _retrieve_full_profile(self):
        uuid = self._get_uuid()
        if uuid == "http_error":
            return "http_error"
        try:
            url = self.moj_api["profile"] + uuid
            response = request.urlopen(url).read()
            profile = json.loads(response)

            # Extract the base64 encoded value from the first property
            if "properties" in profile and len(profile["properties"]) > 0:
                value_encoded = profile["properties"][0]["value"]
                # Decode base64 and parse as JSON
                value_decoded_bytes = b64decode(value_encoded)
                value_decoded_json = json.loads(value_decoded_bytes.decode("utf-8"))
                # Store it back as raw json in the 'value' key
                profile["properties"][0]["value"] = value_decoded_json

            return profile

        except (request.HTTPError, error.URLError, KeyError, IndexError, json.JSONDecodeError):
            return 'http_error'

    @staticmethod
    def _compare_hashes(self, old_skin_hash, skin_hash):
        if old_skin_hash and skin_hash:
            return old_skin_hash == skin_hash
        return False

    def write_new_cache(self):
        print("Writing new skin cache...")
        
        profile_large = self._retrieve_full_profile()
        if profile_large == 'http_error':
            return 'http_error'

        print(f"Retrieved profile for {profile_large['name']}")

        textures = profile_large["properties"][0]["value"]['textures']
        CURRENT_SKIN_URL = textures['SKIN']['url']
        CURRENT_SKIN_HASH = CURRENT_SKIN_URL.split("/")[-1]
        
        try:
            model = textures['SKIN']['metadata']['model']
        except KeyError:
            model = "default"

        TARGET_DIR = Path(f"{self.prefs.addon_directory}/skins/{self.name}")
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

        DOWNLOAD_PATH = TARGET_DIR / f"{CURRENT_SKIN_HASH}.png"
        
        # Download skin if not exists
        if not DOWNLOAD_PATH.exists():
            with request.urlopen(CURRENT_SKIN_URL) as response, open(DOWNLOAD_PATH, 'wb') as out_file:
                out_file.write(response.read())
            print(f"Downloaded skin to {DOWNLOAD_PATH}")

        # Check for Cape
        CAPE_URL = None
        CAPE_PATH = None
        if 'CAPE' in textures:
            CAPE_URL = textures['CAPE']['url']
            CAPE_HASH = CAPE_URL.split("/")[-1]
            CAPE_PATH = str(TARGET_DIR / f"{CAPE_HASH}.png")
            if not Path(CAPE_PATH).exists():
                with request.urlopen(CAPE_URL) as response, open(CAPE_PATH, 'wb') as out_file:
                    out_file.write(response.read())

        JSON_FILE = TARGET_DIR / f"{self.name}.json"
        if JSON_FILE.exists():
            with open(JSON_FILE, "r") as f:
                profile = json.load(f)
        else:
            profile = {
                "UUID": profile_large["id"],
                "NAME": profile_large["name"],
                "SKINS": []
            }

        # Add skin to list if not already there
        skin_exists = False
        for s in profile["SKINS"]:
            if s.get("hash") == CURRENT_SKIN_HASH:
                skin_exists = True
                break
        
        if not skin_exists:
            profile["SKINS"].append({
                "index": len(profile["SKINS"]),
                "url": CURRENT_SKIN_URL,
                "hash": CURRENT_SKIN_HASH,
                "path": str(DOWNLOAD_PATH),
                "model": "1" if model == "slim" else "0",
                "cape_url": CAPE_URL,
                "cape_path": CAPE_PATH
            })

        with open(JSON_FILE, "w") as f:
            json.dump(profile, f, indent=4)

        return 'complete'

    def add_skin(self):
        print(f"Adding skin for {self.name}...")

        profile_large = self._retrieve_full_profile()
        if profile_large == 'http_error':
            return 'http_error'

        textures = profile_large["properties"][0]["value"]['textures']
        CURRENT_SKIN_URL = textures['SKIN']['url']
        CURRENT_SKIN_HASH = CURRENT_SKIN_URL.split("/")[-1]

        try:
            model = textures['SKIN']['metadata']['model']
        except KeyError:
            model = "default"

        TARGET_DIR = Path(f"{self.prefs.addon_directory}/skins/{self.name}")
        JSON_FILE = TARGET_DIR / f"{self.name}.json"

        if not JSON_FILE.exists():
            # If no cache exists, just use write_new_cache
            return self.write_new_cache()

        with open(JSON_FILE, "r") as f:
            profile = json.load(f)

        # Check if the current skin is already in the list
        for s in profile.get("SKINS", []):
            if s.get("hash") == CURRENT_SKIN_HASH:
                return 'already_cached'

        # Download new skin
        DOWNLOAD_PATH = TARGET_DIR / f"{CURRENT_SKIN_HASH}.png"
        if not DOWNLOAD_PATH.exists():
            with request.urlopen(CURRENT_SKIN_URL) as response, open(DOWNLOAD_PATH, 'wb') as out_file:
                out_file.write(response.read())

        # Check for Cape
        CAPE_URL = None
        CAPE_PATH = None
        if 'CAPE' in textures:
            CAPE_URL = textures['CAPE']['url']
            CAPE_HASH = CAPE_URL.split("/")[-1]
            CAPE_PATH = str(TARGET_DIR / f"{CAPE_HASH}.png")
            if not Path(CAPE_PATH).exists():
                with request.urlopen(CAPE_URL) as response, open(CAPE_PATH, 'wb') as out_file:
                    out_file.write(response.read())

        # Add skin to list
        profile["SKINS"].append({
            "index": len(profile["SKINS"]),
            "url": CURRENT_SKIN_URL,
            "hash": CURRENT_SKIN_HASH,
            "path": str(DOWNLOAD_PATH),
            "model": "1" if model == "slim" else "0",
            "cape_url": CAPE_URL,
            "cape_path": CAPE_PATH
        })

        with open(JSON_FILE, "w") as f:
            json.dump(profile, f, indent=4)

        return 'complete'

    def delete_player(self):
        import shutil
        TARGET_DIR = Path(f"{self.prefs.addon_directory}/skins/{self.name}")
        if TARGET_DIR.exists():
            shutil.rmtree(TARGET_DIR)
            return 'complete'
        return 'not_found'

    def get_skin_path(self, skin_index: int):
        JSON_FILE = Path(f"{self.prefs.addon_directory}/skins/{self.name}/{self.name}.json")
        if not JSON_FILE.exists():
            return None

        try:
            with open(JSON_FILE, 'r') as f:
                data = json.load(f)
                skins = data.get("SKINS", [])
                target_skin = next((s for s in skins if s.get("index") == skin_index), None)
                if target_skin and "path" in target_skin:
                    return Path(target_skin["path"])
        except:
            pass
        return None

    def delete_skin(self, skin_index: int):
        JSON_FILE = Path(f"{self.prefs.addon_directory}/skins/{self.name}/{self.name}.json")
        if not JSON_FILE.exists():
            return 'not_found'

        with open(JSON_FILE, "r") as f:
            profile = json.load(f)

        if 0 <= skin_index < len(profile["SKINS"]):
            skin = profile["SKINS"].pop(skin_index)
            
            # Delete skin file
            skin_path = Path(skin.get("path", ""))
            if skin_path.exists():
                skin_path.unlink()
            
            # Delete cape file if it's not used by other skins (though currently each skin has its own CAPE_PATH in this impl)
            cape_path = Path(skin.get("cape_path", ""))
            if cape_path.exists():
                # Check if other skins use this cape path before deleting? 
                # Actually write_new_cache creates unique paths per hash, but here we just delete.
                cape_path.unlink()

            # Re-index remaining skins
            for i, s in enumerate(profile["SKINS"]):
                s["index"] = i

            with open(JSON_FILE, "w") as f:
                json.dump(profile, f, indent=4)
            
            return 'complete'
        
        return 'not_found'

    def apply_skin(self, rig, skin_item):
        """Apply skin to the rig based on skin_item and SkinUtils instance."""
        import os

        utility_bone_name = "Sedaia.Skin_Utility_Config"
        if utility_bone_name not in rig.pose.bones:
            return False, f"Utility bone '{utility_bone_name}' not found on rig."

        try:
            skin_index = int(skin_item.skin_texture_enum)
        except ValueError:
            return False, "Invalid skin selection."

        JSON_FILE = Path(skin_item.json_path)
        if not JSON_FILE.exists():
            return False, f"Metadata not found: {skin_item.json_path}"

        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        
        skin_data = next((s for s in data.get("SKINS", []) if s.get("index") == skin_index), None)
        if not skin_data:
            return False, "Skin texture data not found."

        skinMeta = rig.pose.bones[utility_bone_name]
        
        # Metadata from bone
        mat_obj_query = skinMeta.get("MatObj")
        skin_img_node_id = skinMeta.get("SkinImageNodeID")
        arm_prop_name = skinMeta.get("ArmPropName")
        arm_prop_bone_name = skinMeta.get("ArmPropBone")
        rig_name_suffix = skinMeta.get("RigName", "Rig")

        # Find Material Handler (child object)
        material_manager = lookup_name(bl_list=rig.children, query=mat_obj_query)
        if not material_manager:
            return False, f"Material object '{mat_obj_query}' not found."
        
        # Update texture
        if material_manager.material_slots:
            mat = material_manager.material_slots[0].material
            if mat and mat.use_nodes:
                nodes = mat.node_tree.nodes
                if skin_img_node_id in nodes:
                    node = nodes[skin_img_node_id]
                    if node.type == 'TEX_IMAGE':
                        # Load image
                        img_path = skin_data["path"]
                        img_name = os.path.basename(img_path)
                        
                        if img_name in bpy.data.images:
                            img = bpy.data.images[img_name]
                        else:
                            img = bpy.data.images.load(img_path)
                        
                        if is_packed(img):
                            img.unpack(method="USE_LOCAL")
                        
                        node.image = img
                        img.pack()
        
        # Sync Arms
        if skin_item.sync_arms and arm_prop_bone_name in rig.pose.bones:
            arm_bone = rig.pose.bones[arm_prop_bone_name]
            model_val = int(skin_data["model"]) # "0" for default, "1" for slim
            try:
                arm_bone[arm_prop_name] = model_val
            except:
                pass
        
        # Sync Name
        if skin_item.sync_name:
            new_name = f"{skin_item.name} - {rig_name_suffix}"
            rig.name = new_name
            rig.data.name = new_name
            rig.data["Rig Name"] = new_name

        return True, f"Applied skin: {skin_item.name} (Texture {skin_index})"

    @staticmethod
    def get_all_skins(addon_directory):
        skins = []
        skins_dir = Path(addon_directory) / "skins"
        if not skins_dir.exists():
            return skins
        
        for folder in skins_dir.iterdir():
            if folder.is_dir():
                json_file = folder / f"{folder.name}.json"
                if json_file.exists():
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            skins.append({
                                "name": data.get("NAME", folder.name),
                                "uuid": data.get("UUID", ""),
                                "json_path": str(json_file)
                            })
                    except:
                        continue
        return skins
