import pandas as pd


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the renaming logic from dashboard_inventario_final."""
    col_map = {}
    for col in df.columns:
        name = str(col).lower()
        if "parte" in name or "j19" in name:
            col_map[col] = "Numero de Parte"
        elif "descripcion" in name or "tinte" in name:
            col_map[col] = "Descripcion"
        elif "unidad" in name or "322" in name:
            col_map[col] = "Unidades"
        elif "pintura" in name or "material" in name:
            col_map[col] = "Categoria"
        elif "clasificacion" in name:
            col_map[col] = "Clasificacion"

    df = df.rename(columns=col_map)

    if "Clasificación" in df.columns:
        df = df.drop(columns=["Clasificación"])

    return df


def test_renaming_and_drop():
    data = {
        "parte_num": ["A1", "A2"],
        "descripcion": ["item1", "item2"],
        "unidad_total": [10, 20],
        "tipo_material": ["mat1", "mat2"],
        "Clasificación": ["obsoleto", "nuevo"],
    }
    df = pd.DataFrame(data)

    result = process_dataframe(df)

    assert "Numero de Parte" in result.columns
    assert "Descripcion" in result.columns
    assert "Unidades" in result.columns
    assert "Categoria" in result.columns
    assert "Clasificación" not in result.columns
