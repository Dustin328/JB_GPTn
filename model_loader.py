"""
Model loader for JailbrokeGPT
Handles downloading and loading GGUF models via llama.cpp
"""
import os
from llama_cpp import Llama
from huggingface_hub import hf_hub_download


class ModelLoader:
    def __init__(self, model_repo: str, model_file: str):
        """
        Initialize model loader
        
        Args:
            model_repo: HuggingFace repository (e.g., 'v8karlo/UNCENSORED-TinyLlama...')
            model_file: Name of the GGUF file in the repo
        """
        self.model_repo = model_repo
        self.model_file = model_file
        self.model = None
        
    def download_model(self) -> str:
        """
        Download model from HuggingFace if not already cached
        
        Returns:
            Path to the downloaded model file
        """
        print(f"Downloading model from {self.model_repo}...")
        print("This may take a few minutes on first run...")
        
        model_path = hf_hub_download(
            repo_id=self.model_repo,
            filename=self.model_file,
            cache_dir="./models"
        )
        
        print(f"Model downloaded to: {model_path}")
        return model_path
    
    def load_model(self, n_ctx: int = 2048, n_threads: int = 4) -> Llama:
        """
        Load the model into memory
        
        Args:
            n_ctx: Context window size (default 2048 for longer conversations)
            n_threads: Number of CPU threads to use (default 4)
            
        Returns:
            Loaded Llama model instance
        """
        model_path = self.download_model()
        
        print("Loading model into memory...")
        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=0,  # CPU only (change to -1 for GPU)
            verbose=True  # Enable to see loading details
        )
        
        print("Model loaded successfully!")
        return self.model
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: list = None
    ) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            stop: List of stop sequences
            
        Returns:
            Generated text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if stop is None:
            stop = ["</s>", "User:", "Human:"]
        
        response = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
            echo=False
        )
        
        return response['choices'][0]['text'].strip()
