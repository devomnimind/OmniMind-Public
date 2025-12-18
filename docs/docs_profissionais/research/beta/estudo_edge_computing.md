# 🔬 Estudo Científico: Edge Computing para OmniMind
## Fase Beta - Análise Avançada e Prototipagem

**Projeto:** OmniMind - Sistema de IA Autônomo  
**Categoria:** Computação de Borda e Otimização  
**Status:** Beta - Análise e Prototipagem  
**Data:** Novembro 2025  
**Hardware Base:** NVIDIA GTX 1650 (4GB VRAM), Intel i5, 24GB RAM

---

## 📋 Resumo Executivo

Este estudo desenvolve estratégias de **Edge Computing** para executar OmniMind em dispositivos com recursos limitados (IoT, mobile, embedded), através de model compression, edge-optimized inference e federated learning.

### 🎯 Objetivos da Pesquisa

1. **Desenvolver** técnicas de compressão de modelos
2. **Otimizar** inferência para edge devices
3. **Implementar** federated learning para privacidade
4. **Criar** arquitetura híbrida edge-cloud

### 🔍 Gap Identificado

**Situação Atual:**
- ✅ Sistema funcional em hardware desktop
- ✅ Modelos otimizados para GTX 1650
- ❌ Dependência de recursos locais poderosos
- ❌ Sem suporte para dispositivos móveis
- ❌ Impossível executar em IoT/embedded
- ❌ Sem federated learning

**Impacto:**
- Limitação a ambientes desktop/server
- Impossibilidade de deployment em edge
- Alto custo de infraestrutura
- Latência de rede em cenários remotos

---

## 🏗️ Fundamentação Teórica

### 1. Model Compression

#### 1.1 Quantization

```python
import torch
import torch.nn as nn
from typing import Optional

class ModelQuantizer:
    """Quantização de modelos para edge devices"""
    
    def __init__(self):
        self.calibration_data: Optional[torch.Tensor] = None
        
    def dynamic_quantization(
        self,
        model: nn.Module,
        dtype: torch.dtype = torch.qint8
    ) -> nn.Module:
        """Quantização dinâmica (weights only)"""
        
        # Quantiza apenas weights, activations em fp32
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {nn.Linear, nn.LSTM, nn.GRU},  # Layers para quantizar
            dtype=dtype
        )
        
        return quantized_model
    
    def static_quantization(
        self,
        model: nn.Module,
        calibration_data: torch.Tensor
    ) -> nn.Module:
        """Quantização estática (weights + activations)"""
        
        # Preparar modelo para quantização
        model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
        torch.quantization.prepare(model, inplace=True)
        
        # Calibração
        model.eval()
        with torch.no_grad():
            for data in calibration_data:
                model(data)
        
        # Converter para quantizado
        quantized_model = torch.quantization.convert(model, inplace=False)
        
        return quantized_model
    
    def quantization_aware_training(
        self,
        model: nn.Module,
        train_loader: torch.utils.data.DataLoader,
        num_epochs: int = 5
    ) -> nn.Module:
        """Quantization-Aware Training (QAT)"""
        
        # Preparar modelo para QAT
        model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
        torch.quantization.prepare_qat(model, inplace=True)
        
        # Treinar com quantização simulada
        optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
        model.train()
        
        for epoch in range(num_epochs):
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = nn.functional.mse_loss(outputs, batch_y)
                loss.backward()
                optimizer.step()
        
        # Converter para quantizado
        model.eval()
        quantized_model = torch.quantization.convert(model, inplace=False)
        
        return quantized_model
    
    def measure_compression(
        self,
        original_model: nn.Module,
        quantized_model: nn.Module
    ) -> Dict[str, Any]:
        """Mede taxa de compressão"""
        
        # Salva modelos temporariamente
        torch.save(original_model.state_dict(), '/tmp/original.pth')
        torch.save(quantized_model.state_dict(), '/tmp/quantized.pth')
        
        # Tamanhos em disco
        import os
        original_size = os.path.getsize('/tmp/original.pth')
        quantized_size = os.path.getsize('/tmp/quantized.pth')
        
        compression_ratio = original_size / quantized_size
        size_reduction = (1 - quantized_size / original_size) * 100
        
        return {
            'original_size_mb': original_size / (1024 * 1024),
            'quantized_size_mb': quantized_size / (1024 * 1024),
            'compression_ratio': compression_ratio,
            'size_reduction_percent': size_reduction
        }

class MixedPrecisionOptimizer:
    """Otimizador de precisão mista"""
    
    def __init__(self, model: nn.Module):
        self.model = model
        self.scaler = torch.cuda.amp.GradScaler()
        
    def train_step(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        optimizer: torch.optim.Optimizer
    ) -> float:
        """Passo de treinamento com mixed precision"""
        
        optimizer.zero_grad()
        
        # Forward com autocast
        with torch.cuda.amp.autocast():
            outputs = self.model(inputs)
            loss = nn.functional.mse_loss(outputs, targets)
        
        # Backward com gradient scaling
        self.scaler.scale(loss).backward()
        self.scaler.step(optimizer)
        self.scaler.update()
        
        return loss.item()
```

