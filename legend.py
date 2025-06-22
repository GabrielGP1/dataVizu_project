"""
utils.py

Helper constants and functions used across multiple charts and visualizations.
Includes:
- Common hover configuration for consistent styling
- Custom color mapping for crime types
- Label formatting utilities
- Number formatting with rounding

Author: [Your Name]
Date: June 2025
"""

# ===== Constants =====

# Common hover config used across Plotly figures
COMMON_HOVER_CONFIG = {
    'hoverlabel': {
        'font': {'color': 'white', 'family': 'Arial'},
        'bordercolor': 'white'
    }
}

# Color mapping for crime types (used in maps, Sankey, etc.)
CUSTOM_COLORS = {
    "Assault": "#C10B0B",
    "Battery": "#8E44AD",
    "Burglary": "#2980B9",
    "Criminal damage": "#73C836",
    "Deceptive practice": "#34495E",
    "Motor vehicle theft": "#09A283",
    "Narcotics": "#F39C12",
    "Other offense": "#B6C0C1",
    "Robbery": "#822C22",
    "Theft": "#160B6E"
}


# ===== Helper Functions =====

def format_proper_name(name: str) -> str:
    """
    Converts a string to lowercase and then capitalizes the first letter.
    Useful for standardizing crime names.

    Args:
        name (str): The string to format.

    Returns:
        str: Formatted string with capitalized first letter.
    """
    if not isinstance(name, str):
        return name
    return name.lower().capitalize()


def preprocess_labels(df, columns):
    """
    Apply proper name formatting to specific columns in a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        columns (list of str): Column names to format.

    Returns:
        pd.DataFrame: Modified DataFrame with formatted labels.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(format_proper_name)
    return df


def format_number(num: float) -> float:
    """
    Format a number into thousands with one decimal (e.g. 1400 → 1.4).
    Useful for tick labels or summaries.

    Args:
        num (float): The number to format.

    Returns:
        float: Rounded value in thousands if applicable.
    """
    if num >= 1000:
        return float(f"{num / 1000:.1f}")
    return num
