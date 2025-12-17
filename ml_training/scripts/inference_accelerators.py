#!/usr/bin/env python3
"""
Sisi Lola Inference Accelerators
High-performance inference with:
1. Flash Attention 2 - Faster attention computation
2. vLLM Integration - 5-10x faster serving
3. TGI Integration - Hugging Face Text Generation Inference
4. Context Window Extension - 4K to 8K/16K tokens
"""
import os
import sys
import torch
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class AcceleratorConfig:
    """Configuration for inference accelerators"""
    use_flash_attention: bool = True
    use_vllm: bool = False  # Requires separate vLLM installation
    use_tgi: bool = False   # Requires TGI docker container
    context_length: int = 8192
    gpu_memory_utilization: float = 0.9
    max_batch_size: int = 16
    
    # RoPE scaling for context extension
    rope_scaling_type: str = "dynamic"  # "linear" or "dynamic"
    rope_scaling_factor: float = 2.0


def check_flash_attention() -> Dict[str, Any]:
    """
    Check if Flash Attention 2 is available.
    
    Returns:
        Dict with availability and version info
    """
    result = {
        "available": False,
        "version": None,
        "reason": None
    }
    
    # Check CUDA
    if not torch.cuda.is_available():
        result["reason"] = "CUDA not available"
        return result
    
    # Check GPU compute capability (FA2 requires SM 8.0+)
    try:
        capability = torch.cuda.get_device_capability()
        if capability[0] < 8:
            result["reason"] = f"GPU compute capability {capability[0]}.{capability[1]} < 8.0 required"
            return result
    except:
        pass
    
    # Try importing flash_attn
    try:
        import flash_attn
        result["available"] = True
        result["version"] = getattr(flash_attn, '__version__', 'unknown')
        return result
    except ImportError:
        pass
    
    # Check if transformers supports FA2
    try:
        from transformers.utils import is_flash_attn_2_available
        if is_flash_attn_2_available():
            result["available"] = True
            result["version"] = "via transformers"
            return result
        else:
            result["reason"] = "flash_attn not installed"
    except ImportError:
        result["reason"] = "transformers version too old"
    
    return result


def check_vllm() -> Dict[str, Any]:
    """
    Check if vLLM is available.
    
    Returns:
        Dict with availability info
    """
    result = {
        "available": False,
        "version": None,
        "reason": None
    }
    
    try:
        import vllm
        result["available"] = True
        result["version"] = getattr(vllm, '__version__', 'unknown')
    except ImportError:
        result["reason"] = "vllm not installed (pip install vllm)"
    
    return result


def get_model_load_kwargs(
    config: AcceleratorConfig,
    model_name: str
) -> Dict[str, Any]:
    """
    Get optimized kwargs for model loading.
    
    Args:
        config: Accelerator configuration
        model_name: Name/path of model to load
        
    Returns:
        Dict of kwargs for from_pretrained()
    """
    kwargs = {
        "trust_remote_code": True,
        "token": os.getenv("HUGGINGFACE_TOKEN")
    }
    
    if torch.cuda.is_available():
        kwargs["device_map"] = "auto"
        kwargs["torch_dtype"] = torch.bfloat16  # Better precision than fp16
        
        # Enable Flash Attention 2
        if config.use_flash_attention:
            fa_status = check_flash_attention()
            if fa_status["available"]:
                kwargs["attn_implementation"] = "flash_attention_2"
                print(f"   ⚡ Flash Attention 2 enabled (v{fa_status['version']})")
            else:
                print(f"   ⚠️ Flash Attention 2 not available: {fa_status['reason']}")
        
        # RoPE scaling for context extension
        if config.context_length > 4096:
            kwargs["rope_scaling"] = {
                "type": config.rope_scaling_type,
                "factor": config.rope_scaling_factor
            }
            print(f"   📏 Context extended to {config.context_length} tokens")
    
    return kwargs


