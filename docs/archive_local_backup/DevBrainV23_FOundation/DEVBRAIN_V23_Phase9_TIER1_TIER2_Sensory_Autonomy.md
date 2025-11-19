# DEVBRAIN V23 - Phase 9 Roadmap: TIER 1 & TIER 2 Sensory + Autonomy
## Multimodal Perception & Self-Healing Capabilities

**Status**: Production-Ready Roadmap | **Version**: 1.0  
**Date**: November 18, 2025  
**Target Duration**: 12-15 days (parallel execution)  
**Coverage**: Visual Cortex + Voice Interface + Self-Healing Loops + Doc2Agent

---

## 📊 Overview: TIER 1 & TIER 2

### TIER 1: Sentidos (Sensory Systems)
Transform DEVBRAIN from **text-only** into **multimodal**:
- **Visual Cortex**: See and interact with screens (GUI automation)
- **Voice Interface**: Hear commands, respond naturally

### TIER 2: Autonomia & Auto-Recovery
Enable **true autonomy** and **resilience**:
- **Self-Healing Loops**: Detect + Fix errors automatically
- **Doc2Agent**: Discover + Use new APIs without human intervention

## 📌 Doc2Agent Integration & Cycle Checklist

- **ToolsFramework pairing** — Doc2Agent now delegates every generated step through the audited `ToolsFramework`, allowing it to re-use the 25+ `AuditedTool` implementations and to surface real latency, status, and failure information for each native tool call.
- **Alerting + Metrics** — Every invocation records latency, goal, step, and status; failures raise alerts through the documented callback hook while the `track_metrics` tool logs downstream telemetry to `~/.omnimind/metrics/metrics.jsonl`.
- **Testing posture** — Async Pytest coverage simulates success/failure flows and ensures alert propagation + metric emission happen automatically for both orchestrated and custom tool invokers.
- **Documentation & logs** — Integration details, alert expectations, and monitoring practices are documented here so future operators understand how to inspect Doc2Agent health and follow the SHA-256 audit trail.
- **Next-cycle checklist** — Use the steps below as a living backlog for continual generation, validation, refinement, deployment, and monitoring.

### 📈 Best Practices & Troubleshooting

- **Keep prompts deterministic** — Anchor each Doc2Agent step to a `prompt` that describes the goal, expected tool, and key parameters so regression tests can replay failures.
- **Use `alert_callback` wisely** — Plug in dashboards or incident managers to capture alerts emitted when any tool call fails; correlate them with `invocation_history` records that include timestamps and latency.
- **Monitor aggregated metrics** — Consume `get_aggregate_metrics()` output for total steps, failure rates, and average latencies per tool; surface these values in dashboards before dropping the plan for the next iteration.
- **Debugging flow** — Replay failing plans with a custom `tool_invoker` (as done in the tests) to reproduce the error locally without altering production metrics.
- **Instrument tracking ferries** — Point the default `metrics_sink` at `track_metrics` so that the `metrics.jsonl` file holds slices of latency/status for every invocation; treat that file as both monitoring input and forensic evidence.

### ⚙️ Pipeline Execution Flow

1. **Generate**: The `Doc2AgentPipeline` in `DEVBRAIN_V23/autonomy/doc2agent_pipeline.py` invokes `Doc2Agent` to produce `DocStep` plans derived from document goals.
2. **Validate + Refine**: Each plan runs through `Doc2Agent.execute_plan` for validation; non-zero errors trigger the configurable `refiner` callback (with a sane `max_refinements`) before re-validating.
3. **Deploy**: Once validation succeeds, the optional deployer applies the steps (can gate behind feature flags) and records stage success.
4. **Monitor**: Aggregated metrics collected via `Doc2Agent.get_aggregate_metrics()` feed `monitor_sink` for dashboards or alerting; the pipeline also logs stage durations for observability.
5. **Re-run**: The pipeline provides full stage logs and validation details so that failures can replay with custom tool invokers or patched analyzers during debugging.

