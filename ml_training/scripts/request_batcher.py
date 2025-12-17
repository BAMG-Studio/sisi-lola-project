#!/usr/bin/env python3
"""
Sisi Lola Request Batching System
Implements dynamic batching for efficient GPU utilization.

Features:
1. Dynamic request batching - combine multiple requests
2. Priority queue - VIP users processed first
3. Timeout handling - don't wait forever
4. Continuous batching - process as soon as batch is ready
"""
import os
import sys
import asyncio
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
import threading
import queue
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class Priority(IntEnum):
    """Request priority levels"""
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass(order=True)
class BatchRequest:
    """A request in the batch queue"""
    priority: int
    timestamp: float = field(compare=False)
    request_id: str = field(compare=False)
    prompt: str = field(compare=False)
    config: Dict[str, Any] = field(compare=False, default_factory=dict)
    future: asyncio.Future = field(compare=False, default=None)
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())[:8]


@dataclass
class BatchResult:
    """Result from batch processing"""
    request_id: str
    response: str
    inference_time_ms: float
    batch_size: int
    position_in_batch: int


class RequestBatcher:
    """
    Dynamic request batching for efficient inference.
    
    How it works:
    1. Requests are queued with priority
    2. Batch is formed when either:
       - Max batch size is reached
       - Max wait time is exceeded
    3. Batch is processed together on GPU
    4. Results are distributed to waiting requests
    
    Benefits:
    - Better GPU utilization
    - Higher throughput
    - Fair scheduling with priorities
    """
    
    def __init__(
        self,
        max_batch_size: int = 8,
        max_wait_ms: int = 50,
        inference_fn: Optional[Callable] = None
    ):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.inference_fn = inference_fn
        
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._running = False
        self._worker_thread = None
        self._loop = None
        
        # Stats
        self._total_requests = 0
        self._total_batches = 0
        self._total_wait_time_ms = 0
    
    def _load_config(self) -> Dict[str, Any]:
        """Load batching config"""
        config_path = PROJECT_ROOT / "ml_training" / "configs" / "optimization_config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config.get('request_handling', {}).get('batching', {})
        return {}
    
    async def submit(
        self,
        prompt: str,
        config: Dict[str, Any] = None,
        priority: Priority = Priority.NORMAL,
        timeout: float = 30.0
    ) -> BatchResult:
        """
        Submit a request for batched processing.
        
        Args:
            prompt: The input prompt
            config: Generation configuration
            priority: Request priority
            timeout: Maximum wait time in seconds
            
        Returns:
            BatchResult with response
        """
        # Create request
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        request = BatchRequest(
            priority=priority.value,
            timestamp=time.time(),
            request_id=str(uuid.uuid4())[:8],
            prompt=prompt,
            config=config or {},
            future=future
        )
        
        # Add to queue
        self._queue.put(request)
        self._total_requests += 1
        
        # Wait for result with timeout
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            return BatchResult(
                request_id=request.request_id,
                response="Request timed out",
                inference_time_ms=-1,
                batch_size=0,
                position_in_batch=-1
            )
    
    def _collect_batch(self) -> List[BatchRequest]:
        """Collect requests for a batch"""
        batch = []
        deadline = time.time() + (self.max_wait_ms / 1000)
        
        while len(batch) < self.max_batch_size and time.time() < deadline:
            try:
                request = self._queue.get(timeout=0.001)
                batch.append(request)
            except queue.Empty:
                if batch:
                    # Have some requests, wait a bit more
                    time.sleep(0.001)
                else:
                    # Empty queue, wait longer
                    time.sleep(0.01)
        
        return batch
    
    async def _process_batch(self, batch: List[BatchRequest]):
        """Process a batch of requests"""
        if not batch:
            return
        
        start_time = time.time()
        self._total_batches += 1
        
        try:
            # Extract prompts
            prompts = [r.prompt for r in batch]
            configs = [r.config for r in batch]
            
            # Call inference function
            if self.inference_fn:
                responses = await self.inference_fn(prompts, configs)
            else:
                # Fallback: process individually
                responses = [f"Response to: {p[:50]}..." for p in prompts]
            
            inference_time = (time.time() - start_time) * 1000
            
            # Distribute results
            for i, (request, response) in enumerate(zip(batch, responses)):
                result = BatchResult(
                    request_id=request.request_id,
                    response=response,
                    inference_time_ms=inference_time,
                    batch_size=len(batch),
                    position_in_batch=i
                )
                
                # Track wait time
                wait_time = (time.time() - request.timestamp) * 1000
                self._total_wait_time_ms += wait_time
                
                # Complete the future
                if request.future and not request.future.done():
                    request.future.set_result(result)
                    
        except Exception as e:
            # Error - fail all requests in batch
            for request in batch:
                if request.future and not request.future.done():
                    request.future.set_exception(e)
    
    def _worker_loop(self):
        """Background worker thread"""
        asyncio.set_event_loop(self._loop)
        
        while self._running:
            batch = self._collect_batch()
            if batch:
                asyncio.run_coroutine_threadsafe(
                    self._process_batch(batch),
                    self._loop
                ).result()
            else:
                time.sleep(0.01)
    
    def start(self, loop: asyncio.AbstractEventLoop = None):
        """Start the batch processor"""
        if self._running:
            return
        
        self._running = True
        self._loop = loop or asyncio.get_event_loop()
        
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        
        print(f"✅ Request batcher started (batch_size={self.max_batch_size}, max_wait={self.max_wait_ms}ms)")
    
    def stop(self):
        """Stop the batch processor"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        print("✅ Request batcher stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batcher statistics"""
        avg_wait = self._total_wait_time_ms / max(self._total_requests, 1)
        avg_batch_size = self._total_requests / max(self._total_batches, 1)
        
        return {
            "total_requests": self._total_requests,
            "total_batches": self._total_batches,
            "avg_batch_size": round(avg_batch_size, 2),
            "avg_wait_time_ms": round(avg_wait, 2),
            "queue_size": self._queue.qsize(),
            "running": self._running,
            "config": {
                "max_batch_size": self.max_batch_size,
                "max_wait_ms": self.max_wait_ms
            }
        }


