# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vision_model_trainer_base import *  # noqa: F403,E402


class VisionModelTrainerMixin0:
    """Generates training configurations for vision models."""
    def __init__(self, data_dir: str, task: str = 'detection',
                 framework: str = 'ultralytics'):
        self.data_dir = Path(data_dir)
        self.task = task
        self.framework = framework
        self.config = {}
    def analyze_dataset(self) -> Dict[str, Any]:
        """Analyze dataset structure and statistics."""
        logger.info(f"Analyzing dataset at {self.data_dir}")

        analysis = {
            'path': str(self.data_dir),
            'exists': self.data_dir.exists(),
            'images': {'train': 0, 'val': 0, 'test': 0},
            'annotations': {'format': None, 'classes': []},
            'recommendations': []
        }

        if not self.data_dir.exists():
            analysis['recommendations'].append(
                f"Directory {self.data_dir} does not exist"
            )
            return analysis

        # Check for common dataset structures
        # COCO format
        if (self.data_dir / 'annotations').exists():
            analysis['annotations']['format'] = 'coco'
            for split in ['train', 'val', 'test']:
                ann_file = self.data_dir / 'annotations' / f'{split}.json'
                if ann_file.exists():
                    with open(ann_file, 'r') as f:
                        data = json.load(f)
                        analysis['images'][split] = len(data.get('images', []))
                        if not analysis['annotations']['classes']:
                            analysis['annotations']['classes'] = [
                                c['name'] for c in data.get('categories', [])
                            ]

        # YOLO format
        elif (self.data_dir / 'labels').exists():
            analysis['annotations']['format'] = 'yolo'
            for split in ['train', 'val', 'test']:
                img_dir = self.data_dir / 'images' / split
                if img_dir.exists():
                    analysis['images'][split] = len(list(img_dir.glob('*.*')))

            # Try to read classes from data.yaml
            data_yaml = self.data_dir / 'data.yaml'
            if data_yaml.exists():
                import yaml
                with open(data_yaml, 'r') as f:
                    data = yaml.safe_load(f)
                    analysis['annotations']['classes'] = data.get('names', [])

        # Generate recommendations
        total_images = sum(analysis['images'].values())
        if total_images < 100:
            analysis['recommendations'].append(
                f"Dataset has only {total_images} images. "
                "Consider collecting more data or using transfer learning."
            )
        if total_images < 1000:
            analysis['recommendations'].append(
                "Use aggressive data augmentation (mosaic, mixup) for small datasets."
            )

        num_classes = len(analysis['annotations']['classes'])
        if num_classes > 80:
            analysis['recommendations'].append(
                f"Large number of classes ({num_classes}). "
                "Consider using larger model (yolov8l/x) or longer training."
            )

        logger.info(f"Found {total_images} images, {num_classes} classes")
        return analysis