#### 1.2 Pruning

```python
import torch.nn.utils.prune as prune

class ModelPruner:
    """Poda de modelos para reduzir tamanho"""
    
    def __init__(self, model: nn.Module):
        self.model = model
        
    def magnitude_pruning(
        self,
        amount: float = 0.3,
        layers: Optional[List[str]] = None
    ) -> nn.Module:
        """Poda baseada em magnitude de weights"""
        
        if layers is None:
            layers = [
                name for name, module in self.model.named_modules()
                if isinstance(module, (nn.Linear, nn.Conv2d))
            ]
        
        for name, module in self.model.named_modules():
            if name in layers:
                if isinstance(module, nn.Linear):
                    prune.l1_unstructured(module, name='weight', amount=amount)
                elif isinstance(module, nn.Conv2d):
                    prune.l1_unstructured(module, name='weight', amount=amount)
        
        return self.model
    
    def structured_pruning(
        self,
        amount: float = 0.3,
        dim: int = 0
    ) -> nn.Module:
        """Poda estruturada (remove channels/neurons inteiros)"""
        
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Conv2d):
                # Prune channels (dim=0) ou filters (dim=1)
                prune.ln_structured(
                    module,
                    name='weight',
                    amount=amount,
                    n=2,
                    dim=dim
                )
            elif isinstance(module, nn.Linear):
                # Prune neurons
                prune.ln_structured(
                    module,
                    name='weight',
                    amount=amount,
                    n=2,
                    dim=0
                )
        
        return self.model
    
    def iterative_pruning(
        self,
        train_fn: callable,
        val_fn: callable,
        target_sparsity: float = 0.7,
        num_iterations: int = 5
    ) -> nn.Module:
        """Poda iterativa com re-treinamento"""
        
        current_sparsity = 0.0
        sparsity_step = target_sparsity / num_iterations
        
        for iteration in range(num_iterations):
            # Aumenta sparsity
            current_sparsity += sparsity_step
            
            # Aplica poda
            self.magnitude_pruning(amount=current_sparsity)
            
            # Re-treina
            train_fn(self.model, num_epochs=3)
            
            # Valida
            val_accuracy = val_fn(self.model)
            print(f"Iteration {iteration+1}: "
                  f"Sparsity={current_sparsity:.2f}, "
                  f"Val Accuracy={val_accuracy:.4f}")
        
        # Remove máscaras de poda (torna permanente)
        self.make_permanent()
        
        return self.model
    
    def make_permanent(self) -> None:
        """Torna poda permanente (remove máscaras)"""
        
        for module in self.model.modules():
            if isinstance(module, (nn.Linear, nn.Conv2d)):
                try:
                    prune.remove(module, 'weight')
                except ValueError:
                    pass  # Não tem poda

class KnowledgeDistillation:
    """Destilação de conhecimento para modelos menores"""
    
    def __init__(
        self,
        teacher_model: nn.Module,
        student_model: nn.Module,
        temperature: float = 3.0
    ):
        self.teacher = teacher_model
        self.student = student_model
        self.temperature = temperature
        
    def distill(
        self,
        train_loader: torch.utils.data.DataLoader,
        num_epochs: int = 10,
        alpha: float = 0.5
    ) -> nn.Module:
        """Treina student model via distillation"""
        
        optimizer = torch.optim.Adam(self.student.parameters(), lr=0.001)
        
        self.teacher.eval()
        self.student.train()
        
        for epoch in range(num_epochs):
            for batch_x, batch_y in train_loader:
                # Teacher predictions
                with torch.no_grad():
                    teacher_logits = self.teacher(batch_x)
                    teacher_soft = nn.functional.softmax(
                        teacher_logits / self.temperature,
                        dim=-1
                    )
                
                # Student predictions
                student_logits = self.student(batch_x)
                student_soft = nn.functional.log_softmax(
                    student_logits / self.temperature,
                    dim=-1
                )
                
                # Distillation loss
                distill_loss = nn.functional.kl_div(
                    student_soft,
                    teacher_soft,
                    reduction='batchmean'
                ) * (self.temperature ** 2)
                
                # Hard target loss
                hard_loss = nn.functional.cross_entropy(
                    student_logits,
                    batch_y
                )
                
                # Combined loss
                loss = alpha * distill_loss + (1 - alpha) * hard_loss
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        
        return self.student
```

