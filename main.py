import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    df = pd.read_csv("./Chocolate Sales.csv")
    #convert date col to datetime datatype
    df.Date = pd.to_datetime(df.Date,format="%d-%b-%y")
    # extract month
    #df['Month'] = df.Date.dt.month#
    df["Month"] = df["Date"].dt.strftime("%B")
    #convert the Amount column to float datatype
    df.Amount= df.Amount.str.replace("$","").str.replace(",","").str.strip().astype("float")
    df["Price/Box"] = round(df.Amount / df["Boxes Shipped"], 2)
    return df

df = load_data()

#App title
st.title("Chocolates Sales App")

# create filters
filters = {
    "Sales Person": df["Sales Person"].unique(),
    "Country": df["Country"].unique(),
    "Product": df["Product"].unique(),
}

# store user selection
selected_filters = {}

#generate multi-select widgets dynamically
for key, options in filters.items():
    selected_filters[key]=st.sidebar.multiselect(key,options)

# lets have the full data
filtered_df = df.copy()
for key, selected_values in selected_filters.items():
    if selected_values:
        filtered_df=filtered_df[filtered_df[key].isin(selected_values)]
        

#display the data                 
st.dataframe(filtered_df.head())

#calculations
no_of_transations = len(filtered_df)
total_revenue = filtered_df["Amount"].sum()
total_boxes = filtered_df["Boxes Shipped"].sum()
no_of_products = filtered_df["Product"].nunique()

# streamlit column component
col1, col2, col3, col4, = st.columns(4)
with col1:
    st.metric("Transactions", no_of_transations)

with col2:
    st.metric("Total Revenue", total_revenue)

with col3:
    st.metric("Total Boxes", total_boxes)

with col4:
    st.metric("Products", no_of_products)


#charts
st.subheader("Products with Largest Revenue")
top_products = filtered_df.groupby("Product")["Amount"].sum().nlargest(5).reset_index()

st.write(top_products)

# altair plotting libaray

st.subheader("Top 5 Product by Revenue")

# configure the bar chart
chart = alt.Chart(top_products).mark_bar().encode(
    x=alt.X('Amount:Q', title="Revenue ($)"),
    y=alt.Y("Product:N"),
    color = alt.Color("Product", legend = None)
).properties(height = 300)

# display the chart
st.altair_chart(chart, use_container_width= True)


# pie chart
# Count of each country
country_counts = df["Country"].value_counts()

# Define colors and explode settings
colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854']
explode = [0.05] * len(country_counts)

# Function to show both count and %
def format_autopct(pct, all_vals):
    count = int(round(pct/100 * sum(all_vals)))
    return f"{count} ({pct:.1f}%)"

# Streamlit layout
#st.set_page_config(page_title="Country Pie Chart", layout="centered")

st.title("🌍 Country Distribution Pie Chart")
st.write("This chart shows the count and percentage of countries in the dataset.")

# Plotting the pie chart using matplotlib
fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    country_counts,
    labels=country_counts.index,
    autopct=lambda pct: format_autopct(pct, country_counts),
    startangle=140,
    colors=colors[:len(country_counts)],
    explode=explode[:len(country_counts)],
    shadow=True,
    textprops={'fontsize': 12, 'fontweight': 'bold'}
)

for text in texts:
    text.set_fontsize(13)
    text.set_fontweight("bold")

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(12)
    autotext.set_fontweight("bold")

ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

# Display chart in Streamlit
st.pyplot(fig)


# pie chart Total Amount by Country
# Group and sum
country_amount = filtered_df.groupby("Country")["Amount"].sum().sort_values(ascending=False)

# Define a custom format function to show both value and percentage
def autopct_format(pct, all_vals):
    absolute = int(round(pct / 100. * sum(all_vals)))
    return f"${absolute:,}\n({pct:.1f}%)"


st.title("💵 Distribution of Sales by Country")
st.write("This pie chart displays the total amount for each country along with their percentage share.")

# Plot pie chart
fig, ax = plt.subplots(figsize=(10, 8))
colors = plt.cm.Pastel2.colors
explode = [0.05] * len(country_amount)

wedges, texts, autotexts = ax.pie(
    country_amount,
    labels=country_amount.index,
    autopct=lambda pct: autopct_format(pct, country_amount),
    startangle=140,
    colors=colors,
    explode=explode,
    shadow=True,
    textprops={'fontsize': 12, 'fontweight': 'bold'}
)

for text in texts:
    text.set_fontsize(13)
    text.set_fontweight("bold")

for autotext in autotexts:
    autotext.set_fontsize(11)
    autotext.set_color('black')
    autotext.set_fontweight("semibold")

ax.set_title("💵 Total Amount by Country", fontsize=18, fontweight="bold")
ax.axis("equal")
plt.tight_layout()

# Display in Streamlit
st.pyplot(fig)



#revenue per sales person plot
# Group and sum
sales_data = filtered_df.groupby("Sales Person")["Amount"].sum().sort_values(ascending=False)

# Streamlit app
#st.set_page_config(page_title="Sales by Person", layout="centered")
st.title("💼 Distribution of Total Sales by Sales Person")

# Plot bar chart
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=sales_data.values, y=sales_data.index, palette="viridis", ax=ax)

ax.set_title("💼 Total Sales Distribution", fontsize=16, fontweight="bold")
ax.set_xlabel("Total Amount ($)", fontsize=14)
ax.set_ylabel("Sales Person", fontsize=14)

# Add labels to bars
for index, value in enumerate(sales_data.values):
    ax.text(value, index, f"${value:,.0f}", va='center', fontsize=12, fontweight="bold")

st.pyplot(fig)



## monthly line chart
filtered_df['Month'] = pd.to_datetime(filtered_df['Date']).dt.month_name()  # Assuming the "Date" column exists
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',] 
               #'September', 'October', 'November', 'December']
filtered_df['Month'] = pd.Categorical(filtered_df['Month'], categories=month_order, ordered=True)

monthly_sum = filtered_df.groupby("Month")['Amount'].sum()

st.title('Sales Trend')

# Set a custom style using seaborn
sns.set(style="darkgrid")

# Plot with additional styles
plt.figure(figsize=(10, 6))
sns.lineplot(x=monthly_sum.index, y=monthly_sum.values, 
             marker='o',         # Adding markers to the line
             color='purple',     # Line color
             linewidth=2,        # Line width
             markersize=8,       # Marker size
             markerfacecolor='red',  # Marker face color
             markeredgewidth=2)  # Marker edge width

# Title and labels with custom font sizes
plt.title('Monthly Sales Trend', fontsize=16, fontweight='bold', color='navy')
plt.xlabel('Month', fontsize=14, fontweight='bold', color='darkred')
plt.ylabel('Amount', fontsize=14, fontweight='bold', color='darkred')

# Custom x-tick rotation and style
plt.xticks(rotation=45, fontsize=12, ha='right', color='black')

# Custom y-tick style
plt.yticks(fontsize=12, color='black')

# Add a grid with a specific line style
plt.grid(True, linestyle='--', linewidth=0.7, color='gray')

# Display plot in Streamlit
st.pyplot(plt)
