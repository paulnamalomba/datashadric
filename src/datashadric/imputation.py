# -*- coding: utf-8 -*-
"""
Imputation Functions Module
Comprehensive collection of multiple imputation methods for handling missing data in pandas DataFrames.

Implements three families of imputation strategies:
    1. MICE (Multiple Imputation by Chained Equations) with three imputation kernels:
       - Predictive Mean Matching (PMM)
       - Bayesian Linear Regression (Norm)
       - Logistic Regression (for binary/categorical columns)
    2. Random Forest Imputation
    3. K-Nearest Neighbours (KNN) Imputation

Each function follows the datashadric convention: accepts a pandas DataFrame, operates on
specified columns, prints progress to the console, and returns the imputed DataFrame.
"""

# standard library imports
import warnings
from typing import Optional, Literal

# third-party data science imports
import pandas as pd
import numpy as np
from scipy import stats

# scikit-learn imports for imputation back-ends
from sklearn.experimental import enable_iterative_imputer  # noqa: F401 — required to unlock IterativeImputer
from sklearn.impute import IterativeImputer, KNNImputer
from sklearn.linear_model import BayesianRidge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


# ---------------------------------------------------------------------------
# 1. MICE — Multiple Imputation by Chained Equations
# ---------------------------------------------------------------------------

def df_mice_impute_pmm(df_name, col_list: Optional[list] = None, max_iter: int = 10, n_nearest: int = 5, random_state: int = 42):
    """impute missing values using MICE with Predictive Mean Matching (PMM)

    PMM works by fitting a Bayesian ridge regression for each incomplete column,
    predicting values for the missing entries, then replacing each prediction with
    the observed value whose predicted value is closest (from a pool of the
    n_nearest candidates).  This preserves the marginal distribution of the
    observed data better than plain regression imputation and guarantees that
    imputed values are always drawn from the set of real observed values.

    Parameters
    ----------
    df_name : pandas.DataFrame
        Input DataFrame with missing values (NaN).
    col_list : list of str, optional
        Columns to include in the imputation model.  If None, all numeric
        columns are used.
    max_iter : int, default 10
        Number of MICE iteration rounds (chained-equation cycles).
    n_nearest : int, default 5
        Number of nearest observed candidates to draw from during the
        predictive-mean-matching donor step.
    random_state : int, default 42
        Seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        DataFrame with missing values imputed via PMM-MICE.
    """
    # usage: df_mice_impute_pmm(df, ['col1', 'col2', 'col3'], max_iter=10, n_nearest=5)
    # input: df_name - pandas DataFrame with NaN values, col_list - list of numeric column names to impute
    # output: imputed DataFrame

    df = df_name.copy()
    cols = col_list if col_list is not None else df.select_dtypes(include=[np.number]).columns.tolist()

    na_before = df[cols].isna().sum().sum()
    print(f"MICE-PMM: {na_before} missing values across {len(cols)} columns")

    if na_before == 0:
        print("MICE-PMM: no missing values found — returning original DataFrame")
        return df

    rng = np.random.RandomState(random_state)

    # Initialise missing entries with column medians
    work = df[cols].copy()
    for col in cols:
        median_val = work[col].median()
        work[col] = work[col].fillna(median_val)

    observed_masks = {col: df[col].notna() for col in cols}
    missing_masks = {col: df[col].isna() for col in cols}

    for iteration in range(max_iter):
        for col in cols:
            if not missing_masks[col].any():
                continue

            predictor_cols = [c for c in cols if c != col]
            if not predictor_cols:
                continue

            obs_mask = observed_masks[col]
            mis_mask = missing_masks[col]

            X_obs = work.loc[obs_mask, predictor_cols].values
            y_obs = df.loc[obs_mask, col].values
            X_mis = work.loc[mis_mask, predictor_cols].values

            model = BayesianRidge()
            model.fit(X_obs, y_obs)

            y_hat_obs = model.predict(X_obs)
            y_hat_mis = model.predict(X_mis)

            # PMM donor matching: for each missing prediction, find the
            # n_nearest observed predictions and sample one donor value
            imputed_values = np.empty(len(y_hat_mis))  # type: ignore[arg-type]
            for i, pred in enumerate(y_hat_mis):  # type: ignore[arg-type]
                distances = np.abs(y_hat_obs - pred)
                k = min(n_nearest, len(distances))
                donor_indices = np.argpartition(distances, k)[:k]
                chosen = rng.choice(donor_indices)
                imputed_values[i] = y_obs[chosen]

            work.loc[mis_mask, col] = imputed_values

    df[cols] = work[cols]
    na_after = df[cols].isna().sum().sum()
    print(f"MICE-PMM: imputation complete — {na_before - na_after} values imputed over {max_iter} iterations")

    return df


