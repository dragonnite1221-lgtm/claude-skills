# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vision_model_trainer_base import *  # noqa: F403,E402


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate vision model training configurations"
    )
    parser.add_argument('data_dir', help='Path to dataset directory')
    parser.add_argument('--task', choices=['detection', 'segmentation'],
                       default='detection', help='Task type')
    parser.add_argument('--framework', choices=['ultralytics', 'detectron2', 'mmdetection'],
                       default='ultralytics', help='Training framework')
    parser.add_argument('--arch', default='yolov8m',
                       help='Model architecture')
    parser.add_argument('--epochs', type=int, default=100, help='Training epochs')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    parser.add_argument('--imgsz', type=int, default=640, help='Image size')
    parser.add_argument('--output', '-o', help='Output config file path')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze dataset, do not generate config')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')

    args = parser.parse_args()

    trainer = VisionModelTrainer(
        data_dir=args.data_dir,
        task=args.task,
        framework=args.framework
    )

    # Analyze dataset
    analysis = trainer.analyze_dataset()

    if args.analyze_only:
        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            print("\nDataset Analysis:")
            print(f"  Path: {analysis['path']}")
            print(f"  Format: {analysis['annotations']['format']}")
            print(f"  Classes: {len(analysis['annotations']['classes'])}")
            print(f"  Images - Train: {analysis['images']['train']}, "
                  f"Val: {analysis['images']['val']}, "
                  f"Test: {analysis['images']['test']}")
            if analysis['recommendations']:
                print("\nRecommendations:")
                for rec in analysis['recommendations']:
                    print(f"  - {rec}")
        return

    # Generate configuration
    try:
        if args.framework == 'ultralytics':
            config = trainer.generate_yolo_config(
                arch=args.arch,
                epochs=args.epochs,
                batch=args.batch,
                imgsz=args.imgsz
            )
        elif args.framework == 'detectron2':
            config = trainer.generate_detectron2_config(
                arch=args.arch,
                epochs=args.epochs,
                batch=args.batch
            )
        elif args.framework == 'mmdetection':
            config = trainer.generate_mmdetection_config(
                arch=args.arch,
                epochs=args.epochs,
                batch=args.batch
            )
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Output
    if args.json:
        print(json.dumps(config, indent=2))
    else:
        trainer.print_summary()

        if args.output:
            trainer.save_config(args.output)
