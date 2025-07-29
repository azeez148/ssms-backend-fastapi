import pandas as pd

# Create template dataframe with the provided data
data = {
    'name': [
        'Italy Retro 2006',
        'Brazil Home 2024-25',
        'France Away 2024-25',
        'Germany Home 2024-25',
        'Spain Home 2024-25',
        'England Retro 1998',
        'Netherlands Home 2024-25',
        'Portugal Home 2024-25',
        'Argentina Retro 1986'
    ],
    'description': [
        'Italy Retro 2006',
        'Brazil Home 2024-25',
        'France Away 2024-25',
        'Germany Home 2024-25',
        'Spain Home 2024-25',
        'England Retro 1998',
        'Netherlands Home 2024-25',
        'Portugal Home 2024-25',
        'Argentina Retro 1986'
    ],
    'category_id': [1] * 9,  # Jersey category
    'unit_price': [190, 150, 150, 150, 150, 190, 150, 150, 190],
    'selling_price': [300, 250, 250, 250, 250, 300, 250, 250, 300],
    'is_active': [True] * 9,
    'can_listed': [True] * 9,
    'size_S': [1] * 9,
    'size_M': [1] * 9,
    'size_L': [1] * 9,
    'size_XL': [1] * 9,
    'size_XXL': [1] * 9,
    'size_XXXL': [0, 0, 1, 0, 0, 0, 1, 0, 0]  # Only France Away and Netherlands have XXXL
}

df = pd.DataFrame(data)

# Save to Excel
df.to_excel('jersey_products_template.xlsx', index=False)
print("Template created successfully!")
