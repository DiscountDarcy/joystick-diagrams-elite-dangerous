"""Elite Dangerous XML Parser for use with Joystick Diagrams."""

import hashlib
import logging
import re
import uuid
from pathlib import Path
from typing import Union
from xml.dom import minidom

from joystick_diagrams.input.axis import Axis, AxisDirection
from joystick_diagrams.input.button import Button
from joystick_diagrams.input.hat import Hat, HatDirection
from joystick_diagrams.input.profile_collection import ProfileCollection

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

AXIS_NAME_MAP = {
    "XAxis": "X",
    "YAxis": "Y",
    "ZAxis": "Z",
    "RZAxis": "RZ",
    "RXAxis": "RX",
    "RYAxis": "RY",
}

KEYBOARD_KEY_MAP = {
    "Space": 1,
    "Return": 2,
    "Escape": 3,
    "Tab": 4,
    "Backspace": 5,
    "LeftShift": 6,
    "LeftControl": 7,
    "LeftAlt": 8,
}

FRIENDLY_NAMES = {
    "YawAxisRaw": "Yaw Axis",
    "RollAxisRaw": "Roll Axis",
    "PitchAxisRaw": "Pitch Axis",
    "LateralThrustRaw": "Lateral Thrust",
    "VerticalThrustRaw": "Vertical Thrust",
    "SetSpeed0": "Throttle 0%",
    "SetSpeed25": "Throttle 25%",
    "SetSpeed50": "Throttle 50%",
    "SetSpeed75": "Throttle 75%",
    "SetSpeed100": "Throttle 100%",
    "ThrottleAxis": "Throttle",
    "ToggleReverseThrottleInput": "Reverse Throttle",
    "PrimaryFire": "Primary Fire",
    "SecondaryFire": "Secondary Fire",
    "UseBoostJuice": "Boost Engine",
    "Supercruise": "Supercruise",
    "Hyperspace": "Jump Drive",
    "HyperSuperCombination": "Supercruise / Jump",
    "ToggleFlightAssist": "Flight Assist",
    "LandingGearToggle": "Landing Gear",
    "CargoScoop": "Cargo Scoop",
    "DeployHardpointToggle": "Deploy Hardpoints",
    "DeployHeatSink": "Heat Sink",
    "UseShieldCell": "Shield Cell",
    "FireChaffLauncher": "Chaff",
    "ChargeECM": "Charge ECM",
    "TriggerFieldNeutraliser": "Field Neutralizer",
    "SelectTarget": "Target",
    "CycleNextTarget": "Next Target",
    "CyclePreviousTarget": "Previous Target",
    "SelectHighestThreat": "Highest Threat",
    "WingNavLock": "Wing Nav Lock",
    "IncreaseEnginesPower": "Engine Power Up",
    "IncreaseWeaponsPower": "Weapon Power Up",
    "IncreaseSystemsPower": "System Power Up",
    "ResetPowerDistribution": "Reset Power",
    "UIFocus": "UI Focus",
    "GalaxyMapOpen": "Galaxy Map",
    "SystemMapOpen": "System Map",
    "HeadLookToggle": "Head Look",
    "CamPitchAxis": "Camera Pitch",
    "CamYawAxis": "Camera Yaw",
    "ToggleCargoScoop": "Cargo Scoop",
    "EjectAllCargo": "Eject Cargo",
    "MicrophoneMute": "Mute",
    "HMDReset": "HMD Reset",
    "Pause": "Pause",
    "FriendsMenu": "Friends",
    "OpenCodexGoToDiscovery": "Codex",
    "PlayerHUDModeToggle": "HUD Mode",
    "ExplorationFSSEnter": "FSS Scanner",
    "ExplorationFSSCameraPitchDecrease": "FSS Camera Pitch Down",
    "ExplorationFSSCameraYaw": "FSS Camera Yaw",
    "ExplorationFSSCameraYawIncrease": "FSS Camera Yaw Up",
    "ExplorationFSSCameraYawDecrease": "FSS Camera Yaw Down",
    "ExplorationFSSZoomIn": "FSS Zoom In",
    "ExplorationFSSZoomOut": "FSS Zoom Out",
    "ExplorationFSSMiniZoomIn": "FSS Mini Zoom In",
    "ExplorationFSSMiniZoomOut": "FSS Mini Zoom Out",
    "ExplorationFSSRadioTuningX_Raw": "FSS Radio Tuning X",
    "ExplorationFSSRadioTuningY_Raw": "FSS Radio Tuning Y",
    "ExplorationFSSRadioTuningZ_Raw": "FSS Radio Tuning Z",
    "ExplorationFSSRadioTuningW_Raw": "FSS Radio Tuning W",
    "ToggleButtonUpInput": "Toggle Button Up",
    "ToggleButtonDownInput": "Toggle Button Down",
    "ExplorationFSSShowHelp": "FSS Help",
    "UI_Up": "UI Up",
    "UI_Down": "UI Down",
    "UI_Left": "UI Left",
    "UI_Right": "UI Right",
    "UI_Select": "UI Select",
    "UI_Back": "UI Back",
    "UI_Toggle": "UI Toggle",
    "CycleNextPanel": "Next Panel",
    "CyclePreviousPanel": "Previous Panel",
    "CycleNextPage": "Next Page",
    "CyclePreviousPage": "Previous Page",
    "MouseHeadlook": "Mouse Look",
    "HeadLookReset": "Reset Head Look",
    "HeadLookPitchUp": "Head Look Up",
    "HeadLookPitchDown": "Head Look Down",
    "HeadLookYawLeft": "Head Look Left",
    "HeadLookYawRight": "Head Look Right",
    "HeadLookPitchAxis": "Head Look Pitch",
    "HeadLookYawAxis": "Head Look Yaw",
    "MotionHeadlook": "Motion Look",
    "HeadLookPitchAxisRaw": "Head Pitch Axis",
    "HeadLookYawAxisRaw": "Head Yaw Axis",
    "CamTranslateYAxis": "Camera Up/Down",
    "CamTranslateForward": "Camera Forward",
    "CamTranslateBackward": "Camera Back",
    "CamTranslateXAxis": "Camera Left/Right",
    "CamTranslateLeft": "Camera Left",
    "CamTranslateRight": "Camera Right",
    "CamTranslateZAxis": "Camera Zoom",
    "CamTranslateUp": "Camera Up",
    "CamTranslateDown": "Camera Down",
    "CamZoomAxis": "Camera Zoom",
    "CamZoomIn": "Zoom In",
    "CamZoomOut": "Zoom Out",
    "CamTranslateZHold": "Camera Z Hold",
    "GalaxyMapHome": "Galaxy Map Home",
    "ToggleDriveAssist": "Drive Assist",
    "DriveAssistDefault": "Drive Assist Default",
    "SteeringAxis": "Steering",
    "SteerLeftButton": "Steer Left",
    "SteerRightButton": "Steer Right",
    "BuggyRollAxisRaw": "SRV Roll",
    "BuggyRollLeftButton": "SRV Roll Left",
    "BuggyRollRightButton": "SRV Roll Right",
    "BuggyPitchAxis": "SRV Pitch",
    "BuggyPitchUpButton": "SRV Pitch Up",
    "BuggyPitchDownButton": "SRV Pitch Down",
    "VerticalThrustersButton": "Vertical Thrusters",
    "BuggyPrimaryFireButton": "SRV Primary Fire",
    "BuggySecondaryFireButton": "SRV Secondary Fire",
    "AutoBreakBuggyButton": "SRV Auto Brake",
    "HeadlightsBuggyButton": "SRV Headlights",
    "ToggleBuggyTurretButton": "SRV Turret",
    "BuggyCycleFireGroupNext": "SRV Next Fire Group",
    "BuggyCycleFireGroupPrevious": "SRV Previous Fire Group",
    "SelectTarget_Buggy": "SRV Target",
    "BuggyTurretYawAxisRaw": "SRV Turret Yaw",
    "BuggyTurretYawLeftButton": "SRV Turret Left",
    "BuggyTurretYawRightButton": "SRV Turret Right",
    "BuggyTurretPitchAxisRaw": "SRV Turret Pitch",
    "BuggyTurretPitchUpButton": "SRV Turret Up",
    "BuggyTurretPitchDownButton": "SRV Turret Down",
    "BuggyTurretMouseSensitivity": "SRV Turret Mouse Sensitivity",
    "BuggyTurretMouseDeadzone": "SRV Turret Mouse Deadzone",
    "DriveSpeedAxis": "SRV Speed",
    "BuggyThrottleRange": "SRV Throttle Range",
    "BuggyToggleReverseThrottleInput": "SRV Reverse Throttle",
    "IncreaseSpeedButtonMax": "SRV Max Speed",
    "DecreaseSpeedButtonMax": "SRV Min Speed",
    "ToggleCargoScoop_Buggy": "SRV Cargo Scoop",
    "EjectAllCargo_Buggy": "SRV Eject Cargo",
    "RecallDismissShip": "Recall Ship",
    "UIFocus_Buggy": "SRV UI Focus",
    "FocusLeftPanel_Buggy": "SRV Left Panel",
    "FocusCommsPanel_Buggy": "SRV Comms",
    "QuickCommsPanel_Buggy": "SRV Quick Comms",
    "FocusRadarPanel_Buggy": "SRV Radar",
    "FocusRightPanel_Buggy": "SRV Right Panel",
    "GalaxyMapOpen_Buggy": "SRV Galaxy Map",
    "SystemMapOpen_Buggy": "SRV System Map",
    "OpenCodexGoToDiscovery_Buggy": "SRV Codex",
    "PlayerHUDModeToggle_Buggy": "SRV HUD Mode",
    "HeadLookToggle_Buggy": "SRV Head Look",
    "HumanoidForwardAxis": "Forward",
    "HumanoidForwardButton": "Forward",
    "HumanoidBackwardButton": "Backward",
    "HumanoidStrafeAxis": "Strafe",
    "HumanoidStrafeLeftButton": "Strafe Left",
    "HumanoidStrafeRightButton": "Strafe Right",
    "HumanoidRotateAxis": "Rotate",
    "HumanoidRotateLeftButton": "Turn Left",
    "HumanoidRotateRightButton": "Turn Right",
    "HumanoidPitchAxis": "Look Up/Down",
    "HumanoidPitchUpButton": "Look Up",
    "HumanoidPitchDownButton": "Look Down",
    "HumanoidSprintButton": "Sprint",
    "HumanoidWalkButton": "Walk",
    "HumanoidCrouchButton": "Crouch",
    "HumanoidJumpButton": "Jump",
    "HumanoidPrimaryInteractButton": "Primary Interact",
    "HumanoidSecondaryInteractButton": "Secondary Interact",
    "HumanoidItemWheelButton": "Item Wheel",
    "HumanoidEmoteWheelButton": "Emote Wheel",
    "HumanoidUtilityWheelCycleMode": "Utility Wheel",
    "HumanoidItemWheelButton_XAxis": "Item Wheel X",
    "HumanoidItemWheelButton_YAxis": "Item Wheel Y",
    "HumanoidPrimaryFireButton": "Primary Fire",
    "HumanoidZoomButton": "Zoom",
    "HumanoidThrowGrenadeButton": "Throw Grenade",
    "HumanoidMeleeButton": "Melee",
    "HumanoidReloadButton": "Reload",
    "HumanoidSwitchWeapon": "Switch Weapon",
    "HumanoidSelectPrimaryWeaponButton": "Primary Weapon",
    "HumanoidSelectSecondaryWeaponButton": "Secondary Weapon",
    "HumanoidSelectUtilityWeaponButton": "Utility Weapon",
    "HumanoidSelectNextWeaponButton": "Next Weapon",
    "HumanoidSelectPreviousWeaponButton": "Previous Weapon",
    "HumanoidHideWeaponButton": "Hide Weapon",
    "HumanoidSelectNextGrenadeTypeButton": "Next Grenade",
    "HumanoidSelectPreviousGrenadeTypeButton": "Previous Grenade",
    "HumanoidToggleFlashlightButton": "Flashlight",
    "HumanoidToggleNightVisionButton": "Night Vision",
    "HumanoidToggleShieldsButton": "Shields",
    "HumanoidClearAuthorityLevel": "Clear Authority",
    "HumanoidHealthPack": "Health Pack",
    "HumanoidBattery": "Battery",
    "HumanoidSelectFragGrenade": "Frag Grenade",
    "HumanoidSelectEMPGrenade": "EMP Grenade",
    "HumanoidSelectShieldGrenade": "Shield Grenade",
    "HumanoidSwitchToRechargeTool": "Recharge Tool",
    "HumanoidSwitchToCompAnalyser": "Composition Analyzer",
    "HumanoidSwitchToSuitTool": "Suit Tool",
    "HumanoidToggleToolModeButton": "Tool Mode",
    "HumanoidPing": "Ping",
    "HumanoidOpenAccessPanelButton": "Access Panel",
    "HumanoidConflictContextualUIButton": "Contextual UI",
    "HumanoidEmoteSlot1": "Emote 1",
    "HumanoidEmoteSlot2": "Emote 2",
    "HumanoidEmoteSlot3": "Emote 3",
    "HumanoidEmoteSlot4": "Emote 4",
    "HumanoidEmoteSlot5": "Emote 5",
    "HumanoidEmoteSlot6": "Emote 6",
    "HumanoidEmoteSlot7": "Emote 7",
    "HumanoidEmoteSlot8": "Emote 8",
    "TargetWingman0": "Target Wingman 1",
    "TargetWingman1": "Target Wingman 2",
    "TargetWingman2": "Target Wingman 3",
    "SelectTargetsTarget": "Target's Target",
    "ShipSpotLightToggle": "Ship Lights",
}