def df_mice_impute_norm(df_name, col_list: Optional[list] = None, max_iter: int = 10, random_state: int = 42):
    """impute missing values using MICE with Bayesian Linear Regression (norm)

    Each incomplete numeric column is modelled with a Bayesian ridge regression
    on the remaining columns.  Missing values are replaced by the model's
    posterior predictive draw (point estimate + noise drawn from the residual
    variance), which is equivalent to the ``norm`` method in the R mice package.

    This method is appropriate when data are approximately multivariate normal.
    It tends to produce smoother imputed distributions than PMM but may generate
    values outside the observed range.

    Parameters
    ----------
    df_name : pandas.DataFrame
        Input DataFrame with missing values (NaN).
    col_list : list of str, optional
        Columns to include.  If None, all numeric columns are used.
    max_iter : int, default 10
        Number of MICE iteration rounds.
    random_state : int, default 42
        Seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        DataFrame with missing values imputed via norm-MICE.
    """
    # usage: df_mice_impute_norm(df, ['col1', 'col2'], max_iter=10)
    # input: df_name - pandas DataFrame with NaN values, col_list - list of numeric column names to impute
    # output: imputed DataFrame

    df = df_name.copy()
    cols = col_list if col_list is not None else df.select_dtypes(include=[np.number]).columns.tolist()

    na_before = df[cols].isna().sum().sum()
    print(f"MICE-Norm: {na_before} missing values across {len(cols)} columns")

    if na_before == 0:
        print("MICE-Norm: no missing values found — returning original DataFrame")
        return df

    # scikit-learn's IterativeImputer with BayesianRidge is equivalent to MICE-norm
    imputer = IterativeImputer(
        estimator=BayesianRidge(),
        max_iter=max_iter,
        random_state=random_state,
        sample_posterior=True,
    )

    imputed_array = imputer.fit_transform(df[cols])
    df[cols] = pd.DataFrame(imputed_array, columns=cols, index=df.index)

    na_after = df[cols].isna().sum().sum()
    print(f"MICE-Norm: imputation complete — {na_before - na_after} values imputed over {max_iter} iterations")

    return df


def df_mice_impute_logistic(df_name, col_target: str, col_predictors: Optional[list] = None, max_iter: int = 10, random_state: int = 42):
    """impute missing values in a binary/categorical column using MICE with Logistic Regression

    The target column (binary or low-cardinality categorical) is modelled with
    logistic regression on a set of predictor columns.  This is the standard
    MICE approach for categorical outcomes (equivalent to the ``logreg`` method
    in the R mice package).  Continuous predictor columns with missing values
    are first imputed with MICE-norm before the logistic model is fitted.

    Parameters
    ----------
    df_name : pandas.DataFrame
        Input DataFrame.
    col_target : str
        Name of the binary or categorical column to impute.
    col_predictors : list of str, optional
        Predictor columns.  If None, all other numeric columns are used.
    max_iter : int, default 10
        Number of MICE iteration rounds.
    random_state : int, default 42
        Seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the target column's missing values imputed via
        logistic-regression MICE.
    """
    # usage: df_mice_impute_logistic(df, 'binary_col', ['pred1', 'pred2'], max_iter=10)
    # input: df_name - pandas DataFrame, col_target - binary/categorical column with NaN, col_predictors - list of predictor columns
    # output: imputed DataFrame

    df = df_name.copy()

    na_before = df[col_target].isna().sum()
    print(f"MICE-Logistic: {na_before} missing values in '{col_target}'")

    if na_before == 0:
        print("MICE-Logistic: no missing values found — returning original DataFrame")
        return df

    # Encode target to numeric labels for modelling
    target_is_numeric = pd.api.types.is_numeric_dtype(df[col_target])
    if not target_is_numeric:
        label_map = {v: i for i, v in enumerate(df[col_target].dropna().unique())}
        reverse_map = {i: v for v, i in label_map.items()}
        df[col_target] = df[col_target].map(label_map)
    else:
        reverse_map = None

    # Determine predictor columns
    if col_predictors is None:
        col_predictors = [c for c in df.select_dtypes(include=[np.number]).columns if c != col_target]

    # Pre-impute predictor columns that have missing values using MICE-norm
    predictor_na = df[col_predictors].isna().sum().sum()
    if predictor_na > 0:
        print(f"MICE-Logistic: pre-imputing {predictor_na} missing predictor values with MICE-norm")
        df = df_mice_impute_norm(df, col_list=col_predictors, max_iter=max_iter, random_state=random_state)

    obs_mask = df[col_target].notna()
    mis_mask = df[col_target].isna()

    X_obs = df.loc[obs_mask, col_predictors].values
    y_obs = df.loc[obs_mask, col_target].values.astype(int)
    X_mis = df.loc[mis_mask, col_predictors].values

    rng = np.random.RandomState(random_state)

    for iteration in range(max_iter):
        model = LogisticRegression(max_iter=1000, random_state=random_state, solver='lbfgs')
        model.fit(X_obs, y_obs)

        # Probabilistic imputation: sample from predicted class probabilities
        proba = model.predict_proba(X_mis)
        imputed = np.array([rng.choice(model.classes_, p=p) for p in proba])

        df.loc[mis_mask, col_target] = imputed

        # Re-fit with newly imputed data for the next cycle
        X_obs = df[col_predictors].values
        y_obs = df[col_target].values.astype(int)

    # Restore original labels if the column was categorical
    if reverse_map is not None:
        df[col_target] = df[col_target].map(reverse_map)

    na_after = df[col_target].isna().sum()
    print(f"MICE-Logistic: imputation complete — {na_before - na_after} values imputed over {max_iter} iterations")

    return df


