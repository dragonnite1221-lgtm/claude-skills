# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class CostOptimizerMixin2:
    def _analyze_storage(self) -> float:
        """Analyze Cloud Storage resources."""
        savings = 0.0

        gcs_buckets = self.resources.get('gcs_buckets', [])
        for bucket in gcs_buckets:
            size_gb = bucket.get('size_gb', 0)
            storage_class = bucket.get('storage_class', 'STANDARD')

            if not bucket.get('has_lifecycle_policy', False) and size_gb > 100:
                lifecycle_savings = size_gb * 0.012
                savings += lifecycle_savings
                self.recommendations.append({
                    'service': 'Cloud Storage',
                    'type': 'Lifecycle Policy',
                    'issue': f'Bucket {bucket.get("name", "unknown")} ({size_gb} GB) has no lifecycle policy',
                    'recommendation': 'Add lifecycle rule: Transition to Nearline after 30 days, Coldline after 90 days, Archive after 365 days',
                    'potential_savings': lifecycle_savings,
                    'priority': 'medium'
                })

            if storage_class == 'STANDARD' and size_gb > 500:
                class_savings = size_gb * 0.006
                savings += class_savings
                self.recommendations.append({
                    'service': 'Cloud Storage',
                    'type': 'Storage Class',
                    'issue': f'Large bucket ({size_gb} GB) using Standard class',
                    'recommendation': 'Enable Autoclass for automatic storage class management based on access patterns',
                    'potential_savings': class_savings,
                    'priority': 'high'
                })

        return savings
    def _analyze_database(self) -> float:
        """Analyze Cloud SQL, Firestore, and BigQuery costs."""
        savings = 0.0

        cloud_sql_instances = self.resources.get('cloud_sql_instances', [])
        for db in cloud_sql_instances:
            if db.get('connections_per_day', 1000) < 10:
                db_cost = db.get('monthly_cost', 100)
                savings += db_cost * 0.8
                self.recommendations.append({
                    'service': 'Cloud SQL',
                    'type': 'Idle Resource',
                    'issue': f'Database {db.get("name", "unknown")} has <10 connections/day',
                    'recommendation': 'Stop database if not needed, or take a backup and delete',
                    'potential_savings': db_cost * 0.8,
                    'priority': 'high'
                })

            if db.get('utilization', 100) < 30 and not db.get('has_ha', False):
                rightsize_savings = db.get('monthly_cost', 200) * 0.35
                savings += rightsize_savings
                self.recommendations.append({
                    'service': 'Cloud SQL',
                    'type': 'Right-sizing',
                    'issue': f'Cloud SQL instance {db.get("name", "unknown")} has low utilization (<30%)',
                    'recommendation': 'Downsize to a smaller machine type (e.g., db-custom-2-8192 to db-f1-micro for dev)',
                    'potential_savings': rightsize_savings,
                    'priority': 'medium'
                })

        # BigQuery optimization
        bigquery_datasets = self.resources.get('bigquery_datasets', [])
        for dataset in bigquery_datasets:
            if dataset.get('pricing_model', 'on_demand') == 'on_demand':
                monthly_tb_scanned = dataset.get('monthly_tb_scanned', 0)
                if monthly_tb_scanned > 10:
                    slot_savings = (monthly_tb_scanned * 6.25) * 0.30
                    savings += slot_savings
                    self.recommendations.append({
                        'service': 'BigQuery',
                        'type': 'Pricing Model',
                        'issue': f'Scanning {monthly_tb_scanned} TB/month on on-demand pricing',
                        'recommendation': 'Switch to BigQuery editions with slots for predictable costs (30%+ savings at this volume)',
                        'potential_savings': slot_savings,
                        'priority': 'high'
                    })

            if not dataset.get('has_partitioning', False):
                partition_savings = dataset.get('monthly_query_cost', 50) * 0.50
                savings += partition_savings
                self.recommendations.append({
                    'service': 'BigQuery',
                    'type': 'Table Partitioning',
                    'issue': f'Tables in {dataset.get("name", "unknown")} lack partitioning',
                    'recommendation': 'Partition tables by date and add clustering columns to reduce bytes scanned',
                    'potential_savings': partition_savings,
                    'priority': 'medium'
                })

        return savings
