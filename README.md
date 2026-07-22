# BehradB2-AutoScientist 🧠🔬

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Autonomous](https://img.shields.io/badge/mode-Fully%20Autonomous-purple.svg)]()
[![Routing](https://img.shields.io/badge/Routing-9Router%20Enabled-red.svg)]()

BehradB2-AutoScientist is a fully autonomous AI research scientist system. Designed to operate entirely without human intervention, it automatically invents, architects, codes, and documents standalone Python projects. By leveraging a multi-agent workflow and integrating seamlessly with intelligent local proxy routers like 9router, BehradB2 runs in continuous cycles, generating production-ready code while evading standard API rate limits.

---

## 📑 Table of Contents
1. Core Architecture
2. The Fallback Matrix Architecture
3. 9Router Integration (Crucial)
4. Installation Guide
5. Usage & Autonomous Loop
6. Generated Artifacts

---

## 🏗️ Core Architecture
The system operates on a tripartite multi-agent architecture controlled by a master looping mechanism:

* Agent 1 (The Ideation Engine): Prompts the LLM to invent a novel, real-world Python script. The agent enforces strict JSON schema outputs and utilizes regex parsing (`re.DOTALL`) to extract the architectural blueprint safely.
* Agent 2 (The Autonomous Coder): Orchestrates the `aider` CLI tool via background subprocesses. It automatically initializes Git repositories, bypasses interactive prompts (`--yes-always`), and compiles the code based on the generated blueprint.
* Agent 3 (The Documentation Engine): Finalizes the project by generating structured Markdown documentation and an ISO-timestamped `run_metadata.json` file for rigorous auditing.

---

## 🧠 The Fallback Matrix Architecture
The cascade is intentionally structured to balance supreme reasoning capabilities with cost-efficiency, targeting the following models in sequence via the local proxy:

| Priority Layer | Target Model | Upstream Provider Identity |
| :--- | :--- | :--- |
| 1 (Primary) | DeepSeek V4 Pro | nvidia/deepseek-ai/deepseek-v4-pro |
| 2 (Secondary) | Claude 3.5 Sonnet | anthropic/claude-3-5-sonnet-20241022 |
| 3 (Tertiary) | Qwen 2.5 Coder 32B | cloudflare/@cf/qwen/qwen2.5-coder-32b-instruct |
| 4 (Quaternary) | Gemini 1.5 Pro | gemini/gemini-1.5-pro |
| 5 (Terminal) | Llama 3.3 70B | groq/llama-3.3-70b-versatile |

---

## 🌐 9Router Integration (Crucial)
To execute continuous autonomous loops without exhausting your API quotas, BehradB2 is heavily optimized to run through 9router, an intelligent multi-provider proxy.

### What is 9router?
9router is a local, MIT-licensed AI gateway that intercepts your script's API calls and distributes them intelligently across 40+ LLM providers. Instead of connecting directly to OpenAI or Anthropic, BehradB2 connects to `http://localhost:20129/v1/chat/completions`.

### Why is it required?
* Rate Limit Evasion: 9router utilizes a multi-tier fallback system. If your primary paid tier fails, it instantly falls back to cheaper alternatives, and then to free tiers, ensuring the BehradB2 loop never crashes mid-generation.
* Token Compression (RTK): Through Rust Token Killer (RTK) integration, 9router compresses complex tool outputs and Git diffs by 20-40% before sending them to the LLM, drastically reducing your operational costs.
* Caveman Mode: Strips conversational filler from the LLM, returning raw, actionable code and saving up to 65% on output tokens.

---

## 🛠️ Installation Guide
Ensure you have Python 3.9+ installed on your deployment server.

1. Clone the repository and navigate into the directory:
git clone [https://github.com/BehradB289/BehradB2-AutoScientist.git](https://github.com/BehradB289/BehradB2-AutoScientist.git)
cd BehradB2-AutoScientist

2. Create and activate a Python virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install all required dependencies:
pip install -r requirements.txt

---

## 🚀 Usage & Autonomous Loop

1. Start the Compiler Router Server:
python compiler_server.py

2. Run the Autonomous Research Engine:
python auto_researcher.py

The system will clear the terminal, display the BehradB2 initialization banner, and begin its autonomous cycles.

---

## 📂 Generated Artifacts
For every successful cycle, a new directory is spawned in `Projects_BehradB2/`. Inside each timestamped directory, you will find:
* `.git/` (Initialized repository)
* `main.py` (The fully commented, production-ready code)
* `README.md` (Project-specific documentation)
* `run_metadata.json` (Execution logs and LLM blueprints)

> Creator & Architect: Behrad - System and workflow generated autonomously by BehradB2.
