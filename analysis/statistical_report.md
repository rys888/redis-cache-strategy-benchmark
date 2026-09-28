# Run-level statistical analysis

Statistical unit is one independent run (N=30). Request-level JTL data were not used. Concurrency is treated as a categorical factor. AvgRT and P95 are modelled on the natural log scale; Throughput is modelled on its original scale. All model coefficients, contrasts and omnibus tests use HC3 heteroskedasticity-robust standard errors; 95% CIs are two-sided.

## Descriptive statistics

| strategy     | concurrency | outcome    | n | mean     | sd     | ci95_low | ci95_high |
| ------------ | ----------- | ---------- | - | -------- | ------ | -------- | --------- |
| cache-aside  | 25          | AvgRT      | 5 | 4.097    | 0.028  | 4.063    | 4.132     |
| cache-aside  | 25          | P95        | 5 | 8.200    | 0.447  | 7.645    | 8.755     |
| cache-aside  | 25          | Throughput | 5 | 6073.233 | 41.736 | 6021.411 | 6125.056  |
| cache-aside  | 50          | AvgRT      | 5 | 7.782    | 0.034  | 7.740    | 7.825     |
| cache-aside  | 50          | P95        | 5 | 14.400   | 0.548  | 13.720   | 15.080    |
| cache-aside  | 50          | Throughput | 5 | 6404.927 | 27.760 | 6370.459 | 6439.395  |
| cache-aside  | 100         | AvgRT      | 5 | 15.100   | 0.055  | 15.032   | 15.168    |
| cache-aside  | 100         | P95        | 5 | 24.400   | 0.548  | 23.720   | 25.080    |
| cache-aside  | 100         | Throughput | 5 | 6608.517 | 24.358 | 6578.272 | 6638.761  |
| read-through | 25          | AvgRT      | 5 | 4.192    | 0.029  | 4.156    | 4.229     |
| read-through | 25          | P95        | 5 | 8.600    | 0.548  | 7.920    | 9.280     |
| read-through | 25          | Throughput | 5 | 5936.920 | 42.383 | 5884.295 | 5989.545  |
| read-through | 50          | AvgRT      | 5 | 7.954    | 0.017  | 7.933    | 7.976     |
| read-through | 50          | P95        | 5 | 15.000   | 0.000  | 15.000   | 15.000    |
| read-through | 50          | Throughput | 5 | 6266.217 | 13.951 | 6248.895 | 6283.538  |
| read-through | 100         | AvgRT      | 5 | 15.437   | 0.062  | 15.360   | 15.513    |
| read-through | 100         | P95        | 5 | 25.000   | 0.000  | 25.000   | 25.000    |
| read-through | 100         | Throughput | 5 | 6462.047 | 25.637 | 6430.214 | 6493.879  |

## Variance homogeneity and residual normality

| outcome    | test                                             | statistic | df1     | df2      | p       |
| ---------- | ------------------------------------------------ | --------- | ------- | -------- | ------- |
| AvgRT      | Levene (raw scale, 6 cells, median centered)     | 0.62154   | 5.00000 | 24.00000 | 0.68474 |
| AvgRT      | Levene (modeled scale, 6 cells, median centered) | 0.40261   | 5.00000 | 24.00000 | 0.84214 |
| AvgRT      | Shapiro-Wilk (model residuals)                   | 0.92831   | NA      | NA       | 0.04430 |
| P95        | Levene (raw scale, 6 cells, median centered)     | 1.05455   | 5.00000 | 24.00000 | 0.40949 |
| P95        | Levene (modeled scale, 6 cells, median centered) | 1.09253   | 5.00000 | 24.00000 | 0.38998 |
| P95        | Shapiro-Wilk (model residuals)                   | 0.92751   | NA      | NA       | 0.04219 |
| Throughput | Levene (raw scale, 6 cells, median centered)     | 0.33194   | 5.00000 | 24.00000 | 0.88861 |
| Throughput | Levene (modeled scale, 6 cells, median centered) | 0.33194   | 5.00000 | 24.00000 | 0.88861 |
| Throughput | Shapiro-Wilk (model residuals)                   | 0.93509   | NA      | NA       | 0.06711 |

## HC3 main model coefficients

