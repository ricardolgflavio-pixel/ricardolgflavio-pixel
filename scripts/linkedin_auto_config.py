#!/usr/bin/env python3
"""Preenche o perfil do LinkedIn de Ricardo Luiz G. Flávio a partir de docs/LINKEDIN_KIT.md.

Fluxo
-----
1. Lê do kit os textos exatos: "Sobre", descrição do Projeto e Post 1.
2. Abre o Chromium (contexto persistente) em https://www.linkedin.com/in/ricardo-flavio/.
3. Se houver tela de login/checkpoint, aguarda você concluir manualmente na janela
   (o script nunca lê nem armazena usuário ou senha).
4. Ações automáticas (melhor esforço): A) Headline, B) "Sobre", C) rascunho do Post 1.
   C mantém o rascunho; W publica o post com imagem e comentário, quando solicitado.
5. Fallback: um painel flutuante com botões de 1 clique é injetado em todas as páginas
   do LinkedIn e preenche o campo focado, caso algum seletor tenha mudado.

Uso (a partir da raiz do repositório):
    /tmp/li_venv/bin/python scripts/linkedin_auto_config.py
    /tmp/li_venv/bin/python scripts/linkedin_auto_config.py --only A,C --no-save
    /tmp/li_venv/bin/python scripts/linkedin_auto_config.py --panel-only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from playwright.sync_api import BrowserContext, Locator, Page, sync_playwright
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeout

PROFILE_URL: Final[str] = "https://www.linkedin.com/in/ricardo-flavio/"
FEED_URL: Final[str] = "https://www.linkedin.com/feed/"
USER_DATA_DIR: Final[str] = "/tmp/linkedin_profile_session"
KIT_PATH: Final[Path] = Path(__file__).resolve().parent.parent / "docs" / "LINKEDIN_KIT.md"
LOGIN_TIMEOUT_S: Final[int] = 900
AUTH_URL_TOKENS: Final[tuple[str, ...]] = ("/login", "/authwall", "/checkpoint", "/uas/")

PROJECT_TITLE: Final[str] = "AutoTech AI OS & Zezé da Regulagem"
INDUSTRY_QUERY: Final[str] = "Serviços de tecnologia"
INDUSTRY_LABEL: Final[str] = "Atividades dos serviços de tecnologia da informação"
HEADLINE_LIMIT: Final[int] = 220
ABOUT_LIMIT: Final[int] = 2600
FIRST_NAME: Final[str] = "Ricardo Luiz"
LAST_NAME: Final[str] = "G. Flávio"


@dataclass(frozen=True)
class Education:
    """Entrada da seção Formação acadêmica."""

    school_query: str
    school_match: str
    degree: str
    field: str
    start_year: str
    end_year: str
    activities: str
    skills: tuple[str, ...]


EDUCATION: Final[tuple[Education, ...]] = (
    Education(
        school_query="Universidade Católica de Brasília",
        school_match="Universidade Católica de Brasília",
        degree="Curso Superior de Tecnologia (CST)",
        field="Segurança da Informação",
        start_year="2025",
        end_year="2028",
        activities="3º semestre. AppSec, DevSecOps, criptografia, GRC e segurança de aplicações com IA.",
        skills=(
            "Segurança da informação",
            "Application Security",
            "DevSecOps",
            "OWASP Top 10",
            "Criptografia",
        ),
    ),
    Education(
        school_query="FACIC",
        school_match="FACIC",
        degree="Bacharelado em Direito",
        field="Direito",
        start_year="2023",
        end_year="2028",
        activities="7º semestre. Direito Digital, LGPD, Propriedade Intelectual e Governança de IA.",
        skills=("LGPD", "Direito Digital", "Propriedade Intelectual", "Direitos autorais", "Proteção de dados"),
    ),
    Education(
        school_query="UNI VITÓRIA TEC", school_match="UNI VITÓRIA TEC",
        degree="Curso Técnico", field="Mecatrônica", start_year="2026", end_year="2026",
        activities="Curso Técnico em Mecatrônica — concluinte 2026.", skills=(),
    ),
)
ABOUT_SKILLS: Final[tuple[str, ...]] = (
    "Governança de IA",
    "Inteligência artificial generativa",
    "Compliance",
    "Privacy by Design",
    "Gestão de riscos",
)
PROJECT_SKILLS: Final[tuple[str, ...]] = (
    "Python",
    "LangGraph",
    "Retrieval-Augmented Generation (RAG)",
    "PostgreSQL",
    "Pydantic",
)
GITHUB_URL: Final[str] = "https://github.com/ricardolgflavio-pixel"
FEATURED_URL: Final[str] = "https://github.com/ricardolgflavio-pixel/ricardolgflavio-pixel"
BANNER_PATH: Final[Path] = Path("/tmp/linkedin_banner.png")
REMOVE_SKILLS: Final[tuple[str, ...]] = ("Assured Compliance Assessment Solution (ACAS)",)


@dataclass(frozen=True)
class Texts:
    """Textos prontos extraídos do kit."""

    headline: str
    about: str
    project_title: str
    project_description: str
    post1: str
    headline_en: str
    about_en: str
    project_en: str


def _text_blocks(markdown: str, heading_pattern: str) -> list[str]:
    """Devolve todos os blocos ```text após o cabeçalho que casa com o padrão."""
    heading = re.search(heading_pattern, markdown, re.MULTILINE)
    if heading is None:
        raise ValueError(f"Cabeçalho não encontrado no kit: {heading_pattern}")
    blocks = re.findall(r"```text\n(.*?)```", markdown[heading.end() :], re.DOTALL)
    if not blocks:
        raise ValueError(f"Bloco de texto ausente após: {heading_pattern}")
    return [block.strip() for block in blocks]


def _first_text_block(markdown: str, heading_pattern: str) -> str:
    return _text_blocks(markdown, heading_pattern)[0]


def load_texts(kit_path: Path = KIT_PATH) -> Texts:
    """Carrega e valida os textos de docs/LINKEDIN_KIT.md."""
    markdown = kit_path.read_text(encoding="utf-8")
    english = _text_blocks(markdown, r"^## 7\. Perfil em inglês")
    if len(english) < 3:
        raise ValueError("A seção 7 do kit deve conter headline, about e projeto em inglês.")
    texts = Texts(
        headline=_first_text_block(markdown, r"^## 1\. Headlines"),
        about=_first_text_block(markdown, r"^## 2\. Seção"),
        project_title=PROJECT_TITLE,
        project_description=_first_text_block(markdown, r"^## 3\. Experiência"),
        post1=_first_text_block(markdown, r"^### Post 1"),
        headline_en=english[0],
        about_en=english[1],
        project_en=english[2],
    )
    for label, value in (("Headline", texts.headline), ("Headline EN", texts.headline_en)):
        if len(value) > HEADLINE_LIMIT:
            raise ValueError(f"{label} com {len(value)} caracteres (máx. {HEADLINE_LIMIT}).")
    for label, value in (("Sobre", texts.about), ("Sobre EN", texts.about_en)):
        if len(value) > ABOUT_LIMIT:
            raise ValueError(f"{label} com {len(value)} caracteres (máx. {ABOUT_LIMIT}).")
    return texts


PANEL_JS: Final[str] = r"""
(() => {
  if (window.top !== window.self) return;
  const DATA = __PAYLOAD__;
  const PANEL_ID = "__li_autofill_panel";
  let lastField = null;

  const BLOCKED = ["checkbox", "radio", "button", "submit", "file", "hidden"];
  const isEditable = (el) => !!el && (
    el.tagName === "TEXTAREA" ||
    (el.tagName === "INPUT" && !BLOCKED.includes(el.type)) ||
    el.isContentEditable === true
  );
  document.addEventListener("focusin", (event) => {
    if (isEditable(event.target)) lastField = event.target;
  }, true);

  function setValue(el, text) {
    el.focus();
    if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      const proto = el.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, "value").set.call(el, text);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      return;
    }
    document.execCommand("selectAll", false, null);
    if (!document.execCommand("insertText", false, text)) {
      el.textContent = text;
      el.dispatchEvent(new InputEvent("input", { bubbles: true }));
    }
  }

  function toast(message, ok) {
    let box = document.getElementById(PANEL_ID + "_toast");
    if (!box) {
      box = document.createElement("div");
      box.id = PANEL_ID + "_toast";
      box.style.cssText = "margin-top:8px;padding:6px 8px;border-radius:6px;font:12px/1.3 sans-serif;color:#fff;";
      document.getElementById(PANEL_ID).appendChild(box);
    }
    box.style.background = ok ? "#1f7a4d" : "#b42318";
    box.textContent = message;
    clearTimeout(box._t);
    box._t = setTimeout(() => box.remove(), 6000);
  }

  function currentField() {
    return lastField && document.contains(lastField) ? lastField : null;
  }

  function fill(item) {
    const field = currentField();
    let text = DATA[item.key];
    if (item.key === "project") {
      text = field && field.tagName === "INPUT" ? DATA.project_title : DATA.project_description;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(() => {});
    }
    if (!field) {
      toast("Clique antes no campo de destino. Texto copiado: use Ctrl+V.", false);
      return;
    }
    setValue(field, text);
    toast(item.label + ": " + text.length + " caracteres inseridos.", true);
  }

  function build() {
    if (window.__LI_AUTOMATING || document.getElementById(PANEL_ID) || !document.body) return;
    const panel = document.createElement("div");
    panel.id = PANEL_ID;
    panel.style.cssText = "position:fixed;top:120px;right:12px;width:230px;z-index:2147483647;" +
      "background:#0b1220;color:#fff;border:2px solid #0a66c2;border-radius:10px;padding:10px;" +
      "box-shadow:0 6px 24px rgba(0,0,0,.4);font:13px/1.3 sans-serif;";
    const title = document.createElement("div");
    title.textContent = "Preenchimento 1-clique";
    title.style.cssText = "font-weight:700;margin-bottom:4px;";
    const hint = document.createElement("div");
    hint.textContent = "1) Clique no campo do LinkedIn  2) Clique no botão";
    hint.style.cssText = "font-size:11px;opacity:.8;margin-bottom:8px;";
    panel.append(title, hint);
    [
      { key: "headline", label: "Preencher Headline" },
      { key: "about", label: "Preencher Sobre" },
      { key: "project", label: "Preencher Projeto AutoTech AI OS" },
      { key: "post1", label: "Preencher Post 1" },
    ].forEach((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = item.label;
      button.style.cssText = "display:block;width:100%;margin:4px 0;padding:7px;border:0;" +
        "border-radius:6px;background:#0a66c2;color:#fff;font-weight:600;cursor:pointer;";
      button.addEventListener("mousedown", (event) => event.preventDefault());
      button.addEventListener("click", () => fill(item));
      panel.appendChild(button);
    });
    document.body.appendChild(panel);
  }

  build();
  document.addEventListener("DOMContentLoaded", build);
  setInterval(build, 1000);
})();
"""


def build_panel_script(texts: Texts) -> str:
    """Gera o JavaScript do painel flutuante com os textos embutidos como JSON."""
    payload = {
        "headline": texts.headline,
        "about": texts.about,
        "project_title": texts.project_title,
        "project_description": texts.project_description,
        "post1": texts.post1,
    }
    return PANEL_JS.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))


def log(message: str) -> None:
    """Imprime mensagem de progresso imediatamente."""
    sys.stdout.write(f"[li-auto] {message}\n")
    sys.stdout.flush()


def is_logged_in(page: Page) -> bool:
    """Sessão ativa: cookie li_at presente e URL de perfil/feed fora das telas de login."""
    url = page.url
    if any(token in url for token in AUTH_URL_TOKENS):
        return False
    if "/in/ricardo-flavio" not in url and "/feed" not in url:
        return False
    try:
        cookies = page.context.cookies("https://www.linkedin.com")
    except PlaywrightError:
        return False
    return any(cookie["name"] == "li_at" for cookie in cookies)


def wait_for_login(context: BrowserContext) -> Page | None:
    """Aguarda o login manual em qualquer aba; devolve a página logada ou None."""
    deadline = time.monotonic() + LOGIN_TIMEOUT_S
    announced = False
    while time.monotonic() < deadline:
        open_pages = [candidate for candidate in context.pages if not candidate.is_closed()]
        if not open_pages:
            log("A janela foi fechada antes do login. Rode o script novamente.")
            return None
        for candidate in open_pages:
            if is_logged_in(candidate):
                return candidate
        if not announced:
            log("Faça login (ou resolva o checkpoint) na janela aberta. Aguardando...")
            announced = True
        time.sleep(2)
    return None


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _type_rich(field: Locator, text: str) -> None:
    """Substitui o conteúdo de um campo contenteditable (editor do LinkedIn)."""
    field.wait_for(state="visible", timeout=15000)
    field.click()
    inserted = field.evaluate(
        """(el, value) => {
            el.focus();
            document.execCommand("selectAll", false, null);
            return document.execCommand("insertText", false, value);
        }""",
        text,
    )
    if not inserted:
        field.press("Control+A")
        field.page.keyboard.insert_text(text)


def _verify(field: Locator, expected: str, label: str) -> None:
    current = _normalize(field.inner_text())
    target = _normalize(expected)
    close_in_size = abs(len(current) - len(target)) <= max(5, len(target) // 20)
    if not (current.startswith(target[:40]) and close_in_size):
        raise PlaywrightError(f"O campo {label} não refletiu o texto esperado.")


def _goto(page: Page, url: str) -> None:
    """Navega com uma nova tentativa quando o SPA aborta a navegação anterior."""
    for attempt in range(3):
        try:
            page.goto(url, wait_until="domcontentloaded")
            return
        except PlaywrightError as exc:
            if "ERR_ABORTED" not in str(exc) or attempt == 2:
                raise
            page.wait_for_timeout(2000)


def _open_dialog(page: Page, url: str, marker: str) -> Locator:
    """Abre a URL de edição e devolve o <dialog> aberto que contém o campo-alvo."""
    _goto(page, url)
    dialog = page.locator(f"dialog[open]:has({marker})").first
    dialog.wait_for(state="attached", timeout=30000)
    return dialog


def _save_and_wait(dialog: Locator, page: Page) -> bool:
    save = dialog.get_by_role("button", name=re.compile(r"^(Salvar|Save)$", re.IGNORECASE)).first
    save.click(timeout=8000)
    try:
        dialog.wait_for(state="hidden", timeout=20000)
    except PlaywrightTimeout:
        raise PlaywrightError("Formulário permaneceu aberto após Salvar: " + dialog.inner_text()[-1600:]) from None
    page.wait_for_timeout(1500)
    return True


def _select_industry(dialog: Locator, page: Page) -> None:
    """Preenche o Setor (obrigatório) escolhendo a opção do typeahead, se estiver vazio."""
    field = dialog.locator('input[aria-label="Setor"], input[aria-label="Industry"]').first
    if field.count() == 0 or field.input_value().strip():
        return
    field.scroll_into_view_if_needed()
    field.click()
    field.fill(INDUSTRY_QUERY)
    option = page.get_by_role("option", name=re.compile(re.escape(INDUSTRY_LABEL), re.IGNORECASE)).first
    option.wait_for(state="visible", timeout=15000)
    option.click()
    page.wait_for_timeout(500)


def _add_skills(dialog: Locator, page: Page, skills: tuple[str, ...]) -> None:
    """Adiciona competências (digita, escolhe a sugestão do LinkedIn ou pula se não houver)."""
    added: list[str] = []
    for skill in skills:
        add_button = dialog.get_by_role("button", name=re.compile(r"^(Adicionar competência|Add skill)$", re.I)).first
        if add_button.count() > 0 and add_button.is_visible():
            add_button.click()
        box = dialog.locator('input[placeholder^="Competência"], input[placeholder^="Skill"]').first
        box.wait_for(state="visible", timeout=10000)
        box.click()
        box.fill("")
        box.type(skill, delay=70)
        page.wait_for_timeout(1800)
        options = page.locator('[role="option"]')
        preferred = options.filter(has_text=skill)
        if preferred.count() > 0:
            preferred.first.click()
            added.append(skill)
        elif options.count() > 0:
            label = options.first.inner_text().strip().splitlines()[0]
            options.first.click()
            added.append(label)
        else:
            box.fill("")
            log(f"Sem sugestão do LinkedIn para a competência '{skill}'; pulada.")
        page.wait_for_timeout(1200)
    log(f"Competências adicionadas: {', '.join(added)}")


def _typeahead(page: Page, field: Locator, query: str, match: str) -> None:
    """Digita em um campo com sugestões e escolhe a opção de texto igual (ou que começa com ele)."""
    field.click()
    field.fill("")
    field.type(query, delay=70)
    page.wait_for_timeout(2500)
    options = page.locator('[role="option"]')
    labels = [options.nth(i).inner_text().strip() for i in range(min(options.count(), 12))]
    wanted = match.casefold()
    exact = [i for i, label in enumerate(labels) if label.casefold() == wanted]
    prefix = [i for i, label in enumerate(labels) if label.casefold().startswith(wanted)]
    chosen = exact or prefix
    if chosen:
        options.nth(chosen[0]).click()
    else:
        log(f"Sem sugestão compatível para '{query}' (opções: {labels[:4]}); mantendo o texto digitado.")
    page.wait_for_timeout(800)


def action_headline(page: Page, texts: Texts, save: bool) -> bool:
    """Ação A: abre /edit/intro/, atualiza nome, headline e setor."""
    dialog = _open_dialog(
        page,
        PROFILE_URL + "edit/intro/",
        '[role="textbox"][aria-label="Título"], [role="textbox"][aria-label="Headline"]',
    )
    field = dialog.locator('[role="textbox"][aria-label="Título"], [role="textbox"][aria-label="Headline"]').first
    _type_rich(field, texts.headline)
    _verify(field, texts.headline, "Headline")
    for label, value in (("Nome", FIRST_NAME), ("Sobrenome", LAST_NAME)):
        name_field = dialog.locator(f'input[aria-label="{label}"]').first
        if name_field.count() > 0 and name_field.input_value() != value:
            name_field.fill(value)
    _select_industry(dialog, page)
    if save:
        dialog.get_by_role("button", name=re.compile(r"^(Salvar|Save)$", re.I)).first.click()
        page.wait_for_timeout(3000)
        dialog = _open_dialog(page, PROFILE_URL + "edit/intro/", '[role="textbox"]')
        field = dialog.locator('[role="textbox"][aria-label="Título"], [role="textbox"][aria-label="Headline"]').first
        field.wait_for(state="visible", timeout=15000)
        page.wait_for_timeout(2000)
        if _normalize(field.inner_text()) != _normalize(texts.headline):
            raise PlaywrightError("Headline não persistiu após salvar.")
        return True
    log("Introdução preenchida; salve manualmente (--no-save).")
    return True


def _fill_about(page: Page, texts: Texts, save: bool, with_skills: bool) -> bool:
    dialog = _open_dialog(
        page,
        PROFILE_URL + "edit/forms/summary/new/",
        '[role="textbox"][aria-label="Sobre"], [role="textbox"][aria-label="About"], [contenteditable="true"]',
    )
    field = dialog.locator('[role="textbox"][aria-label="Sobre"], [role="textbox"][aria-label="About"]').first
    if field.count() == 0:
        field = dialog.locator('[aria-label="Sobre"], [aria-label="About"], [contenteditable="true"]').first
    _type_rich(field, texts.about)
    _verify(field, texts.about, "Sobre")
    if with_skills:
        _add_skills(dialog, page, ABOUT_SKILLS)
    if save:
        return _save_and_wait(dialog, page)
    log("Seção Sobre preenchida; salve manualmente (--no-save).")
    return True


def action_about(page: Page, texts: Texts, save: bool) -> bool:
    """Ação B: abre /edit/forms/summary/new/, preenche o Sobre e adiciona competências."""
    return _fill_about(page, texts, save, with_skills=True)


def action_about_text(page: Page, texts: Texts, save: bool) -> bool:
    """Ação M: atualiza apenas o texto do Sobre (sem tocar nas competências)."""
    return _fill_about(page, texts, save, with_skills=False)


def action_english_headline(page: Page, texts: Texts, save: bool) -> bool:
    """Ação L: atualiza a headline na aba English do perfil secundário."""
    dialog = _open_dialog(page, PROFILE_URL + "edit/intro/", '[role="textbox"]')
    dialog.get_by_text("English", exact=True).first.click(timeout=10000)
    page.wait_for_timeout(2500)
    field = dialog.locator('[role="textbox"]').first
    _type_rich(field, texts.headline_en)
    _verify(field, texts.headline_en, "Headline (EN)")
    if save:
        return _save_and_wait(dialog, page)
    return True


def action_education_update(page: Page, texts: Texts, save: bool) -> bool:
    """Ação Q: atualiza as atividades (semestre) das formações já cadastradas."""
    for item in EDUCATION:
        _goto(page, PROFILE_URL + "details/education/")
        links = page.locator('a[href*="/details/education/edit/forms/"]')
        links.first.wait_for(state="attached", timeout=30000)
        target = ""
        for index in range(links.count()):
            label = links.nth(index).get_attribute("aria-label") or ""
            if item.school_match.casefold() in label.casefold():
                target = links.nth(index).get_attribute("href") or ""
                break
        if not target:
            raise PlaywrightError(f"Formação '{item.school_match}' não encontrada.")
        dialog = _open_dialog(page, target, 'textarea[aria-label^="Atividades"], textarea[aria-label^="Activities"]')
        area = dialog.locator('textarea[aria-label^="Atividades"], textarea[aria-label^="Activities"]').first
        area.fill(item.activities)
        if area.input_value() != item.activities:
            raise PlaywrightError("O campo Atividades não refletiu o texto esperado.")
        if save:
            _save_and_wait(dialog, page)
        log(f"Formação atualizada: {item.school_match}")
    return True


def action_banner(page: Page, texts: Texts, save: bool) -> bool:
    """Ação N: envia o banner 1584x396 como imagem de capa do perfil."""
    if not BANNER_PATH.exists():
        raise PlaywrightError(f"Banner ausente: {BANNER_PATH} (rode generate_linkedin_banner.py).")
    _goto(page, PROFILE_URL)
    page.wait_for_timeout(5000)
    page.locator('button[aria-label*="imagem de fundo" i], button[aria-label*="imagem de capa" i]').first.click(
        timeout=20000
    )
    page.get_by_text(re.compile(r"^(Adicionar|Alterar) imagem de capa$")).first.click(timeout=10000)
    dialog = page.locator("dialog[open]:has(button)").last
    dialog.wait_for(state="visible", timeout=30000)
    with page.expect_file_chooser(timeout=15000) as chooser:
        dialog.get_by_role("button", name=re.compile(r"Carregar foto", re.I)).first.click()
    chooser.value.set_files(str(BANNER_PATH))
    page.wait_for_timeout(4000)
    for name in ("Salvar alterações", "Salvar"):
        button = page.locator("dialog[open]").get_by_role("button", name=re.compile(rf"^{name}$", re.I)).last
        if button.count() > 0 and save:
            button.wait_for(state="visible", timeout=15000)
            button.click(timeout=10000)
            page.wait_for_timeout(5000)
    return True


def action_contact_site(page: Page, texts: Texts, save: bool) -> bool:
    """Ação P: adiciona o GitHub como site nas informações de contato."""
    dialog = _open_dialog(page, PROFILE_URL + "edit/forms/contact-info/new/", "select")
    dialog.get_by_role("button", name=re.compile("Adicionar site")).click(timeout=10000)
    page.wait_for_timeout(1500)
    url_input = dialog.locator('input[type="text"]').last
    url_input.fill(GITHUB_URL)
    dialog.locator("select").last.select_option(label="Portfólio")
    if url_input.input_value() != GITHUB_URL:
        raise PlaywrightError("O campo do site não refletiu a URL esperada.")
    if save:
        return _save_and_wait(dialog, page)
    return True


def action_featured_link(page: Page, texts: Texts, save: bool) -> bool:
    """Ação O: adiciona o repositório do GitHub à seção Em destaque."""
    _goto(page, PROFILE_URL + "details/featured/")
    page.get_by_role("button", name="Menu de estouro em destaque").click(timeout=30000)
    page.get_by_role("menuitem").filter(has_text="Adicionar link").first.click(timeout=10000)
    dialog = page.locator("dialog[open]:has(input)").first
    dialog.wait_for(state="attached", timeout=15000)
    box = dialog.locator("input").first
    box.fill(FEATURED_URL)
    dialog.get_by_role("button", name=re.compile(r"^Adicionar$")).first.click(timeout=10000)
    page.wait_for_timeout(6000)
    if save:
        return _save_and_wait(dialog, page)
    return True


def action_post(page: Page, texts: Texts, _save: bool) -> bool:
    """Ação C: abre o compositor de publicação e cola o Post 1 (sem publicar)."""
    _goto(page, FEED_URL)
    start = page.get_by_role(
        "button", name=re.compile(r"(Começar publicação|Start a post)", re.IGNORECASE)
    ).first
    start.click(timeout=20000)
    dialog = page.locator('dialog[open]:has([role="textbox"])').first
    dialog.wait_for(state="attached", timeout=30000)
    editor = dialog.locator('[role="textbox"]').first
    _type_rich(editor, texts.post1)
    log("Post 1 colado no rascunho. Revise e clique em 'Publicar' (o script não publica).")
    return True


def action_project(page: Page, texts: Texts, save: bool) -> bool:
    """Ação D: cadastra o projeto AutoTech AI OS na seção Projetos."""
    dialog = _open_dialog(
        page,
        PROFILE_URL + "edit/forms/project/new/",
        'textarea[aria-label^="Descrição"], textarea[aria-label^="Description"]',
    )
    name = dialog.locator('input[type="text"]').first
    name.wait_for(state="visible", timeout=15000)
    name.fill(texts.project_title)
    description = dialog.locator('textarea[aria-label^="Descrição"], textarea[aria-label^="Description"]').first
    description.fill(texts.project_description)
    if name.input_value() != texts.project_title or description.input_value() != texts.project_description:
        raise PlaywrightError("Os campos do projeto não refletiram o texto esperado.")
    if save:
        return _save_and_wait(dialog, page)
    log("Projeto preenchido; salve manualmente (--no-save).")
    return True


def action_edit_post(page: Page, texts: Texts, save: bool) -> bool:
    """Ação E: edita a publicação já feita com o texto corrigido do Post 1."""
    _goto(page, PROFILE_URL + "recent-activity/all/")
    menu = page.locator('button[aria-label*="menu de controle da publicação" i]').first
    menu.wait_for(state="visible", timeout=30000)
    page.wait_for_timeout(5000)
    item = page.get_by_role("menuitem").filter(has_text="Editar publicação").first
    for _attempt in range(3):
        menu.click()
        try:
            item.wait_for(state="visible", timeout=5000)
            break
        except PlaywrightTimeout:
            page.keyboard.press("Escape")
            page.wait_for_timeout(1500)
    item.click(timeout=10000)
    dialog = page.locator('dialog[open]:has([role="textbox"])').first
    dialog.wait_for(state="attached", timeout=30000)
    editor = dialog.locator('[role="textbox"]').first
    _type_rich(editor, texts.post1)
    _verify(editor, texts.post1, "Post")
    if save:
        return _save_and_wait(dialog, page)
    log("Post editado; salve manualmente (--no-save).")
    return True


def action_comment(page: Page, texts: Texts, save: bool) -> bool:
    """Ação F: adiciona o comentário com o link do GitHub, se ainda não existir."""
    _goto(page, PROFILE_URL + "recent-activity/all/")
    comment_button = page.get_by_role("button", name=re.compile(r"^Comentar$", re.I)).first
    comment_button.wait_for(state="visible", timeout=30000)
    page.wait_for_timeout(5000)
    if "ricardolgflavio-pixel" in page.locator("main").inner_text():
        log("Comentário com o link do GitHub já existe; nada a fazer.")
        return True
    box = page.get_by_role("textbox", name=re.compile(r"coment", re.I)).first
    for _attempt in range(3):
        comment_button.click()
        try:
            box.wait_for(state="visible", timeout=6000)
            break
        except PlaywrightTimeout:
            page.wait_for_timeout(1500)
    box.wait_for(state="visible", timeout=10000)
    comment = f"Código, pipeline de CI e ADR de governança: {GITHUB_URL}/ricardolgflavio-pixel"
    _type_rich(box, comment)
    if save:
        page.get_by_role("button", name=re.compile(r"^Comentar$", re.I)).last.click(timeout=10000)
        page.wait_for_timeout(3000)
    return True


def _pick_year(dialog: Locator, index: int, year: str) -> None:
    dialog.locator("select").nth(index).select_option(label=year)


def action_education(page: Page, texts: Texts, save: bool) -> bool:
    """Ação G: cadastra UCB e FACIC em Formação acadêmica (com 5 competências cada)."""
    for item in EDUCATION:
        dialog = _open_dialog(
            page,
            PROFILE_URL + "edit/forms/education/new/",
            'input[aria-label="Diploma"], input[aria-label="Degree"]',
        )
        school = dialog.get_by_label(re.compile(r"Instituição de ensino|School", re.I)).first
        _typeahead(page, school, item.school_query, item.school_match)
        degree = dialog.locator('input[aria-label="Diploma"], input[aria-label="Degree"]').first
        _typeahead(page, degree, item.degree, item.degree)
        study = dialog.locator('input[aria-label="Área de estudo"], input[aria-label="Field of study"]').first
        _typeahead(page, study, item.field, item.field)
        _pick_year(dialog, 1, item.start_year)
        _pick_year(dialog, 3, item.end_year)
        dialog.locator('textarea[aria-label^="Atividades"], textarea[aria-label^="Activities"]').first.fill(item.activities)
        _add_skills(dialog, page, item.skills)
        if save:
            _save_and_wait(dialog, page)
        else:
            log(f"Formação '{item.school_query}' preenchida; salve manualmente (--no-save).")
            return True
        log(f"Formação cadastrada: {item.field} ({item.school_query})")
    return True


def action_project_skills(page: Page, texts: Texts, save: bool) -> bool:
    """Ação H: abre o projeto existente e adiciona 5 competências."""
    _goto(page, PROFILE_URL + "details/projects/")
    link = page.locator('a[href*="/details/projects/edit/forms/"]').first
    link.wait_for(state="attached", timeout=30000)
    href = link.get_attribute("href") or ""
    dialog = _open_dialog(page, href, 'textarea[aria-label^="Descrição"], textarea[aria-label^="Description"]')
    _add_skills(dialog, page, PROJECT_SKILLS)
    if save:
        return _save_and_wait(dialog, page)
    return True


def action_remove_skills(page: Page, texts: Texts, save: bool) -> bool:
    """Ação R: remove competências sugeridas incorretamente pelo LinkedIn."""
    dialog = _open_dialog(page, PROFILE_URL + "edit/forms/summary/new/", '[role="textbox"]')
    page.wait_for_timeout(3000)
    for skill in REMOVE_SKILLS:
        button = dialog.get_by_role("button", name=f"Remover {skill} da lista").first
        if button.count() == 0:
            log(f"Competência '{skill}' não está neste item; nada a remover.")
            continue
        button.click()
        page.wait_for_timeout(800)
        log(f"Competência removida: {skill}")
    if save:
        return _save_and_wait(dialog, page)
    return True


def action_english_profile(page: Page, texts: Texts, save: bool) -> bool:
    """Ação I: cria o perfil secundário em inglês (nome e headline)."""
    _goto(page, PROFILE_URL + "edit/secondary-language/")
    page.locator("a:has-text('Adicionar idioma')").first.click(timeout=30000)
    dialog = page.locator("dialog[open]:has(select)").first
    dialog.wait_for(state="attached", timeout=15000)
    dialog.locator("select").first.select_option(label="English (Inglês)")
    page.wait_for_timeout(1500)
    names = dialog.locator('input[type="text"]')
    names.nth(0).fill(FIRST_NAME)
    names.nth(1).fill(LAST_NAME)
    headline_area = dialog.locator("textarea").first
    if headline_area.count() > 0:
        headline_area.fill(texts.headline_en)
        if headline_area.input_value() != texts.headline_en:
            raise PlaywrightError("O campo Título (EN) não refletiu o texto esperado.")
    else:
        headline = dialog.locator('[role="textbox"]').first
        _type_rich(headline, texts.headline_en)
        _verify(headline, texts.headline_en, "Headline (EN)")
    if save:
        return _save_and_wait(dialog, page)
    log("Perfil em inglês preenchido; salve manualmente (--no-save).")
    return True


def action_english_about(page: Page, texts: Texts, save: bool) -> bool:
    """Ação J: preenche o Sobre na aba English do perfil secundário."""
    dialog = _open_dialog(
        page,
        PROFILE_URL + "edit/forms/summary/new/?language=en_US&locale=en_US",
        '[role="textbox"]',
    )
    dialog.get_by_text("English", exact=True).first.click(timeout=10000)
    page.wait_for_timeout(2500)
    field = dialog.locator('[role="textbox"]').first
    _type_rich(field, texts.about_en)
    _verify(field, texts.about_en, "About (EN)")
    if save:
        return _save_and_wait(dialog, page)
    log("About (EN) preenchido; salve manualmente (--no-save).")
    return True


def action_english_project(page: Page, texts: Texts, save: bool) -> bool:
    """Ação K: preenche título e descrição do projeto na aba English, se existir."""
    _goto(page, PROFILE_URL + "details/projects/")
    link = page.locator('a[href*="/details/projects/edit/forms/"]').first
    link.wait_for(state="attached", timeout=30000)
    href = link.get_attribute("href") or ""
    separator = "&" if "?" in href else "?"
    dialog = _open_dialog(
        page,
        f"{href}{separator}language=en_US&locale=en_US",
        'textarea[aria-label^="Descrição"], textarea[aria-label^="Description"]',
    )
    dialog.get_by_text("English", exact=True).first.click(timeout=10000)
    page.wait_for_timeout(2500)
    name = dialog.locator('input[type="text"]').first
    name.fill(texts.project_title)
    description = dialog.locator("textarea").first
    description.fill(texts.project_en)
    if description.input_value() != texts.project_en:
        raise PlaywrightError("A descrição do projeto (EN) não refletiu o texto esperado.")
    if save:
        return _save_and_wait(dialog, page)
    log("Projeto (EN) preenchido; salve manualmente (--no-save).")
    return True


PROFILE_DATA_PATH = Path(__file__).with_name("linkedin_profile_data.json")
POST_CARD_PATH = Path("/tmp/linkedin_post_card.png")
POST_RECEIPT = Path("/tmp/linkedin_post_receipt.json")


def _profile_data() -> dict:
    return json.loads(PROFILE_DATA_PATH.read_text(encoding="utf-8"))


def _section_text(page: Page, section: str) -> str:
    _goto(page, PROFILE_URL + f"details/{section}/")
    page.locator("main").wait_for(state="visible", timeout=20000)
    page.wait_for_timeout(2500)
    return _normalize(page.locator("main").inner_text()).casefold()


def _plain_field(field: Locator, value: str) -> None:
    """Preenche texto sem selecionar uma organização homônima sugerida."""
    field.fill(value)
    field.press("Tab")
    if field.input_value() != value:
        raise PlaywrightError("Campo não preservou o valor solicitado.")


def action_location(page: Page, texts: Texts, save: bool) -> bool:
    dialog = _open_dialog(page, PROFILE_URL + "edit/intro/", 'input[aria-label="Cidade"]')
    city = dialog.get_by_label("Cidade", exact=True)
    expected = "Lorena, São Paulo, Brasil"
    if city.input_value() == expected:
        log("Localização persistida já confirmada: " + expected)
        return True
    _typeahead(page, city, "Lorena", expected)
    if city.input_value() != expected:
        raise PlaywrightError("Sugestão de cidade não selecionada.")
    if save:
        dialog.get_by_role("button", name="Salvar", exact=True).click()
        page.wait_for_timeout(3000)
        dialog = _open_dialog(page, PROFILE_URL + "edit/intro/", 'input[aria-label="Cidade"]')
        if dialog.get_by_label("Cidade", exact=True).input_value() != expected:
            raise PlaywrightError("Cidade não persistiu após salvar.")
    return True


def _set_checkbox(field: Locator, checked: bool) -> None:
    """Aciona o input nativo dos controles estilizados e confirma seu estado."""
    if field.is_checked() != checked:
        field.evaluate("element => element.click()")
    if field.is_checked() != checked:
        raise PlaywrightError("Checkbox não refletiu o estado solicitado.")


def action_experiences(page: Page, texts: Texts, save: bool) -> bool:
    for item in _profile_data()["experiences"]:
        existing = _section_text(page, "experience")
        if _normalize(item["title"]).casefold() in existing:
            log("Experiência já cadastrada: " + item["title"])
            continue
        dialog = _open_dialog(page, PROFILE_URL + "edit/forms/position/new/", 'input:not([type]),input[type="text"]')
        notification = dialog.get_by_role("switch")
        if notification.count() and notification.is_checked():
            _set_checkbox(notification, False)
        fields = dialog.locator('input:not([type]),input[type="text"]')
        _plain_field(fields.nth(0), item["title"])
        _plain_field(fields.nth(1), item["company"])
        _plain_field(fields.nth(2), item["location"])
        current = dialog.get_by_label("Trabalho aqui atualmente", exact=True)
        _set_checkbox(current, not bool(item["end"]))
        for checkbox in dialog.locator('input[type="checkbox"]').all():
            if checkbox.get_attribute("id") != current.get_attribute("id"):
                _set_checkbox(checkbox, False)
        dialog.get_by_label("Ano de início", exact=False).select_option(item["start"])
        if item["end"]:
            dialog.get_by_label("Ano de término", exact=False).select_option(item["end"])
        dialog.get_by_label("Mês de início", exact=False).select_option("")
        if item["end"]:
            dialog.get_by_label("Mês de término", exact=False).select_option("")
        description = dialog.locator('[role="textbox"],textarea').first
        if description.evaluate("el=>el.tagName") == "TEXTAREA":
            description.fill(item["description"])
        else:
            _type_rich(description, item["description"])
            _verify(description, item["description"], "Experiência")
        if not save:
            return True
        # Alguns controles só aparecem após datas/descrição; preservar as posições paralelas.
        for checkbox in dialog.locator('input[type="checkbox"]').all():
            if checkbox.get_attribute("id") != current.get_attribute("id"):
                _set_checkbox(checkbox, False)
        _save_and_wait(dialog, page)
        if _normalize(item["title"]).casefold() not in _section_text(page, "experience"):
            raise PlaywrightError("Experiência não encontrada após salvar.")
        log("Experiência salva e verificada: " + item["company"] + " " + item["start"])
    return True


def action_year_only_dates(page: Page, texts: Texts, save: bool) -> bool:
    """Remove meses automáticos: o titular forneceu somente os anos das experiências."""
    for item in _profile_data()["experiences"]:
        _section_text(page, "experience")
        entry = page.locator('a[href*="/details/experience/edit/forms/"]:not([aria-label])').filter(has_text=item["title"]).first
        existing_dates = entry.inner_text()
        if (item["start"] in existing_dates and (not item["end"] or item["end"] in existing_dates)
                and not re.search(r"\b(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\.", existing_dates, re.I)):
            log("Datas já confirmadas apenas por ano: " + item["company"])
            continue
        edit = page.get_by_role("link", name="Editar " + item["title"] + " na empresa " + item["company"], exact=True).first
        target = edit.get_attribute("href")
        if not target:
            raise PlaywrightError("Link de edição da experiência ausente.")
        dialog = _open_dialog(page, target, 'select')
        dialog.get_by_label("Mês de início", exact=False).select_option("")
        if item["end"]:
            dialog.get_by_label("Mês de término", exact=False).select_option("")
        notification = dialog.get_by_role("switch")
        if notification.count():
            _set_checkbox(notification.first, False)
        if not save:
            return True
        _save_and_wait(dialog, page)
        _section_text(page, "experience")
        entry = page.locator('a[href*="/details/experience/edit/forms/"]:not([aria-label])').filter(has_text=item["title"]).first
        date_text = entry.inner_text()
        if item["start"] not in date_text or (item["end"] and item["end"] not in date_text):
            raise PlaywrightError("Os anos fornecidos não persistiram após a edição.")
        if re.search(r"\b(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\.", date_text, re.I):
            raise PlaywrightError("LinkedIn manteve mês obrigatório; os meses reais precisam ser informados pelo titular.")
        log("Datas com precisão de ano confirmadas: " + item["company"] + " " + item["start"])
    return True


def action_certifications(page: Page, texts: Texts, save: bool) -> bool:
    for item in _profile_data()["certifications"]:
        existing = _section_text(page, "certifications")
        if _normalize(item["name"]).casefold() in existing:
            log("Certificado já cadastrado: " + item["name"])
            continue
        dialog = _open_dialog(page, PROFILE_URL + "edit/forms/certification/new/", 'input[aria-label="Nome*"]')
        name = item["name"] + f" ({item['hours']}h" + (f" — {item['grade']}" if item["grade"] else "") + ")"
        _plain_field(dialog.get_by_label("Nome*", exact=True), name)
        _plain_field(dialog.get_by_label("Organização emissora*", exact=True), item["issuer"])
        dialog.locator("select").nth(0).select_option(str(item["month"]))
        dialog.locator("select").nth(1).select_option(item["year"])
        if item["credential"]:
            dialog.get_by_label("Código da credencial", exact=False).fill(item["credential"])
        if not save:
            return True
        _save_and_wait(dialog, page)
        if _normalize(item["name"]).casefold() not in _section_text(page, "certifications"):
            raise PlaywrightError("Certificado não encontrado após salvar.")
        log("Certificado salvo e verificado: " + item["name"])
    return True


def action_mechatronics(page: Page, texts: Texts, save: bool) -> bool:
    if "uni vitória tec" in _section_text(page, "education"):
        log("UNI VITÓRIA TEC já cadastrada.")
        return True
    item = EDUCATION[-1]
    dialog = _open_dialog(page, PROFILE_URL + "edit/forms/education/new/", 'input[aria-label="Diploma"]')
    _plain_field(dialog.get_by_label(re.compile(r"Instituição de ensino|School", re.I)).first, item.school_query)
    _plain_field(dialog.get_by_label("Diploma", exact=True), item.degree)
    _plain_field(dialog.get_by_label("Área de estudo", exact=True), item.field)
    _pick_year(dialog, 1, item.start_year)
    _pick_year(dialog, 3, item.end_year)
    dialog.locator('textarea[aria-label^="Atividades"]').first.fill(item.activities)
    if save:
        _save_and_wait(dialog, page)
        if "uni vitória tec" not in _section_text(page, "education"):
            raise PlaywrightError("Formação não encontrada após salvar.")
    return True


def render_post_card(context: BrowserContext) -> None:
    card = context.new_page()
    card.set_viewport_size({"width": 1200, "height": 627})
    try:
        source = KIT_PATH.parent.parent / "assets" / "linkedin_post_card.html"
        card.set_content(source.read_text(encoding="utf-8"))
        card.screenshot(path=str(POST_CARD_PATH))
    finally:
        card.close()


def _comment_on_post(page: Page, url: str, save: bool) -> bool:
    _goto(page, url)
    page.wait_for_timeout(2500)
    article = page.locator('div.feed-shared-update-v2, article').filter(has_text="DA EPROM AO LANGGRAPH").first
    if not article.count():
        article = page.locator("main")
    # A URL identifica a publicação recém-criada; nunca comentar na primeira atividade arbitrária.
    if FEATURED_URL in article.inner_text():
        return True
    button = article.get_by_role("button", name=re.compile(r"^Comentar$|^Comment$", re.I)).first
    button.click()
    editor = article.locator('[contenteditable="true"][role="textbox"]').first
    _type_rich(editor, "Código, pipeline de CI e ADR de governança: " + FEATURED_URL)
    if save:
        article.get_by_role("button", name=re.compile(r"^Comentar$|^Comment$", re.I)).last.click()
        article.get_by_text("Código, pipeline de CI e ADR de governança:", exact=False).first.wait_for(timeout=15000)
    return True


def action_publish_card(page: Page, texts: Texts, save: bool) -> bool:
    render_post_card(page.context)
    if POST_RECEIPT.exists():
        receipt = json.loads(POST_RECEIPT.read_text())
        if receipt.get("text") == texts.post1:
            return _comment_on_post(page, receipt["url"], save)
    _goto(page, PROFILE_URL + "recent-activity/all/")
    page.wait_for_timeout(2500)
    if "DA EPROM AO LANGGRAPH: 31 ANOS" in page.locator("main").inner_text():
        raise PlaywrightError("Post já existe; falta recibo com URL. Publicação interrompida para evitar duplicata.")
    action_post(page, texts, False)
    dialog = page.locator('dialog[open]:has([role="textbox"])').first
    _verify(dialog.locator('[role="textbox"]').first, texts.post1, "Post")
    media = dialog.get_by_role("button", name=re.compile(r"mídia|media|foto|photo", re.I)).first
    with page.expect_file_chooser() as chooser:
        media.click()
    chooser.value.set_files(str(POST_CARD_PATH))
    page.wait_for_timeout(1500)
    next_button = page.get_by_role("button", name=re.compile(r"^Avançar$|^Next$", re.I)).last
    if next_button.is_visible():
        next_button.click()
    preview = dialog.locator('img[src^="blob:"],img[src*="media.licdn.com"]')
    preview.first.wait_for(state="visible", timeout=30000)
    if not save:
        return True
    dialog.get_by_role("button", name=re.compile(r"^Publicar$|^Post$", re.I)).click()
    dialog.wait_for(state="hidden", timeout=30000)
    view = page.get_by_role("link", name=re.compile(r"Ver publicação|View post", re.I)).first
    view.wait_for(state="visible", timeout=20000)
    url = view.get_attribute("href")
    if not url:
        raise PlaywrightError("Publicação enviada; URL não confirmada. Não executar novamente sem inspeção.")
    POST_RECEIPT.write_text(json.dumps({"url": url, "text": texts.post1}, ensure_ascii=False))
    log("Publicação confirmada: " + url)
    return _comment_on_post(page, url, save)


ACTIONS: Final[dict[str, tuple[str, Callable[[Page, Texts, bool], bool]]]] = {
    "X": ("Datas de experiências apenas por ano", action_year_only_dates),
    "S": ("Localização Lorena", action_location),
    "T": ("Oito experiências profissionais", action_experiences),
    "U": ("Sete certificados", action_certifications),
    "V": ("Formação em Mecatrônica", action_mechatronics),
    "W": ("Publicar card e comentar link", action_publish_card),
    "L": ("Headline em inglês", action_english_headline),
    "M": ("Sobre (apenas texto)", action_about_text),
    "N": ("Banner de capa", action_banner),
    "O": ("Em destaque (link do GitHub)", action_featured_link),
    "P": ("Site do GitHub nas informações de contato", action_contact_site),
    "Q": ("Atualizar formações (semestres)", action_education_update),
    "J": ("Sobre em inglês", action_english_about),
    "K": ("Projeto em inglês", action_english_project),
    "I": ("Perfil em inglês (nome e headline)", action_english_profile),
    "R": ("Remover competências incorretas", action_remove_skills),
    "A": ("Introdução (nome, headline, setor)", action_headline),
    "B": ("Sobre e competências", action_about),
    "C": ("Rascunho do Post 1", action_post),
    "D": ("Projeto AutoTech AI OS", action_project),
    "E": ("Editar publicação", action_edit_post),
    "F": ("Comentário com link do GitHub", action_comment),
    "G": ("Formação acadêmica", action_education),
    "H": ("Competências do projeto", action_project_skills),
}


def run_actions(page: Page, texts: Texts, selected: list[str], save: bool) -> bool:
    """Executa as ações em melhor esforço; falhas apontam para o painel de fallback."""
    success = True
    for key in selected:
        name, action = ACTIONS[key]
        try:
            if not action(page, texts, save):
                raise PlaywrightError("Ação retornou falha.")
            log(f"Ação {key} ({name}): OK")
        except (PlaywrightTimeout, PlaywrightError) as exc:
            detail = str(exc).strip().splitlines()
            summary = " | ".join(detail[:12]) if detail else type(exc).__name__
            log(f"Ação {key} ({name}): falhou ({summary}). Use o painel flutuante.")
            success = False
    return success


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Interpreta os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Automatiza o preenchimento do perfil do LinkedIn.")
    parser.add_argument(
        "--only",
        default="",
        help="ações a executar, ex.: A,E (A intro, B sobre, C rascunho, D projeto, E editar post, "
        "F comentário, G formação, H competências do projeto, S cidade, T experiências, "
        "U certificados, V Mecatrônica, W publicar card e comentário, X precisão de anos). Sem valor, só abre o painel.",
    )
    parser.add_argument("--batch", action="store_true", help="executa e encerra; exige sessão já autenticada")
    parser.add_argument("--headless", action="store_true", help="executa sem janela")
    parser.add_argument("--render-card", action="store_true", help="gera somente o card HTML em 1200x627")
    parser.add_argument("--no-save", action="store_true", help="preenche, mas não clica em Salvar")
    parser.add_argument("--panel-only", action="store_true", help="apenas abre o painel flutuante")
    parser.add_argument("--print-texts", action="store_true", help="mostra os tamanhos e sai")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada."""
    args = parse_args(argv)
    texts = load_texts()
    if args.print_texts:
        sys.stdout.write(
            f"headline={len(texts.headline)} about={len(texts.about)} "
            f"projeto={len(texts.project_description)} post1={len(texts.post1)} caracteres\n"
        )
        return 0
    selected = [key.strip().upper() for key in args.only.split(",") if key.strip()]
    unknown = [key for key in selected if key not in ACTIONS]
    if unknown:
        sys.stderr.write(f"Ações inválidas: {', '.join(unknown)} (use {', '.join(sorted(ACTIONS))})\n")
        return 2

    with sync_playwright() as playwright:
        if args.render_card:
            browser = playwright.chromium.launch(headless=True)
            card_context = browser.new_context(device_scale_factor=1)
            render_post_card(card_context)
            browser.close()
            return 0
        context: BrowserContext = playwright.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=args.headless,
            viewport={"width": 1440, "height": 1000} if args.headless else None,
            args=["--start-maximized"],
        )
        if selected and not args.panel_only:
            context.add_init_script("window.__LI_AUTOMATING = true;")
        if not args.batch:
            context.add_init_script(build_panel_script(texts))
            context.grant_permissions(
                ["clipboard-read", "clipboard-write"], origin="https://www.linkedin.com"
            )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(PROFILE_URL, wait_until="domcontentloaded")
        log(f"Aberto: {PROFILE_URL}")

        logged_page = (page if is_logged_in(page) else None) if args.batch else wait_for_login(context)
        success = True
        if logged_page is not None:
            log("Login detectado; perfil carregado.")
            if not args.panel_only:
                success = run_actions(logged_page, texts, selected, save=not args.no_save)
                logged_page.evaluate("window.__LI_AUTOMATING = false")
            if not args.batch:
                log("Painel flutuante disponível à direita. Feche a janela quando terminar.")
        else:
            log("Sem sessão ativa; encerrando.")
            return 1
        if args.batch:
            context.close()
            return 0 if success else 1
        try:
            context.wait_for_event("close", timeout=0)
        except PlaywrightError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
