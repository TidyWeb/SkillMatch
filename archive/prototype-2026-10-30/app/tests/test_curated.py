from skillmatch.sources.curated import COLUMNS, CuratedAdapter, validate

HEADER = ",".join(COLUMNS)


def write(tmp_path, *rows):
    p = tmp_path / "adverts.csv"
    p.write_text("\n".join([HEADER, *rows]) + "\n")
    return p


def test_example_file_is_valid_and_loads(tmp_path):
    from skillmatch import config

    example = config.DATA_DIR / "curated" / "adverts.example.csv"
    assert validate(example) == []
    vacs = CuratedAdapter(example).fetch()
    assert len(vacs) == 1 and vacs[0].source_tier == "B"
    assert "Essential" in vacs[0].description_html


def test_validation_catches_problems(tmp_path):
    p = write(
        tmp_path,
        'Site,ftp://x,21/10/2026,Data Officer,Acme,Walsall,sometimes,9,,,"Excel; E: SQL"',
    )
    problems = "\n".join(validate(p))
    assert "advert_url must start with http" in problems
    assert "checked_date" in problems
    assert "arrangement must be" in problems
    assert "office_days must be" in problems
    assert "must start with E: or D:" in problems


def test_wrong_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("title,url\nx,y\n")
    assert "columns must be exactly" in validate(p)[0]