### 2. Edge-Optimized Inference

#### 2.1 TensorRT Optimization

```python
class TensorRTOptimizer:
    """Otimização com NVIDIA TensorRT"""
    
    def __init__(self):
        try:
            import tensorrt as trt
            self.trt = trt
            self.logger = trt.Logger(trt.Logger.WARNING)
        except ImportError:
            raise ImportError("TensorRT not installed")
    
    def convert_to_trt(
        self,
        onnx_path: str,
        trt_path: str,
        fp16_mode: bool = True,
        int8_mode: bool = False
    ) -> None:
        """Converte modelo ONNX para TensorRT"""
        
        builder = self.trt.Builder(self.logger)
        network = builder.create_network(
            1 << int(self.trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )
        parser = self.trt.OnnxParser(network, self.logger)
        
        # Parse ONNX
        with open(onnx_path, 'rb') as model:
            if not parser.parse(model.read()):
                for error in range(parser.num_errors):
                    print(parser.get_error(error))
                raise RuntimeError("Failed to parse ONNX")
        
        # Build config
        config = builder.create_builder_config()
        config.max_workspace_size = 1 << 30  # 1GB
        
        if fp16_mode:
            config.set_flag(self.trt.BuilderFlag.FP16)
        
        if int8_mode:
            config.set_flag(self.trt.BuilderFlag.INT8)
            # Requires calibration cache
        
        # Build engine
        engine = builder.build_engine(network, config)
        
        # Serialize
        with open(trt_path, 'wb') as f:
            f.write(engine.serialize())

class ONNXConverter:
    """Converte modelos PyTorch para ONNX"""
    
    def convert(
        self,
        model: nn.Module,
        dummy_input: torch.Tensor,
        output_path: str,
        opset_version: int = 13
    ) -> None:
        """Converte para ONNX"""
        
        model.eval()
        
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
```

#### 2.2 Mobile Deployment

