import streamlit as st

st.set_page_config(page_title="Shariah Screening Prototype", layout="wide")

st.title("2-Tier Quantitative Screening Prototype (Rule-Based)")
st.caption("Tier 1 is a PASS/FAIL gate based on Contribution vs PBT (≤ 5%). Tier 2 appears only if Tier 1 = PASS.")

# -------------------------
# Sidebar settings
# -------------------------
st.sidebar.header("Settings")
tier1_benchmark = st.sidebar.number_input(
    "Tier 1 benchmark (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1
)
tier2_threshold = st.sidebar.number_input(
    "Tier 2 threshold (%)", min_value=0.0, max_value=100.0, value=33.0, step=0.1
)

def safe_percent(n, d):
    if d is None or d == 0:
        return None
    return (n / d) * 100

# =========================
# TIER 1
# =========================
st.subheader("Non-permissible activities contribution (Benchmark reference)")
st.write("User enters figures based on audited financial statements.")

# -------------------------------------------------
# STEP 1: LIST OF NON-PERMISSIBLE ACTIVITIES (TOP)
# -------------------------------------------------
st.markdown("#### List of Non-Permissible Activities (Multi-select)")

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

selected_items = st.multiselect("Select applicable activities", options=master_list, default=[])

item_amounts = {}
if selected_items:
    st.markdown("#### Insert amounts (RM) for selected activities")
    for item in selected_items:
        item_amounts[item] = st.number_input(
            f"Amount (RM) — {item}",
            min_value=0.0, value=0.0, step=100.0, format="%.2f"
        )
else:
    st.info("Select one or more activities to enter amounts.")

total_non_perm = sum(item_amounts.values()) if item_amounts else 0.0

st.divider()

# -------------------------------------------------
# STEP 2: GROUP FINANCIAL INPUTS (MOVED BELOW)
# -------------------------------------------------
st.markdown("#### Group Financial Information")

c1, c2 = st.columns(2, gap="large")
with c1:
    group_total_income = st.number_input(
        "Group Total Income (RM)",
        min_value=0.0, value=0.0, step=1000.0, format="%.2f"
    )
with c2:
    group_pbt = st.number_input(
        "Group Profit Before Tax (PBT) (RM)",
        value=0.0, step=1000.0, format="%.2f"
    )

st.divider()

# -------------------------------------------------
# STEP 3: TIER 1 OUTPUT (PBT ONLY)
# -------------------------------------------------
st.markdown("### Tier 1 Output (PBT-based only)")

o1, o2, o3 = st.columns(3)
with o1:
    st.metric("Total Non-permissible (RM)", f"{total_non_perm:,.2f}")
with o2:
    st.metric("Benchmark", f"{tier1_benchmark:.1f}%")
with o3:
    if group_pbt <= 0:
        contribution_pbt = None
        tier1_status = "FAIL"
        st.metric("Contribution vs PBT (%)", "—")
    else:
        contribution_pbt = safe_percent(total_non_perm, group_pbt)
        st.metric("Contribution vs PBT (%)", f"{contribution_pbt:.3f}%")
        tier1_status = "PASS" if contribution_pbt <= tier1_benchmark else "FAIL"

if group_pbt <= 0:
    st.error("Tier 1 Status: FAIL — PBT must be positive to evaluate Tier 1. Tier 2 is locked.")
elif tier1_status == "PASS":
    st.success("Tier 1 Status: PASS — You may proceed to Tier 2.")
else:
    st.error("Tier 1 Status: FAIL — Tier 2 is locked.")

st.caption("Note: Group Total Income is retained as Tier 1 reference input, but Tier 1 decision is based on PBT only.")

# =========================
# TIER 2 (ONLY IF TIER 1 PASS)
# =========================
if tier1_status == "PASS":
    st.divider()
    st.subheader("Tier 2 — Measuring riba-based elements through financial ratios (<33%)")

    colA, colB = st.columns(2, gap="large")

    with colA:
        cash_conventional = st.number_input(
            "Cash in conventional account(s) (RM)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f"
        )
        interest_bearing_debt = st.number_input(
            "Total interest-bearing debt (RM)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f"
        )
        total_assets = st.number_input(
            "Total Assets (RM)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f"
        )

    cash_ratio = safe_percent(cash_conventional, total_assets)
    debt_ratio = safe_percent(interest_bearing_debt, total_assets)

    with colB:
        st.markdown("### Tier 2 Output")
        st.metric("Tier 2 Threshold", f"{tier2_threshold:.1f}%")

        if cash_ratio is not None:
            st.metric("Cash / Total Assets (%)", f"{cash_ratio:.3f}%")
        else:
            st.metric("Cash / Total Assets (%)", "—")

        if debt_ratio is not None:
            st.metric("Debt / Total Assets (%)", f"{debt_ratio:.3f}%")
        else:
            st.metric("Debt / Total Assets (%)", "—")

        st.divider()

        if cash_ratio is None or debt_ratio is None:
            st.warning("Tier 2 Status: NOT READY — Complete all inputs.")
        else:
            tier2_status = "PASS" if (cash_ratio <= tier2_threshold and debt_ratio <= tier2_threshold) else "FAIL"
            if tier2_status == "PASS":
                st.success("Tier 2 Status: PASS — Both ratios are within 33% threshold.")
            else:
                st.error("Tier 2 Status: FAIL — One or both ratios exceed the 33% threshold.")

        st.caption("Tier 2 decision is based on BOTH ratios meeting the <33% threshold (rule-based).")
