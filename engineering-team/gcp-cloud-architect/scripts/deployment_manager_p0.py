# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402


def main():
    parser = argparse.ArgumentParser(
        description='GCP Deployment Manager - Generates gcloud CLI scripts and Terraform configurations'
    )
    parser.add_argument(
        '--app-name', '-a',
        type=str,
        required=True,
        help='Application name'
    )
    parser.add_argument(
        '--pattern', '-p',
        type=str,
        choices=['serverless_web', 'gke_microservices', 'data_pipeline'],
        default='serverless_web',
        help='Architecture pattern (default: serverless_web)'
    )
    parser.add_argument(
        '--region', '-r',
        type=str,
        default='us-central1',
        help='GCP region (default: us-central1)'
    )
    parser.add_argument(
        '--project-id',
        type=str,
        default='my-project',
        help='GCP project ID (default: my-project)'
    )
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['gcloud', 'terraform', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON format'
    )

    args = parser.parse_args()

    requirements = {
        'pattern': args.pattern,
        'region': args.region,
        'project_id': args.project_id
    }

    manager = DeploymentManager(args.app_name, requirements)

    if args.json:
        output = {}
        if args.format in ('gcloud', 'both'):
            output['gcloud_script'] = manager.generate_gcloud_script()
        if args.format in ('terraform', 'both'):
            output['terraform_config'] = manager.generate_terraform_configuration()
        print(json.dumps(output, indent=2))
    elif args.output:
        import os
        os.makedirs(args.output, exist_ok=True)

        if args.format in ('gcloud', 'both'):
            gcloud_path = os.path.join(args.output, 'deploy.sh')
            with open(gcloud_path, 'w') as f:
                f.write(manager.generate_gcloud_script())
            os.chmod(gcloud_path, 0o755)
            print(f"gcloud script written to {gcloud_path}")

        if args.format in ('terraform', 'both'):
            tf_path = os.path.join(args.output, 'main.tf')
            with open(tf_path, 'w') as f:
                f.write(manager.generate_terraform_configuration())
            print(f"Terraform config written to {tf_path}")
    else:
        if args.format in ('gcloud', 'both'):
            print("# ===== gcloud CLI Script =====")
            print(manager.generate_gcloud_script())

        if args.format in ('terraform', 'both'):
            print("# ===== Terraform Configuration =====")
            print(manager.generate_terraform_configuration())