# ---------------------------------------------------------------------------
# 2. Random Forest Imputation
# ---------------------------------------------------------------------------

def df_impute_random_forest(df_name, col_list: Optional[list] = None, n_estimators: int = 100, max_iter: int = 10, random_state: int = 42):
    """impute missing values using iterative Random Forest imputation

    Each incomplete column is predicted by a Random Forest model fitted on the
    remaining columns.  Numeric columns use RandomForestRegressor and
    categorical columns use RandomForestClassifier.  The process iterates in
    a chained-equations style (like missForest in R) until convergence or
    `max_iter` rounds.

    This is the method of choice when relationships between features are
    non-linear or when the data contains interactions that linear models
    cannot capture.

    Parameters
    ----------
    df_name : pandas.DataFrame
        Input DataFrame with missing values.
    col_list : list of str, optional
        Columns to impute.  If None, all columns with missing values are
        used.
    n_estimators : int, default 100
        Number of trees in each Random Forest.
    max_iter : int, default 10
        Maximum number of imputation iterations.
    random_state : int, default 42
        Seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        DataFrame with missing values imputed via Random Forest.
    """
    # usage: df_impute_random_forest(df, ['col1', 'col2'], n_estimators=100, max_iter=10)
    # input: df_name - pandas DataFrame with NaN values, col_list - columns to impute
    # output: imputed DataFrame

    df = df_name.copy()

    if col_list is None:
        col_list = df.columns[df.isna().any()].tolist()

    if not col_list:
        print("RF Imputation: no missing values found — returning original DataFrame")
        return df

    # Separate numeric and categorical columns
    numeric_cols = [c for c in col_list if pd.api.types.is_numeric_dtype(df[c])]
    cat_cols = [c for c in col_list if not pd.api.types.is_numeric_dtype(df[c])]

    all_feature_cols = df.columns.tolist()

    # Encode categoricals to numeric for use as predictors
    label_maps = {}
    reverse_maps = {}
    for col in cat_cols:
        label_map = {v: i for i, v in enumerate(df[col].dropna().unique())}
        label_maps[col] = label_map
        reverse_maps[col] = {i: v for v, i in label_map.items()}
        df[col] = df[col].map(label_map)

    na_before = df[col_list].isna().sum().sum()
    print(f"RF Imputation: {na_before} missing values across {len(col_list)} columns ({len(numeric_cols)} numeric, {len(cat_cols)} categorical)")

    # Store original missing positions
    missing_masks = {col: df[col].isna() for col in col_list}

    # Initial fill: median for numeric, mode for categorical
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
    for col in cat_cols:
        mode_val = df[col].mode()
        df[col] = df[col].fillna(mode_val.iloc[0] if len(mode_val) > 0 else 0)

    # Sort columns by number of missing values (fewest first) for stable convergence
    sorted_cols = sorted(col_list, key=lambda c: missing_masks[c].sum())

    iteration = 0
    for iteration in range(max_iter):
        changes = 0
        for col in sorted_cols:
            if not missing_masks[col].any():
                continue

            predictor_cols = [c for c in all_feature_cols if c != col]
            obs_mask = ~missing_masks[col]
            mis_mask = missing_masks[col]

            X_obs = df.loc[obs_mask, predictor_cols].values
            y_obs = df.loc[obs_mask, col].values
            X_mis = df.loc[mis_mask, predictor_cols].values

            if col in cat_cols:
                rf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)
            else:
                rf = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)

            rf.fit(X_obs, y_obs)
            new_values = rf.predict(X_mis)

            old_values = df.loc[mis_mask, col].values
            changes += np.sum(np.abs(new_values - old_values) > 1e-6)
            df.loc[mis_mask, col] = new_values

        if changes == 0:
            print(f"RF Imputation: converged at iteration {iteration + 1}")
            break

    # Restore categorical labels
    for col in cat_cols:
        df[col] = df[col].round().astype(int).map(reverse_maps[col])

    na_after = df[col_list].isna().sum().sum()
    print(f"RF Imputation: complete — {na_before - na_after} values imputed over {min(iteration + 1, max_iter)} iterations")

    return df


