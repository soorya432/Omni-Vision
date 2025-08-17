OmniVision

Unified Cognitive Vision Intelligence System

Overview

OmniVision is a research-driven framework for multimodal cognitive AI. It integrates computer vision, natural language processing, and behavioral analytics into a single system capable of perception, reasoning, and interaction.

The platform supports tasks ranging from real-time monitoring and decision support to applied research in education, healthcare, and defense. OmniVision is designed as a modular system, but all modules operate under one unified architecture.

Features

Vision Core (YOLOv8 + custom layers): Object detection, OCR, anomaly detection.

Cognitive Brain Module (brain/): Fusion of vision + NLP pipelines for contextual reasoning.

GUI Application (gui.py): Interactive desktop interface for real-time testing and evaluation.

Configuration (config.py): Centralized settings for model selection, thresholds, and runtime parameters.

Patching Utilities: Self-contained patches (patch_fix_gui.py, patch_fix_analyze.py, etc.) to update/extend components without rewriting core code.

Evaluation-Only Licensing: Distributed under a restrictive evaluation license to enable testing without risk of derivative misuse.

Repository Structure
omnivision/
├── brain/                 # Core AI modules (vision + NLP integration)
├── models/                # Model checkpoints, pretrained weights
├── outputs/               # Inference and evaluation results
├── utils/                 # Utility functions and helpers
├── config.py              # System configuration
├── gui.py                 # Main GUI application
├── gui_backup_ai_only.py  # Backup GUI (AI-only mode)
├── main.py                # Entry point for running system
├── patches/               # Hotfix scripts (patch_* files)
├── yolov8n.pt             # YOLOv8 model weights
├── LICENSE                # Evaluation-only license
├── Makefile               # Common tasks (setup, train, run, clean)
├── requirements.txt       # Python dependencies
├── RUN.file               # Runtime notes
├── README.md              # Documentation
└── CONTRIBUTING.md        # Contribution guidelines

Installation
Prerequisites

Python 3.10+

CUDA-capable GPU (recommended for real-time performance)

pip and virtualenv

Setup
git clone https://github.com/<your-org>/omnivision.git
cd omnivision
make setup

Usage

Run the main desktop application:

make run       # Windows
make run-sh    # Linux/macOS


Run training:

make train


Clean artifacts:

make clean

License

OmniVision is distributed under the OmniVision Evaluation License v1.0.

Free for testing and evaluation.

Redistribution, modification, or derivative use is strictly prohibited.

Commercial or institutional licensing inquiries: sooryakiranrocks@gmail.com .
Author

Soorya Kiran
Developer of AI systems under the AANSC initiative