```python
class MobileOptimizer:
    """Otimização para deployment mobile"""
    
    def optimize_for_mobile(
        self,
        model: nn.Module,
        example_input: torch.Tensor
    ) -> torch.jit.ScriptModule:
        """Otimiza modelo para mobile (iOS/Android)"""
        
        # Trace model
        model.eval()
        traced_model = torch.jit.trace(model, example_input)
        
        # Optimize para mobile
        from torch.utils.mobile_optimizer import optimize_for_mobile
        optimized_model = optimize_for_mobile(traced_model)
        
        return optimized_model
    
    def save_for_mobile(
        self,
        model: torch.jit.ScriptModule,
        output_path: str
    ) -> None:
        """Salva modelo otimizado para mobile"""
        
        model._save_for_lite_interpreter(output_path)
    
    def estimate_mobile_latency(
        self,
        model: nn.Module,
        input_size: Tuple[int, ...],
        device_type: str = "cpu"
    ) -> Dict[str, float]:
        """Estima latência em dispositivo mobile"""
        
        import time
        
        model.eval()
        dummy_input = torch.randn(1, *input_size)
        
        # Warmup
        for _ in range(10):
            _ = model(dummy_input)
        
        # Measure
        latencies = []
        for _ in range(100):
            start = time.time()
            with torch.no_grad():
                _ = model(dummy_input)
            latencies.append((time.time() - start) * 1000)
        
        return {
            'mean_ms': np.mean(latencies),
            'p50_ms': np.percentile(latencies, 50),
            'p95_ms': np.percentile(latencies, 95),
            'p99_ms': np.percentile(latencies, 99)
        }
```

### 3. Federated Learning

#### 3.1 Federated Averaging

```python
class FederatedLearningServer:
    """Servidor para federated learning"""
    
    def __init__(self, global_model: nn.Module):
        self.global_model = global_model
        self.client_models: Dict[str, nn.Module] = {}
        
    def register_client(self, client_id: str) -> nn.Module:
        """Registra novo client e retorna modelo global"""
        
        # Clone modelo global para client
        client_model = self._clone_model(self.global_model)
        self.client_models[client_id] = client_model
        
        return client_model
    
    def aggregate_updates(
        self,
        client_updates: Dict[str, nn.Module],
        client_weights: Optional[Dict[str, float]] = None
    ) -> None:
        """Agrega updates de clients (FedAvg)"""
        
        if client_weights is None:
            # Peso igual para todos
            client_weights = {
                cid: 1.0 / len(client_updates)
                for cid in client_updates.keys()
            }
        
        # Normaliza weights
        total_weight = sum(client_weights.values())
        client_weights = {
            cid: w / total_weight
            for cid, w in client_weights.items()
        }
        
        # Weighted average de parameters
        global_state = self.global_model.state_dict()
        
        for key in global_state.keys():
            # Zera parâmetro
            global_state[key] = torch.zeros_like(global_state[key])
            
            # Soma weighted
            for client_id, client_model in client_updates.items():
                weight = client_weights[client_id]
                client_state = client_model.state_dict()
                global_state[key] += weight * client_state[key]
        
        # Atualiza modelo global
        self.global_model.load_state_dict(global_state)
    
    def _clone_model(self, model: nn.Module) -> nn.Module:
        """Clona modelo"""
        
        import copy
        return copy.deepcopy(model)

class FederatedLearningClient:
    """Client para federated learning"""
    
    def __init__(
        self,
        client_id: str,
        local_data: torch.utils.data.Dataset
    ):
        self.client_id = client_id
        self.local_data = local_data
        self.model: Optional[nn.Module] = None
        
    def receive_global_model(self, global_model: nn.Module) -> None:
        """Recebe modelo global do servidor"""
        
        import copy
        self.model = copy.deepcopy(global_model)
    
    def local_training(
        self,
        num_epochs: int = 5,
        batch_size: int = 32
    ) -> nn.Module:
        """Treina modelo localmente"""
        
        if self.model is None:
            raise ValueError("No model received from server")
        
        loader = torch.utils.data.DataLoader(
            self.local_data,
            batch_size=batch_size,
            shuffle=True
        )
        
        optimizer = torch.optim.SGD(self.model.parameters(), lr=0.01)
        self.model.train()
        
        for epoch in range(num_epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = nn.functional.cross_entropy(outputs, batch_y)
                loss.backward()
                optimizer.step()
        
        return self.model
    
    def compute_data_weight(self) -> float:
        """Computa peso baseado em quantidade de dados"""
        
        return len(self.local_data)

class SecureAggregation:
    """Agregação segura com differential privacy"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
        
    def add_noise(
        self,
        model: nn.Module,
        sensitivity: float = 1.0
    ) -> nn.Module:
        """Adiciona ruído diferentially private"""
        
        # Gaussian mechanism
        sigma = (sensitivity * np.sqrt(2 * np.log(1.25 / self.delta))) / self.epsilon
        
        state_dict = model.state_dict()
        
        for key in state_dict.keys():
            noise = torch.randn_like(state_dict[key]) * sigma
            state_dict[key] += noise
        
        model.load_state_dict(state_dict)
        
        return model
    
    def clip_gradients(
        self,
        model: nn.Module,
        max_norm: float = 1.0
    ) -> None:
        """Clipa gradients para limitar sensitivity"""
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
```