| outcome    | term                      | coefficient | std_error_HC3 | df_resid | ci95_low   | ci95_high  | t         | p         | interpreted_effect | interpreted_ci95_low | interpreted_ci95_high | interpreted_scale                |
| ---------- | ------------------------- | ----------- | ------------- | -------- | ---------- | ---------- | --------- | --------- | ------------------ | -------------------- | --------------------- | -------------------------------- |
| AvgRT      | Intercept                 | 1.41033     | 0.00343       | 24.00000 | 1.40325    | 1.41741    | 411.16543 | 1.078e-47 | 4.09732            | 4.06842              | 4.12643               | geometric mean at reference cell |
| AvgRT      | Strategy[read-through]    | 0.02287     | 0.00491       | 24.00000 | 0.01273    | 0.03301    | 4.65450   | 9.997e-05 | 2.31356            | 1.28115              | 3.35649               | percent change                   |
| AvgRT      | Concurrency[50]           | 0.64152     | 0.00408       | 24.00000 | 0.63310    | 0.64995    | 157.21036 | 1.121e-37 | 89.93716           | 88.34421             | 91.54358              | percent change                   |
| AvgRT      | Concurrency[100]          | 1.30434     | 0.00388       | 24.00000 | 1.29634    | 1.31235    | 336.35689 | 1.335e-45 | 268.52649          | 265.58876            | 271.48782             | percent change                   |
| AvgRT      | Strategy×Concurrency[50]  | -0.00101    | 0.00550       | 24.00000 | -0.01235   | 0.01034    | -0.18291  | 0.85640   | -0.10051           | -1.22767             | 1.03951               | percent change                   |
| AvgRT      | Strategy×Concurrency[100] | -0.00081    | 0.00560       | 24.00000 | -0.01238   | 0.01075    | -0.14512  | 0.88582   | -0.08130           | -1.23041             | 1.08118               | percent change                   |
| P95        | Intercept                 | 2.10300     | 0.02634       | 24.00000 | 2.04864    | 2.15736    | 79.84931  | 1.249e-30 | 8.19069            | 7.75735              | 8.64823               | geometric mean at reference cell |
| P95        | Strategy[read-through]    | 0.04711     | 0.04164       | 24.00000 | -0.03883   | 0.13306    | 1.13137   | 0.26908   | 4.82407            | -3.80885             | 14.23177              | percent change                   |
| P95        | Concurrency[50]           | 0.56366     | 0.03241       | 24.00000 | 0.49676    | 0.63055    | 17.38948  | 4.171e-15 | 75.70853           | 64.33846             | 87.86525              | percent change                   |
| P95        | Concurrency[100]          | 1.09138     | 0.02861       | 24.00000 | 1.03233    | 1.15044    | 38.14480  | 5.413e-23 | 197.83947          | 180.76083            | 215.95701             | percent change                   |
| P95        | Strategy×Concurrency[50]  | -0.00572    | 0.04573       | 24.00000 | -0.10010   | 0.08866    | -0.12503  | 0.90154   | -0.57012           | -9.52501             | 9.27110               | percent change                   |
| P95        | Strategy×Concurrency[100] | -0.02262    | 0.04312       | 24.00000 | -0.11161   | 0.06637    | -0.52462  | 0.60466   | -2.23661           | -10.56065            | 6.86214               | percent change                   |
| Throughput | Intercept                 | 6073.23340  | 20.86809      | 24.00000 | 6030.16378 | 6116.30302 | 291.02970 | 4.305e-44 | 6073.23340         | 6030.16378           | 6116.30302            | req/s difference                 |
| Throughput | Strategy[read-through]    | -136.31340  | 29.74143      | 24.00000 | -197.69670 | -74.93010  | -4.58328  | 0.00012   | -136.31340         | -197.69670           | -74.93010             | req/s difference                 |
| Throughput | Concurrency[50]           | 331.69340   | 25.06243      | 24.00000 | 279.96708  | 383.41972  | 13.23469  | 1.604e-12 | 331.69340          | 279.96708            | 383.41972             | req/s difference                 |
| Throughput | Concurrency[100]          | 535.28320   | 24.16213      | 24.00000 | 485.41501  | 585.15139  | 22.15381  | 1.737e-17 | 535.28320          | 485.41501            | 585.15139             | req/s difference                 |
| Throughput | Strategy×Concurrency[50]  | -2.39680    | 33.55377      | 24.00000 | -71.64838  | 66.85478   | -0.07143  | 0.94365   | -2.39680           | -71.64838            | 66.85478              | req/s difference                 |
| Throughput | Strategy×Concurrency[100] | -10.15660   | 34.60054      | 24.00000 | -81.56860  | 61.25540   | -0.29354  | 0.77163   | -10.15660          | -81.56860            | 61.25540              | req/s difference                 |

