import streamlit as st

st.set_page_config(page_title="Shariah Screening Prototype", layout="wide")

# =========================
# FIXED BENCHMARKS
# =========================
TIER1_BENCHMARK = 5.0     # %
TIER2_THRESHOLD = 33.0   # %

def safe_percent(n, d):
    if d is None or d == 0:
        return None
    return (n / d) * 100

def within_exceeds(value, threshold):
    if value is None:
        return "Not computed"
    return "Within threshold" if value <= threshold else "Exceeds threshold"

# =========================
# APP HEADER
# =========================
st.title("SHARIAH-COMPLIANT SECURITIES SCREENING")
st.caption(
    "Two-stage quantitative screening using Business Activity Benchmark (5%) "
    "and Financial Ratio Benchmark (33%)."
)

# =========================
# TIER 1 — BUSINESS ACTIVITY BENCHMARK
# =========================
st.subheader("Business Activity Benchmark")
st.write("User enters figures based on audited financial statements.")

# -------------------------------------------------
# STEP 1: Shariah non-compliant business activities
# -------------------------------------------------
st.markdown("#### Shariah non-compliant business activities")
st.write("Multiple select Shariah non-compliant business activity and enter amount.")

activities = [
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

selected_items = st.multiselect(
    "Select applicable activities",
    options=activities
)

item_amounts = {}
if selected_items:
    st.markdown("#### Insert amounts (RM) for selected activities")
    for item in selected_items:
        item_amounts[item] = st.number_input(
            f"Amount (RM) — {item}",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
            key=f"amt_{item}"
        )
else:
    st.info("Select one or more activities to enter amounts.")

total_non_compliant = sum(item_amounts.values()) if item_amounts else 0.0

st.divider()

# -------------------------------------------------
# STEP 2: Group Financial Information — NBA Income
# -------------------------------------------------
st.markdown("#### Group Financial Information")
st.write("Total Income = Revenue + Other Income + Share of Profit")

c1, c2, c3 = st.columns(3)
with c1:
    revenue = st.number_input(
        "Revenue (RM)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%.2f"
    )
with c2:
    other_income = st.number_input(
        "Other Income (RM)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%.2f"
    )
with c3:
    share_of_profit = st.number_input(
        "Share of Profit (RM)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%.2f"
    )

total_income_nba = revenue + other_income + share_of_profit
st.metric("Total Income (RM)", f"{total_income_nba:,.2f}")

st.divider()

# -------------------------------------------------
# STEP 3: Tier 1 Computation (UPDATED LAYOUT)
# -------------------------------------------------
st.markdown("### Computation Business Activity Benchmark")

r1, r2, r3 = st.columns(3)

with r1:
    st.metric("Total non-compliant amount (RM)", f"{total_non_compliant:,.2f}")

with r2:
    if total_income_nba <= 0:
        contribution_income = None
        tier1_status = "FAIL"
        st.metric("Contribution vs Total Income (%)", "—")
    else:
        contribution_income = safe_percent(total_non_compliant, total_income_nba)
        st.metric(
            "Contribution vs Total Income (%)",
            f"{contribution_income:.3f}%"
        )
        tier1_status = "PASS" if contribution_income <= TIER1_BENCHMARK else "FAIL"

with r3:
    st.metric("Benchmark", f"{TIER1_BENCHMARK:.1f}%")

if total_income_nba <= 0:
    st.error(
        "Tier 1 Status: FAIL — Total Income (NBA) must be positive. "
        "Tier 2 is locked."
    )
elif tier1_status == "PASS":
    st.success("Tier 1 Status: PASS — You may proceed to Tier 2.")
else:
    st.error("Tier 1 Status: FAIL — Tier 2 is locked.")

st.caption(
    "Note: Total Income is computed from Revenue + Other Income + Share of Profit."
)

# =========================
# TIER 2 — FINANCIAL RATIO BENCHMARK
# =========================
if tier1_status == "PASS":
    st.divider()
    st.subheader("Financial Ratio Benchmark")
    st.write(
        "Measure riba or riba based elements in a company's statements "
        "of financial position."
    )

    left, right = st.columns(2, gap="large")

    with left:
        cash_conventional = st.number_input(
            "Cash in conventional account(s) (RM)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.2f"
        )
        interest_bearing_debt = st.number_input(
            "Total interest-bearing debt (RM)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.2f"
        )
        total_assets = st.number_input(
            "Total Assets (RM)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.2f"
        )

    cash_ratio = safe_percent(cash_conventional, total_assets)
    debt_ratio = safe_percent(interest_bearing_debt, total_assets)

    with right:
        st.markdown("### Computation Financial Ratio Benchmark")
        st.metric("Threshold", f"{TIER2_THRESHOLD:.1f}%")

        # Cash Ratio
        if cash_ratio is None:
            st.metric("Cash Ratio (%)", "—")
            cash_status = "Not computed"
        else:
            st.metric("Cash Ratio (%)", f"{cash_ratio:.3f}%")
            cash_status = within_exceeds(cash_ratio, TIER2_THRESHOLD)
        st.write("Cash Ratio Status:", cash_status)

        st.write("")

        # Debt Ratio
        if debt_ratio is None:
            st.metric("Debt Ratio (%)", "—")
            debt_status = "Not computed"
        else:
            st.metric("Debt Ratio (%)", f"{debt_ratio:.3f}%")
            debt_status = within_exceeds(debt_ratio, TIER2_THRESHOLD)
        st.write("Debt Ratio Status:", debt_status)

        st.divider()

        # Overall Tier 2 decision
        if cash_ratio is None or debt_ratio is None:
            st.warning(
                "Tier 2 Status: NOT READY — Please ensure Total Assets > 0 "
                "and complete inputs."
            )
        else:
            tier2_status = (
                "PASS"
                if cash_ratio <= TIER2_THRESHOLD and debt_ratio <= TIER2_THRESHOLD
                else "FAIL"
            )
            if tier2_status == "PASS":
                st.success(
                    "Tier 2 Status: PASS — Both ratios are within the threshold."
                )
            else:
                st.error(
                    "Tier 2 Status: FAIL — One or both ratios exceed the threshold."
                )
