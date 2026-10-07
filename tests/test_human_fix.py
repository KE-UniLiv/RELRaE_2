import unittest
from unittest.mock import patch

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDFS

from relrae.modules.human_fix import HumanFix


class HumanFixTests(unittest.TestCase):
    def test_replace_relation_updates_every_position(self):
        ns = Namespace("https://example.org/")
        for original in ("old", ns.old):
            with self.subTest(original=original):
                graph = Graph()
                graph.add((ns.old, RDFS.label, Literal("old")))
                graph.add((ns.subject, ns.old, ns.object))
                graph.add((ns.old, ns.old, ns.old))
                graph.add((ns.other, RDFS.label, ns.old))
                fix = HumanFix(None, graph, "ex", ns, None, [], "")
                fix.user.id = "reviewer"
                fix.replace_relation(original, "new")
                self.assertIn((ns.new, RDFS.label, Literal("new")), graph)
                self.assertIn((ns.subject, ns.new, ns.object), graph)
                self.assertIn((ns.new, ns.new, ns.new), graph)
                self.assertIn((ns.other, RDFS.label, ns.new), graph)
                self.assertFalse(any(ns.old in triple for triple in graph))

    def test_manual_fix_passes_relation_uri(self):
        ns = Namespace("https://example.org/")
        fix = HumanFix(None, Graph(), "ex", ns, None, [], "")
        errors = [[ns.old, {"ex:old": []}, ["rejected"]]]
        with patch("builtins.input", return_value="new"), \
                patch("builtins.print"), \
                patch.object(fix, "replace_relation") as replace:
            fix.fix_llm_ref(errors)
        replace.assert_called_once_with(ns.old, "new")


if __name__ == "__main__":
    unittest.main()