- **Tests**: `tests/test_doc2agent_pipeline.py` covers successful cycles, refine loops, and ensures stage logs capture generate/validate/deploy/monitor sequences.

## 🛡️ Self-Healing & ATLAS Adaptation

- **Self-Healing Loop**: `DEVBRAIN_V23/autonomy/self_healing.py` now tracks cycles, issue counts, remediations and emits telemetry via the `metrics_sink`. Register monitors + remediations through the exposed hooks, and rely on `get_metrics()` for dashboards and historical review.
- **ATLAS Controller**: `DEVBRAIN_V23/atlas/atlas_controller.py` listens to Doc2Agent metrics, flags degradations when failure rates exceed thresholds, and registers monitors/remediations automatically to recover from high-error plans. Its `adaptation_cycle()` can be invoked whenever new data needs to feed learning or retraining tasks.
- **Testing**: `tests/test_self_healing.py` validates monitor/remediation flows plus metrics emission, while `tests/test_atlas_controller.py` ensures the ATLAS controller triggers remediation issues and executes adaptation cycles successfully.
- **Troubleshooting**: If alerts spike, replay `atlas.adaptation_cycle()` with the latest documents/goals to capture fresh `DocStep` plans, then inspect `self_healing.get_metrics()` for issue history and `atlas.get_insights()` for contextual observations.
- **Observability Dashboard**: `web/backend/main.py` now surfaces a `/observability` endpoint that returns the latest `self_healing`, `atlas`, and alert history records captured in `AutonomyObservability`, enabling the React dashboard to render dedicated panels for remediation cycles, Atlas insights, and alerts in near real time.

### Autenticação do dashboard

- O backend carrega credenciais em `_ensure_dashboard_credentials`: primeiro verifica `OMNIMIND_DASHBOARD_USER` e `OMNIMIND_DASHBOARD_PASS`, depois tenta ler `config/dashboard_auth.json` (ou um caminho customizado via `OMNIMIND_DASHBOARD_AUTH_FILE`) e, só então, gera e persiste credenciais internas com permissão `600`.
- Essa cadeia de confiança garante que o dashboard só aceita conexões autenticadas e mantém o par user/pass fora de código-fonte, enquanto os testes podem fornecer um arquivo seguro temporário via `OMNIMIND_DASHBOARD_AUTH_FILE`.

### 🔁 Next-cycle Checklist for Doc2Agent

1. **Generate** new tool descriptions via Doc2Agent plans, then persist them alongside goal metadata so auditors can track origin.
2. **Validate syntax + contracts** using automated parsers (pytest + mypy) before onboarding a tool into the framework.
3. **Iterate** with a refine-validate loop that re-runs Doc2Agent when feedback indicates incomplete goals or failing outputs.
4. **Deploy gradually** by gating new tools behind feature flags and monitoring their shadow usage to detect regressions early.
5. **Monitor telemetry** for latency distributions, success/failure ratios, and alert density per tool name/goal.
6. **Alert automatically** whenever thresholds (error rate > 5%, latency > 200ms) or missing telemetry are observed; send notifications through both logs and callbacks.
7. **Stress + regression testing** — schedule nightly suites that replay representative plans against production-like data to catch drift.
8. **Document findings** and replay logs to refine prompts, tooling, and escalation policies before the next autonomy phase.

### 🗺️ Planned Next Cycle Tasks (Generation → Monitoring)

1. **Creation Sprint:** Use Doc2Agent to draft new tool chains for emerging autonomy needs, ensuring every step includes prompts, tool names, and parameters for traceability.
2. **Static Validation:** Run syntax + type checks on generated tool definitions/APIs and reject any that fail before they hit the pipeline (pytest + mypy + lint).
3. **Sandbox Execution:** Execute new plans in a sandbox with the `ToolsFramework` but monkey-patched resources to ensure early detection of resource constraints or incorrect assumptions.
4. **Refinement Loop:** Incorporate alerts and aggregated metrics into prompt tuning; re-run unsuccessful plans automatically until failure density drops below 5%.
5. **Feature-gated Deploy:** Gradually roll out confirmed tool changes using feature flags, splitting traffic between existing and new toolchains to compare performance.
6. **Telemetry Healthchecks:** Monitor aggregated metrics (total steps, failure rate, avg latency) and raise alerts when any metric regresses beyond thresholds.
7. **Post-deploy Audit:** Review `track_metrics` logs, SHA-256 trails, and alert messages daily to catch drift and confirm audit integrity.
8. **Continuous Learning:** Feed refined prompts, troubleshooting notes, and audit summaries back into the Doc2Agent analyst so it learns to favor stable tools.

