#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

def test_model():
    print("=" * 60)
    print("   OmniMind - Teste do Modelo")
    print("=" * 60)
    print("")
    
    MODEL_PATH = os.path.expanduser(
        "~/models/llama-models/Qwen2-7B-Instruct-Q4_K_M.gguf"
    )
    
    if not os.path.exists(MODEL_PATH):
        print(f"Erro: Modelo nao encontrado: {MODEL_PATH}")
        return False
    
    print(f"Modelo: {MODEL_PATH}")
    print(f"Tamanho: {os.path.getsize(MODEL_PATH) / 1024**3:.1f}GB")
    print("")
    
    try:
        from llama_cpp import Llama
        
        print("Carregando modelo...")
        start = time.time()
        
        llm = Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=20,
            n_ctx=2048,
            n_threads=8,
            verbose=False
        )
        
        load_time = time.time() - start
        print(f"Tempo de carregamento: {load_time:.1f}s")
        print("")
        
        print("Teste de inferencia...")
        prompt = "Ola, como voce funciona? Responda em portugues."
        
        print(f"Prompt: {prompt}")
        print("")
        print("Resposta:")
        print("-" * 60)
        
        start = time.time()
        response = llm(
            prompt,
            max_tokens=128,
            temperature=0.7,
            top_p=0.9
        )
        inference_time = time.time() - start
        
        print(response['choices'][0]['text'])
        print("-" * 60)
        
        tokens = response['usage']['completion_tokens']
        tps = tokens / inference_time
        
        print("")
        print(f"Tempo: {inference_time:.1f}s ({tokens} tokens)")
        print(f"Performance: {tps:.1f} tokens/segundo")
        print("")
        
        if tps > 3:
            print("SUCESSO: Performance excelente!")
        
        print("=" * 60)
        print("TESTE CONCLUIDO COM SUCESSO!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model()
    sys.exit(0 if success else 1)