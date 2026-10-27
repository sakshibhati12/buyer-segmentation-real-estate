# Buyer Segmentation & Investment Profiling - Real Estate

Machine-learning buyer segmentation (K-Means, 4 segments) with an interactive Streamlit dashboard.

**Live dashboard:** (https://buyer-segmentation-real-estate-hfdhctty53qikfesodwv6f.streamlit.app/)

## Files
- `01_exploration.ipynb`: cleaning, feature engineering, clustering, statistical tests
- `app.py`: Streamlit dashboard
- `buyers_clustered.csv`: final data with segment labels
- `clients.csv`, `properties.csv`: source data

## Method
Buyers were clustered on purchase behaviour (units bought, average unit price, office share).
Demographics were used to describe the clusters, not to form them.