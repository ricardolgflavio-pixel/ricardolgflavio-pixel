"""Regressões locais das decisões SEO; sem abrir navegador ou acessar rede.

Executar: /tmp/li_venv/bin/python -B -m unittest discover -s tests -v
"""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import linkedin_auto_config as li


class SeoDecisionTests(unittest.TestCase):
    def test_job_added_share_prompt_is_closed_without_publishing(self):
        dialog, page = MagicMock(), MagicMock()
        dialog.wait_for.side_effect = li.PlaywrightTimeout('dialog replaced by share prompt')
        dialog.inner_text.return_value = 'Cargo adicionado. Agora, compartilhe esta atualização com sua rede.'
        self.assertTrue(li._save_and_wait(dialog, page))
        patterns = [request.kwargs['name'].pattern for request in dialog.get_by_role.call_args_list]
        self.assertEqual(len(patterns), 2)
        self.assertIn('Salvar', patterns[0])
        self.assertIn('Fechar', patterns[1])
        self.assertTrue(all('Publicar' not in pattern for pattern in patterns))

    def test_missing_project_date_does_not_create_position(self):
        page = MagicMock()
        with patch.object(li, '_seo_entry', return_value=None), patch.object(
            li, '_profile_data', return_value={}
        ), patch.object(li, '_open_dialog') as create:
            with self.assertRaises(li.PlaywrightError):
                li.action_seo_position(page, SimpleNamespace(seo_start_year=None), True)
            create.assert_not_called()

    def test_invalid_project_date_does_not_create_position(self):
        with patch.object(li, '_seo_entry', return_value=None), patch.object(
            li, '_profile_data', return_value={}
        ), patch.object(li, '_open_dialog') as create:
            with self.assertRaises(li.PlaywrightError):
                li.action_seo_position(MagicMock(), SimpleNamespace(seo_start_year='2026x'), True)
            create.assert_not_called()

    def test_confirmed_month_is_not_replaced_by_default_month(self):
        dialog = MagicMock()
        year_field, month_field, current = MagicMock(), MagicMock(), MagicMock()
        dialog.get_by_label.side_effect = lambda label, **kwargs: {
            'Ano de início': year_field,
            'Mês de início': month_field,
            'Trabalho aqui atualmente': current,
        }[label]
        configured = {'seo_primary_position': {'start_year': '2026', 'start_month': '1'}}
        with patch.object(li, '_profile_data', return_value=configured), patch.object(
            li, '_seo_entry', return_value=None
        ), patch.object(li, '_open_dialog', return_value=dialog), patch.object(
            li, '_plain_field'
        ), patch.object(li, '_set_checkbox'), patch.object(li, '_type_rich'), patch.object(
            li, '_seo_dates'
        ), patch.object(li, '_save_and_wait') as save:
            self.assertTrue(li.action_seo_position(MagicMock(), SimpleNamespace(seo_start_year=None), False))
        self.assertEqual(month_field.select_option.call_args_list[-1], call('1'))
        year_field.select_option.assert_called_with('2026')
        save.assert_not_called()

    def test_invalid_confirmed_month_does_not_open_form(self):
        configured = {'seo_primary_position': {'start_year': '2026', 'start_month': '13'}}
        with patch.object(li, '_profile_data', return_value=configured), patch.object(
            li, '_open_dialog'
        ) as create, self.assertRaises(li.PlaywrightError):
            li.action_seo_position(MagicMock(), SimpleNamespace(seo_start_year=None), True)
        create.assert_not_called()

    def test_company_is_matched_as_exact_line(self):
        page = MagicMock()
        unrelated = MagicMock()
        unrelated.inner_text.return_value = 'Cargo\nOutra empresa\nProjeto: ' + li.SEO_COMPANY
        expected = MagicMock()
        expected.inner_text.return_value = li.SEO_POSITION + '\n' + li.SEO_COMPANY + '\n2026 – o momento'
        page.locator.return_value.all.return_value = [unrelated, expected]
        with patch.object(li, '_section_text'):
            self.assertIs(li._seo_entry(page, li.SEO_COMPANY), expected)

    def test_duplicate_company_requires_disambiguation(self):
        page = MagicMock()
        entry = MagicMock()
        entry.inner_text.return_value = 'Cargo\n' + li.SEO_COMPANY
        page.locator.return_value.all.return_value = [entry, entry]
        with patch.object(li, '_section_text'), self.assertRaises(li.PlaywrightError):
            li._seo_entry(page, li.SEO_COMPANY)

    def test_date_cleanup_does_not_end_current_position(self):
        dialog = MagicMock()
        current = MagicMock()
        current.get_attribute.side_effect = lambda key: {'aria-label': 'Trabalho atualmente neste cargo'}.get(key)
        ending = MagicMock()
        ending.get_attribute.side_effect = lambda key: {'aria-label': 'Encerrar cargo atual a partir de agora - Outro'}.get(key)
        dialog.locator.return_value.all.return_value = [current, ending]
        with patch.object(li, '_set_checkbox') as toggle:
            li._seo_dates(dialog, '2018 – o momento')
            toggle.assert_called_once_with(ending, False)
        self.assertEqual(dialog.get_by_label.return_value.select_option.call_count, 2)

    def test_real_month_is_preserved(self):
        dialog = MagicMock()
        dialog.locator.return_value.all.return_value = []
        li._seo_dates(dialog, 'nov. de 2024 – o momento')
        dialog.get_by_label.assert_not_called()

    def test_description_with_ituran_does_not_invalidate_new_title(self):
        title = 'Ricardo Luiz G. Flávio - AutoTech AI OS | LinkedIn'
        result = 'Title\n' + title + '\nDescription\nExperiência anterior na Ituran'
        self.assertEqual(li._seo_inspector_title(result), title)
        self.assertTrue(li._seo_title_matches(li._seo_inspector_title(result)))

    def test_inspector_table_uses_tab_separated_title(self):
        title = 'Ricardo Luiz G. Flávio - Credenciado Ituran Rastreadores | LinkedIn'
        result = 'Property\tValue\nTitle\t' + title + '\nType\tArticle'
        self.assertEqual(li._seo_inspector_title(result), title)
        self.assertFalse(li._seo_title_matches(li._seo_inspector_title(result)))

    def test_unrelated_keywords_are_not_metadata_proof(self):
        result = 'Inspect\nDevSecOps\nDescription\nUm texto sobre AutoTech'
        self.assertIsNone(li._seo_inspector_title(result))
        self.assertFalse(li._seo_title_matches(None))

    def test_old_company_title_is_not_success(self):
        title = 'Ricardo Luiz G. Flávio - Credenciado Ituran Rastreadores | LinkedIn'
        self.assertFalse(li._seo_title_matches(li._seo_inspector_title('Title\n' + title)))


if __name__ == '__main__':
    unittest.main()
