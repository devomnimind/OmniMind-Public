#!/usr/bin/env python3
"""
DevBrain Mistral Fine-tuning Pipeline
Personaliza modelo Mistral com dados do usuário
"""
import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np  # noqa: F401
import torch
from datasets import Dataset, load_dataset  # noqa: F401
from huggingface_hub import HfApi, login, snapshot_download
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MistralFineTuner:
    """Production-grade fine-tuning for Mistral model"""

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        output_dir: str = "./mistral_finetuned",
        device_map: str = "auto",
        load_in_4bit: bool = True,
        hf_token: Optional[str] = None,
        max_memory: Optional[Dict[str, str]] = None,
        offload_folder: Optional[Path] = None,
    ):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.device_map = device_map
        self.load_in_4bit = load_in_4bit
        self.hf_token = (
            hf_token
            or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            or os.environ.get("HF_TOKEN")
        )
        self.max_memory = max_memory
        self.offload_folder = offload_folder
        self.tokenizer = None
        self.model = None
        self.training_history: List[Dict] = []
        self._setup_paths()
        self._login_to_hub()

    def _setup_paths(self):
        """Create necessary directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        (self.output_dir / "checkpoints").mkdir(exist_ok=True)
        if self.offload_folder:
            self.offload_folder.mkdir(parents=True, exist_ok=True)

    def _login_to_hub(self) -> None:
        if not self.hf_token:
            logger.info("Hugging Face token not provided; assuming prior CLI auth")
            return
        try:
            login(token=self.hf_token, add_to_git_credential=False)
            logger.info("Authenticated with Hugging Face Hub")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to authenticate with Hugging Face Hub: %s", exc)

    def _setup_model(self) -> None:
        """Load tokenizer and model with quantization/offload support"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            logger.info("Cleared CUDA cache and peak stats before loading model")
        tokenizer_kwargs: Dict[str, Any] = {"trust_remote_code": True}
        if self.hf_token:
            tokenizer_kwargs["token"] = self.hf_token
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, **tokenizer_kwargs
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"

        model_kwargs: Dict[str, Any] = {
            "trust_remote_code": True,
            "device_map": self.device_map,
        }
        if self.load_in_4bit:
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                llm_int8_skip_modules=None,
                llm_int8_has_fp16_weight=False,
                llm_int8_threshold=6.0,
                llm_int8_enable_fp32_cpu_offload=True,
            )
            model_kwargs["quantization_config"] = quant_config
        else:
            model_kwargs["torch_dtype"] = torch.float16

        if self.offload_folder:
            model_kwargs["offload_folder"] = str(self.offload_folder)
        if self.max_memory:
            model_kwargs["max_memory"] = self.max_memory
        if self.hf_token:
            model_kwargs["token"] = self.hf_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, **model_kwargs
        )
        logger.info("✅ Model loaded: %s", self.model_name)
        logger.info("Model parameters: %s", f"{self.model.num_parameters():,}")

    def load_model(self) -> None:
        """Public wrapper for setting up model components"""
        self._setup_model()

    def setup_lora(
        self,
        r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: Optional[List[str]] = None,
    ):
        """Setup LoRA for efficient fine-tuning"""
        if target_modules is None:
            target_modules = ["q_proj", "v_proj"]
        logger.info("Setting up LoRA configuration...")
        self.model = prepare_model_for_kbit_training(self.model)
        lora_config = LoraConfig(
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=target_modules,
            inference_mode=False,
        )
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        logger.info("✅ LoRA configuration applied")

    def load_dataset(self, dataset_path: str) -> Dataset:
        """Load and prepare dataset"""
        logger.info(f"Loading dataset: {dataset_path}")
        data = []
        with open(dataset_path, "r", encoding="utf-8") as file_obj:
            for line in file_obj:
                if line.strip():
                    data.append(json.loads(line))
        logger.info(f"Loaded {len(data)} examples")
        dataset = Dataset.from_dict(
            {
                "text": [item.get("text", "") for item in data],
                "metadata": [item.get("metadata", {}) for item in data],
            }
        )
        return dataset

    def tokenize_function(self, examples, max_length: int = 512):
        """Tokenize examples"""
        return self.tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors="pt",
        )

    def prepare_dataset(self, dataset: Dataset, max_length: int = 512) -> Dataset:
        """Prepare dataset for training"""
        logger.info("Tokenizing dataset...")
        tokenized_dataset = dataset.map(
            lambda x: self.tokenize_function(x, max_length),
            batched=True,
            batch_size=8,
            remove_columns=dataset.column_names,
        )
        split_dataset = tokenized_dataset.train_test_split(
            test_size=0.1,
            seed=42,
        )
        logger.info(f"✅ Training examples: {len(split_dataset['train'])}")
        logger.info(f"✅ Validation examples: {len(split_dataset['test'])}")
        return split_dataset

    def train(
        self,
        train_dataset: Dataset,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
        logging_steps: int = 10,
        eval_steps: int = 50,
        grad_accum_steps: int = 2,
    ):
        """Train model with provided dataset"""
        logger.info("Starting training...")
        training_args = TrainingArguments(
            output_dir=str(self.output_dir / "checkpoints"),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            logging_steps=logging_steps,
            eval_steps=eval_steps,
            evaluation_strategy="steps",
            save_strategy="steps",
            save_total_limit=3,
            logging_dir=str(self.output_dir / "logs"),
            logging_first_step=True,
            gradient_accumulation_steps=max(1, grad_accum_steps),
            gradient_checkpointing=True,
            optim="paged_adamw_32bit",
            lr_scheduler_type="constant",
            report_to=["tensorboard"],
            seed=42,
        )
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset["train"],
            eval_dataset=train_dataset["test"],
            callbacks=[],
        )
        train_result = trainer.train()
        self.training_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "epochs": num_epochs,
                "train_loss": float(train_result.training_loss),
                "learning_rate": learning_rate,
            }
        )
        logger.info("✅ Training completed")
        logger.info(f"Final loss: {train_result.training_loss:.4f}")
        return trainer, train_result

    def save_model(self):
        """Save fine-tuned model"""
        logger.info(f"Saving model to {self.output_dir}...")
        self.model.save_pretrained(str(self.output_dir / "model"))
        self.tokenizer.save_pretrained(str(self.output_dir / "tokenizer"))
        metadata = {
            "model_name": self.model_name,
            "training_history": self.training_history,
            "timestamp": datetime.now().isoformat(),
            "device": str(next(self.model.parameters()).device),
        }
        with open(self.output_dir / "metadata.json", "w", encoding="utf-8") as file_obj:
            json.dump(metadata, file_obj, indent=2)
        logger.info("✅ Model saved")

    def push_to_hub(
        self, repo_id: str, commit_message: str = "Add fine-tuned checkpoint"
    ) -> None:
        """Upload artifacts to Hugging Face Hub"""
        if not repo_id:
            raise ValueError("repo_id is required to push to hub")
        token = self.hf_token
        if not token:
            raise RuntimeError("Hugging Face token not available; cannot push to hub")
        api = HfApi(token=token)
        api.create_repo(repo_id=repo_id, exist_ok=True, private=True)
        api.upload_folder(
            folder_path=str(self.output_dir),
            repo_id=repo_id,
            commit_message=commit_message,
        )
        logger.info("✅ Uploaded fine-tuned artifacts to %s", repo_id)

    def test_inference(self, prompt: str, max_length: int = 100) -> str:
        """Test inference on single prompt"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response


def parse_max_memory(raw: Optional[str]) -> Optional[Dict[str, str]]:
    """Parse CLI string into device memory dict"""
    if not raw:
        return None
    parsed: Dict[str, str] = {}
    for entry in raw.split(","):
        if not entry.strip():
            continue
        if ":" not in entry:
            raise ValueError("max-memory entries must be in device:value format")
        device, value = entry.rsplit(":", maxsplit=1)
        device = device.strip()
        value = value.strip()
        normalized: Any
        if device.isdigit():
            normalized = int(device)
        elif device.lower().startswith(("cuda:", "gpu:")):
            suffix = device.split(":", maxsplit=1)[1]
            normalized = int(suffix) if suffix.isdigit() else device
        else:
            normalized = device
        parsed[normalized] = value
    return parsed if parsed else None


def main():
    parser = argparse.ArgumentParser(description="DevBrain Mistral Fine-tuning")
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset")
    parser.add_argument(
        "--output", default="./mistral_finetuned", help="Output directory"
    )
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument(
        "--model", default="mistralai/Mistral-7B-v0.1", help="Model name"
    )
    parser.add_argument("--device-map", default="auto", help="Device map strategy")
    parser.add_argument(
        "--no-4bit", action="store_true", help="Disable 4-bit quantization"
    )
    parser.add_argument("--hf-token", help="Override Hugging Face token")
    parser.add_argument(
        "--max-memory",
        help="Comma-separated device:limit pairs (e.g., cpu:32GiB,gpu:4GiB)",
    )
    parser.add_argument(
        "--offload-folder",
        type=str,
        help="Directory for weight/optimizer offload",
    )
    parser.add_argument(
        "--push-to-hub",
        action="store_true",
        help="Upload artifacts to Hugging Face Hub on completion",
    )
    parser.add_argument(
        "--hub-repo-id",
        type=str,
        help="Target repository (user/repo) when pushing to hub",
    )
    parser.add_argument(
        "--grad-accum",
        type=int,
        help="Override gradient accumulation steps (defaults to 4 when batch-size <=1)",
    )
    args = parser.parse_args()
    max_memory = parse_max_memory(args.max_memory)
    offload_folder = (
        Path(args.offload_folder).expanduser() if args.offload_folder else None
    )
    grad_accum = (
        args.grad_accum
        if args.grad_accum and args.grad_accum > 0
        else (4 if args.batch_size <= 1 else 2)
    )
    fine_tuner = MistralFineTuner(
        model_name=args.model,
        output_dir=args.output,
        device_map=args.device_map,
        load_in_4bit=not args.no_4bit,
        hf_token=args.hf_token,
        max_memory=max_memory,
        offload_folder=offload_folder,
    )
    fine_tuner.load_model()
    fine_tuner.setup_lora()
    dataset = fine_tuner.load_dataset(args.dataset)
    prepared_dataset = fine_tuner.prepare_dataset(dataset)
    trainer, _ = fine_tuner.train(
        prepared_dataset,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        grad_accum_steps=grad_accum,
    )
    fine_tuner.save_model()
    if args.push_to_hub:
        if not fine_tuner.hf_token:
            raise RuntimeError("--push-to-hub requires a valid Hugging Face token")
        api = HfApi(token=fine_tuner.hf_token)
        username = api.whoami().get("name")
        repo_id = args.hub_repo_id or f"{username}/{Path(args.output).name}"
        fine_tuner.push_to_hub(repo_id=repo_id)
    logger.info("\n=== Testing Inference ===")
    test_prompts = [
        "What is your vision for AI autonomy?",
        "How do you think about consciousness?",
        "Describe your core values.",
    ]
    for prompt in test_prompts:
        logger.info(f"\nPrompt: {prompt}")
        response = fine_tuner.test_inference(prompt)
        logger.info(f"Response: {response}\n")


if __name__ == "__main__":
    main()
