# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vision_model_trainer_base import *  # noqa: F403,E402


class VisionModelTrainerMixin3:
    def generate_mmdetection_config(self, arch: str, epochs: int = 12,
                                    batch: int = 16, **kwargs) -> Dict[str, Any]:
        """Generate MMDetection training configuration."""
        if arch not in MMDETECTION_ARCHITECTURES:
            available = ', '.join(MMDETECTION_ARCHITECTURES.keys())
            raise ValueError(f"Unknown architecture: {arch}. Available: {available}")

        arch_info = MMDETECTION_ARCHITECTURES[arch]

        config = {
            '_base_': [
                f'../_base_/models/{arch}.py',
                '../_base_/datasets/coco_detection.py',
                '../_base_/schedules/schedule_1x.py',
                '../_base_/default_runtime.py'
            ],
            'model': {
                'roi_head': {
                    'bbox_head': {
                        'num_classes': len(self._get_classes())
                    }
                }
            },
            'data': {
                'samples_per_gpu': batch // 2,
                'workers_per_gpu': 4,
                'train': {
                    'type': 'CocoDataset',
                    'ann_file': str(self.data_dir / 'annotations' / 'train.json'),
                    'img_prefix': str(self.data_dir / 'images' / 'train'),
                },
                'val': {
                    'type': 'CocoDataset',
                    'ann_file': str(self.data_dir / 'annotations' / 'val.json'),
                    'img_prefix': str(self.data_dir / 'images' / 'val'),
                },
                'test': {
                    'type': 'CocoDataset',
                    'ann_file': str(self.data_dir / 'annotations' / 'val.json'),
                    'img_prefix': str(self.data_dir / 'images' / 'val'),
                }
            },
            'optimizer': {
                'type': 'SGD',
                'lr': 0.02,
                'momentum': 0.9,
                'weight_decay': 0.0001
            },
            'optimizer_config': {
                'grad_clip': {'max_norm': 35, 'norm_type': 2}
            },
            'lr_config': {
                'policy': 'step',
                'warmup': 'linear',
                'warmup_iters': 500,
                'warmup_ratio': 0.001,
                'step': [int(epochs * 0.7), int(epochs * 0.9)]
            },
            'runner': {
                'type': 'EpochBasedRunner',
                'max_epochs': epochs
            },
            'checkpoint_config': {
                'interval': 1
            },
            'log_config': {
                'interval': 50,
                'hooks': [
                    {'type': 'TextLoggerHook'},
                    {'type': 'TensorboardLoggerHook'}
                ]
            },
            'work_dir': f'./work_dirs/{arch}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'load_from': None,
            'resume_from': None,
            'fp16': {'loss_scale': 512.0}
        }

        config.update(kwargs)
        config['_metadata'] = {
            'architecture': arch,
            'arch_info': arch_info,
            'task': self.task,
            'framework': 'mmdetection',
            'generated_at': datetime.now().isoformat()
        }

        self.config = config
        return config
    def _get_classes(self) -> List[str]:
        """Get class names from dataset."""
        analysis = self.analyze_dataset()
        classes = analysis['annotations']['classes']
        if not classes:
            classes = ['object']  # Default fallback
        return classes