## HC3 omnibus tests

| outcome    | term                                | df_num | df_den   | F_HC3        | p_HC3     |
| ---------- | ----------------------------------- | ------ | -------- | ------------ | --------- |
| AvgRT      | Strategy (equal-weight marginal)    | 1      | 24.00000 | 119.01452    | 8.747e-11 |
| AvgRT      | Concurrency (equal-weight marginal) | 2      | 24.00000 | 130655.63131 | 3.599e-49 |
| AvgRT      | Strategy × Concurrency              | 2      | 24.00000 | 0.01673      | 0.98342   |
| P95        | Strategy (equal-weight marginal)    | 1      | 24.00000 | 5.76217      | 0.02449   |
| P95        | Concurrency (equal-weight marginal) | 2      | 24.00000 | 2097.54109   | 1.148e-27 |
| P95        | Strategy × Concurrency              | 2      | 24.00000 | 0.38741      | 0.68298   |
| Throughput | Strategy (equal-weight marginal)    | 1      | 24.00000 | 123.50146    | 6.021e-11 |
| Throughput | Concurrency (equal-weight marginal) | 2      | 24.00000 | 485.51112    | 3.877e-20 |
| Throughput | Strategy × Concurrency              | 2      | 24.00000 | 0.07070      | 0.93194   |

The omnibus interaction test has 2 df; the two individual interaction coefficients each have 1 df.

## Strategy simple effects and marginal effects

| outcome    | contrast                                      | estimate_model_scale | std_error_HC3 | ci95_low_model_scale | ci95_high_model_scale | t         | p         | interpreted_effect | interpreted_ci95_low | interpreted_ci95_high | interpreted_scale                                            |
| ---------- | --------------------------------------------- | -------------------- | ------------- | -------------------- | --------------------- | --------- | --------- | ------------------ | -------------------- | --------------------- | ------------------------------------------------------------ |
| AvgRT      | read-through - cache-aside at concurrency 25  | 0.02287              | 0.00491       | 0.01273              | 0.03301               | 4.65450   | 9.997e-05 | 2.31356            | 1.28115              | 3.35649               | read-through vs cache-aside (%)                              |
| AvgRT      | read-through - cache-aside at concurrency 50  | 0.02187              | 0.00247       | 0.01678              | 0.02696               | 8.86831   | 4.859e-09 | 2.21072            | 1.69190              | 2.73219               | read-through vs cache-aside (%)                              |
| AvgRT      | read-through - cache-aside at concurrency 100 | 0.02206              | 0.00270       | 0.01650              | 0.02762               | 8.18481   | 2.102e-08 | 2.23038            | 1.66331              | 2.80060               | read-through vs cache-aside (%)                              |
| AvgRT      | equal-weight marginal strategy effect         | 0.02227              | 0.00204       | 0.01805              | 0.02648               | 10.90938  | 8.747e-11 | 2.25154            | 1.82173              | 2.68317               | equal-weight marginal read-through vs cache-aside (%)        |
| P95        | read-through - cache-aside at concurrency 25  | 0.04711              | 0.04164       | -0.03883             | 0.13306               | 1.13137   | 0.26908   | 4.82407            | -3.80885             | 14.23177              | read-through vs cache-aside (%)                              |
| P95        | read-through - cache-aside at concurrency 50  | 0.04140              | 0.01889       | 0.00240              | 0.08039               | 2.19089   | 0.03841   | 4.22645            | 0.24023              | 8.37118               | read-through vs cache-aside (%)                              |
| P95        | read-through - cache-aside at concurrency 100 | 0.02449              | 0.01118       | 0.00142              | 0.04757               | 2.19089   | 0.03841   | 2.47956            | 0.14207              | 4.87161               | read-through vs cache-aside (%)                              |
| P95        | equal-weight marginal strategy effect         | 0.03767              | 0.01569       | 0.00528              | 0.07005               | 2.40045   | 0.02449   | 3.83858            | 0.52951              | 7.25657               | equal-weight marginal read-through vs cache-aside (%)        |
| Throughput | read-through - cache-aside at concurrency 25  | -136.31340           | 29.74143      | -197.69670           | -74.93010             | -4.58328  | 0.00012   | -136.31340         | -197.69670           | -74.93010             | read-through minus cache-aside (req/s)                       |
| Throughput | read-through - cache-aside at concurrency 50  | -138.71020           | 15.53392      | -170.77064           | -106.64976            | -8.92950  | 4.275e-09 | -138.71020         | -170.77064           | -106.64976            | read-through minus cache-aside (req/s)                       |
| Throughput | read-through - cache-aside at concurrency 100 | -146.47000           | 17.68175      | -182.96335           | -109.97665            | -8.28368  | 1.694e-08 | -146.47000         | -182.96335           | -109.97665            | read-through minus cache-aside (req/s)                       |
| Throughput | equal-weight marginal strategy effect         | -140.49787           | 12.64252      | -166.59075           | -114.40499            | -11.11312 | 6.021e-11 | -140.49787         | -166.59075           | -114.40499            | equal-weight marginal read-through minus cache-aside (req/s) |

