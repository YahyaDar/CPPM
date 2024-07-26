import streamlit as st
import pandas as pd
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Load data from CSV file
df = pd.read_csv('scrape_output/data1_clean.csv')

# Define feature types
categorical_features = ['brand', 'itemCondition', 'fuelType', 'vehicleTransmission', 'location', 'model']
numeric_features = ['modelDate', 'vehicleEngine', 'mileageFromOdometer']

# Set up preprocessing
categorical_transformer = OneHotEncoder(handle_unknown='ignore')
numeric_transformer = StandardScaler()

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', categorical_transformer, categorical_features),
        ('num', numeric_transformer, numeric_features)
    ])

pipeline = Pipeline(steps=[('preprocessor', preprocessor)])

# Separate features and target
X = pipeline.fit_transform(df.drop(columns=['price']))
y = df['price']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model
model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Compute SHAP values
explainer = shap.Explainer(model)
shap_values = explainer(X_test)

# Convert X_test to dense format
X_test_dense = X_test.toarray() if hasattr(X_test, 'toarray') else X_test

# Streamlit App
st.title("XGBoost Model SHAP Values Visualization")

# Display SHAP Summary Plot
st.subheader("SHAP Summary Plot")
fig, ax = plt.subplots(figsize=(10, 6))
shap.summary_plot(shap_values, X_test_dense, feature_names=pipeline.named_steps['preprocessor'].get_feature_names_out(), show=False)
st.pyplot(fig)

# Display SHAP Dependence Plot for a selected feature
st.subheader("SHAP Dependence Plot")
feature = st.selectbox("Select feature for dependence plot", options=pipeline.named_steps['preprocessor'].get_feature_names_out())
fig, ax1 = plt.subplots(figsize=(10, 6))
shap.dependence_plot(feature, shap_values.values, X_test_dense, feature_names=pipeline.named_steps['preprocessor'].get_feature_names_out(), ax=ax1)
st.pyplot(fig)
