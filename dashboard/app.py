"""Chronic or episodic? — corridor compliance dashboard (BDA25707).

Reads only the anonymised CSVs in dashboard/data/ (the folder §15–§16 of the
notebook exports). No place names, coordinates or chainage are held here.
Run from the repository root:  streamlit run dashboard/app.py
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# data folder sits next to this file, so the app runs from any working directory
DATA_DIR = Path(os.environ.get("DASH_DATA", Path(__file__).resolve().parent / "data"))
FOOTER = "Site codes only. No place names, coordinates or chainage are held in this app or in the folder it reads."
DOMS = ["surface_water", "noise", "air", "ground_water"]
DOM_COL = {"surface_water": "#1f77b4", "air": "#ff7f0e", "ground_water": "#2ca02c", "noise": "#d62728"}
REG_COL = {"chronic": "#c0392b", "episodic": "#e67e22", "compliant": "#27ae60"}
C_F1, C_REC = "#C9A227", "#2F6B4F"
TEMPLATE = "simple_white"

st.set_page_config(page_title="Chronic or episodic?", layout="wide")

# --- lightweight styling to match the polished dashboard look ---
st.markdown("""
<style>
  .block-container { padding-top: 1.4rem; max-width: 1250px; }
  /* dark header band */
  .cc-header { background:#12232B; border-radius:10px; padding:20px 26px; margin-bottom:14px; }
  .cc-header h1 { color:#fff; font-size:26px; font-weight:700; margin:0; letter-spacing:-.3px; }
  .cc-header p  { color:#9FB3BC; font-size:13.5px; margin:6px 0 0 0; }
  /* KPI cards */
  .cc-card { background:#fff; border:1px solid #E3E9EC; border-radius:12px;
             padding:16px 20px; box-shadow:0 1px 3px rgba(20,40,50,.05); height:100%; }
  .cc-num  { font-size:30px; font-weight:800; line-height:1.05; }
  .cc-lab  { color:#5A6B73; font-size:12.5px; margin-top:2px; }
  .cc-pill { display:inline-block; font-size:10.5px; font-weight:700; letter-spacing:.4px;
             padding:2px 9px; border-radius:20px; margin-top:9px; }
  .cc-insight { background:#FBF3E4; border-left:4px solid #C97E1E; border-radius:8px;
                padding:13px 18px; font-size:13.5px; color:#3B4A57; margin-top:6px; }
  .cc-insight b { color:#12232B; }
  .cc-sub { color:#12232B; font-weight:700; font-size:16px; margin:6px 0 0 0; }
  .cc-subcap { color:#7E8C97; font-size:12px; margin:0 0 4px 0; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load(name: str, **kw) -> pd.DataFrame | None:
    p = DATA_DIR / name
    if not p.exists():
        return None
    try:
        return pd.read_csv(p, **kw)
    except Exception:
        return None


def need(df, name, tab):
    if df is None:
        tab.warning(f"`{name}` not found in `{DATA_DIR}/` — re-run §15–§16 of the notebook and copy the export here.")
        return True
    return False


def hbar(df, x, y, color=None, color_map=None, fmt=None, **kw):
    fig = px.bar(df, x=x, y=y, color=color, orientation="h",
                 color_discrete_map=color_map, template=TEMPLATE, **kw)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), legend_title=None)
    if fmt:
        fig.update_xaxes(tickformat=fmt)
    return fig


st.markdown(f"""
<div class="cc-header">
  <h1>Corridor Environmental Compliance — Monitoring Triage Dashboard</h1>
  <p>Anonymised 172 km linear-infrastructure corridor · Oct 2020 – Nov 2023 · 4 domains · 38 sites · 2,777 readings · BDA25707</p>
</div>
""", unsafe_allow_html=True)
if (DATA_DIR / "_SAMPLE_DATA.txt").exists():
    st.warning("**Sample data loaded.** Metric files carry the frozen-run values; site-level and "
               "time-series files are synthetic placeholders. Replace the folder with the real "
               "notebook export and delete `_SAMPLE_DATA.txt`.")

tabs = st.tabs(["Overview", "Validation", "Models", "Class balance", "RQ1 zones",
                "RQ2 clusters", "RQ3 typology", "Triage", "Priority", "Over time"])
(t_over, t_val, t_mod, t_bal, t_rq1, t_rq2, t_rq3, t_tri, t_pri, t_time) = tabs

# ---------------------------------------------------------------- Overview
with t_over:
    exc = load("exceedance_by_site_domain.csv")
    reg = load("parameter_regimes.csv")
    if not need(exc, "exceedance_by_site_domain.csv", t_over):
        n_sites = exc.site_id.nunique()
        n_read = int(exc.n.sum())
        rate = float(np.average(exc.exc_rate, weights=exc.n))
        # Canonical headline exceedance is 704/3,497 (readings matched to a standard).
        # The site-level file covers a slightly different population, so quote the
        # canonical figure on the card to match its caption and the report/slides.
        canonical_rate = 704 / 3497   # = 0.201
        n_dom = exc.domain.nunique()

        # --- four styled KPI cards ---
        cards = [
            (f"{n_read:,}", "#12232B", "Readings w/ standard & typology", "analysis base", "#E8EEF0", "#12232B"),
            (f"{canonical_rate:.1%}", "#B23A2E", "Overall exceedance (704 / 3,497)", "non-compliant", "#F7E4E1", "#B23A2E"),
            (f"{n_sites}", "#12232B", "Monitoring sites, 4 zones", "typology-linked", "#E8EEF0", "#17708C"),
            ("0.925", "#17708C", "Surface-water holdout recall", "primary", "#E4F0E9", "#2E7D4F"),
        ]
        cols = st.columns(4)
        for c, (num, ncol, lab, pill, pbg, pcol) in zip(cols, cards):
            c.markdown(f"""<div class="cc-card">
              <div class="cc-num" style="color:{ncol}">{num}</div>
              <div class="cc-lab">{lab}</div>
              <span class="cc-pill" style="background:{pbg};color:{pcol}">{pill}</span>
            </div>""", unsafe_allow_html=True)

        st.write("")
        left, right = st.columns(2)

        # --- LEFT: exceedance rate by parameter (bar) ---
        with left:
            st.markdown('<p class="cc-sub">Exceedance rate by parameter</p>'
                        '<p class="cc-subcap">Non-compliance concentrates in a handful of parameters</p>',
                        unsafe_allow_html=True)
            if reg is not None:
                r = reg.sort_values("exc_rate", ascending=True).copy()
                r["pct"] = r.exc_rate * 100
                fig = px.bar(r, x="pct", y="label", orientation="h", color="regime",
                             color_discrete_map=REG_COL, template=TEMPLATE,
                             labels={"pct": "exceedance rate (%)", "label": ""})
                fig.update_layout(height=430, showlegend=False,
                                  margin=dict(l=10, r=10, t=6, b=10))
                st.plotly_chart(fig, width="stretch")

        # --- RIGHT: readings by domain (donut) ---
        with right:
            st.markdown('<p class="cc-sub">Readings by domain</p>'
                        '<p class="cc-subcap">The four domains are markedly unequal — drives the tiering</p>',
                        unsafe_allow_html=True)
            dom_n = exc.groupby("domain").n.sum().reindex(
                ["surface_water", "air", "ground_water", "noise"]).fillna(0)
            labels = ["Surface water", "Air", "Groundwater", "Noise"]
            palette = ["#17708C", "#6E5BA6", "#B07C2B", "#3C7A5E"]
            donut = go.Figure(go.Pie(
                labels=labels, values=dom_n.values, hole=0.62,
                marker=dict(colors=palette, line=dict(color="#fff", width=2)),
                textinfo="label+value", textposition="inside",
                insidetextorientation="radial", sort=False))
            donut.update_layout(height=430, showlegend=False,
                                margin=dict(l=10, r=10, t=6, b=10),
                                annotations=[dict(text=f"{n_read:,}<br>readings",
                                                  x=0.5, y=0.5, font_size=15,
                                                  font_color="#12232B", showarrow=False)])
            st.plotly_chart(donut, width="stretch")

        # --- corrected headline insight banner ---
        st.markdown("""<div class="cc-insight">
          <b>Headline insight.</b> Within riverine zones, 81.5% of exceedances come from chronic
          parameters, while only 17.0% of riverine monitoring observations target them. Across zones,
          39–56% of effort is spent on compliant-regime parameters. See the Triage tab.
          <i>(Shares are computed within each zone, not as a zone's slice of the corridor total.)</i>
        </div>""", unsafe_allow_html=True)
    st.caption(FOOTER)

# ---------------------------------------------------------------- Validation
with t_val:
    st.subheader("Leakage audit")
    st.caption("The old pipeline averaged the current month into its own predictor, so it partly saw "
               "the answer. Positive inflation is what the old code over-reported.")
    audit = load("leakage_audit.csv")
    if not need(audit, "leakage_audit.csv", t_val):
        a = audit.copy()
        a["tag"] = np.where(a.features.str.contains("leak"), "leaky (old pipeline)", "fixed (this study)")
        st.plotly_chart(hbar(a, "cv_f1", "domain", color="tag",
                             color_map={"leaky (old pipeline)": "#b23b3b", "fixed (this study)": "#2F6B4F"},
                             barmode="group", labels={"cv_f1": "cross-validated F1"}),
                        width="stretch")
        piv = a.pivot_table(index="domain", columns="tag", values="cv_f1")
        infl = float((piv["leaky (old pipeline)"] - piv["fixed (this study)"]).mean())
        st.metric("Mean F1 inflation removed", f"+{infl:.3f}")
    st.subheader("Baselines — the honest ceiling")
    st.caption("If parameter identity alone scores nearly as well as the full model, history and "
               "position are not doing the work.")
    base = load("baselines.csv")
    if not need(base, "baselines.csv", t_val):
        order_b = ["parameter_code only", "no value features", "full (fixed)"]
        b = base[base.baseline.isin(order_b)].copy()
        b["baseline"] = pd.Categorical(b.baseline, order_b)
        st.plotly_chart(hbar(b.sort_values("baseline"), "cv_f1", "domain", color="baseline",
                             color_map={"parameter_code only": "#9aa0a6",
                                        "no value features": "#C9A227", "full (fixed)": "#2F6B4F"},
                             barmode="group", labels={"cv_f1": "cross-validated F1"}),
                        width="stretch")
    st.caption(FOOTER)

# ---------------------------------------------------------------- Models
with t_mod:
    st.subheader("Model comparison")
    mc = load("model_comparison.csv")
    if not need(mc, "model_comparison.csv", t_mod):
        fig = px.bar(mc, x="model", y="cv_f1", error_y="cv_f1_std", facet_col="domain",
                     color="model", template=TEMPLATE, labels={"cv_f1": "CV F1"},
                     category_orders={"domain": sorted(mc.domain.unique())})
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
        fig.for_each_annotation(lambda x: x.update(text=x.text.split("=")[-1]))
        fig.update_xaxes(tickangle=45, title=None)
        st.plotly_chart(fig, width="stretch")
        st.caption("Error bars are ±1 SD across outer folds. Wide bars mean the fold-to-fold "
                   "variance is large relative to the score itself.")
        st.subheader("Cross-validated vs single holdout window")
        win = mc.dropna(subset=["holdout_f1"])
        if len(win):
            rows = [{"domain": r.domain, "measure": m, "F1": v}
                    for r in win.itertuples()
                    for m, v in [("CV F1 (mean of folds)", r.cv_f1), ("holdout F1", r.holdout_f1)]]
            st.plotly_chart(px.bar(pd.DataFrame(rows), x="domain", y="F1", color="measure",
                                   barmode="group", template=TEMPLATE,
                                   color_discrete_sequence=[C_F1, C_REC])
                            .update_layout(legend_title=None, margin=dict(l=10, r=10, t=30, b=10)),
                            width="stretch")
            st.caption("Opposite directions on the same split: a single holdout window is not a "
                       "verdict. Preliminary domains (no post-cutoff rows) have no holdout bar.")
        st.dataframe(mc, width="stretch", hide_index=True)
    st.caption(FOOTER)

# ---------------------------------------------------------------- Class balance
with t_bal:
    st.subheader("Class balance — SMOTE inside training folds only")
    sm = load("smote_sensitivity.csv")
    if not need(sm, "smote_sensitivity.csv", t_bal):
        s = sm.copy()
        s["row"] = s.domain.str.replace("_", " ") + " · " + s.model
        long = s.melt(id_vars="row", value_vars=[c for c in ["d_f1", "d_recall"] if c in s.columns],
                      var_name="Δ", value_name="change")
        long["Δ"] = long["Δ"].map({"d_f1": "Δ F1", "d_recall": "Δ recall"})
        fig = px.bar(long, x="change", y="row", color="Δ", orientation="h", barmode="group",
                     template=TEMPLATE, color_discrete_map={"Δ F1": C_F1, "Δ recall": C_REC},
                     labels={"change": "change vs class weighting", "row": ""})
        fig.add_vline(x=0, line_color="#444")
        fig.update_layout(height=560, legend_title=None, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, width="stretch")
        st.caption("Negative F1 with positive recall means SMOTE buys recall by spending precision.")
    st.caption(FOOTER)

# ---------------------------------------------------------------- RQ1 zones
with t_rq1:
    st.subheader("RQ1 — zone differences, compared within each domain")
    st.caption("Averaging zones across domains mixes air with water. Every comparison here stays "
               "inside one domain.")
    exc = load("exceedance_by_site_domain.csv")
    if not need(exc, "exceedance_by_site_domain.csv", t_rq1):
        g = (exc.dropna(subset=["zone_type"])
                .groupby(["domain", "zone_type"])
                .apply(lambda x: pd.Series({"exc_rate": np.average(x.exc_rate, weights=x.n),
                                            "sites": x.site_id.nunique(), "readings": int(x.n.sum())}),
                       include_groups=False)
                .reset_index())
        fig = px.bar(g, x="exc_rate", y="zone_type", facet_row="domain", orientation="h",
                     color="domain", color_discrete_map=DOM_COL, template=TEMPLATE,
                     labels={"exc_rate": "exceedance rate", "zone_type": ""})
        fig.update_layout(height=640, showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
        fig.update_xaxes(tickformat=".0%")
        fig.for_each_annotation(lambda x: x.update(text=x.text.split("=")[-1]))
        st.plotly_chart(fig, width="stretch")
        st.caption("Read the sites and readings columns before any zone claim. Where a zone rests on "
                   "one site or a handful of readings, the number is descriptive only.")
        st.dataframe(g.assign(exc_rate=(g.exc_rate * 100).round(1)), width="stretch",
                     hide_index=True)
    st.caption(FOOTER)

# ---------------------------------------------------------------- RQ2 clusters
with t_rq2:
    st.subheader("RQ2 — do behaviour clusters recover geography?")
    sc = load("site_clusters.csv")
    if not need(sc, "site_clusters.csv", t_rq2):
        if {"pc1", "pc2"}.issubset(sc.columns):
            fig = px.scatter(sc, x="pc1", y="pc2", color=sc.cluster.astype(str),
                             symbol="zone_type", template=TEMPLATE,
                             labels={"pc1": "PC1", "pc2": "PC2", "color": "cluster"})
            fig.update_traces(marker=dict(size=13, line=dict(width=1, color="black")))
            fig.update_layout(legend_title=None, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, width="stretch")
        st.markdown("**Cluster × zone**")
        st.dataframe(pd.crosstab(sc.cluster, sc.zone_type), width="stretch")
        st.caption("If clusters tracked geography, this table would be near-diagonal. Judge it by "
                   "eye, then quote the ARI from the notebook rather than reading the table as evidence.")
        exc_cols = [c for c in sc.columns if c.startswith("exc_")]
        if exc_cols:
            with st.expander("Cluster signatures"):
                st.dataframe(sc.groupby("cluster")[exc_cols].mean().round(3),
                             width="stretch")
    st.caption(FOOTER)

# ---------------------------------------------------------------- RQ3 typology
with t_rq3:
    st.subheader("RQ3 — does typology add anything?")
    st.caption("A = no spatial · B = chainage only · C = chainage + typology · D = typology only. "
               "D−A asks whether typology carries signal at all; C−B asks whether it adds anything "
               "beyond position.")
    ab = load("ablation_rq3.csv")
    if not need(ab, "ablation_rq3.csv", t_rq3):
        cfg = {"recall_A_no_spatial": "A_no_spatial", "recall_B_chainage_only": "B_chainage_only",
               "recall_C_chainage_typo": "C_chainage_typo", "recall_D_typology_only": "D_typology_only"}
        cols = [c for c in cfg if c in ab.columns]
        long = ab.melt(id_vars="domain", value_vars=cols, var_name="config", value_name="recall")
        long["config"] = long.config.map(cfg)
        fig = px.bar(long, x="recall", y="config", facet_row="domain", orientation="h",
                     color="domain", color_discrete_map=DOM_COL, template=TEMPLATE,
                     category_orders={"config": list(cfg.values())[::-1]})
        fig.update_layout(height=680, showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
        fig.for_each_annotation(lambda x: x.update(text=x.text.split("=")[-1]))
        st.plotly_chart(fig, width="stretch")
        c1, c2 = st.columns(2)
        if "D_minus_A" in ab.columns:
            c1.metric("Mean D − A", f"{ab.D_minus_A.mean():+.3f}")
        if "C_minus_B" in ab.columns:
            c2.metric("Mean C − B", f"{ab.C_minus_B.mean():+.3f}")
        st.caption("State the null against the positive control from the notebook: the same design "
                   "detects a planted zone effect on synthetic data. That is what makes this result "
                   "informative rather than a failed test.")
    st.caption(FOOTER)

# ---------------------------------------------------------------- Triage
with t_tri:
    st.subheader("Parameter triage — chronic, episodic, compliant")
    reg = load("parameter_regimes.csv")
    if not need(reg, "parameter_regimes.csv", t_tri):
        regimes = st.multiselect("Regimes", sorted(reg.regime.unique()),
                                 default=sorted(reg.regime.unique()))
        r = reg[reg.regime.isin(regimes)]
        fig = px.scatter(r, x="exc_rate", y="persistence", color="regime", size="n",
                         text="label", color_discrete_map=REG_COL, template=TEMPLATE,
                         labels={"exc_rate": "exceedance rate (chronicity)",
                                 "persistence": "persistence  P(exc | prev exc) − P(exc | prev ok)"})
        fig.update_traces(textposition="top center", textfont_size=10,
                          marker=dict(line=dict(width=1, color="black")))
        fig.update_xaxes(tickformat=".0%")
        fig.update_layout(height=520, legend_title=None, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, width="stretch")
        st.caption("Chronic parameters call for intervention, not prediction. Episodic parameters "
                   "are where a forecast earns its keep. Compliant parameters are where monitoring "
                   "effort can be reduced.")
    st.subheader("Zone × regime")
    eff, bur, mis = (load(f"zone_regime_{n}.csv", index_col=0) for n in
                     ("effort", "burden", "misalignment"))
    if eff is not None and bur is not None and mis is not None:
        c1, c2, c3 = st.columns(3)
        c1.markdown("**Monitoring effort share**"); c1.dataframe(eff, width="stretch")
        c2.markdown("**Exceedance burden share**"); c2.dataframe(bur, width="stretch")
        c3.markdown("**Misalignment (effort − burden)**"); c3.dataframe(mis, width="stretch")
        st.caption("Positive misalignment = effort spent where exceedance is absent or already "
                   "certain; negative = burden under-monitored.")
    else:
        st.warning(f"`zone_regime_*.csv` not all found in `{DATA_DIR}/`.")
    st.caption(FOOTER)

# ---------------------------------------------------------------- Priority
with t_pri:
    st.subheader("Monitoring priority")
    st.caption("Priority is risk only. The coverage and frequency gaps (Pillars 2 and 3) are still "
               "empty, so this is not yet the composite score.")
    pri = load("site_priority.csv")
    if not need(pri, "site_priority.csv", t_pri):
        top = st.slider("Show top sites", 5, len(pri), min(20, len(pri)))
        p = pri.sort_values("priority", ascending=False).head(top)
        fig = hbar(p.sort_values("priority"), "priority", "site_id",
                   color="zone_type" if "zone_type" in p.columns else None,
                   labels={"priority": "priority (mean predicted risk)", "site_id": ""})
        fig.update_layout(height=max(360, 24 * top))
        st.plotly_chart(fig, width="stretch")
    st.caption(FOOTER)

# ---------------------------------------------------------------- Over time
with t_time:
    st.subheader("Over time — observed and predicted")
    act, prd = load("timeseries_actual.csv"), load("timeseries_predicted.csv")
    if not need(act, "timeseries_actual.csv", t_time):
        dom = st.selectbox("Domain", sorted(act.domain.unique()))
        zsel = st.multiselect("Zones", sorted(act.zone_type.dropna().unique()),
                              default=sorted(act.zone_type.dropna().unique()))
        a = act[(act.domain == dom) & act.zone_type.isin(zsel)].sort_values("month")
        fig = px.line(a, x="month", y="exc_rate", color="zone_type", markers=True,
                      template=TEMPLATE, labels={"exc_rate": "observed exceedance rate"})
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(legend_title=None, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, width="stretch")
        st.caption("Gaps in the line are months with no readings, not months with no exceedances.")
        if prd is not None:
            st.markdown("**Predicted risk**")
            p = prd[(prd.domain == dom) & prd.zone_type.isin(zsel)].sort_values("month")
            fig2 = px.line(p, x="month", y="pred_risk", color="zone_type", markers=True,
                           template=TEMPLATE, labels={"pred_risk": "mean predicted probability"})
            fig2.update_layout(legend_title=None, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig2, width="stretch")
    st.caption(FOOTER)
