import streamlit as st

st.set_page_config(page_title="2-Tier Shariah Screening Prototype", layout="wide")

st.title("2-Tier Quantitative Screening Prototype (Rule-Based)")
st.caption("Tier 1: Contribution vs PBT (≤ 5%) → PASS/FAIL gate. Tier 2 appears ONLY if Tier 1 = PASS.")

# -------------------------
# Sidebar settings
# -------------------------
st.sidebar.header("Settings")
tier1_benchmark = st.sidebar.number_input(
    "Tier 1 benchmark (%)",
    min_value=0.0, max_value=100.0,
    value=5.0, step=0.1
)
tier2_threshold = st.sidebar.number_input(
    "Tier 2 threshold (%)",
    min_value=0.0, max_value=100.0,
    value=33.0, step=0.1
)

# -------------------------
# Tier 1 Inputs
# -------------------------
st.subheader("Tier 1 — Non-permissible contribution (Based on Group Profit Before Tax)")

t1_left, t1_right = st.columns([1, 1], gap="large")

with t1_left:
    group_pbt = st.number_input(
        "Group Profit Before Tax (PBT) (RM)",
        value=0.0, step=1000.0, format="%.2f"
    )

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

    item_amounts = {}
    if selected_items:
        for item in selected_items:
            item_amounts[item] = st.number_input(
                f"Amount (RM) — {item}",
                min_value=0.0, value=0.0, step=100.0, format="%.2f"
            )
    else:
        st.info("Select one or more activities to enter amounts.")

    total_non_perm = sum(item_amounts.values()) if item_amounts else 0.0

with t1_right:
    st.markdown("### Tier 1 Calculation Output")

    st.metric("Total Non-permissible (RM)", f"{total_non_perm:,.2f}")
    st.metric("Tier 1 Benchmark", f"{tier1_benchmark:.1f}%")

    # Contribution vs PBT ONLY
    if group_pbt <= 0:
        contribution_pbt = None
        tier1_status = "FAIL"
        st.error("PBT is ≤ 0, so Tier 1 cannot be evaluated. Please enter a valid (positive) PBT.")
        st.metric("Contribution vs PBT (%)", "—")
    else:
        contribution_pbt = (total_non_perm / group_pbt) * 100
        st.metric("Contribution vs PBT (%)", f"{contribution_pbt:.3f}%")

        if contribution_pbt <= tier1_benchmark:
            tier1_status = "PASS"
            st.success("Tier 1 Status: PASS (You may proceed to Tier 2)")
        else:
            tier1_status = "FAIL"
            st.error("Tier 1 Status: FAIL (Tier 2 is not available)")

    st.caption("Tier 2 will only appear when Tier 1 = PASS.")

# -------------------------
# Tier 2 (ONLY if Tier 1 PASS)
# -------------------------
if tier1_status == "PASS":
    st.divider()
    st.subheader("Tier 2 — Riba-based ratios (Threshold reference)")

    colA, colB = st.columns([1, 1], gap="large")

    with colA:
        cash_conventional = st.number_input(
            "Cash in conventional accounts (RM)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f"
        )
        interest_bearing_debt = st.number_input(
            "Interest-bearing debt (RM)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f"
        )
        total_assets = st.number_input(
            "Total Assets (RM)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f"
        )

    with colB:
        st.markdown("### Tier 2 Output")

        def safe_percent(n, d):
            if d is None or d == 0:
                return None
            return (n / d) * 100

        cash_ratio = safe_percent(cash_conventional, total_assets)
        debt_ratio = safe_percent(interest_bearing_debt, total_assets)

        st.metric("Tier 2 Threshold", f"{tier2_threshold:.1f}%")

        if cash_ratio is None:
            st.metric("Cash / Total Assets (%)", "—")
            st.warning("Cannot compute Cash Ratio (Total Assets = 0).")
        else:
            st.metric("Cash / Total Assets (%)", f"{cash_ratio:.3f}%")
            st.write(
                "**Label:**",
                "Within threshold" if cash_ratio <= tier2_threshold else "Exceeds threshold"
            )

        if debt_ratio is None:
            st.metric("Debt / Total Assets (%)", "—")
            st.warning("Cannot compute Debt Ratio (Total Assets = 0).")
        else:
            st.metric("Debt / Total Assets (%)", f"{debt_ratio:.3f}%")
            st.write(
                "**Label:**",
                "Within threshold" if debt_ratio <= tier2_threshold else "Exceeds threshold"
            )

        st.caption("Tier 2 labels are indicative measures of riba-related exposure (rule-based).")
