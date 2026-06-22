# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402


class ArchitectureDesignerMixin4:
    def _data_pipeline_architecture(self) -> Dict[str, Any]:
        """Serverless data pipeline with BigQuery."""
        return {
            'pattern_name': 'Serverless Data Pipeline',
            'description': 'Scalable data ingestion, processing, and analytics',
            'use_case': 'Analytics, IoT data, log processing, ETL, data warehousing',
            'services': {
                'ingestion': {
                    'service': 'Pub/Sub',
                    'purpose': 'Real-time event and data ingestion',
                    'configuration': {
                        'throughput': 'Unlimited (auto-scaling)',
                        'retention': '7 days (configurable to 31 days)',
                        'ordering': 'Ordering keys for ordered delivery',
                        'dead_letter': 'Dead letter topic for failed messages'
                    }
                },
                'processing': {
                    'service': 'Dataflow (Apache Beam)',
                    'purpose': 'Stream and batch data processing',
                    'configuration': {
                        'mode': 'Streaming or batch',
                        'autoscaling': 'Horizontal autoscaling',
                        'workers': f'{max(1, self.data_size_gb // 20)} initial workers',
                        'sdk': 'Python or Java Apache Beam SDK'
                    }
                },
                'warehouse': {
                    'service': 'BigQuery',
                    'purpose': 'Serverless data warehouse and analytics',
                    'configuration': {
                        'pricing': 'On-demand ($6.25/TB queried) or slots',
                        'partitioning': 'By ingestion time or custom field',
                        'clustering': 'Up to 4 clustering columns',
                        'streaming_insert': 'Real-time data availability'
                    }
                },
                'storage': {
                    'service': 'Cloud Storage (Data Lake)',
                    'purpose': 'Raw data lake and archival storage',
                    'configuration': {
                        'format': 'Parquet or Avro (columnar)',
                        'partitioning': 'By date (year/month/day)',
                        'lifecycle': 'Transition to Coldline after 90 days',
                        'catalog': 'Dataplex for data governance'
                    }
                },
                'visualization': {
                    'service': 'Looker / Looker Studio',
                    'purpose': 'Business intelligence dashboards',
                    'configuration': {
                        'source': 'BigQuery direct connection',
                        'refresh': 'Real-time or scheduled',
                        'sharing': 'Embedded or web dashboards'
                    }
                },
                'orchestration': {
                    'service': 'Cloud Composer (Airflow)',
                    'purpose': 'Workflow orchestration for batch pipelines',
                    'configuration': {
                        'environment': 'Cloud Composer 2 (auto-scaling)',
                        'dags': 'Python DAG definitions',
                        'scheduling': 'Cron-based scheduling'
                    }
                }
            },
            'estimated_cost': {
                'monthly_usd': self._calculate_data_pipeline_cost(),
                'breakdown': {
                    'Pub/Sub': '5-30 USD',
                    'Dataflow': '20-150 USD',
                    'BigQuery': '10-100 USD (on-demand)',
                    'Cloud Storage': '5-30 USD',
                    'Looker Studio': '0 USD (free)',
                    'Cloud Composer': '300+ USD (if used)'
                }
            },
            'pros': [
                'Fully serverless data stack',
                'BigQuery scales to petabytes',
                'Real-time and batch in same pipeline',
                'Cost-effective with on-demand pricing',
                'ML integration via BigQuery ML'
            ],
            'cons': [
                'Dataflow has steep learning curve (Beam SDK)',
                'BigQuery costs based on data scanned',
                'Cloud Composer expensive for small workloads',
                'Schema evolution requires planning'
            ],
            'scaling_characteristics': {
                'events_per_second': '1,000 - 10,000,000',
                'data_volume': '1 GB - 1 PB per day',
                'scaling_method': 'Automatic (all services auto-scale)'
            }
        }
