COMMON_HOVER_CONFIG = {
    'hoverlabel': {
        'font': {'color': 'white', 'family': 'Arial'},
        'bordercolor': 'white'
    }
}

CUSTOM_COLORS = {
    "Assault": "#C10B0B",          # Strong red - suggests danger/violence
    "Battery": "#8E44AD",          # Deep purple - distinct from assault
    "Burglary": "#2980B9",         # Professional blue - property crime
    "Criminal damage": "#73C836",   # Burnt orange - damage/destruction
    "Deceptive practice": "#34495E", # Dark slate - serious/deceptive
    "Motor vehicle theft": "#09A283", # Teal - transportation related
    "Narcotics": "#F39C12",        # Amber/gold - drug-related
    "Other offense": "#B6C0C1",    # Neutral gray - miscellaneous
    "Robbery": "#822C22",          # Dark red - violent property crime
    "Theft": "#160B6E"             # Forest green - property crime
}

def format_proper_name(name):
    if not isinstance(name, str):
        return name
    return name.lower().capitalize()

def preprocess_labels(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(format_proper_name)
    return df