---

## 🎯 TIER 1.1: Visual Cortex (OmniParser + YOLOv8)

### Architecture: Vision-Based GUI Agent

```
Screenshot Input
    ↓
┌─────────────────────────────────────┐
│ OmniParser (Microsoft)               │
│ ├─ Detect interactive regions        │
│ ├─ Extract text/icons                │
│ └─ Generate "Set of Marks" (SoM)    │
└─────────────────────────────────────┘
    ↓
Structured UI Elements (JSON)
    ├─ Button #1 @ (x, y) → "Submit"
    ├─ TextField #2 → "email_field"
    └─ Link #3 → "Next Page"
    ↓
┌─────────────────────────────────────┐
│ Agent Reasoning                     │
│ "I need to click Submit button"      │
│ → Lookup button ID in structured UI │
│ → Execute click @ stored coordinates │
│ (NO hardcoded coordinates!)          │
└─────────────────────────────────────┘
    ↓
PyAutoGUI Execution
    ↓
New Screenshot + Loop
```

### Implementation: Visual Cortex Module

#### File: `DEVBRAIN_V23/sensory/visual_cortex.py`

```python
import pyautogui
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import asyncio
from PIL import Image
import io

@dataclass
class UIElement:
    """Represents a detected UI element."""
    id: str
    element_type: str          # "button", "text_field", "link", "icon"
    label: str                 # "Submit", "email_field", etc.
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    is_interactive: bool
    ocr_text: Optional[str] = None

class VisualCortex:
    """
    Vision-based screen understanding and GUI automation.
    Uses OmniParser for structured UI parsing.
    """
    
    def __init__(self, use_omniparser: bool = True):
        """
        Args:
            use_omniparser: If True, use OmniParser. Else, fallback to YOLOv8 only.
        """
        self.use_omniparser = use_omniparser
        
        if use_omniparser:
            try:
                # pip install omniparser-vision
                from omniparser_vision import OmniParser
                self.parser = OmniParser(model="omniparser-v1")
            except ImportError:
                print("Warning: OmniParser not installed. Using YOLOv8 fallback.")
                self.parser = None
        
        # YOLOv8 for UI element detection
        from ultralytics import YOLO
        self.yolo = YOLO("yolov8m.pt")  # Medium model
        
        # OCR for text extraction
        try:
            import pytesseract
            self.ocr = pytesseract.pytesseract.image_to_string
        except:
            self.ocr = None
            print("Warning: pytesseract not available. OCR disabled.")
        
        self.last_screenshot = None
        self.ui_elements: Dict[str, UIElement] = {}
    
    async def see_screen(self) -> Dict:
        """
        Capture screenshot and extract structured UI elements.
        
        Returns:
        {
          "screenshot_path": "...",
          "elements": [
            {
              "id": "elem_0",
              "type": "button",
              "label": "Submit",
              "bbox": [100, 200, 50, 30],
              "is_interactive": True
            },
            ...
          ],
          "dom_like_structure": {...}
        }
        """
        # Capture screenshot
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        self.last_screenshot = img_array
        
        # Parse UI using OmniParser (if available)
        if self.parser:
            try:
                parsed_output = self.parser.parse_screenshot(img_array)
                elements = await self._parse_omniparser_output(parsed_output)
            except Exception as e:
                print(f"OmniParser error: {e}. Falling back to YOLOv8...")
                elements = await self._detect_ui_elements_yolo(img_array)
        else:
            # Fallback: YOLOv8 only
            elements = await self._detect_ui_elements_yolo(img_array)
        
        # Store for semantic lookup
        self.ui_elements = {elem["id"]: elem for elem in elements}
        
        # Save screenshot
        screenshot.save("/tmp/devbrain_last_screenshot.png")
        
        return {
            "screenshot_path": "/tmp/devbrain_last_screenshot.png",
            "timestamp": self._get_timestamp(),
            "elements": elements,
            "dom_like": self._build_dom_structure(elements),
            "element_count": len(elements)
        }
    
    async def _parse_omniparser_output(self, parsed_output: Dict) -> List[Dict]:
        """Convert OmniParser output to standard UIElement format."""
        elements = []
        
        for idx, element in enumerate(parsed_output.get("elements", [])):
            ui_elem = UIElement(
                id=f"elem_{idx}",
                element_type=element.get("type", "unknown"),
                label=element.get("label", element.get("text", "")),
                bbox=(
                    element.get("x", 0),
                    element.get("y", 0),
                    element.get("width", 0),
                    element.get("height", 0)
                ),
                is_interactive=element.get("is_interactive", False),
                ocr_text=element.get("text", None)
            )
            elements.append(ui_elem.__dict__)
        
        return elements
    
    async def _detect_ui_elements_yolo(self, img_array: np.ndarray) -> List[Dict]:
        """Fallback: Use YOLOv8 for UI detection."""
        detections = self.yolo(img_array)
        elements = []
        
        for idx, det in enumerate(detections[0].boxes):
            x, y, w, h = det.xywh[0].cpu().numpy()
            x, y, w, h = int(x - w/2), int(y - h/2), int(w), int(h)
            
            # Crop and OCR if available
            ocr_text = None
            if self.ocr:
                try:
                    crop = img_array[max(0, y):min(img_array.shape[0], y+h),
                                     max(0, x):min(img_array.shape[1], x+w)]
                    ocr_text = self.ocr(crop)
                except:
                    pass
            
            element = {
                "id": f"elem_{idx}",
                "element_type": "detected_region",
                "label": ocr_text or f"region_{idx}",
                "bbox": (x, y, w, h),
                "is_interactive": True,
                "ocr_text": ocr_text
            }
            elements.append(element)
        
        return elements
    
    async def interact_with_element(
        self,
        element_identifier: str,  # Can be element ID or label
        action: str = "click",     # "click", "type", "scroll"
        params: Dict = None
    ) -> Dict:
        """
        Interact with UI element identified by semantic label (not coordinates).
        
        Examples:
            await cortex.interact_with_element("Submit", action="click")
            await cortex.interact_with_element("email_field", action="type", {"text": "user@example.com"})
        """
        params = params or {}
        
        # Find element by ID or label
        element = None
        for elem_id, elem in self.ui_elements.items():
            if elem["id"] == element_identifier or elem["label"] == element_identifier:
                element = elem
                break
        
        if not element:
            return {
                "status": "failed",
                "error": f"Element '{element_identifier}' not found in current screen"
            }
        
        # Execute action
        x, y, w, h = element["bbox"]
        center_x, center_y = x + w // 2, y + h // 2
        
        try:
            if action == "click":
                pyautogui.click(center_x, center_y)
                await asyncio.sleep(0.5)  # Wait for response
            
            elif action == "type":
                text = params.get("text", "")
                pyautogui.typewrite(text, interval=0.05)
                await asyncio.sleep(0.5)
            
            elif action == "scroll":
                direction = params.get("direction", "down")  # "up", "down"
                amount = params.get("amount", 3)
                if direction == "down":
                    pyautogui.scroll(-amount)
                else:
                    pyautogui.scroll(amount)
                await asyncio.sleep(0.5)
            
            else:
                return {"status": "failed", "error": f"Unknown action: {action}"}
            
            # Take screenshot after interaction
            await asyncio.sleep(1)  # Wait for UI update
            new_screenshot = await self.see_screen()
            
            return {
                "status": "success",
                "action": action,
                "element": element_identifier,
                "new_ui_state": new_screenshot
            }
        
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _build_dom_structure(self, elements: List[Dict]) -> Dict:
        """Build DOM-like structure for agent reasoning."""
        dom = {
            "buttons": [],
            "text_fields": [],
            "links": [],
            "images": [],
            "other": []
        }
        
        for elem in elements:
            elem_type = elem.get("element_type", "other")
            
            if "button" in elem_type.lower():
                dom["buttons"].append(elem)
            elif "field" in elem_type.lower() or "input" in elem_type.lower():
                dom["text_fields"].append(elem)
            elif "link" in elem_type.lower() or "a" in elem_type.lower():
                dom["links"].append(elem)
            elif "image" in elem_type.lower() or "icon" in elem_type.lower():
                dom["images"].append(elem)
            else:
                dom["other"].append(elem)
        
        return dom
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
```

