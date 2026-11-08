"""Sync the player named on the rig from Mojang, then apply their current skin.

Run from the UI (``INVOKE_DEFAULT``), the sync runs on a worker thread while a
modal operator keeps Blender responsive, shows progress in the status bar and
the Skin Manager panel, and lets Esc cancel. Run from a script
(``EXEC_DEFAULT``) or in background mode, which has no window event loop to
drive a modal operator, it blocks until done.
"""

import asyncio

import bpy
import bpy.types as T

from ....core.background import BackgroundTask
from ....core.skin_manager import SyncCancelledError, SyncResult, sync_progress
from ....core.skin_targets import registry as skin_targets
from .base import OFFLINE_MESSAGE, REPORTED_ERRORS, SkinOperator, build_manager, call_operator
from .constants import OperatorID

# How often, in seconds, the modal operator checks the worker for progress.
POLL_INTERVAL = 0.1


def redraw_skin_ui(context) -> None:
    """Redraw the 3D Viewports, whose sidebar holds the Skin Manager panel."""
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


class SkinAdd(SkinOperator, T.Operator):
    """Check Mojang for the player's current skin, download it if it is new, and apply it"""

    bl_idname = OperatorID.ADD
    bl_label = "Check for New Skin"
    bl_options = {"REGISTER", "UNDO"}

    blocked_while_syncing = True

    # Plain attributes, not annotations: Blender reads class annotations as
    # operator properties. `_task` holds a `BackgroundTask[SyncResult]`.
    _timer = None
    _task = None
    _rig_name = ""
    _username = ""

    def prepare(self, context) -> str | None:
        """Check Online Access, the rig, and the username. Return the username, or `None` after reporting."""
        if not bpy.app.online_access:
            self.report({"ERROR"}, OFFLINE_MESSAGE)
            return None
        found = self.rig_target(context)
        if found is None:
            return None
        self._rig_name = found[0].name
        return self.username(*found)

    def execute(self, context):
        username = self.prepare(context)
        if username is None:
            return {"CANCELLED"}
        try:
            result = asyncio.run(build_manager().sync(username))
        except REPORTED_ERRORS as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        return self.apply(context, result)

    def invoke(self, context, event):
        username = self.prepare(context)
        if username is None:
            return {"CANCELLED"}
        self._username = username

        manager = build_manager()  # On the main thread: it resolves paths with bpy.
        task: BackgroundTask[SyncResult] = BackgroundTask()
        manager.subscribe(lambda stage, name: task.publish((stage, name)))
        sync_progress.start(username, task)
        task.start(lambda: manager.sync(username, should_cancel=task.cancelled))
        self._task = task

        wm = context.window_manager
        self._timer = wm.event_timer_add(POLL_INTERVAL, window=context.window)
        wm.modal_handler_add(self)
        self.show_progress(context)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        task = self._task
        if task is None:
            return {"CANCELLED"}
        if event.type == "ESC" and event.value == "PRESS":
            sync_progress.cancel()
            self.show_progress(context)
            return {"RUNNING_MODAL"}
        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        sync_progress.update(task.drain())
        if not task.done():
            self.show_progress(context)
            return {"PASS_THROUGH"}

        self.finish(context)
        try:
            result = task.result()
        except SyncCancelledError:
            self.report({"INFO"}, "Skin download cancelled")
            return {"CANCELLED"}
        except REPORTED_ERRORS as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        return self.apply(context, result)

    def cancel(self, context):
        """Called by Blender when it ends the modal operator, such as on a file load."""
        sync_progress.cancel()
        self.finish(context)

    def show_progress(self, context) -> None:
        """Show the sync's progress in the status bar and redraw the panel."""
        text = f"Skin Manager: {sync_progress.text}... (Esc to cancel)"
        if context.workspace is not None:
            context.workspace.status_text_set(text)
        redraw_skin_ui(context)

    def finish(self, context) -> None:
        """Remove the timer, clear the status bar, and forget the sync. Safe to call twice."""
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if context.workspace is not None:
            context.workspace.status_text_set(None)
        if sync_progress.task is self._task:
            sync_progress.reset()
        self._task = None
        redraw_skin_ui(context)

    def apply(self, context, result: SyncResult):
        """Apply the synced skin to the rig the sync started on, if it is still there."""
        if not result.downloaded:
            self.report({"INFO"}, f"{result.player.name}'s skin has not changed; using the stored copy")

        rig = bpy.data.objects.get(self._rig_name)
        target = skin_targets.for_rig(rig) if rig is not None else None
        if rig is None or target is None:
            self.report({"WARNING"}, f"Saved {result.player.name}'s skin, but the rig is gone. "
                                     "Apply it with Load Saved Skin")
            return {"CANCELLED"}

        settings = rig.pose.bones.get(target.username.bone)
        current = str(settings.get(target.username.key, "")).strip() if settings is not None else ""
        if self._username and current.lower() != self._username.lower():
            self.report({"WARNING"}, f"Saved {result.player.name}'s skin, but the rig's username "
                                     "changed during the download, so it was not applied")
            return {"CANCELLED"}

        # The user may have selected something else while the download ran.
        with context.temp_override(active_object=rig, object=rig):
            if not call_operator(self, OperatorID.LOAD, index=result.skin.index):
                return {"CANCELLED"}
        return {"FINISHED"}


classes = (SkinAdd,)
