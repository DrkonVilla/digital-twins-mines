import streamlit as st
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import plotly.express as px
from utils.i18n import init_i18n

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the main page.")
    st.stop()

init_i18n()
t = st.session_state.t

st.title(t["nav_training"])

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("../data/raw/synthetic_interactions.csv")
        # Ensure target is categorical/numeric suitable for classification
        df['target'] = df['risk_level'].map({'BAJO': 0, 'MEDIO': 1, 'ALTO': 2})
        # Features
        X = df[['distance', 'relative_velocity', 'angle', 'visibility', 'noise_level']]
        y = df['target']
        return X, y, df
    except Exception as e:
        return None, None, None

X, y, df = load_data()

if X is not None:
    st.sidebar.header("Hyperparameters")
    max_depth = st.sidebar.slider("Max Depth", 3, 10, 6)
    n_estimators = st.sidebar.slider("Estimators", 50, 300, 100)
    learning_rate = st.sidebar.select_slider("Learning Rate", options=[0.01, 0.05, 0.1, 0.2, 0.3], value=0.1)
    
    if st.button(t["btn_train"]):
        with st.spinner("Training model with K-Fold Cross Validation..."):
            model = xgb.XGBClassifier(
                max_depth=max_depth,
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                eval_metric="mlogloss"
            )
            
            # K-Fold CV
            kfold = KFold(n_splits=5, shuffle=True, random_state=42)
            results = cross_val_score(model, X, y, cv=kfold)
            
            st.success(f"Cross Validation Accuracy: {results.mean()*100:.2f}% (+/- {results.std()*100:.2f}%)")
            
            # Train on full for feature importance
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Feature Importance
            importance = model.feature_importances_
            feat_imp_df = pd.DataFrame({'Feature': X.columns, 'Importance': importance}).sort_values(by='Importance', ascending=False)
            fig_imp = px.bar(feat_imp_df, x='Importance', y='Feature', orientation='h', title="Feature Importance (XGBoost)")
            st.plotly_chart(fig_imp, use_container_width=True)
            
            # Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            fig_cm = px.imshow(cm, text_auto=True, title="Confusion Matrix", x=['BAJO', 'MEDIO', 'ALTO'], y=['BAJO', 'MEDIO', 'ALTO'])
            st.plotly_chart(fig_cm, use_container_width=True)
else:
    st.warning("Data not available.")
