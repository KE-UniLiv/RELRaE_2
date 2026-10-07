import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from relrae.modules.LLM_Ref import LLM, LLMRefinement, EvaluatorResponse


VALID = {"evaluation": "Yes", "justification": "Accurate", "confidence": 95}


class LLMTests(unittest.TestCase):
    def model(self, settings='gpt-example,none,{"temperature":0.5,"top_p":0.9}', repeats=1):
        return LLM(settings, EvaluatorResponse, repeats, "https://example.org/", "ex")

    def test_model_and_multiple_parameters_are_parsed(self):
        model = self.model()
        self.assertEqual(model.model, "gpt-example")
        self.assertEqual(model.api_key, "none")
        self.assertEqual(model.provider, "openai")
        self.assertEqual(model.get_params(42, "openai"),
                         {"temperature": 0.5, "top_p": 0.9, "seed": 42})

    def test_provider_selection(self):
        for settings, provider in [
            ('gemini-example,none,{}', 'google'),
            ('gemma:small,none,{}', 'ollama'),
            ('custom,none,{},openai', 'openai'),
            ('custom,none,{"provider":"google"}', 'google'),
            ('["custom","none",{},"openai"]', 'openai'),
            (["custom", "none", {}, "openai"], 'openai'),
        ]:
            with self.subTest(settings=settings):
                self.assertEqual(self.model(settings).provider, provider)

    def test_bad_settings_fail_before_provider_call(self):
        for settings in ['gpt-example', 'gpt-example,none,{broken}',
                         'gpt-example,none,[]', ',none,{}']:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                self.model(settings)
        with self.assertRaises(ValueError):
            self.model(repeats=0)

    def test_persistent_failure_stops_after_ten_calls(self):
        model = self.model(repeats=3)
        failure = RuntimeError("provider unavailable")
        model.call_provider = Mock(side_effect=failure)
        with self.assertRaisesRegex(RuntimeError, "after 10 attempts") as error:
            model.run_prompt([])
        self.assertIs(error.exception.__cause__, failure)
        self.assertEqual(model.call_provider.call_count, 10)

    def test_partial_success_does_not_hide_exhausted_retries(self):
        model = self.model(repeats=2)
        model.call_provider = Mock(side_effect=[VALID] + [ValueError("failed")] * 10)
        with self.assertRaisesRegex(RuntimeError, "repeat 2"):
            model.run_prompt([])
        self.assertEqual(model.call_provider.call_count, 11)

    def test_invalid_response_can_recover(self):
        model = self.model(repeats=2)
        model.call_provider = Mock(side_effect=['invalid JSON', VALID, VALID])
        results, logs = model.run_prompt([])
        self.assertEqual(results, [VALID, VALID])
        self.assertEqual(len(logs), 3)

    def test_config_prompt_data_is_parsed_without_interpolation(self):
        with tempfile.TemporaryDirectory() as root:
            config = Path(root) / "config"
            config.mkdir()
            (config / "LLM_ref_conf.txt").write_text(
                '[MAIN]\neval_examples=[[{"role":"user","content":"example"}]]\n'
                'ref_examples=[]\neval_messages=["100% accurate"]\n'
                'ref_messages=["refine"]\n', encoding="utf-8")
            refinement = LLMRefinement(None, None, "ex", "https://example.org/", root)
            self.assertEqual(refinement.config["eval_messages"], ["100% accurate"])
            examples = refinement.get_examples("eval", "one")
            messages = self.model().build_eval_prompt(
                "ex:relation", "domain", "XML", {}, [],
                refinement.config["eval_messages"], examples)
            self.assertEqual(messages[0]["content"], "100% accurate")
            self.assertEqual(messages[1]["content"], "example")


if __name__ == "__main__":
    unittest.main()