# ---------------------------------------------------------------------------
# 3. K-Nearest Neighbours (KNN) Imputation
# ---------------------------------------------------------------------------

def df_impute_knn(df_name, col_list: Optional[list] = None, n_neighbors: int = 5, weights: Literal['uniform', 'distance'] = 'uniform'):
    """impute missing values using K-Nearest Neighbours

    Each missing value is replaced by the (optionally weighted) mean of the
    values from its k nearest complete neighbours in feature space.  Distance
    is computed using a nan-aware Euclidean metric so that partially-observed
    rows can still serve as donors.

    KNN imputation is a good default when the dataset is not too large, the
    feature space is reasonably low-dimensional, and you want a non-parametric
    method that requires no distributional assumptions.

    Parameters
    ----------
    df_name : pandas.DataFrame
        Input DataFrame with missing values.
    col_list : list of str, optional
        Numeric columns to include.  If None, all numeric columns are used.
    n_neighbors : int, default 5
        Number of nearest neighbours to use for imputation.
    weights : str, default 'uniform'
        Weight function:  'uniform' gives equal weight to all neighbours;
        'distance' weights by the inverse of the Euclidean distance.

    Returns
    -------
    pandas.DataFrame
        DataFrame with missing values imputed via KNN.
    """
    # usage: df_impute_knn(df, ['col1', 'col2'], n_neighbors=5, weights='distance')
    # input: df_name - pandas DataFrame with NaN values, col_list - numeric columns to impute
    # output: imputed DataFrame

    df = df_name.copy()
    cols = col_list if col_list is not None else df.select_dtypes(include=[np.number]).columns.tolist()

    na_before = df[cols].isna().sum().sum()
    print(f"KNN Imputation: {na_before} missing values across {len(cols)} columns, k={n_neighbors}, weights='{weights}'")

    if na_before == 0:
        print("KNN Imputation: no missing values found — returning original DataFrame")
        return df

    imputer = KNNImputer(n_neighbors=n_neighbors, weights=weights)
    imputed_array = imputer.fit_transform(df[cols])
    df[cols] = pd.DataFrame(imputed_array, columns=cols, index=df.index)

    na_after = df[cols].isna().sum().sum()
    print(f"KNN Imputation: complete — {na_before - na_after} values imputed")

    return df


def df_impute_summary(df_original, df_imputed, col_list: Optional[list] = None):
    """print a before/after summary comparing missing value counts and basic descriptive statistics

    Useful for quickly validating any imputation method's output against the
    original DataFrame.

    Parameters
    ----------
    df_original : pandas.DataFrame
        The original DataFrame before imputation.
    df_imputed : pandas.DataFrame
        The DataFrame after imputation.
    col_list : list of str, optional
        Columns to summarise.  If None, all columns that had missing values
        in the original DataFrame are used.

    Returns
    -------
    pandas.DataFrame
        Summary DataFrame with columns: column, na_before, na_after, mean_before,
        mean_after, std_before, std_after.
    """
    # usage: df_impute_summary(df_original, df_imputed)
    # input: df_original - original DataFrame, df_imputed - imputed DataFrame
    # output: summary DataFrame with before/after statistics

    if col_list is None:
        col_list = df_original.columns[df_original.isna().any()].tolist()

    if not col_list:
        print("Imputation Summary: no columns to summarise")
        return pd.DataFrame()

    rows = []
    for col in col_list:
        row = {
            'column': col,
            'na_before': df_original[col].isna().sum(),
            'na_after': df_imputed[col].isna().sum(),
        }
        if pd.api.types.is_numeric_dtype(df_original[col]):
            row['mean_before'] = df_original[col].mean()
            row['mean_after'] = df_imputed[col].mean()
            row['std_before'] = df_original[col].std()
            row['std_after'] = df_imputed[col].std()
        else:
            row['mean_before'] = None
            row['mean_after'] = None
            row['std_before'] = None
            row['std_after'] = None
        rows.append(row)

    summary = pd.DataFrame(rows)
    print("Imputation Summary:")
    print(summary.to_string(index=False))

    return summary
