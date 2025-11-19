#!/usr/bin/env python3
import argparse
import glob
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetCollector:
    """Coleta dados pessoais para fine-tuning"""

    def __init__(self, output_path: str = "datasets/personal_corpus.jsonl") -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.examples: List[Dict] = []
        self.created_at = datetime.utcnow()

    def collect_chat_history(self, chat_file: str) -> List[Dict]:
        """Coleta histórico de conversas"""
        logger.info(f"Coletando chat history: {chat_file}")
        examples: List[Dict] = []
        try:
            with open(chat_file, "r") as file_obj:
                for line in file_obj:
                    try:
                        entry = json.loads(line)
                        if "text" in entry or "message" in entry:
                            text = entry.get("text") or entry.get("message")
                            examples.append(
                                {
                                    "text": text,
                                    "source": "chat_history",
                                    "timestamp": entry.get("timestamp", ""),
                                }
                            )
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            logger.warning(f"Chat file not found: {chat_file}")
        logger.info(f"✅ Collected {len(examples)} chat examples")
        return examples

    def collect_documents(self, doc_dir: str) -> List[Dict]:
        """Coleta documentos texto"""
        logger.info(f"Coletando documentos: {doc_dir}")
        examples: List[Dict] = []
        for txt_file in glob.glob(f"{doc_dir}/**/*.txt", recursive=True):
            try:
                with open(txt_file, "r", encoding="utf-8", errors="ignore") as file_obj:
                    content = file_obj.read()
                paragraphs = content.split("\n\n")
                for para in paragraphs:
                    if len(para.strip()) > 50:
                        examples.append(
                            {
                                "text": para.strip(),
                                "source": "document",
                                "filename": os.path.basename(txt_file),
                            }
                        )
            except Exception as e:
                logger.warning(f"Error reading {txt_file}: {e}")
        logger.info(f"✅ Collected {len(examples)} document examples")
        return examples

    def collect_voice_transcripts(self, transcript_dir: str) -> List[Dict]:
        """Coleta transcrições de voz"""
        logger.info(f"Coletando transcrições: {transcript_dir}")
        examples: List[Dict] = []
        for json_file in glob.glob(f"{transcript_dir}/**/*.json", recursive=True):
            try:
                with open(json_file, "r") as file_obj:
                    data = json.load(file_obj)
                if isinstance(data, dict) and "text" in data:
                    examples.append(
                        {
                            "text": data["text"],
                            "source": "voice_transcript",
                            "confidence": data.get("confidence", 0.0),
                        }
                    )
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "text" in item:
                            examples.append(
                                {"text": item["text"], "source": "voice_transcript"}
                            )
            except Exception as e:
                logger.warning(f"Error reading {json_file}: {e}")
        logger.info(f"✅ Collected {len(examples)} transcript examples")
        return examples

    def save_dataset(self) -> None:
        """Salva dataset em formato JSONL"""
        logger.info(f"Salvando dataset: {self.output_path}")
        with open(self.output_path, "w") as file_obj:
            for example in self.examples:
                file_obj.write(json.dumps(example) + "\n")
        logger.info(f"✅ Saved {len(self.examples)} examples to {self.output_path}")

    def validate(self) -> bool:
        """Valida qualidade do dataset"""
        if not self.examples:
            logger.error("❌ Dataset is empty!")
            return False
        if len(self.examples) < 50:
            logger.warning(
                f"⚠️ Dataset has only {len(self.examples)} examples (target: ≥50)"
            )
        avg_length = sum(len(ex.get("text", "")) for ex in self.examples) / len(
            self.examples
        )
        logger.info(f"Average text length: {avg_length:.0f} chars")
        if avg_length < 50:
            logger.warning("⚠️ Average text too short")
        sources: Dict[str, int] = {}
        for example in self.examples:
            source = example.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        logger.info("Dataset composition:")
        for source, count in sources.items():
            logger.info(f" {source}: {count}")
        return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat", help="Chat history file")
    parser.add_argument("--docs", help="Documents directory")
    parser.add_argument("--transcripts", help="Transcripts directory")
    parser.add_argument("--output", default="datasets/personal_corpus.jsonl")
    args = parser.parse_args()
    collector = DatasetCollector(args.output)
    if args.chat:
        collector.examples.extend(collector.collect_chat_history(args.chat))
    if args.docs:
        collector.examples.extend(collector.collect_documents(args.docs))
    if args.transcripts:
        collector.examples.extend(collector.collect_voice_transcripts(args.transcripts))
    if not collector.examples:
        logger.info("No data sources provided. Adding example data...")
        collector.examples = [
            {
                "text": "I believe AI should be transparent, ethical, and respectful of h",
                "source": "manual",
            },
            {
                "text": "My approach to problem-solving is systematic and creative.",
                "source": "manual",
            },
            {
                "text": "I value privacy, learning, and meaningful connections.",
                "source": "manual",
            },
        ]
    collector.validate()
    collector.save_dataset()


if __name__ == "__main__":
    main()