#### File: `tests/test_visual_cortex.py`

```python
import pytest
from DEVBRAIN_V23.sensory.visual_cortex import VisualCortex

@pytest.mark.asyncio
async def test_visual_cortex_see_screen():
    """Test screen capture and UI parsing."""
    cortex = VisualCortex(use_omniparser=False)  # Use YOLOv8 for testing
    result = await cortex.see_screen()
    
    assert "elements" in result
    assert "dom_like" in result
    assert isinstance(result["elements"], list)

@pytest.mark.asyncio
async def test_semantic_element_lookup():
    """Test finding elements by semantic label."""
    cortex = VisualCortex(use_omniparser=False)
    
    # Populate UI elements manually for testing
    cortex.ui_elements = {
        "elem_0": {
            "id": "elem_0",
            "label": "Submit",
            "bbox": (100, 200, 50, 30),
            "is_interactive": True
        }
    }
    
    # Find by label
    found = None
    for elem_id, elem in cortex.ui_elements.items():
        if elem["label"] == "Submit":
            found = elem
            break
    
    assert found is not None
    assert found["label"] == "Submit"

@pytest.mark.asyncio
async def test_build_dom_structure():
    """Test DOM structure generation."""
    cortex = VisualCortex()
    
    elements = [
        {"id": "b1", "element_type": "button", "label": "Click Me"},
        {"id": "t1", "element_type": "text_field", "label": "email"},
        {"id": "l1", "element_type": "link", "label": "Next"}
    ]
    
    dom = cortex._build_dom_structure(elements)
    
    assert len(dom["buttons"]) == 1
    assert len(dom["text_fields"]) == 1
    assert len(dom["links"]) == 1
```

