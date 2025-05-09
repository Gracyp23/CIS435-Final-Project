# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14e_KUmdJGeS0ZNtCM2UHmsYUJOhr2D-k
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# Load datasets
tbl_user = pd.read_csv('/content/TblUser.txt', header=None, names=['RawData'])
tbl_user_matrix = pd.read_csv('/content/TbluserMatrix.txt', header=None, names=['RawData'])
tbl_user_category = pd.read_csv('/content/tblUserwebCategoryMatrix.txt', header=None, names=['RawData'])

# Extract and clean user data
tbl_user['UserID'] = tbl_user['RawData'].str.extract(r'>(\d+)<')
tbl_user = tbl_user.drop(columns=['RawData']).dropna().astype(int)

# Extract and clean friendship data
tbl_user_matrix['UserID'] = tbl_user_matrix['RawData'].str.extract(r'<userId>(\d+)</userId>')
tbl_user_matrix['FriendID'] = tbl_user_matrix['RawData'].str.extract(r'<friendId>(\d+)</friendId>')
tbl_user_matrix = tbl_user_matrix.drop(columns=['RawData']).dropna().astype(int)

# Extract and clean category data
tbl_user_category['UserID'] = tbl_user_category['RawData'].str.extract(r'<userId>(\d+)</userId>')
tbl_user_category['Category'] = tbl_user_category['RawData'].str.extract(r'<webCategory>(.*?)</webCategory>')
tbl_user_category = tbl_user_category.drop(columns=['RawData']).dropna()

# Remove any remaining NaN values
tbl_user_matrix = tbl_user_matrix.dropna(how='any')
tbl_user_category = tbl_user_category.dropna(how='any')

# Display cleaned data
print("✅ Cleaned User Table:\n", tbl_user.head())
print()
print("✅ Cleaned Friendship Table:\n", tbl_user_matrix.head())
print()
print("✅ Cleaned Category Table:\n", tbl_user_category.head())
print()

# Create the graph
G = nx.Graph()
edges = list(zip(tbl_user_matrix['UserID'], tbl_user_matrix['FriendID']))
G.add_edges_from(edges)
G.remove_edges_from(nx.selfloop_edges(G))
print(f"✅ Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
print()

# Compute core numbers
core_numbers = nx.core_number(G)
core_df = pd.DataFrame(core_numbers.items(), columns=['UserID', 'CoreNumber'])
print("✅ Top Core Users:\n", core_df.sort_values(by='CoreNumber', ascending=False).head())
print()

# Merge core numbers with user categories
core_df['UserID'] = core_df['UserID'].astype(int)
tbl_user_category['UserID'] = tbl_user_category['UserID'].astype(int)
core_category_df = pd.merge(core_df, tbl_user_category, on='UserID', how='left')
core_category_df = core_category_df.dropna()
print("✅ Core-Category Merged Data:\n", core_category_df.head())
print()

# Compute category distribution within core groups
core_category_distribution = core_category_df.groupby(['CoreNumber', 'Category']).size().reset_index(name='Count')
core_category_distribution = core_category_distribution.sort_values(by=['CoreNumber', 'Count'], ascending=[False, False])
print("✅ Core-Category Distribution:\n", core_category_distribution.head())
print()

# Find the dominant category per core group
dominant_category_per_core = core_category_distribution.loc[
    core_category_distribution.groupby('CoreNumber')['Count'].idxmax()
]
print("✅ Dominant Category per Core:\n", dominant_category_per_core[['CoreNumber', 'Category', 'Count']].head(10))
print()

# Plot the distribution of top core-category combinations
plt.figure(figsize=(12, 6))
sns.barplot(x='CoreNumber', y='Count', hue='Category', data=core_category_distribution.head(10))
plt.title('Top Core-Category Combinations')
plt.xlabel('Core Number')
plt.ylabel('Count')
plt.legend(title='Category')
plt.show()

# Save results
core_df.to_csv('core_results.csv', index=False)
core_category_distribution.to_csv('core_category_distribution.csv', index=False)
print("✅ Core analysis results saved successfully.")