_GENERAL_BINDING_PREFIXES = [
    "UI",
    "Focus",
    "GalaxyMap",
    "SystemMap",
    "Codex",
    "FriendsMenu",
    "CycleNextPanel",
    "CyclePreviousPanel",
    "CycleNextPage",
    "CyclePreviousPage",
    "QuickCommsPanel",
    "PlayerHUDModeToggle",
    "ShowPGScoreSummaryInput",
    "CamPitch",
    "CamYaw",
    "CamTranslate",
    "CamZoom",
    "CamTranslateZHold",
    "HeadLook",
    "MouseHeadlook",
    "MotionHeadlook",
    "PitchCamera",
    "YawCamera",
    "RollCamera",
    "Pause",
    "HMDReset",
    "MicrophoneMute",
    "PhotoCamera",
    "VanityCamera",
    "FreeCam",
    "MoveFreeCam",
    "ToggleRotationLock",
    "FixCameraRelativeToggle",
    "FixCameraWorldToggle",
    "QuitCamera",
    "ToggleAdvanceMode",
    "FreeCamZoom",
    "FStop",
    "CommanderCreator",
    "GalnetAudio",
    "GalaxyMapHome",
    "MultiCrew",
    "Order",
    "OpenCodexGoToDiscovery",
    "UseBoostJuice",
    "Supercruise",
    "Hyperspace",
    "ToggleDriveAssist",
]


