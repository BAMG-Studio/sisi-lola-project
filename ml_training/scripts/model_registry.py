#!/usr/bin/env python3
"""
Model Registry - Track and manage all Sisi Lola models
"""
import json
import os
from datetime import datetime
from pathlib import Path

class ModelRegistry:
    """Central registry for all trained models"""
    
    def __init__(self, registry_path="ml_training/outputs/model_registry.json"):
        self.registry_path = registry_path
        self.registry = self.load_registry()
    
    def load_registry(self):
        """Load existing registry or create new"""
        if os.path.exists(self.registry_path):
            with open(self.registry_path) as f:
                return json.load(f)
        return {"models": [], "active": {}}
    
    def save_registry(self):
        """Save registry to disk"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self, model_type, model_path, metadata):
        """Register a new trained model"""
        model_entry = {
            "id": f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": model_type,
            "path": model_path,
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata,
            "status": "registered"
        }
        
        self.registry["models"].append(model_entry)
        
        # Set as active if first of type or explicitly requested
        if model_type not in self.registry["active"]:
            self.set_active(model_type, model_entry["id"])
        
        self.save_registry()
        return model_entry["id"]
    
    def set_active(self, model_type, model_id):
        """Set a model as active for production"""
        # Find model
        model = next((m for m in self.registry["models"] if m["id"] == model_id), None)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Update status
        for m in self.registry["models"]:
            if m["type"] == model_type:
                m["status"] = "active" if m["id"] == model_id else "inactive"
        
        self.registry["active"][model_type] = model_id
        self.save_registry()
    
    def get_active_model(self, model_type):
        """Get currently active model for a type"""
        model_id = self.registry["active"].get(model_type)
        if not model_id:
            return None
        
        return next((m for m in self.registry["models"] if m["id"] == model_id), None)
    
    def list_models(self, model_type=None):
        """List all models, optionally filtered by type"""
        models = self.registry["models"]
        if model_type:
            models = [m for m in models if m["type"] == model_type]
        return models
    
    def get_model_info(self, model_id):
        """Get detailed info about a model"""
        model = next((m for m in self.registry["models"] if m["id"] == model_id), None)
        if not model:
            return None
        
        # Add file size if path exists
        if os.path.exists(model["path"]):
            size = sum(f.stat().st_size for f in Path(model["path"]).rglob('*') if f.is_file())
            model["size_mb"] = round(size / 1024 / 1024, 2)
        
        return model
    
    def export_production_config(self, output_path="ml_training/outputs/production_config.json"):
        """Export config for active models"""
        config = {
            "sisi_lola_production": {
                "version": "1.0.0",
                "updated": datetime.now().isoformat(),
                "models": {}
            }
        }
        
        for model_type, model_id in self.registry["active"].items():
            model = self.get_model_info(model_id)
            if model:
                config["sisi_lola_production"]["models"][model_type] = {
                    "id": model["id"],
                    "path": model["path"],
                    "metadata": model["metadata"],
                    "registered_at": model["registered_at"]
                }
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return output_path

def main():
    """CLI for model registry"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sisi Lola Model Registry")
    parser.add_argument("command", choices=["list", "active", "info", "export"])
    parser.add_argument("--type", help="Model type (brain/voice)")
    parser.add_argument("--id", help="Model ID")
    
    args = parser.parse_args()
    
    registry = ModelRegistry()
    
    if args.command == "list":
        models = registry.list_models(args.type)
        print(f"\n📋 Models ({len(models)}):")
        for m in models:
            status = "🟢" if m["status"] == "active" else "⚪"
            print(f"  {status} {m['id']} ({m['type']}) - {m['registered_at']}")
    
    elif args.command == "active":
        print("\n🟢 Active Models:")
        for model_type, model_id in registry.registry["active"].items():
            model = registry.get_model_info(model_id)
            print(f"  {model_type}: {model_id}")
            if model:
                print(f"    Path: {model['path']}")
                print(f"    Size: {model.get('size_mb', 'N/A')} MB")
    
    elif args.command == "info":
        if not args.id:
            print("❌ --id required for info command")
            return
        
        model = registry.get_model_info(args.id)
        if model:
            print(f"\n📊 Model Info: {model['id']}")
            print(f"  Type: {model['type']}")
            print(f"  Path: {model['path']}")
            print(f"  Status: {model['status']}")
            print(f"  Size: {model.get('size_mb', 'N/A')} MB")
            print(f"  Registered: {model['registered_at']}")
            print(f"  Metadata: {json.dumps(model['metadata'], indent=4)}")
        else:
            print(f"❌ Model {args.id} not found")
    
    elif args.command == "export":
        config_path = registry.export_production_config()
        print(f"✅ Production config exported to: {config_path}")

if __name__ == "__main__":
    main()