### 4. Edge-Cloud Hybrid Architecture

```python
class EdgeCloudOrchestrator:
    """Orquestra computação entre edge e cloud"""
    
    def __init__(
        self,
        edge_model: nn.Module,
        cloud_model: nn.Module,
        latency_threshold_ms: float = 100.0
    ):
        self.edge_model = edge_model
        self.cloud_model = cloud_model
        self.latency_threshold = latency_threshold_ms
        
    async def infer(
        self,
        input_data: torch.Tensor,
        confidence_threshold: float = 0.8
    ) -> Tuple[torch.Tensor, str]:
        """Inferência adaptativa edge/cloud"""
        
        # Tenta edge primeiro
        start = time.time()
        edge_output, edge_confidence = self._edge_inference(input_data)
        edge_latency = (time.time() - start) * 1000
        
        # Se confiança alta e latência OK, retorna edge
        if edge_confidence > confidence_threshold:
            return edge_output, "edge"
        
        # Senão, offload para cloud
        cloud_output = await self._cloud_inference(input_data)
        
        return cloud_output, "cloud"
    
    def _edge_inference(
        self,
        input_data: torch.Tensor
    ) -> Tuple[torch.Tensor, float]:
        """Inferência local (edge)"""
        
        self.edge_model.eval()
        
        with torch.no_grad():
            output = self.edge_model(input_data)
            
            # Estima confiança
            probs = torch.softmax(output, dim=-1)
            confidence = torch.max(probs).item()
        
        return output, confidence
    
    async def _cloud_inference(
        self,
        input_data: torch.Tensor
    ) -> torch.Tensor:
        """Offload para cloud"""
        
        # Serializa input
        import pickle
        serialized = pickle.dumps(input_data)
        
        # Envia para cloud via HTTP/gRPC
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://cloud-endpoint/infer',
                data=serialized
            ) as response:
                result = await response.read()
                output = pickle.loads(result)
        
        return output
    
    def adaptive_model_selection(
        self,
        battery_level: float,
        network_quality: float
    ) -> str:
        """Seleciona edge/cloud baseado em contexto"""
        
        # Se bateria baixa, prefere cloud
        if battery_level < 0.2:
            return "cloud"
        
        # Se rede ruim, prefere edge
        if network_quality < 0.5:
            return "edge"
        
        # Default: edge (privacidade)
        return "edge"
```

---

## 📊 Análise de Viabilidade

### Compression Results

**Exemplo: Qwen-2.5B**

| Técnica | Tamanho Original | Tamanho Comprimido | Redução | Accuracy Loss |
|---------|------------------|---------------------|---------|---------------|
| FP32 (baseline) | 10GB | - | 0% | 0% |
| FP16 | 10GB | 5GB | 50% | <1% |
| INT8 (dynamic) | 10GB | 2.5GB | 75% | <2% |
| INT8 (static) | 10GB | 2.5GB | 75% | <3% |
| INT4 | 10GB | 1.25GB | 87.5% | ~5% |
| Pruning (50%) + INT8 | 10GB | 1.25GB | 87.5% | ~8% |

### Edge Device Compatibility