class ContinuousBatcher:
    """
    Continuous batching for streaming inference.
    
    Unlike static batching, continuous batching:
    - Doesn't wait for batch to fill
    - Processes new requests as slots become available
    - Better for variable-length outputs
    
    Ideal for: streaming responses, chat applications
    """
    
    def __init__(
        self,
        max_concurrent: int = 8,
        inference_fn: Optional[Callable] = None
    ):
        self.max_concurrent = max_concurrent
        self.inference_fn = inference_fn
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_requests = 0
        self._total_requests = 0
    
    async def submit(
        self,
        prompt: str,
        config: Dict[str, Any] = None,
        stream: bool = False
    ):
        """
        Submit request for processing.
        
        Args:
            prompt: Input prompt
            config: Generation config
            stream: Whether to stream response
            
        Returns:
            Response string or async generator for streaming
        """
        async with self._semaphore:
            self._active_requests += 1
            self._total_requests += 1
            
            try:
                if self.inference_fn:
                    if stream:
                        async for chunk in self.inference_fn(prompt, config, stream=True):
                            yield chunk
                    else:
                        result = await self.inference_fn(prompt, config)
                        yield result
                else:
                    yield f"Response to: {prompt[:50]}..."
            finally:
                self._active_requests -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batcher statistics"""
        return {
            "max_concurrent": self.max_concurrent,
            "active_requests": self._active_requests,
            "total_requests": self._total_requests,
            "available_slots": self.max_concurrent - self._active_requests
        }


# Singleton instances
_request_batcher: Optional[RequestBatcher] = None
_continuous_batcher: Optional[ContinuousBatcher] = None


def get_request_batcher() -> RequestBatcher:
    """Get global request batcher"""
    global _request_batcher
    if _request_batcher is None:
        _request_batcher = RequestBatcher()
    return _request_batcher


def get_continuous_batcher() -> ContinuousBatcher:
    """Get global continuous batcher"""
    global _continuous_batcher
    if _continuous_batcher is None:
        _continuous_batcher = ContinuousBatcher()
    return _continuous_batcher


async def main():
    """Demo batching functionality"""
    print("="*60)
    print("Request Batching Demo")
    print("="*60)
    
    # Create batcher
    batcher = RequestBatcher(max_batch_size=4, max_wait_ms=100)
    batcher.start()
    
    print("\n📦 Submitting requests...")
    
    # Submit multiple requests concurrently
    async def submit_requests():
        tasks = []
        for i in range(10):
            priority = Priority.HIGH if i < 2 else Priority.NORMAL
            task = batcher.submit(
                prompt=f"Request {i}: Tell me about Nigeria",
                priority=priority
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    results = await submit_requests()
    
    print(f"\n📊 Results:")
    for result in results:
        print(f"   [{result.request_id}] batch_size={result.batch_size}, pos={result.position_in_batch}")
    
    print(f"\n📈 Stats: {batcher.get_stats()}")
    
    batcher.stop()
    print("\n✅ Batching demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
