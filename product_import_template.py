import pandas as pd

# Create template dataframe
template_data = {
    'name': ['Argentina Home 2022-23', 'Example Product 2'],
    'description': ['Argentina Home 2022-23', 'Example Description 2'],
    'unit_price': [150, 200],
    'selling_price': [250, 300],
    'category_id': [1, 1],
    'is_active': [True, True],
    'can_listed': [True, True],
    'size_S': [1, 0],
    'size_M': [2, 0],
    'size_L': [2, 0],
    'size_XL': [2, 0],
    'size_XXL': [1, 0]
}

df = pd.DataFrame(template_data)

# Save to Excel
df.to_excel('product_template.xlsx', index=False)
print("Template created successfully!")
