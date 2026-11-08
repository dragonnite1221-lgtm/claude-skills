"""Regression coverage for full-vector TF-IDF cosine normalization."""
import contextlib
import importlib.util
import io
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/rag-architect/retrieval_evaluator.py'
SPEC = importlib.util.spec_from_file_location('retrieval_evaluator', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def retriever(contents):
    documents = [MODULE.Document(key, key, value) for key, value in contents]
    with contextlib.redirect_stdout(io.StringIO()):
        return MODULE.TFIDFRetriever(documents)


class RetrievalCosineTests(unittest.TestCase):
    def test_exact_match_outranks_partial_match_in_every_order(self):
        docs = [('partial', 'alpha noise noise'), ('exact', 'alpha beta'), ('other', 'gamma')]
        for order in itertools.permutations(docs):
            with self.subTest(order=order):
                results = retriever(order).search('alpha beta', 3)
                self.assertEqual([key for key, _ in results], ['exact', 'partial'])
                self.assertAlmostEqual(results[0][1], 1.0)
                self.assertGreater(results[1][1], 0.0)
                self.assertLess(results[1][1], 1.0)

    def test_document_only_terms_contribute_to_norm(self):
        score = retriever([('noisy', 'alpha noise noise'), ('other', 'gamma')]).search('alpha')[0][1]
        self.assertAlmostEqual(score, 1 / math.sqrt(5))

    def test_query_only_terms_contribute_to_norm(self):
        results = retriever([('a', 'alpha'), ('b', 'beta'), ('c', 'gamma')]).search('alpha beta')
        self.assertEqual([key for key, _ in results], ['a', 'b'])
        for _, score in results:
            self.assertAlmostEqual(score, 1 / math.sqrt(2))

    def test_repetition_scaling_and_unknown_terms(self):
        engine = retriever([('a', 'alpha beta'), ('b', 'gamma')])
        score = engine.search('alpha alpha beta')[0][1]
        self.assertAlmostEqual(score, 3 / math.sqrt(10))
        self.assertAlmostEqual(engine.search('alpha alpha beta unseen unseen')[0][1], score)
        self.assertAlmostEqual(engine.search('alpha alpha alpha alpha beta beta')[0][1], score)

    def test_zero_vectors_and_disjoint_terms(self):
        engine = retriever([('a', 'common alpha'), ('b', 'common beta'), ('empty', '')])
        self.assertEqual(engine.search(''), [])
        self.assertEqual(engine.search('unknown'), [])
        self.assertEqual(engine.search('!!!'), [])
        self.assertEqual(retriever([('a', 'common'), ('b', 'common')]).search('common'), [])
        self.assertEqual(retriever([]).search('alpha'), [])

    def test_evaluation_metrics_follow_correct_ranking(self):
        engine = retriever([('partial', 'alpha noise noise'), ('exact', 'alpha beta'), ('other', 'gamma')])
        with contextlib.redirect_stdout(io.StringIO()):
            report = MODULE.RetrievalEvaluator().evaluate(
                [{'id': 'q', 'query': 'alpha beta'}], {'q': ['exact']}, engine, [1, 3, 5, 10])
        metrics = report['aggregate_metrics']
        self.assertEqual(metrics['mean_precision@1'], 1.0)
        self.assertEqual(metrics['mean_recall@1'], 1.0)
        self.assertEqual(metrics['mean_reciprocal_rank'], 1.0)
        self.assertEqual(metrics['mean_ndcg@1'], 1.0)

    def test_cli_output_and_input_preservation(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            corpus = root / 'corpus'
            corpus.mkdir()
            for key, value in [('partial', 'alpha noise noise'), ('exact', 'alpha beta'), ('other', 'gamma')]:
                (corpus / (key + '.txt')).write_text(value)
            queries, truth = root / 'queries.json', root / 'truth.json'
            queries.write_text(json.dumps([{'id': 'q', 'query': 'alpha beta'}]))
            truth.write_text(json.dumps({'q': ['exact']}))
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
            for flags in ([], ['--verbose', '--k-values', '1', '3']):
                output = root / 'result.json'
                process = subprocess.run([sys.executable, '-B', str(SCRIPT), str(queries),
                    str(corpus), str(truth), '--output', str(output), *flags], capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                self.assertEqual(process.stderr, '')
                report = json.loads(output.read_text())
                self.assertEqual(report['query_results'][0]['retrieved_docs'][0][0], 'exact')
                self.assertEqual(report['aggregate_metrics']['mean_precision@1'], 1.0)
                self.assertIn('Evaluation Summary', process.stdout)
            for path, expected in before.items():
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), expected)


if __name__ == '__main__':
    unittest.main()
