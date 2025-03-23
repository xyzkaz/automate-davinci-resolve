# import tkinter as tk
# from pathlib import Path
# from tkinter import filedialog

from typing import NamedTuple

from ..extended_resolve import davinci_resolve_module
from ..extended_resolve.media_pool_item import MediaPoolItem
from ..extended_resolve.constants import MediaPoolItemType
from ..extended_resolve.track import TrackHandle
from ..resolve_types import PyRemoteComposition, PyRemoteOperator
from ..utils.math import FrameRange
from ..smart_edit.errors import UserError
from ..smart_edit.uni_textplus import UniTextPlus
from ..smart_edit.ui.loading_window import LoadingWindow
from .script_utils import ScriptUtils


class CopyInfo(NamedTuple):
    src_tool: PyRemoteOperator
    src_input_name: str
    dst_tool_name: str
    dst_input_name: str


def get_copy_infos(composition: PyRemoteComposition, adjust_fusion: PyRemoteOperator):
    copy_infos = []

    input_expressions = adjust_fusion.GetInput("SourceInputs")

    for input_expression in input_expressions.split("\n"):
        input_expression = input_expression.strip()
        tokens = input_expression.split(".", maxsplit=1)

        src_tool_name = None
        src_input_name = None

        if len(tokens) == 1:
            src_input_name = tokens[0]
        else:
            src_tool_name = tokens[0]
            src_input_name = tokens[1]

        src_tool = composition.FindTool(src_tool_name) if src_tool_name is not None else adjust_fusion

        if src_tool is None:
            continue

        copy_infos.append(
            CopyInfo(
                src_tool=src_tool,
                src_input_name=src_input_name,
                dst_tool_name=src_tool_name,
                dst_input_name=src_input_name,
            )
        )

    return copy_infos


def is_valid_source_input(composition: PyRemoteComposition, tool: PyRemoteOperator, source_input: str):
    tokens = source_input.split(".", maxsplit=1)

    src_tool_name = None
    src_input_name = None

    if len(tokens) == 1:
        src_input_name = tokens[0]
    else:
        src_tool_name = tokens[0]
        src_input_name = tokens[1]

    src_tool = composition.FindTool(src_tool_name) if src_tool_name is not None else tool

    if src_tool is None:
        return False

    src_input = getattr(src_tool, src_input_name)

    if src_input is None:
        return False

    return True


def on_add_source_input(composition: PyRemoteComposition, tool_name: str):
    if composition is None:
        return

    tool = composition.FindTool(tool_name)

    if tool is not None:
        expression: str = tool.AddSourceInput.GetExpression()

        if expression is None:
            tool.AddSourceInput.SetExpression("")
        else:
            source_input = expression.strip()

            if is_valid_source_input(composition, tool, source_input):
                source_inputs = tool.GetInput("SourceInputs")

                if source_inputs == "":
                    source_inputs = source_input
                elif source_input not in source_inputs:
                    source_inputs += f"\n{source_input}"

                tool.SetInput("SourceInputs", source_inputs)


def on_copy_for_clip(composition: PyRemoteComposition):
    resolve = davinci_resolve_module.get_resolve()
    timeline = resolve.get_current_timeline()
    curr_item = ScriptUtils.get_timeline_item_from_composition(composition)
    curr_track_handle = curr_item.get_track_handle()
    curr_frame_range = curr_item.get_frame_range()

    adjust_fusion = composition.FindToolByID("Fuse.AdjustFusion")
    track_num = adjust_fusion.GetInput("NumberOfTracks")
    # target_inputs = [get_input_from_expression(input_expression) for input_expression in adjust_fusion.GetInput("SourceInputs").split("\n")]
    copy_infos = get_copy_infos(composition, adjust_fusion)

    min_underneath_track_index = max(curr_track_handle.index - track_num, 1)
    max_underneath_track_index = max(curr_track_handle.index - 1, 1)

    if min_underneath_track_index == max_underneath_track_index:
        return

    curr_item.get_frame_range()

    for track_index in range(min_underneath_track_index, max_underneath_track_index + 1):
        for item in timeline.iter_items_in_track(
            TrackHandle(curr_track_handle.type, track_index), lambda item: FrameRange.is_started_in_range(item.get_frame_range(), curr_frame_range)
        ):
            dst_comp = item._item.GetFusionCompByIndex(1)

            if dst_comp is None:
                continue

            for copy_info in copy_infos:
                dst_tool = dst_comp.FindTool(copy_info.dst_tool_name)

                if dst_tool is None:
                    continue

                value = copy_info.src_tool.GetInput(copy_info.src_input_name)
                dst_tool.SetInput(copy_info.dst_input_name, value)