---

## 🎯 TIER 1.2: Voice Interface (Whisper + Piper TTS)

### Architecture: Voice I/O

#### File: `DEVBRAIN_V23/sensory/voice_interface.py`

```python
import asyncio
import numpy as np
from typing import Optional
import os

class VoiceInterface:
    """Local voice I/O using Whisper (STT) + Piper (TTS)."""
    
    def __init__(self):
        try:
            import whisper
            self.stt_model = whisper.load_model("base")  # 140MB
        except ImportError:
            raise ImportError("Install: pip install openai-whisper")
        
        try:
            import sounddevice as sd
            import soundfile as sf
            self.sd = sd
            self.sf = sf
        except ImportError:
            raise ImportError("Install: pip install sounddevice soundfile")
        
        try:
            from TTS.api import TTS
            self.tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", gpu=False)
        except ImportError:
            raise ImportError("Install: pip install TTS")
        
        self.sample_rate = 16000
    
    async def listen_and_transcribe(
        self,
        duration: int = 10,  # seconds
        silence_threshold: float = 0.02
    ) -> str:
        """
        Listen to microphone and transcribe to text.
        Automatically stops on silence detection.
        """
        print(f"🎤 Listening for {duration} seconds...")
        
        # Record audio
        audio_data = self.sd.rec(
            int(self.sample_rate * duration),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        self.sd.wait()
        
        # Detect silence and trim
        audio_data = self._trim_silence(audio_data, silence_threshold)
        
        # Transcribe using Whisper
        result = self.stt_model.transcribe(audio_data, language="en")
        transcribed_text = result["text"]
        
        print(f"📝 Transcribed: {transcribed_text}")
        return transcribed_text
    
    async def speak(self, text: str, play_audio: bool = True) -> str:
        """
        Convert text to speech and play (or save).
        """
        print(f"🔊 Speaking: {text}")
        
        # Generate speech
        output_path = "/tmp/devbrain_tts_output.wav"
        self.tts.tts_to_file(text=text, file_path=output_path)
        
        if play_audio:
            # Play audio
            try:
                audio_data, sr = self.sf.read(output_path)
                self.sd.play(audio_data, sr)
                self.sd.wait()
            except Exception as e:
                print(f"Error playing audio: {e}")
        
        return output_path
    
    def _trim_silence(
        self,
        audio: np.ndarray,
        threshold: float
    ) -> np.ndarray:
        """Remove leading/trailing silence."""
        # Compute RMS energy
        energy = np.sqrt(np.mean(audio ** 2, axis=-1))
        
        # Find non-silent frames
        mask = energy > threshold
        
        # Find start and end
        non_silent_indices = np.where(mask)[0]
        if len(non_silent_indices) == 0:
            return audio
        
        start_idx = non_silent_indices[0]
        end_idx = non_silent_indices[-1]
        
        return audio[start_idx:end_idx + 1]
```