class EliteDangerous:
    """Parser for Elite Dangerous .binds XML files."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.data = self._load_file()
        self.devices: dict = {}
        self.device_guid_map: dict[str, str] = {}

    # ------------------------------------------------------------------
    # File loading & validation
    # ------------------------------------------------------------------

    def _load_file(self) -> str:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if self.file_path.suffix != ".binds":
            raise Exception("File must be a .binds file")
        data = self.file_path.read_text(encoding="utf-8")
        try:
            self._validate_file(data)
        except ValueError as e:
            raise Exception("File is not a valid Elite Dangerous XML") from e
        return data

    @staticmethod
    def _validate_file(data: str) -> bool:
        parsed_xml = minidom.parseString(data)
        root = parsed_xml.documentElement
        if root.tagName == "Root" and root.hasAttribute("PresetName"):
            return True
        raise Exception("File is not a valid Elite Dangerous bindings file")

    # ------------------------------------------------------------------
    # XML helpers
    # ------------------------------------------------------------------

    @staticmethod
    def parse_file_data(data: str):
        return minidom.parseString(data)

    @staticmethod
    def parse_binding_element(element) -> tuple[str, str] | None:
        """Parse a binding element and return (device, key) or None."""
        device = element.getAttribute("Device")
        key = element.getAttribute("Key")
        if not device or not key or device == "{NoDevice}":
            return None
        return (device, key)

    # ------------------------------------------------------------------
    # Device GUID resolution
    # ------------------------------------------------------------------

    def get_device_guid(self, device_name: str) -> str:
        """Get or create a deterministic GUID for a device name."""
        if device_name not in self.device_guid_map:
            self.device_guid_map[device_name] = str(
                uuid.uuid5(uuid.NAMESPACE_DNS, f"ed-device-{device_name}")
            )
        return self.device_guid_map[device_name]

    def resolve_input(
        self, device_name: str, key: str
    ) -> tuple[str, Union[Axis, Button, Hat, None]] | None:
        """Resolve a device/key combination to (device_guid, input_control)."""
        if not device_name or not key:
            return None
        device_guid = self.get_device_guid(device_name)
        input_control = self.parse_key(key)
        if not input_control:
            _logger.warning("Could not parse key: %s", key)
            return None
        return (device_guid, input_control)

    # ------------------------------------------------------------------
    # Key parsing (dispatcher + focused helpers)
    # ------------------------------------------------------------------

    def parse_key(self, key: str) -> Union[Axis, Button, Hat, None]:
        """Parse an Elite Dangerous key string into an input control."""
        key = key.strip()

        # Directional joystick axes: Pos_Joy_RXAxis / Neg_Joy_RYAxis
        if key.startswith(("Pos_Joy_", "Neg_Joy_")):
            axis_name = key[key.find("Joy_") + 4 :]
            return self._resolve_axis(axis_name)

        # Numbered joystick buttons: Joy_1, Joy_23, ...
        if key.startswith("Joy_") and key[4:].isdigit():
            return Button(int(key[4:]))

        # Named joystick inputs: Joy_XAxis, Joy_POV1Up, Joy_Hat1Left, ...
        if key.startswith("Joy_"):
            return self._parse_joy_input(key[4:])

        # Keyboard keys: Key_Space, Key_A, ...
        if key.startswith("Key_"):
            return self._resolve_keyboard_key(key[4:])

        # Mouse buttons: Mouse_1, Mouse_2, ...
        if key.startswith("Mouse_") and key[6:].isdigit():
            return Button(int(key[6:]))

        # Mouse wheel
        if key in ("Pos_Mouse_ZAxis", "Neg_Mouse_ZAxis"):
            return Button(4 if key == "Pos_Mouse_ZAxis" else 5)

        _logger.warning("Unrecognized key format: %s", key)
        return None

    @staticmethod
    def _resolve_axis(axis_name: str) -> Axis | None:
        """Map an Elite axis name (XAxis, RZAxis, ...) to an Axis object."""
        if axis_name in AXIS_NAME_MAP:
            return Axis(AxisDirection[AXIS_NAME_MAP[axis_name]])
        return None

    def _parse_joy_input(self, axis_part: str) -> Axis | Hat | None:
        """Parse a Joy_ suffix that may be an axis or POV hat."""
        if axis_part in AXIS_NAME_MAP:
            return Axis(AxisDirection[AXIS_NAME_MAP[axis_part]])

        if axis_part.startswith("POV") or "Hat" in axis_part:
            return self._resolve_hat_direction(axis_part)

        return None

    @staticmethod
    def _resolve_hat_direction(axis_part: str) -> Hat | None:
        """Resolve a POV/Hat direction suffix to a Hat object."""
        direction_map = {
            "Up": HatDirection.U,
            "Down": HatDirection.D,
            "Left": HatDirection.L,
            "Right": HatDirection.R,
        }
        for suffix, direction in direction_map.items():
            if axis_part.endswith(suffix):
                return Hat(1, direction)
        return None

    @staticmethod
    def _resolve_keyboard_key(key_name: str) -> Button:
        """Map a keyboard key name to a deterministic Button ID."""
        button_id = KEYBOARD_KEY_MAP.get(key_name)
        if button_id is None:
            digest = hashlib.md5(key_name.encode()).hexdigest()
            button_id = int(digest, 16) % 1000 + 100
        return Button(button_id)

    # ------------------------------------------------------------------
    # Friendly name resolution
    # ------------------------------------------------------------------

    @staticmethod
    def get_human_readable_name(binding_name: str) -> str:
        """Convert a binding name to a human-readable label."""
        if binding_name in FRIENDLY_NAMES:
            return FRIENDLY_NAMES[binding_name]

        # Automatic formatting fallback
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", binding_name)
        name = re.sub(r"([a-zA-Z])([A-Z][a-z])", r"\1 \2", name)
        name = re.sub(r"\s+Button$", "", name)
        return name.strip().title()

    # ------------------------------------------------------------------
    # Binding classification
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_binding(binding_name: str) -> tuple[str, str]:
        """Classify a binding element name into (scheme, clean_name)."""
        if binding_name.endswith("_Landing"):
            return ("Flight", binding_name[:-8])
        if binding_name.endswith("_Buggy"):
            return ("SRV", binding_name[:-6])
        if binding_name.endswith("_Humanoid"):
            return ("On Foot", binding_name[:-9])
        if binding_name.startswith("Humanoid"):
            return ("On Foot", binding_name[8:])
        if binding_name.startswith("Buggy"):
            return ("SRV", binding_name[6:])
        if "Buggy" in binding_name:
            return ("SRV", binding_name)
        if any(binding_name.startswith(p) for p in _GENERAL_BINDING_PREFIXES):
            return ("General", binding_name)
        return ("Flight", binding_name)

    # ------------------------------------------------------------------
    # Main parse entry point
    # ------------------------------------------------------------------

    def parse(self) -> ProfileCollection:
        """Parse the Elite Dangerous bindings file and return a ProfileCollection."""
        root = self.parse_file_data(self.data).documentElement
        profile_collection = ProfileCollection()

        control_schemes: dict[str, list[dict]] = {
            "Flight": [],
            "Landing": [],
            "SRV": [],
            "On Foot": [],
            "General": [],
        }

        for child in root.childNodes:
            if (
                child.nodeType != child.ELEMENT_NODE
                or child.tagName == "KeyboardLayout"
            ):
                continue

            scheme, clean_name = self._classify_binding(child.tagName)
            human_name = self.get_human_readable_name(clean_name)

            for elem in self._iter_binding_elements(child):
                binding_info = self.parse_binding_element(elem)
                if not binding_info:
                    continue
                device_name, key = binding_info
                resolved = self.resolve_input(device_name, key)
                if not resolved:
                    continue
                device_guid, input_control = resolved
                control_schemes[scheme].append(
                    {
                        "device_guid": device_guid,
                        "device_name": device_name,
                        "input_control": input_control,
                        "human_name": human_name,
                    }
                )

        self._build_profiles(profile_collection, control_schemes)
        return profile_collection

    @staticmethod
    def _iter_binding_elements(parent):
        """Yield Primary, Secondary, and Binding child elements from an XML node."""
        for subchild in parent.childNodes:
            if subchild.nodeType == subchild.ELEMENT_NODE and subchild.tagName in (
                "Primary",
                "Secondary",
                "Binding",
            ):
                yield subchild

    @staticmethod
    def _build_profiles(
        profile_collection: ProfileCollection,
        control_schemes: dict[str, list[dict]],
    ) -> None:
        """Populate a ProfileCollection from classified binding data."""
        for scheme_name, bindings in control_schemes.items():
            if not bindings:
                continue
            profile_obj = profile_collection.create_profile(scheme_name)
            for binding in bindings:
                device_obj = profile_obj.add_device(
                    binding["device_guid"], binding["device_name"]
                )
                if device_obj and binding["input_control"]:
                    device_obj.create_input(
                        binding["input_control"], binding["human_name"]
                    )


if __name__ == "__main__":
    pass