## Partial eta-squared (model scale; stratified bootstrap 95% CI)

| outcome    | term                   | partial_eta_squared | bootstrap_ci95_low | bootstrap_ci95_high | bootstrap_reps |
| ---------- | ---------------------- | ------------------- | ------------------ | ------------------- | -------------- |
| AvgRT      | Strategy               | 0.86109             | 0.81873            | 0.95466             | 10000          |
| AvgRT      | Concurrency            | 0.99993             | 0.99991            | 0.99998             | 10000          |
| AvgRT      | Strategy × Concurrency | 0.00237             | 0.00197            | 0.28502             | 10000          |
| P95        | Strategy               | 0.23084             | 0.03030            | 0.75718             | 10000          |
| P95        | Concurrency            | 0.99396             | 0.99292            | 0.99866             | 10000          |
| P95        | Strategy × Concurrency | 0.01913             | 0.00270            | 0.60882             | 10000          |
| Throughput | Strategy               | 0.86545             | 0.82473            | 0.95606             | 10000          |
| Throughput | Concurrency            | 0.98420             | 0.97852            | 0.99553             | 10000          |
| Throughput | Strategy × Concurrency | 0.00609             | 0.00201            | 0.31029             | 10000          |

## Cohen's d (read-through minus cache-aside; original scale; stratified bootstrap 95% CI)

| outcome    | concurrency | cohens_d_readthrough_minus_cacheaside | bootstrap_ci95_low | bootstrap_ci95_high | valid_bootstrap_reps |
| ---------- | ----------- | ------------------------------------- | ------------------ | ------------------- | -------------------- |
| AvgRT      | 25          | 3.3000                                | 2.4389             | 9.8118              | 10000                |
| AvgRT      | 50          | 6.2982                                | 4.5658             | 22.4006             | 10000                |
| AvgRT      | 100         | 5.7714                                | 4.5180             | 17.3799             | 10000                |
| P95        | 25          | 0.8000                                | -0.4000            | 2.5298              | 9700                 |
| P95        | 50          | 1.5492                                | 0.6325             | 2.5298              | 9120                 |
| P95        | 100         | 1.5492                                | 0.6325             | 2.5298              | 9096                 |
| Throughput | 25          | -3.2409                               | -9.6998            | -2.4152             | 10000                |
| Throughput | 50          | -6.3141                               | -23.6226           | -4.5355             | 10000                |
| Throughput | 100         | -5.8574                               | -18.1687           | -4.5537             | 10000                |

## order_in_block

| outcome    | raw_spearman_rho | raw_spearman_p | adjusted_order_coefficient_model_scale | std_error_HC3 | adjusted_ci95_low_model_scale | adjusted_ci95_high_model_scale | adjusted_t | adjusted_p | interpreted_effect | interpreted_ci95_low | interpreted_ci95_high | interpreted_scale            |
| ---------- | ---------------- | -------------- | -------------------------------------- | ------------- | ----------------------------- | ------------------------------ | ---------- | ---------- | ------------------ | -------------------- | --------------------- | ---------------------------- |
| AvgRT      | 0.01240          | 0.94813        | 0.00083                                | 0.00071       | -0.00065                      | 0.00231                        | 1.15754    | 0.25893    | 0.08275            | -0.06508             | 0.23079               | % per one position later     |
| P95        | 0.06778          | 0.72194        | 0.00821                                | 0.00548       | -0.00311                      | 0.01954                        | 1.49986    | 0.14725    | 0.82475            | -0.31100             | 1.97343               | % per one position later     |
| Throughput | 0.08456          | 0.65684        | -5.02212                               | 4.39755       | -14.11914                     | 4.07490                        | -1.14203   | 0.26519    | -5.02212           | -14.11914            | 4.07490               | req/s per one position later |