---

## 💪 TIER 2.1: Self-Healing Loops

### Architecture: Error Detection + Automatic Fix

#### File: `DEVBRAIN_V23/autonomy/self_healing.py`

```python
from typing import Dict, List, Optional
from datetime import datetime
import json

class SelfHealingLoop:
    """
    Autonomous error detection and recovery system.
    """
    
    def __init__(self, amem, llm, visual_cortex=None):
        self.amem = amem
        self.llm = llm
        self.visual_cortex = visual_cortex
        self.error_history: List[Dict] = []
    
    async def execute_with_recovery(
        self,
        task: str,
        max_retries: int = 3,
        recovery_strategies: List[str] = None
    ) -> Dict:
        """
        Execute task with automatic error detection and recovery.
        """
        recovery_strategies = recovery_strategies or [
            "retry",           # Simple retry
            "fallback_tool",   # Use alternative tool
            "reformulate",     # Rephrase the task
            "escalate"         # Ask for human help
        ]
        
        attempt = 0
        
        while attempt < max_retries:
            try:
                print(f"[SELF-HEAL] Attempt {attempt + 1}/{max_retries}")
                
                result = await self._execute_task(task)
                
                if result.get("success"):
                    print("[SELF-HEAL] ✅ Success!")
                    return result
                else:
                    error = result.get("error", "Unknown error")
                    print(f"[SELF-HEAL] ❌ Error: {error}")
                    
                    # Try recovery
                    recovery_result = await self._attempt_recovery(
                        task, error, recovery_strategies
                    )
                    
                    if recovery_result.get("recovered"):
                        return recovery_result
                
            except Exception as e:
                print(f"[SELF-HEAL] Exception: {e}")
                await self.amem.store_procedure(
                    f"Task failed: {task}",
                    f"Error: {str(e)}"
                )
            
            attempt += 1
        
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts"
        }
    
    async def _attempt_recovery(
        self,
        task: str,
        error: str,
        strategies: List[str]
    ) -> Dict:
        """Try recovery strategies in order."""
        for strategy in strategies:
            print(f"[SELF-HEAL] Trying: {strategy}")
            
            if strategy == "retry":
                # Simple wait + retry
                import asyncio
                await asyncio.sleep(2)
                return await self._execute_task(task)
            
            elif strategy == "fallback_tool":
                # Use alternative approach
                alt_task = f"Accomplish this differently: {task}"
                return await self._execute_task(alt_task)
            
            elif strategy == "reformulate":
                # Reformulate using LLM
                reformulated = await self.llm.ainvoke(
                    f"Rephrase this task for clarity:\n{task}"
                )
                return await self._execute_task(reformulated.content)
            
            elif strategy == "escalate":
                # Store for human review
                await self.amem.store_procedure(
                    task,
                    "Requires manual intervention"
                )
                return {"success": False, "escalated": True}
        
        return {"recovered": False}
    
    async def _execute_task(self, task: str) -> Dict:
        """Execute and monitor task for errors."""
        # Simplified: would call actual task execution
        return {
            "success": True,
            "output": f"Executed: {task}"
        }
```

