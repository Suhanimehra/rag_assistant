import unittest
from backend.services.ranking import Candidate, reciprocal_rank_fusion, bm25_rank
from backend.services.chunking import extract_pages, normalize

class RankingTests(unittest.TestCase):
    def test_rrf_rewards_agreement(self):
        a = Candidate(1, 1, "a.pdf", 1, "python decorators", 0.8)
        b = Candidate(2, 1, "a.pdf", 2, "java classes", 0.7)
        c = Candidate(3, 2, "b.pdf", 1, "python classes", 0.5)
        self.assertEqual(reciprocal_rank_fusion([a, b], [c, b])[0].id, 2)
    def test_lexical_rank(self):
        a = Candidate(1, 1, "a", 1, "decorators decorators python", 0)
        b = Candidate(2, 1, "a", 2, "java classes", 0)
        self.assertEqual([c.id for c in bm25_rank("decorators", [b, a])], [1])
    def test_empty(self):
        self.assertEqual(reciprocal_rank_fusion([]), [])
        self.assertEqual(bm25_rank("anything", []), [])
    def test_text_preserves_lines(self):
        self.assertEqual(extract_pages(b"Title\n\n    code", "a.txt"), [(None, "Title\n\n    code")])
    def test_format_validation(self):
        with self.assertRaises(ValueError):
            extract_pages(b"not a PDF", "a.pdf")
    def test_empty_file(self):
        with self.assertRaises(ValueError):
            extract_pages(b"  ", "a.txt")

if __name__ == "__main__":
    unittest.main()
