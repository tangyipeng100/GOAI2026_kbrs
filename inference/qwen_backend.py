"""Adapter for a waypoint-enabled Qwen-VL checkpoint and processor.

The caller supplies the model, processor and vision preprocessor. Their model
definition and weights are external to this repository.
"""

from __future__ import annotations

import math
from typing import Any, Callable

from .runtime import HISTORY_FRAMES, PREDICT_SCALE, ModelOutput


def _plain(value: Any) -> Any:
    if hasattr(value, "detach"):
        value = value.detach().float().cpu()
    if hasattr(value, "tolist"):
        value = value.tolist()
    while isinstance(value, list) and len(value) == 1 and isinstance(value[0], list):
        value = value[0]
    return value


def _flatten(value: Any) -> list[float]:
    value = _plain(value)
    if isinstance(value, (list, tuple)):
        return [item for child in value for item in _flatten(child)]
    return [float(value)]


class QwenWaypointBackend:
    def __init__(
        self,
        model: Any,
        processor: Any,
        process_vision_info: Callable[[Any], tuple[Any, Any]],
        *,
        device: str = "cuda",
        flow_sample_count: int = 1,
        flow_seed: int = 0,
        flow_num_inference_steps: int = 10,
    ) -> None:
        self.model = model
        self.processor = processor
        self.process_vision_info = process_vision_info
        self.device = device
        self.flow_sample_count = flow_sample_count
        self.flow_seed = flow_seed
        self.flow_num_inference_steps = flow_num_inference_steps

    def predict(self, images: list[Any], prompt: str, input_waypoints: list[list[float]]) -> ModelOutput:
        import torch

        if len(images) not in (HISTORY_FRAMES + 1, HISTORY_FRAMES + 3):
            raise ValueError("Expected history plus one or three current views")
        if len(input_waypoints) != 6:
            raise ValueError("Expected five odom coordinates and one goal coordinate")

        current_views = len(images) - HISTORY_FRAMES
        content = [
            {
                "type": "image",
                "image": image,
                "resized_height": image.height,
                "resized_width": image.width,
            }
            for image in images
        ]
        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        text += "<|im_end|>"
        image_token = "<|vision_start|><|image_pad|><|vision_end|>"
        text = text.replace(image_token, "")
        anchor = "Your historical pictures are: "
        index = text.rfind(anchor)
        if index < 0:
            raise ValueError("Prompt has no historical-image anchor")
        index += len(anchor)
        text = text[:index] + image_token * HISTORY_FRAMES + text[index:]
        if current_views == 3:
            for view in ("leftside", "frontside", "rightside"):
                text = text.replace(f"{view}: ", f"{view}: {image_token}", 1)
        else:
            text = text.replace("frontside: ", f"frontside: {image_token}", 1)

        image_inputs, video_inputs = self.process_vision_info(messages)
        inputs = self.processor(
            text=text, images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt"
        ).to(self.device)
        goal_tensor = torch.tensor(input_waypoints, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            wp_pred, arrive_logits, sin_angle, cos_angle = self.model.forward(
                **inputs,
                input_waypoints=goal_tensor,
                action_former=True,
                gt_waypoints=0,
                train=False,
                train_branch=["continue"],
                flow_sample_count=self.flow_sample_count,
                flow_seed=self.flow_seed,
                flow_num_inference_steps=self.flow_num_inference_steps,
            )
        if wp_pred.ndim == 4:
            wp_pred, sin_angle, cos_angle = wp_pred[:, 0], sin_angle[:, 0], cos_angle[:, 0]
        waypoints = _plain(wp_pred * PREDICT_SCALE)
        logits = _flatten(arrive_logits)
        sin_values, cos_values = _flatten(sin_angle), _flatten(cos_angle)
        return ModelOutput(
            waypoints=[[float(v) for v in point] for point in waypoints],
            arrive_logits=logits,
            heading_angles=[math.atan2(float(s), float(c)) for s, c in zip(sin_values, cos_values)],
        )