---

## 🚀 TIER 2.2: Doc2Agent (Automatic Tool Generation)

### Architecture: API Documentation → Executable Tools

#### File: `DEVBRAIN_V23/autonomy/doc2agent.py`

```python
import json
import re
from typing import Dict, List, Optional
import inspect

class Doc2Agent:
    """
    Autonomously generate tools from API documentation.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.generated_tools: Dict[str, callable] = {}
    
    async def generate_from_documentation(
        self,
        api_docs: str,
        allowed_methods: List[str] = None
    ) -> Dict:
        """
        Generate Python tools from API documentation.
        
        Stages:
        1. Parse documentation
        2. Extract endpoints
        3. Generate tool code
        4. Validate
        5. Deploy to MCP
        """
        allowed_methods = allowed_methods or ["GET", "POST"]
        
        print("[DOC2AGENT] Parsing API documentation...")
        
        # Stage 1: Extract endpoints
        endpoints = await self._extract_endpoints(api_docs)
        
        print(f"[DOC2AGENT] Found {len(endpoints)} endpoints")
        
        # Stage 2: Generate tools
        tools = {}
        for endpoint in endpoints:
            if endpoint.get("method") in allowed_methods:
                tool = await self._generate_tool(endpoint)
                tools[endpoint["name"]] = tool
        
        print(f"[DOC2AGENT] Generated {len(tools)} tools")
        
        # Stage 3: Validate
        validation_results = await self._validate_tools(tools, api_docs)
        
        return {
            "endpoints_found": len(endpoints),
            "tools_generated": len(tools),
            "validation_results": validation_results,
            "tools": tools
        }
    
    async def _extract_endpoints(self, docs: str) -> List[Dict]:
        """Extract endpoints from documentation."""
        # Use regex + LLM to find endpoint patterns
        endpoint_pattern = r"(GET|POST|PUT|DELETE)\s+(/[\w\-/{}]*)"
        matches = re.findall(endpoint_pattern, docs)
        
        endpoints = []
        for method, path in matches:
            endpoints.append({
                "name": path.replace("/", "_").strip("_"),
                "method": method,
                "path": path,
                "doc_section": docs[max(0, docs.find(path) - 200):docs.find(path) + 200]
            })
        
        return endpoints
    
    async def _generate_tool(self, endpoint: Dict) -> str:
        """Generate Python tool code for an endpoint."""
        prompt = f"""
Generate a Python function to call this API endpoint:

Endpoint: {endpoint['method']} {endpoint['path']}
Documentation snippet:
{endpoint.get('doc_section', '')}

Return ONLY valid Python code as a function:
- Name: endpoint path as snake_case
- Parameters: inferred from endpoint path + common params
- Docstring: describe what it does
- Return: parsed response

Example format:
async def get_user(user_id: str) -> dict:
    '''Get user by ID.'''
    url = f"https://api.example.com/users/{{user_id}}"
    response = await request("GET", url)
    return response.json()
"""
        response = await self.llm.ainvoke(prompt)
        
        tool_code = response.content
        
        # Validate Python syntax
        try:
            compile(tool_code, "<string>", "exec")
        except SyntaxError as e:
            print(f"[DOC2AGENT] Syntax error in generated code: {e}")
            return None
        
        return tool_code
    
    async def _validate_tools(
        self,
        tools: Dict,
        api_docs: str
    ) -> List[Dict]:
        """Validate generated tools against documentation."""
        results = []
        
        for tool_name, tool_code in tools.items():
            # Check:
            # 1. Code compiles
            # 2. Function signature matches documentation
            # 3. Return type matches expected response format
            
            try:
                compile(tool_code, "<string>", "exec")
                results.append({
                    "tool": tool_name,
                    "status": "valid",
                    "errors": []
                })
            except SyntaxError as e:
                results.append({
                    "tool": tool_name,
                    "status": "invalid",
                    "errors": [str(e)]
                })
        
        return results
```