## Leave-one-out robustness

| outcome    | component           | full_estimate_model_scale | loo_min_estimate | loo_max_estimate | sign_reversals | full_p    | loo_min_p | loo_max_p | significant_loo_models_of_30 | significance_flips |
| ---------- | ------------------- | ------------------------- | ---------------- | ---------------- | -------------- | --------- | --------- | --------- | ---------------------------- | ------------------ |
| AvgRT      | marginal strategy   | 0.022266                  | 0.021256         | 0.023167         | 0.000000       | 8.747e-11 | 9.562e-12 | 1.223e-09 | 30                           | 0                  |
| AvgRT      | strategy at c25     | 0.022872                  | 0.019844         | 0.025577         | 0.000000       | 9.997e-05 | 3.108e-06 | 0.000692  | 30                           | 0                  |
| AvgRT      | strategy at c50     | 0.021866                  | 0.021031         | 0.023744         | 0.000000       | 4.859e-09 | 2.715e-14 | 3.871e-07 | 30                           | 0                  |
| AvgRT      | strategy at c100    | 0.022059                  | 0.020469         | 0.023598         | 0.000000       | 2.102e-08 | 1.078e-10 | 5.886e-07 | 30                           | 0                  |
| AvgRT      | omnibus interaction | NA                        | NA               | NA               | NA             | 0.983418  | 0.731760  | 0.997585  | 0                            | 0                  |
| P95        | marginal strategy   | 0.037667                  | 0.033741         | 0.045520         | 0.000000       | 0.024486  | 0.001929  | 0.064491  | 27                           | 3                  |
| P95        | strategy at c25     | 0.047113                  | 0.035335         | 0.070670         | 0.000000       | 0.269078  | 0.038854  | 0.462390  | 1                            | 1                  |
| P95        | strategy at c50     | 0.041396                  | 0.034496         | 0.051745         | 0.000000       | 0.038407  | 0.016079  | 0.147217  | 27                           | 3                  |
| P95        | strategy at c100    | 0.024493                  | 0.020411         | 0.030616         | 0.000000       | 0.038407  | 0.016079  | 0.147217  | 27                           | 3                  |
| P95        | omnibus interaction | NA                        | NA               | NA               | NA             | 0.682981  | 0.360403  | 0.847483  | 0                            | 0                  |
| Throughput | marginal strategy   | -140.497867               | -145.943450      | -134.363150      | 0.000000       | 6.021e-11 | 7.452e-12 | 7.630e-10 | 30                           | 0                  |
| Throughput | strategy at c25     | -136.313400               | -152.650150      | -117.909250      | 0.000000       | 0.000120  | 3.771e-06 | 0.000799  | 30                           | 0                  |
| Throughput | strategy at c50     | -138.710200               | -150.546150      | -133.385300      | 0.000000       | 4.275e-09 | 1.955e-14 | 3.498e-07 | 30                           | 0                  |
| Throughput | strategy at c100    | -146.470000               | -156.711650      | -136.195850      | 0.000000       | 1.694e-08 | 8.282e-11 | 4.378e-07 | 30                           | 0                  |
| Throughput | omnibus interaction | NA                        | NA               | NA               | NA             | 0.931936  | 0.592102  | 0.992419  | 0                            | 0                  |

## Figures

- `group_results.png`: the 30 run-level observations, cell means, and 95% t intervals with df=4.
- `model_diagnostics.png`: residual-versus-fitted and Q-Q plots for the three main models.

## Method and limitations

- Each cell contains only 5 runs. The power of the Levene and Shapiro-Wilk tests is limited; failing to reject an assumption does not establish that it holds.
- P95 values are integers because they are aggregated from request-level quantiles, and the two read-through cells at concurrency 50 and 100 have zero within-cell SD. Their linear-model inference should be treated as approximate; interpret direction, intervals and the leave-one-out results rather than point significance.
- HC3 handles heteroskedasticity of general form, but N=30 remains small. Effect-size bootstrap confidence intervals may be wide or unstable when each cell has only n=5.
- The data come from a single application instance, a single dataset size and one continuous experimental session. Conclusions are limited to the current implementation and environment.
- The raw correlation of `order_in_block` is confounded with strategy and concurrency; the HC3 order coefficient that controls the full factorial structure is the appropriate summary.
