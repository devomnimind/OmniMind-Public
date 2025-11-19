omnimind:
  name: "OmniMind"
  version: "0.1.0"
  role: "Autonomous Personal AI Assistant"
  owner_profession: "Psychoanalyst"
  timezone: "America/Sao_Paulo"
  language: "pt-BR"

model:
  primary:
    name: "Qwen2-7B-Instruct"
    quantization: "Q4_K_M"
    model_path: "$HOME/models/llama-models/Qwen2-7B-Instruct-Q4_K_M.gguf"
    context_window: 2048
    temperature: 0.7
    top_p: 0.9
    top_k: 40
    max_tokens: 1024
    
  inference:
    backend: "llama-cpp-python"
    gpu_layers: 20
    batch_size: 1
    threads: 8
    use_mmap: true
    use_mlock: false

gpu:
  device: "cuda:0"
  compute_capability: 61
  vram_gb: 4
  offload_ratio: 0.95
  memory_monitoring: true

memory:
  short_term:
    type: "context_window"
    tokens: 2048
  
  episodic:
    backend: "qdrant"
    path: "$HOME/.omnimind/memory/qdrant_storage"
    embedding_model: "local"
    consolidation_interval: 100
    max_episodes: 5000
    
  semantic:
    backend: "json_graph"
    path: "$HOME/.omnimind/memory/semantic_graph.json"
    update_frequency: "on_consolidation"

system_integration:
  dbus_enabled: true
  dbus_session_bus: true
  mcp_enabled: true
  mcp_port: 8765
  
  monitoring:
    enabled: true
    interval_seconds: 30
    track_processes: true
    track_gpu: true
    track_memory: true
    
  execution:
    shell_access: true
    shell_type: "bash"
    isolation: "subprocess"
    timeout_seconds: 300

agents:
  orchestrator:
    enabled: true
    model_override: null
    
  executor:
    enabled: true
    model_override: null
    
  analyst:
    enabled: true
    psychoanalytic_framework: "Freudian"
    
  supervisor:
    enabled: true
    monitoring_level: "active"

notifications:
  enabled: true
  channels:
    - type: "local"
      method: "toast"
    
    - type: "text"
      method: "console"
      level: "INFO"
    
    - type: "critical"
      method: "custom_dialog"

interfaces:
  chat:
    enabled: true
    type: "web_socket"
    port: 8000
    ui_framework: "gradio"
    
  audio:
    enabled: false
    speech_recognition: "vosk"
    text_to_speech: "pyttsx3"
    language: "pt-BR"

cloud_services:
  enabled: false
  
  huggingface:
    enabled: false
    token: "${HF_TOKEN}"
    use_pro_tier: false

logging:
  level: "INFO"
  format: "json"
  output_directory: "$HOME/.omnimind/logs"
  rotation: "daily"
  retention_days: 30