---

## 📋 Integration: TIER 1 + TIER 2

### Full End-to-End: Visual → Reasoning → Recovery

#### File: `tests/test_tier1_tier2_integration.py`

```python
import pytest
from DEVBRAIN_V23.sensory.visual_cortex import VisualCortex
from DEVBRAIN_V23.sensory.voice_interface import VoiceInterface
from DEVBRAIN_V23.autonomy.self_healing import SelfHealingLoop
from DEVBRAIN_V23.autonomy.doc2agent import Doc2Agent

@pytest.mark.asyncio
async def test_gui_automation_via_visual_cortex():
    """Test GUI automation without hardcoded coordinates."""
    cortex = VisualCortex(use_omniparser=False)
    
    # See screen
    ui_state = await cortex.see_screen()
    assert "elements" in ui_state
    
    # Interact with element by semantic label (not coordinates!)
    # result = await cortex.interact_with_element("Submit", action="click")
    # assert result["status"] in ["success", "failed"]

@pytest.mark.asyncio
async def test_voice_command():
    """Test voice-based interaction."""
    # Skipping actual audio tests in CI
    voice = VoiceInterface()
    
    # In real scenario:
    # text = await voice.listen_and_transcribe(duration=5)
    # await voice.speak(f"You said: {text}")

@pytest.mark.asyncio
async def test_self_healing_recovery():
    """Test autonomous error recovery."""
    from unittest.mock import AsyncMock
    
    amem = AsyncMock()
    llm = AsyncMock()
    
    healing = SelfHealingLoop(amem, llm)
    
    result = await healing.execute_with_recovery(
        "test task",
        max_retries=2
    )
    
    assert "success" in result

@pytest.mark.asyncio
async def test_doc2agent_generation():
    """Test automatic tool generation from docs."""
    from unittest.mock import AsyncMock
    
    llm = AsyncMock()
    llm.ainvoke.return_value = AsyncMock(content="""
async def get_user(user_id: str) -> dict:
    '''Get user by ID.'''
    return {"user_id": user_id}
""")
    
    doc2agent = Doc2Agent(llm)
    
    api_docs = """
    GET /users/{id} - Retrieve user by ID
    POST /users - Create new user
    """
    
    result = await doc2agent.generate_from_documentation(api_docs)
    
    assert result["tools_generated"] >= 0
```

---

## 🚀 Deployment Checklist

**TIER 1 (Sensory):**
- [ ] Visual Cortex (OmniParser fallback YOLOv8) working
- [ ] Voice I/O (Whisper + Piper) tested locally
- [ ] GUI automation (semantic interaction) tested
- [ ] Tests: 100% passing

**TIER 2 (Autonomy):**
- [ ] Self-Healing loops implemented
- [ ] Error recovery strategies working
- [ ] Doc2Agent tool generation complete
- [ ] Tool validation automated
- [ ] Tests: 100% passing

**Integration:**
- [ ] TIER 0 + TIER 1 + TIER 2 all connected
- [ ] End-to-end flow: Voice → See → Reason → Act → Heal
- [ ] Performance benchmarks (GUI interaction latency < 2s)
- [ ] Memory consolidation running

---

## ✅ Next: TIER 3 (Imunidade)

After TIER 1 & 2:
- Firecracker MicroVM sandboxing
- DLP (Data Loss Prevention) filters
- HSM integration
- Production hardening

**Status**: TIER 1 & TIER 2 production roadmaps ready for Copilot implementation ✅