class VLLMEngine:
    """
    vLLM-based inference engine for production.
    
    vLLM provides:
    - PagedAttention for efficient memory use
    - Continuous batching
    - 5-10x faster than HuggingFace
    """
    
    def __init__(
        self,
        model_name: str,
        config: Optional[AcceleratorConfig] = None
    ):
        self.model_name = model_name
        self.config = config or AcceleratorConfig()
        self._llm = None
        self._sampling_params = None
    
    def load(self):
        """Load vLLM engine"""
        try:
            from vllm import LLM, SamplingParams
            
            print(f"\n🚀 Loading vLLM engine: {self.model_name}")
            
            self._llm = LLM(
                model=self.model_name,
                trust_remote_code=True,
                max_model_len=self.config.context_length,
                gpu_memory_utilization=self.config.gpu_memory_utilization,
                dtype="bfloat16"
            )
            
            self._sampling_params = SamplingParams(
                temperature=0.8,
                top_p=0.9,
                max_tokens=256
            )
            
            print("   ✅ vLLM engine loaded")
            
        except ImportError:
            raise RuntimeError("vLLM not installed. Install with: pip install vllm")
    
    def generate(
        self,
        prompts: List[str],
        max_tokens: int = 256,
        temperature: float = 0.8,
        top_p: float = 0.9
    ) -> List[str]:
        """
        Generate responses for multiple prompts (batched).
        
        Args:
            prompts: List of input prompts
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            List of generated responses
        """
        if self._llm is None:
            self.load()
        
        from vllm import SamplingParams
        
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        outputs = self._llm.generate(prompts, sampling_params)
        
        responses = []
        for output in outputs:
            text = output.outputs[0].text
            responses.append(text)
        
        return responses
    
    async def stream(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.8
    ):
        """Stream response token by token"""
        # vLLM streaming requires async server mode
        # For now, return full response
        responses = self.generate([prompt], max_tokens, temperature)
        yield responses[0]


class TGIClient:
    """
    Text Generation Inference (TGI) client.
    
    TGI runs as a separate Docker container:
    docker run --gpus all -p 8080:80 ghcr.io/huggingface/text-generation-inference:latest \
        --model-id mistralai/Mistral-7B-Instruct-v0.3
    """
    
    def __init__(self, endpoint: str = "http://localhost:8080"):
        self.endpoint = endpoint
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.8,
        stream: bool = False
    ):
        """Generate response using TGI"""
        import aiohttp
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "do_sample": True
            }
        }
        
        async with aiohttp.ClientSession() as session:
            if stream:
                async with session.post(
                    f"{self.endpoint}/generate_stream",
                    json=payload
                ) as response:
                    async for line in response.content:
                        if line:
                            yield line.decode('utf-8')
            else:
                async with session.post(
                    f"{self.endpoint}/generate",
                    json=payload
                ) as response:
                    result = await response.json()
                    yield result.get("generated_text", "")


def create_optimized_model(
    model_name: str,
    config: Optional[AcceleratorConfig] = None
):
    """
    Create an optimized model with all accelerators enabled.
    
    This is the main entry point for loading production models.
    
    Args:
        model_name: HuggingFace model name or path
        config: Accelerator configuration
        
    Returns:
        Tuple of (model, tokenizer)
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    config = config or AcceleratorConfig()
    
    print(f"\n🔧 Loading optimized model: {model_name}")
    
    # Get optimized loading kwargs
    load_kwargs = get_model_load_kwargs(config, model_name)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        token=os.getenv("HUGGINGFACE_TOKEN")
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with optimizations
    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    model.eval()
    
    print("   ✅ Model loaded with optimizations")
    
    return model, tokenizer


def get_accelerator_status() -> Dict[str, Any]:
    """Get status of all available accelerators"""
    return {
        "cuda": {
            "available": torch.cuda.is_available(),
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "memory_gb": torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0
        },
        "flash_attention_2": check_flash_attention(),
        "vllm": check_vllm(),
        "bf16_support": torch.cuda.is_bf16_supported() if torch.cuda.is_available() else False
    }


def main():
    """Demo accelerator functionality"""
    print("="*60)
    print("Inference Accelerators Status")
    print("="*60)
    
    status = get_accelerator_status()
    
    print("\n🖥️ CUDA:")
    print(f"   Available: {status['cuda']['available']}")
    if status['cuda']['available']:
        print(f"   Device: {status['cuda']['device']}")
        print(f"   Memory: {status['cuda']['memory_gb']:.1f} GB")
    
    print("\n⚡ Flash Attention 2:")
    fa = status['flash_attention_2']
    print(f"   Available: {fa['available']}")
    if fa['available']:
        print(f"   Version: {fa['version']}")
    else:
        print(f"   Reason: {fa['reason']}")
    
    print("\n🚀 vLLM:")
    vllm = status['vllm']
    print(f"   Available: {vllm['available']}")
    if vllm['available']:
        print(f"   Version: {vllm['version']}")
    else:
        print(f"   Reason: {vllm['reason']}")
    
    print(f"\n📊 BF16 Support: {status['bf16_support']}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not status['cuda']['available']:
        print("   ⚠️ No GPU detected - inference will be slow")
    
    if not status['flash_attention_2']['available']:
        print("   📦 Install Flash Attention 2: pip install flash-attn --no-build-isolation")
    
    if not status['vllm']['available']:
        print("   📦 Install vLLM for 5-10x speedup: pip install vllm")
    
    print("\n✅ Accelerator check complete!")


if __name__ == "__main__":
    main()
