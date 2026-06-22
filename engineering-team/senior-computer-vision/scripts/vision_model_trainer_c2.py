# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vision_model_trainer_base import *  # noqa: F403,E402


class VisionModelTrainerMixin2:
    def generate_detectron2_config(self, arch: str, epochs: int = 12,
                                   batch: int = 16, **kwargs) -> Dict[str, Any]:
        """Generate Detectron2 training configuration."""
        if arch not in DETECTRON2_ARCHITECTURES:
            available = ', '.join(DETECTRON2_ARCHITECTURES.keys())
            raise ValueError(f"Unknown architecture: {arch}. Available: {available}")

        arch_info = DETECTRON2_ARCHITECTURES[arch]
        iterations = epochs * 1000  # Approximate

        config = {
            'MODEL': {
                'WEIGHTS': f'detectron2://COCO-Detection/{arch}_3x/137849458/model_final_280758.pkl',
                'ROI_HEADS': {
                    'NUM_CLASSES': len(self._get_classes()),
                    'BATCH_SIZE_PER_IMAGE': 512,
                    'POSITIVE_FRACTION': 0.25,
                    'SCORE_THRESH_TEST': 0.05,
                    'NMS_THRESH_TEST': 0.5,
                },
                'BACKBONE': {
                    'FREEZE_AT': 2
                },
                'FPN': {
                    'IN_FEATURES': ['res2', 'res3', 'res4', 'res5']
                },
                'ANCHOR_GENERATOR': {
                    'SIZES': [[32], [64], [128], [256], [512]],
                    'ASPECT_RATIOS': [[0.5, 1.0, 2.0]]
                },
                'RPN': {
                    'PRE_NMS_TOPK_TRAIN': 2000,
                    'PRE_NMS_TOPK_TEST': 1000,
                    'POST_NMS_TOPK_TRAIN': 1000,
                    'POST_NMS_TOPK_TEST': 1000,
                }
            },
            'DATASETS': {
                'TRAIN': ('custom_train',),
                'TEST': ('custom_val',),
            },
            'DATALOADER': {
                'NUM_WORKERS': 4,
                'SAMPLER_TRAIN': 'TrainingSampler',
                'FILTER_EMPTY_ANNOTATIONS': True,
            },
            'SOLVER': {
                'IMS_PER_BATCH': batch,
                'BASE_LR': 0.001,
                'STEPS': (int(iterations * 0.7), int(iterations * 0.9)),
                'MAX_ITER': iterations,
                'WARMUP_FACTOR': 1.0 / 1000,
                'WARMUP_ITERS': 1000,
                'WARMUP_METHOD': 'linear',
                'GAMMA': 0.1,
                'MOMENTUM': 0.9,
                'WEIGHT_DECAY': 0.0001,
                'WEIGHT_DECAY_NORM': 0.0,
                'CHECKPOINT_PERIOD': 5000,
                'AMP': {
                    'ENABLED': True
                }
            },
            'INPUT': {
                'MIN_SIZE_TRAIN': (640, 672, 704, 736, 768, 800),
                'MAX_SIZE_TRAIN': 1333,
                'MIN_SIZE_TEST': 800,
                'MAX_SIZE_TEST': 1333,
                'FORMAT': 'BGR',
            },
            'TEST': {
                'EVAL_PERIOD': 5000,
                'DETECTIONS_PER_IMAGE': 100,
            },
            'OUTPUT_DIR': f'./output/{arch}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        }

        # Add mask head for instance segmentation
        if 'mask' in arch.lower():
            config['MODEL']['MASK_ON'] = True
            config['MODEL']['ROI_MASK_HEAD'] = {
                'POOLER_RESOLUTION': 14,
                'POOLER_SAMPLING_RATIO': 0,
                'POOLER_TYPE': 'ROIAlignV2'
            }

        config.update(kwargs)
        config['_metadata'] = {
            'architecture': arch,
            'arch_info': arch_info,
            'task': self.task,
            'framework': 'detectron2',
            'generated_at': datetime.now().isoformat()
        }

        self.config = config
        return config
