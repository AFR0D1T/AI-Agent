"""Чтение папки документов в RawDocument[] — чистый код, без сети.

PDF-извлечение (pymupdf) не тестируем отдельно — библиотека сторонняя и
хорошо протестирована сама по себе; здесь важна логика обхода папки:
поддерживаемые расширения, пропуск прочих файлов, doc_id по содержимому.
"""

from pathlib import Path

from bank_ai_agent.ingestion.document_source import load_documents


def test_load_documents_reads_text_files_and_skips_unknown(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("hello world", encoding="utf-8")
    (tmp_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "Thumbs.db").write_bytes(b"\x00\x01")  # не документ, должен быть пропущен

    documents = load_documents(tmp_path)

    assert {Path(d.source_path).name for d in documents} == {"note.txt", "data.csv"}
    txt_doc = next(d for d in documents if Path(d.source_path).name == "note.txt")
    assert txt_doc.text == "hello world"
    assert len(txt_doc.doc_id) == 16


def test_load_documents_doc_id_depends_on_content(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("same content", encoding="utf-8")
    (tmp_path / "b.txt").write_text("same content", encoding="utf-8")

    documents = load_documents(tmp_path)

    assert documents[0].doc_id == documents[1].doc_id
