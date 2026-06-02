import copy
import unittest

from src.provenance_tool.merge import merge_provenance


class ProvenanceMergeTest(unittest.TestCase):
    def test_dedupes_by_source_and_sorts_tags(self):
        records = [
            {"source_id": "b", "path": "b.py", "tags": ["tool"]},
            {"source_id": "a", "path": "a.py", "tags": ["code"]},
            {"source_id": "b", "path": "b.py", "tags": ["review", "tool"]},
        ]
        before = copy.deepcopy(records)
        self.assertEqual(
            merge_provenance(records),
            [
                {"source_id": "b", "path": "b.py", "tags": ["review", "tool"]},
                {"source_id": "a", "path": "a.py", "tags": ["code"]},
            ],
        )
        self.assertEqual(records, before)


if __name__ == "__main__":
    unittest.main()