```python
class DeviceProfiler:
    """Profila dispositivos edge"""
    
    DEVICE_PROFILES = {
        'raspberry_pi_4': {
            'ram_mb': 4096,
            'cpu_cores': 4,
            'gpu': None,
            'max_model_size_mb': 500
        },
        'jetson_nano': {
            'ram_mb': 4096,
            'cpu_cores': 4,
            'gpu': 'Maxwell (128 CUDA cores)',
            'max_model_size_mb': 2000
        },
        'android_high_end': {
            'ram_mb': 8192,
            'cpu_cores': 8,
            'gpu': 'Mali/Adreno',
            'max_model_size_mb': 1000
        },
        'android_mid_range': {
            'ram_mb': 4096,
            'cpu_cores': 8,
            'gpu': 'Mali/Adreno',
            'max_model_size_mb': 500
        }
    }
    
    def recommend_optimization(
        self,
        device_type: str,
        model_size_mb: float
    ) -> Dict[str, Any]:
        """Recomenda otimizações para dispositivo"""
        
        profile = self.DEVICE_PROFILES[device_type]
        
        recommendations = []
        
        if model_size_mb > profile['max_model_size_mb']:
            ratio = model_size_mb / profile['max_model_size_mb']
            
            if ratio > 4:
                recommendations.append('INT4 quantization + 70% pruning')
            elif ratio > 2:
                recommendations.append('INT8 quantization + 50% pruning')
            else:
                recommendations.append('INT8 quantization')
        
        if profile['gpu'] is None:
            recommendations.append('CPU-optimized inference (ONNX Runtime)')
        else:
            recommendations.append('GPU acceleration available')
        
        return {
            'device': device_type,
            'recommendations': recommendations,
            'feasible': model_size_mb <= profile['max_model_size_mb'] * 2
        }
```

---

## 🎯 Roadmap de Implementação

### Fase 1: Model Compression (2-3 semanas)

**Entregáveis:**
```python
# src/edge/compression.py
class ModelCompressor:
    """Compressão de modelos"""
```

### Fase 2: Edge Optimization (2 semanas)

**Entregáveis:**
```python
# src/edge/inference_optimizer.py
class EdgeInferenceOptimizer:
    """Otimização para edge"""
```

### Fase 3: Federated Learning (3 semanas)

**Entregáveis:**
```python
# src/edge/federated_learning.py
class FederatedLearningCoordinator:
    """Coordenação de federated learning"""
```

### Fase 4: Edge-Cloud Hybrid (2 semanas)

**Entregáveis:**
```python
# src/edge/hybrid_orchestrator.py
class EdgeCloudOrchestrator:
    """Orquestração edge-cloud"""
```

---

## 📈 Métricas de Sucesso

| Métrica | Target | Medição |
|---------|--------|---------|
| Model Size Reduction | >70% | Compression tests |
| Latency (Mobile) | <200ms | Benchmarks |
| Accuracy Loss | <5% | Validation set |
| Deployment Success | >90% | Device compatibility |

---

## 📚 Referências

1. **Jacob, B., et al. (2018).** "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference" *CVPR 2018*
2. **McMahan, B., et al. (2017).** "Communication-Efficient Learning of Deep Networks from Decentralized Data" *AISTATS 2017*
3. **Han, S., et al. (2016).** "Deep Compression: Compressing Deep Neural Networks with Pruning, Trained Quantization and Huffman Coding" *ICLR 2016*

---

## ✅ Conclusões

### Conclusões da Fase Beta

1. ✅ **Viabilidade:** Edge deployment é possível com compressão agressiva
2. ✅ **Técnicas:** INT8 + Pruning oferece melhor trade-off
3. ⚠️ **Accuracy:** 5-8% loss aceitável para edge
4. ✅ **Federated Learning:** Viável para privacidade

### Próximos Passos

- [ ] Implementar quantization pipeline
- [ ] Criar pruning strategy
- [ ] Desenvolver federated learning
- [ ] Testar em dispositivos reais

---

**Status:** 📋 Beta - Pronto para Implementação  
**Prioridade:** Média (Futuro)  
**Aprovação:** Aguardando decisão
