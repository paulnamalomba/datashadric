# datashadric — Module Reference Notes
**Package version**: 0.3.3  
**Location**: `src/datashadric/`

This document provides a concise reference for every module in the `datashadric` package, listing each
public function alongside a brief description of what it does and its key parameters.

## Contents

- [datashadric — Module Reference Notes](#datashadric--module-reference-notes)
  - [Contents](#contents)
  - [`__init__.py` — Package Entry Point](#__init__py--package-entry-point)
  - [`dataframing.py` — Data Manipulation \& Cleaning](#dataframingpy--data-manipulation--cleaning)
  - [`stochastics.py` — Statistical Analysis \& Hypothesis Testing](#stochasticspy--statistical-analysis--hypothesis-testing)
  - [`mlearning.py` — Machine Learning Models \& Evaluation](#mlearningpy--machine-learning-models--evaluation)
  - [`regression.py` — Regression Analysis \& Diagnostics](#regressionpy--regression-analysis--diagnostics)
  - [`plotters.py` — Visualisation](#plotterspy--visualisation)
  - [`aiagents.py` — AI-Assisted Analysis](#aiagentspy--ai-assisted-analysis)
  - [`imputation.py` — Multiple Imputation Methods *(new in v0.3.1)*](#imputationpy--multiple-imputation-methods-new-in-v031)

---

## `__init__.py` — Package Entry Point
Defines `__version__`, `__author__`, `__email__`, imports all sub-modules, and declares `__all__`
for wildcard export.  No user-facing functions live here.

---

## `dataframing.py` — Data Manipulation & Cleaning
General-purpose pandas utilities for loading, inspecting, transforming, and cleaning DataFrames.
Prefix convention: `df_` for DataFrame functions; standalone string helpers have no prefix.

| Function | Summary |
|---|---|
| `df_load_dataset(excel_path, data_separator, header)` | Load CSV/Excel into a DataFrame. Separator and header row are configurable. |
| `df_print_row_and_columns(df_name)` | Print total rows and columns with dtypes overview. |
| `df_get_count_on_axis(df_name, axis)` | Return count of rows (`axis=0`) or columns (`axis=1`). |
| `df_check_na_values(df_name, *args)` | Comprehensive missing-value report (counts + percentages per column). |
| `df_drop_na(df_name, ax)` | Drop rows (`ax=0`) or columns (`ax=1`) containing NaN. |
| `df_datetime_converter(df_name, col_datetime_lookup)` | Parse a string column into `datetime64` and set it as the index. |
| `df_explore_unique_categories(df_name, col)` | Print unique values and their counts for a categorical column. |
| `df_mask_with_list(df, df_col, list_comp, mask_type)` | Filter rows where column values are in (`mask_type=0`) or not in (`mask_type=1`) a list. |
| `df_groupby_mask_operate(df, col_name_masker, col_name_operate, *args)` | Group by one column and aggregate another with a given operation. |
| `df_cross_corr_check(df_name, cols_y, cols_x)` | Compute cross-correlation matrix between two sets of columns. |
| `df_class_balance(df_filtered)` | Print class-balance statistics for a categorical Series. |
| `df_drop_dupes(df, col_dupes, *args)` | Remove duplicate rows, optionally based on a subset column. |
| `df_drop_col(df, col_name)` | Drop a single column by name. |
| `df_drop_multicol(df, col_names)` | Drop multiple columns by a list of names. |
| `df_corr_check(df_name, col_y, col_x)` | Pearson correlation between two columns with print output. |
| `df_head(df_name, head_num)` | Return and print the first `head_num` rows. |
| `df_one_hot_enconding(df_name, col_name, *binary_bool)` | One-hot encode a categorical column (optionally drop first for binary). |
| `df_info_dtypes(df_name, *args)` | Print column data types and memory usage. |
| `df_column_nms(df_name, *args)` | Print or return the column names of a DataFrame. |
| `remove_whitespace(str_target)` | Strip and collapse internal whitespace from a string. |
| `remove_unicode(str_target)` | Transliterate Unicode characters to ASCII (via `unidecode`). |
| `degree_symbol_parse(str_target)` | Replace degree symbols (`°`) and directional suffixes in geographic strings. |
| `df_standardize_colnames(df_name)` | Lowercase and snake_case all column names. |
| `df_move_col_to_pos(df, col_name, pos)` | Reorder columns by moving one column to a specific position. |
| `df_rename_col(df, col_old_name, col_new_name)` | Rename a single column. |
| `df_rename_multicol(df, col_rename_dict)` | Rename multiple columns via a dictionary mapping. |
| `df_replace_in_col(df, col_name, to_replace, value)` | Replace specific values in a column. |
| `df_replace_in_multicol(df, col_replace_dict)` | Replace values across multiple columns via a dictionary. |
| `df_convert_col_type(df, col_name, new_type)` | Cast a column to a new dtype. |
| `df_convert_multicol_type(df, col_type_dict)` | Cast multiple columns to specified dtypes. |
| `df_fill_na_with_value(df, col_name, fill_value)` | Fill NaN with a constant value. |
| `df_fill_na_with_method(df, col_name, method)` | Fill NaN with `'ffill'` or `'bfill'`. |
| `df_fill_na_with_mean(df, col_name)` | Fill NaN with the column mean. |
| `df_fill_na_with_median(df, col_name)` | Fill NaN with the column median. |
| `df_fill_na_with_mode(df, col_name)` | Fill NaN with the column mode. |
| `df_describe(df_name, *args)` | Print descriptive statistics (wrapper around `DataFrame.describe`). |
| `df_to_numpy(df_name, *args)` | Convert DataFrame to a NumPy array. |
| `df_from_numpy(np_array, col_names)` | Create a DataFrame from a NumPy array with given column names. |
| `df_concat(df_list, axis)` | Concatenate a list of DataFrames along an axis. |
| `df_merge(df_left, df_right, on, how)` | Merge two DataFrames on a key column. |
| `df_sample(df_name, n, replace, random_state)` | Random sample of `n` rows. |
| `df_sort_by_col(df, col_name, ascending)` | Sort DataFrame by a column. |
| `df_reset_index(df, drop)` | Reset the DataFrame index. |
| `df_set_index(df, col_name)` | Set a column as the DataFrame index. |
| `df_append_row(df, row_data)` | Append a row from a dictionary. |
| `df_apply_function(df, col_name, func)` | Apply a custom function to a column. |
| `df_remove_rows_by_condition(df, col_name, condition)` | Remove rows matching a boolean condition. |
| `df_rename_index(df, new_index_name)` | Rename the DataFrame index. |
| `df_get_index_name(df)` | Return the current index name. |
| `df_get_column_name_by_index(df, index)` | Return the column name at a positional index. |
| `df_get_column_index_by_name(df, col_name)` | Return the positional index of a named column. |
| `df_get_all_column_names(df)` | Return all column names as a list. |
| `df_get_all_column_indices(df)` | Return positional indices for all columns. |

---

## `stochastics.py` — Statistical Analysis & Hypothesis Testing
Functions for normality testing, confidence intervals, z-scores, ANOVA, chi-square tests,
VIF multicollinearity diagnostics, post-hoc comparisons, and outlier filtering.
Uses `scipy.stats`, `statsmodels`, `numpy`, `pandas`, `matplotlib`.

| Function | Summary |
|---|---|
| `df_gaussian_checks(df_name, col_name, *args)` | Shapiro-Wilk test for normality with optional Q-Q plot. |
| `df_calc_conf_interval(moe_vals, mean_val)` | Compute confidence interval from margin of error and mean. |
| `df_calc_moe(stderr_val, z_score_cl)` | Calculate margin of error from standard error and z-score. |
| `df_calc_stderr(df_name, col_z, stddev_val)` | Compute standard error for a column. |
| `df_calc_zscore(df_name, col_z, confidence_levels, mean_val, stddev_val)` | Compute z-scores at given confidence levels. |
| `df_residual_analysis(df_name, col_actual, col_predicted)` | Compute residuals, MSE, MAE, R-squared, and Durbin-Watson statistic. |
| `df_vif_calculation(df_name, col_list)` | Variance Inflation Factor for multicollinearity detection. |
| `df_tukey_hsd(df_name, col_group, col_value, alpha)` | Tukey Honest Significant Difference post-hoc test. |
| `df_anova_oneway(df_name, col_group, col_value)` | One-way ANOVA F-test. |
| `df_anova_twoway(df_name, col_factor1, col_factor2, col_value)` | Two-way ANOVA with interaction term. |
| `df_chi_square_test(df_name, col1, col2)` | Chi-square test of independence on a cross-tabulation. |
| `df_residual_based_filtering(df_name, col_actual, col_predicted, threshold)` | Remove rows whose absolute residual exceeds a threshold. |
| `df_zscore_based_filtering(df_name, col_x, col_y, z_threshold, plot_zscores_data, save_path)` | Remove statistical outliers by z-score with optional visualisation. |
| `df_plot_zscores(df, z_scores, col_x, col_y, save_path)` | Plot z-score distributions for two columns. |
| `df_ds_score_filtering(df_name, col_x_name, col_y_name, ds_score_tuner, log_base, ...)` | Custom DS-score (log-scaled normalised product) outlier filtering algorithm. |

---

## `mlearning.py` — Machine Learning Models & Evaluation
Supervised and unsupervised learning workflows: Naive Bayes, logistic regression,
K-Means clustering, Isolation Forest, Local Outlier Factor, KS-score evaluation.
Uses `scikit-learn`.

| Function | Summary |
|---|---|
| `logr_predictor(df_name, log_regression_model)` | Predict probabilities with a fitted logistic regression model. |
| `logr_classifier(df_name, log_regression_model)` | Classify observations using a logistic regression model. |
| `logr_train_test_split(df_name, col_response, col_predictor, test_size, random_state)` | Train/test split for logistic regression (single predictor). |
| `ml_train_test_split(df_name, col_target, test_size, random_state)` | General-purpose train/test split returning a dict of splits. |
| `ml_naive_bayes_model(train_test_split_nm)` | Train a Gaussian Naive Bayes model and return predictions. |
| `ml_naive_bayes_metrics(naive_bayes_nm)` | Compute accuracy, precision, recall, F1 for a trained NB model. |
| `ml_naive_bayes_confusion(naive_bayes_nm)` | Generate and display a confusion matrix for a NB model. |
| `ml_naive_bayes_roc(naive_bayes_nm)` | Plot ROC curve and compute AUC for a NB model. |
| `ml_iforest_outlier_detection(df_name, col_list, contamination, random_state)` | Isolation Forest outlier detection; returns DataFrame with anomaly labels. |
| `ml_lof_outlier_detection(df_name, col_list, n_neighbors, contamination)` | Local Outlier Factor outlier detection. |
| `ml_ks_score_evaluation(y_true, y_scores)` | Kolmogorov-Smirnov statistic for binary classification model evaluation. |
| `ml_kmeans_clustering(df_name, col_list, n_clusters, random_state)` | K-Means clustering with cluster-label assignment. |

---

## `regression.py` — Regression Analysis & Diagnostics
OLS and GLM regression modelling with residual diagnostics and assumption checking.
Uses `statsmodels.formula.api`, `statsmodels.api`, `scipy.stats`.

| Function | Summary |
|---|---|
| `lr_check_homoscedasticity(fitted, resid, *args)` | Breusch-Pagan / White test for homoscedasticity of residuals. |
| `lr_check_normality(resid)` | Shapiro-Wilk normality test on regression residuals. |
| `lr_qqplots_normality(resid)` | Q-Q plot of residuals against a normal distribution. |
| `lr_post_hoc_test(df_name, col_response, col_predictor, alpha)` | Tukey HSD post-hoc comparison for categorical predictors. |
| `lr_ols_model(df_name, col_response, col_cont_predictors, col_cat_predictors)` | Fit an OLS model with mixed continuous and categorical predictors. |
| `lr_glm_model(df_name, col_response, col_cont_predictors, col_cat_predictors, family)` | Fit a GLM (Gaussian, Binomial, Poisson, etc.) with formula API. |

---

## `plotters.py` — Visualisation
A wide range of matplotlib / seaborn / plotly plotting functions.  All accept an optional `save_path`
argument to save the figure to disk.

| Function | Summary |
|---|---|
| `df_boxplot_plotter(df_name, col_xplot, col_yplot, type_plot, save_path, *args)` | Box plot (seaborn or plotly depending on `type_plot`). |
| `df_histogram_plotter(df_name, col_plot, type_plot, bins, save_path, *args)` | Histogram with configurable bins and backend. |
| `df_grouped_histogram_plotter(df_name, col_groupby, col_plot, type_plot, bins, save_path)` | Histogram grouped by a categorical column. |
| `df_grouped_barplotter(df_name, col_groupby, col_plot, type_plot, save_path)` | Grouped bar chart. |
| `df_scatter_plotter(df_grouped, col_xplot, col_yplot, save_path)` | Simple scatter plot. |
| `df_pairplot_plotter(df_name, save_path)` | Seaborn pair plot for all numeric columns. |
| `df_heatmap_plotter(df_name, col_list, save_path)` | Correlation heatmap for selected columns. |
| `df_lowess_plotter(x, y, frac, title, save_path)` | LOWESS smoothing curve via `statsmodels`. |
| `df_candlestick_plotter(df, title, save_path)` | Plotly candlestick chart (expects Open/High/Low/Close columns). |
| `df_timeseries_plotter(df, col_date, col_value, title, save_path)` | Time-series line plot. |
| `df_barplot_plotter(df, col_x, col_y, title, save_path)` | Simple bar plot. |
| `df_piechart_plotter(df, col_labels, col_values, title, save_path)` | Pie chart. |
| `df_lineplot_plotter(df, col_x, col_y, title, save_path)` | Line plot. |
| `df_violinplot_plotter(df, col_x, col_y, title, save_path)` | Violin plot for distribution comparison. |
| `df_areaplot_plotter(df, col_x, col_y, title, save_path)` | Area (filled line) plot. |
| `df_scattermatrix_plotter(df, cols_list, title, save_path)` | Plotly scatter matrix for selected columns. |
| `df_lollipop_plotter(df, col_x, col_y, title, save_path)` | Lollipop (stem) plot. |
| `df_ridgeplot_plotter(df, col_x, col_y, title, save_path)` | Ridge (joy) plot for overlapping distributions. |
| `df_bubbleplot_plotter(df, col_x, col_y, col_size, title, save_path)` | Bubble chart with variable marker size. |
| `df_scatterplot_boundingboxes_plotter(df, col_x, col_y, boxes, title, save_path)` | Scatter plot with rectangular bounding boxes overlay (for AI outlier annotation). |

---

## `aiagents.py` — AI-Assisted Analysis
Multimodal AI functions powered by Google Gemini.  Requires the `GOOGLE_API_KEY` environment variable
to be set.

We are nowusing Gemma 4 for AI Vision.

| Function | Summary |
|---|---|
| `ai_generate_text(prompt, model, max_tokens)` | Generate text from a Gemini model. |
| `ai_generate_image(prompt, model, size)` | Generate an image from a Gemini image-preview model. Returns a `PIL.Image`. |
| `ai_visual_recognition(image_path, model)` | Describe an image using Gemini's vision capabilities. |
| `ai_analyze_plot_data_with_vision(df, excel_path, image_path, col_x, col_y, prompt)` | Create a scatter plot from data, then ask Gemini to analyse it visually. |
| `ai_analyze_plot_data_with_bounding_boxes(df, excel_path, image_path, col_x, col_y, prompt)` | Same as above but Gemini returns bounding-box coordinates for detected outliers. |

---

## `imputation.py` — Multiple Imputation Methods *(new in v0.3.1)*
Advanced imputation strategies for handling missing data in DataFrames.  Implements three families:
MICE (chained equations), Random Forest, and K-Nearest Neighbours.

| Function | Summary |
|---|---|
| `df_mice_impute_pmm(df_name, col_list, max_iter, n_nearest, random_state)` | MICE with Predictive Mean Matching — imputes from real observed donor values. |
| `df_mice_impute_norm(df_name, col_list, max_iter, random_state)` | MICE with Bayesian Linear Regression (norm) — smooth posterior-predictive draws. |
| `df_mice_impute_logistic(df_name, col_target, col_predictors, max_iter, random_state)` | MICE with Logistic Regression — for binary or categorical target columns. |
| `df_impute_random_forest(df_name, col_list, n_estimators, max_iter, random_state)` | Iterative Random Forest imputation (missForest-style) for numeric and categorical data. |
| `df_impute_knn(df_name, col_list, n_neighbors, weights)` | K-Nearest Neighbours imputation using nan-aware Euclidean distance. |
| `df_impute_summary(df_original, df_imputed, col_list)` | Before/after summary table comparing NaN counts and descriptive statistics. |
