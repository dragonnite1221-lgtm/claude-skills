# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vision_model_trainer_base import *  # noqa: F403,E402


class VisionModelTrainerMixin4:
    def save_config(self, output_path: str) -> str:
        """Save configuration to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.framework == 'ultralytics':
            # YOLO uses YAML
            import yaml
            with open(output_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        else:
            # Detectron2 and MMDetection use Python configs
            with open(output_path, 'w') as f:
                f.write("# Auto-generated configuration\n")
                f.write(f"# Generated at: {datetime.now().isoformat()}\n\n")
                f.write(f"config = {json.dumps(self.config, indent=2)}\n")

        logger.info(f"Configuration saved to {output_path}")
        return str(output_path)
    def generate_training_command(self) -> str:
        """Generate the training command for the framework."""
        if self.framework == 'ultralytics':
            return f"yolo detect train data={self.config.get('data', 'data.yaml')} " \
                   f"model={self.config.get('model', 'yolov8m.pt')} " \
                   f"epochs={self.config.get('epochs', 100)} " \
                   f"imgsz={self.config.get('imgsz', 640)}"
        elif self.framework == 'detectron2':
            return f"python train_net.py --config-file config.yaml --num-gpus 1"
        elif self.framework == 'mmdetection':
            return f"python tools/train.py config.py"
        return ""
    def print_summary(self):
        """Print configuration summary."""
        meta = self.config.get('_metadata', {})

        print("\n" + "=" * 60)
        print("TRAINING CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"Framework:     {meta.get('framework', 'unknown')}")
        print(f"Architecture:  {meta.get('architecture', 'unknown')}")
        print(f"Task:          {meta.get('task', 'detection')}")

        if 'arch_info' in meta:
            info = meta['arch_info']
            if 'params' in info:
                print(f"Parameters:    {info['params']}")
            if 'map' in info:
                print(f"COCO mAP:      {info['map']}")

        print("-" * 60)
        print("Training Command:")
        print(f"  {self.generate_training_command()}")
        print("=" * 60 + "\n")
