import streamlit as st

st.set_page_config(page_title="2-Tier Shariah Screening Prototype", layout="wide")

st.title("2-Tier Quantitative Screening Prototype (Rule-Based)")
st.caption("Tier 1: Non-permissible contribution (benchmark 5%).  Tier 2: Riba ratios (threshold 33%). Soft labels only.")

# -------------------------
# Helpers
# -------------------------
def safe_percent(numerator: float, denominator: float):
    if denominator is None or denominator == 0:
        return None
    return (numerator / denominator) * 100

def soft_label(value, threshold, below_text, above_text):
    if value is None:
        return "Not computed (invalid denominator)"
    return below_text if value <= threshold else above_text

def rm(x):
    try:
        return float(x)
    except:
        return 0.0

# -------------------------
# Sidebar settings
# -------------------------
st.sidebar.header("Prototype Settings")
tier1_benchmark = st.sidebar.number_input("Tier 1 benchmark (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
tier2_threshold = st.sidebar.number_input("Tier 2 threshold (%)", min_value=0.0, max_value=100.0, value=33.0, step=0.1)

st.sidebar.divider()
st.sidebar.markdown("**Soft label mode:** No PASS/FAIL. Only threshold comparisons.")

# -------------------------
# Layout
# -------------------------
col1, col2 = st.columns([1, 1], gap="large")

# =========================================================
# TIER 1
# =========================================================
with col1:
    st.subheader("Tier 1 — Non-permissible activities contribution (Benchmark reference)")
    st.markdown("User enters figures based on audited financial statements.")

    t1_a, t1_b = st.columns(2)
    with t1_a:
        group_total_income = st.number_input("Group Total Income (RM)", min_value=0.0, value=0.0, step=1000.0, format="%.2f")
    with t1_b:
        group_pbt = st.number_input("Group Profit Before Tax (PBT) (RM)", value=0.0, step=1000.0, format="%.2f")

    st.markdown("### Select non-permissible items (multi-select) and enter amounts")
    master_list = [
        "Conventional banking & lending",
        "Conventional insurance",
        "Gambling",
        "Liquor-related activities",
        "Pork-related activities",
        "Non-halal F&B / no halal certification",
        "Tobacco / cigarette / vape-related",
        "Interest income / interest-related charges",
        "Dividends from non-Shariah investments",
        "Non-Shariah entertainment",
        "Share trading",
        "Stockbroking business",
        "Cinema",
        "Rental from non-compliant activities",
        "Others (as determined by SAC)"
    ]

    selected_items = st.multiselect("Non-permissible activities", options=master_list, default=[])

    # amounts for selected items
    item_amounts = {}
    if selected_items:
        for item in selected_items:
            item_amounts[item] = st.number_input(f"Amount (RM) — {item}", min_value=0.0, value=0.0, step=100.0, format="%.2f")
    else:
        st.info("Select one or more activities to enter amounts, or leave empty.")

    total_non_perm = sum(item_amounts.values()) if item_amounts else 0.0

    st.divider()
    st.markdown("### Tier 1 Computation (soft labels)")
    c_income = safe_percent(total_non_perm, group_total_income)
    # For PBT: if <= 0, not applicable
    c_pbt = None if group_pbt <= 0 else safe_percent(total_non_perm, group_pbt)

    label_income = soft_label(
        c_income, tier1_benchmark,
        f"Below {tier1_benchmark:.1f}% benchmark",
        f"Above {tier1_benchmark:.1f}% benchmark"
    )

    label_pbt = "Not applicable (PBT ≤ 0)" if group_pbt <= 0 else soft_label(
        c_pbt, tier1_benchmark,
        f"Below {tier1_benchmark:.1f}% benchmark",
        f"Above {tier1_benchmark:.1f}% benchmark"
    )

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Non-permissible (RM)", f"{total_non_perm:,.2f}")
    k2.metric("Contribution vs Income (%)", "-" if c_income is None else f"{c_income:.3f}%")
    k3.metric("Tier 1 Benchmark", f"{tier1_benchmark:.1f}%")

    st.write("**Label (vs Income):**", label_income)
    st.write("**Contribution vs PBT (%):**", "—" if c_pbt is None else f"{c_pbt:.3f}%")
    st.write("**Label (vs PBT):**", label_pbt)

    st.caption("Note: Tier 1 labels are indicative only and do not constitute a Shariah compliance decision.")

# =========================================================
# TIER 2
# =========================================================
with col2:
    st.subheader("Tier 2 — Riba-based ratios (Threshold reference)")
    st.markdown("Measures exposure using cash/debt ratios relative to total assets.")

    t2_a, t2_b = st.columns(2)
    with t2_a:
        cash_conventional = st.number_input("Cash in conventional accounts (RM)", min_value=0.0, value=0.0, step=1000.0, format="%.2f")
    with t2_b:
        interest_bearing_debt = st.number_input("Interest-bearing debt (RM)", min_value=0.0, value=0.0, step=1000.0, format="%.2f")

    total_assets = st.number_input("Total Assets (RM)", min_value=0.0, value=0.0, step=1000.0, format="%.2f")

    st.divider()
    st.markdown("### Tier 2 Computation (soft labels)")
    cash_ratio = safe_percent(cash_conventional, total_assets)
    debt_ratio = safe_percent(interest_bearing_debt, total_assets)

    label_cash = soft_label(
        cash_ratio, tier2_threshold,
        f"Within {tier2_threshold:.1f}% threshold",
        f"Exceeds {tier2_threshold:.1f}% threshold"
    )
    label_debt = soft_label(
        debt_ratio, tier2_threshold,
        f"Within {tier2_threshold:.1f}% threshold",
        f"Exceeds {tier2_threshold:.1f}% threshold"
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Cash Ratio (%)", "-" if cash_ratio is None else f"{cash_ratio:.3f}%")
    m2.metric("Debt Ratio (%)", "-" if debt_ratio is None else f"{debt_ratio:.3f}%")
    m3.metric("Tier 2 Threshold", f"{tier2_threshold:.1f}%")

    st.write("**Label (Cash Ratio):**", label_cash)
    st.write("**Label (Debt Ratio):**", label_debt)

    st.caption("Note: Tier 2 labels are indicative measures of riba-related exposure and are not final compliance decisions.")

st.divider()
st.subheader("Tester Notes")
st.markdown(
    """
- This is a **rule-based prototype** (no AI).  
- Users input figures based on financial reports; the system computes **Tier 1 (5%)** and **Tier 2 (33%)** outputs with **soft labels**.
- You can change benchmark/threshold in the sidebar.
"""
)
