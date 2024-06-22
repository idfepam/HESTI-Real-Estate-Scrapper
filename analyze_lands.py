import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import re
from connector import collection

# Retrieve data from MongoDB
data = list(collection.find())
df = pd.DataFrame(data)


# Ensure price is numeric
def clean_price(price_str):
    price_str = price_str.replace(" ", "")  # Remove spaces
    price_str = price_str.replace("$", "")  # Remove dollar sign
    return float(price_str)


df["price_numeric"] = df["price"].apply(clean_price)


def extract_total_size(size_str):
    match = re.match(r"(\d+)", size_str)
    if match:
        return float(match.group(1))
    else:
        return None


# Apply the function to extract the total size
df["size_numeric"] = df["size"].apply(extract_total_size)

# Calculate price per square meter
df = df.dropna(subset=["price_numeric", "size_numeric"])
df["price_per_sqm"] = df["price_numeric"] / df["size_numeric"]

# Define thresholds for categorization
cheap_threshold = df["price_per_sqm"].quantile(0.33)
expensive_threshold = df["price_per_sqm"].quantile(0.67)


def categorize(price_per_sqm):
    if price_per_sqm <= cheap_threshold:
        return "Cheap"
    elif price_per_sqm <= expensive_threshold:
        return "Moderate"
    else:
        return "Expensive"


# Categorize each document
df["category"] = df["price_per_sqm"].apply(categorize)

# Update MongoDB with new category field
for index, row in df.iterrows():
    collection.update_one({"_id": row["_id"]}, {"$set": {"category": row["category"]}})

print("Migration completed successfully.")

# Calculate average price per square meter for each location
location_avg_price = df.groupby("location")["price_per_sqm"].mean().reset_index()
location_avg_price = location_avg_price.sort_values(by="price_per_sqm", ascending=False)

# Identify Top 5 Most Expensive Locations
top_5_locations = location_avg_price.head(5)
print(top_5_locations)

# Generate Bar Chart
plt.figure(figsize=(10, 6))
plt.bar(top_5_locations["location"], top_5_locations["price_per_sqm"], color="blue")
plt.xlabel("Location")
plt.ylabel("Average Price per Square Meter")
plt.title("Top 5 Most Expensive Locations")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("top_locations.png")
plt.show()
