
import json
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="YottaFlex | Quality Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "yottaflex_synthetic.db"


# =========================================================
# CUSTOM UI STYLING
# =========================================================

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263247;
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    /* Headings */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    p, label, .stMarkdown {
        color: #cbd5e1;
    }

    /* KPI cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #172338, #111c2e);
        border: 1px solid #263a56;
        border-radius: 14px;
        padding: 18px 20px;
        min-height: 115px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 14px;
    }

    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 28px;
        font-weight: 700;
    }

    /* Sidebar radio navigation */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: #172338;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 5px;
    }

    /* Inputs */
    [data-baseweb="select"] > div {
        background: #172338;
        border-color: #334155;
    }

    [data-testid="stTextInput"] input {
        background: #172338;
        color: #f8fafc;
    }

    /* Buttons */
    .stButton button,
    .stDownloadButton button {
        background: #0284c7;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        background: #0369a1;
        color: white;
        border: none;
    }

    /* Tables and chart containers */
    [data-testid="stDataFrame"],
    [data-testid="stPlotlyChart"] {
        background: #111c2e;
        border: 1px solid #263247;
        border-radius: 12px;
        padding: 8px;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #111c2e;
        border: 1px solid #263247;
        border-radius: 10px;
    }

    /* Dividers */
    hr {
        border-color: #263247;
    }

    /* Captions */
    [data-testid="stCaptionContainer"] {
        color: #94a3b8;
    }

    /* Info messages */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* App header */
    .brand-header {
        background: linear-gradient(120deg, #172338, #102a43);
        border: 1px solid #263a56;
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 24px;
    }

    .brand-title {
        color: #f8fafc;
        font-size: 30px;
        font-weight: 800;
        margin: 0;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }

    .section-caption {
        color: #94a3b8;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE CONNECTION
# READ-ONLY: DOES NOT MODIFY THE DATABASE
# =========================================================

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()


def get_connection():
    return sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True,
    )


@st.cache_data(ttl=60)
def load_data(query):
    connection = get_connection()
    try:
        return pd.read_sql_query(query, connection)
    finally:
        connection.close()


def load_parameterized_data(query, params):
    connection = get_connection()
    try:
        return pd.read_sql_query(
            query,
            connection,
            params=params,
        )
    finally:
        connection.close()


def show_metric(label, value):
    st.metric(label, f"{int(value):,}")


def style_chart(fig, height=350):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111c2e",
        plot_bgcolor="#111c2e",
        font=dict(
            color="#cbd5e1",
            family="Arial",
        ),
        title_font=dict(
            size=17,
            color="#f8fafc",
        ),
        height=height,
        margin=dict(l=20, r=20, t=55, b=25),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    fig.update_xaxes(
        gridcolor="#263247",
        zerolinecolor="#263247",
    )

    fig.update_yaxes(
        gridcolor="#263247",
        zerolinecolor="#263247",
    )

    return fig


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## 🏭 YottaFlex")
    st.caption("MANUFACTURING INTELLIGENCE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard Overview",
            "Quality Analytics",
            "Defect Traceability",
            "CAPA Management",
            "Anomaly Monitoring",
        ],
    )

    st.divider()

    st.markdown("**System Information**")
    st.caption("Database: SQLite")
    st.caption("Dataset: Synthetic")
    st.caption("Access: Read-only")
    st.caption("Version: 1.0.0")


# =========================================================
# APPLICATION HEADER
# =========================================================

st.markdown("""
<div class="brand-header">
    <div class="brand-title">🏭 YottaFlex</div>
    <div class="brand-subtitle">
        Manufacturing Quality & Defect Traceability System
        &nbsp; | &nbsp; Production Intelligence
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# DASHBOARD OVERVIEW
# =========================================================

if page == "Dashboard Overview":

    st.header("Dashboard Overview")
    st.caption("Monitor manufacturing operations and quality performance.")

    metrics_query = """
    SELECT
        (SELECT COUNT(*) FROM products) AS products,
        (SELECT COUNT(*) FROM suppliers) AS suppliers,
        (SELECT COUNT(*) FROM material_lots) AS material_lots,
        (SELECT COUNT(*) FROM production_orders) AS production_orders,
        (SELECT COUNT(*) FROM inspection_results) AS inspections,
        (SELECT COUNT(*) FROM defects) AS defects,
        (SELECT COUNT(*) FROM corrective_actions) AS capas,
        (SELECT COUNT(*) FROM machines) AS machines
    """

    metrics = load_data(metrics_query).iloc[0]

    row1 = st.columns(4)

    metric_items_1 = [
        ("Products", "products"),
        ("Suppliers", "suppliers"),
        ("Material Lots", "material_lots"),
        ("Production Orders", "production_orders"),
    ]

    for column, (label, key) in zip(row1, metric_items_1):
        with column:
            show_metric(label, metrics[key])

    row2 = st.columns(4)

    metric_items_2 = [
        ("Inspection Results", "inspections"),
        ("Defects", "defects"),
        ("Corrective Actions", "capas"),
        ("Machines", "machines"),
    ]

    for column, (label, key) in zip(row2, metric_items_2):
        with column:
            show_metric(label, metrics[key])

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Defects by Severity")

        severity_data = load_data("""
            SELECT severity, COUNT(*) AS total
            FROM defects
            GROUP BY severity
            ORDER BY total DESC
        """)

        if not severity_data.empty:
            fig = px.pie(
                severity_data,
                names="severity",
                values="total",
                hole=0.5,
                title="Defect Severity Distribution",
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True,
            )

    with right:
        st.subheader("CAPA Lifecycle")

        capa_data = load_data("""
            SELECT lifecycle_status, COUNT(*) AS total
            FROM corrective_actions
            GROUP BY lifecycle_status
            ORDER BY total DESC
        """)

        if not capa_data.empty:
            fig = px.bar(
                capa_data,
                x="lifecycle_status",
                y="total",
                title="Corrective Actions by Status",
                labels={
                    "lifecycle_status": "CAPA Status",
                    "total": "Number of CAPAs",
                },
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True,
            )

    st.divider()

    st.subheader("Recent Production Orders")

    recent_orders = load_data("""
        SELECT
            po.order_id,
            p.product_name,
            po.planned_quantity,
            po.actual_quantity,
            po.priority,
            po.lifecycle_status,
            po.start_date
        FROM production_orders po
        JOIN products p ON p.product_id = po.product_id
        ORDER BY po.start_date DESC
        LIMIT 10
    """)

    st.dataframe(
        recent_orders,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# QUALITY ANALYTICS
# =========================================================

elif page == "Quality Analytics":

    st.header("Quality Analytics")
    st.caption("Analyze inspection performance and manufacturing defects.")

    quality = load_data("""
        SELECT
            COUNT(*) AS total_inspections,
            COALESCE(SUM(inspected_quantity), 0) AS inspected,
            COALESCE(SUM(passed_quantity), 0) AS passed,
            COALESCE(SUM(failed_quantity), 0) AS failed
        FROM inspection_results
    """).iloc[0]

    total_inspected = int(quality["inspected"])
    total_passed = int(quality["passed"])
    total_failed = int(quality["failed"])

    first, second, third = st.columns(3)

    with first:
        show_metric(
            "Total Inspections",
            quality["total_inspections"],
        )

    with second:
        show_metric("Units Passed", total_passed)

    with third:
        show_metric("Units Failed", total_failed)

    st.divider()

    if total_inspected > 0:

        pass_rate = total_passed / total_inspected * 100
        fail_rate = total_failed / total_inspected * 100

        st.subheader("Quality Performance Rates")

        a, b = st.columns(2)

        with a:
            st.metric("Pass Rate", f"{pass_rate:.2f}%")

        with b:
            st.metric("Failure Rate", f"{fail_rate:.2f}%")

        rate_data = pd.DataFrame({
            "Result": ["Passed", "Failed"],
            "Units": [total_passed, total_failed],
        })

        rate_fig = px.pie(
            rate_data,
            names="Result",
            values="Units",
            hole=0.55,
            title="Passed vs Failed Units",
        )

        st.plotly_chart(
            style_chart(rate_fig),
            use_container_width=True,
        )

    st.divider()

    st.subheader("Defects by Category")

    category_data = load_data("""
        SELECT defect_category, COUNT(*) AS total
        FROM defects
        GROUP BY defect_category
        ORDER BY total DESC
    """)

    if not category_data.empty:

        fig = px.bar(
            category_data,
            x="defect_category",
            y="total",
            title="Defect Category Analysis",
            labels={
                "defect_category": "Defect Category",
                "total": "Number of Defects",
            },
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    st.divider()

    st.subheader("Inspection Results Over Time")

    timeline = load_data("""
        SELECT
            DATE(inspection_date) AS inspection_day,
            COUNT(*) AS inspections,
            SUM(failed_quantity) AS failed_units
        FROM inspection_results
        GROUP BY DATE(inspection_date)
        ORDER BY inspection_day
    """)

    if not timeline.empty:

        fig = px.line(
            timeline,
            x="inspection_day",
            y=["inspections", "failed_units"],
            markers=True,
            title="Inspection and Failure Trends",
            labels={
                "inspection_day": "Date",
                "value": "Count",
                "variable": "Metric",
            },
        )

        st.plotly_chart(
            style_chart(fig, height=400),
            use_container_width=True,
        )


# =========================================================
# DEFECT TRACEABILITY
# =========================================================

elif page == "Defect Traceability":

    st.header("Defect Traceability")

    st.caption(
        "Trace a defect through inspection, production, machine, "
        "material lot, supplier and corrective action."
    )

    defects = load_data("""
        SELECT defect_id
        FROM defects
        ORDER BY defect_id
    """)

    if defects.empty:

        st.info("No defects are available.")

    else:

        selected_defect = st.selectbox(
            "Search or select a Defect ID",
            defects["defect_id"].tolist(),
        )

        trace_query = """
            SELECT
                d.defect_id,
                d.defect_category,
                d.defect_description,
                d.defect_quantity,
                d.severity,
                d.defect_status,
                d.detected_at,

                ir.inspection_id,
                ir.inspection_date,
                ir.inspected_quantity,
                ir.failed_quantity,

                po.order_id,
                po.lifecycle_status AS order_status,
                po.planned_quantity,

                p.product_id,
                p.product_name,

                m.machine_id,
                m.machine_name,

                COALESCE(
                    ml.lot_id,
                    (
                        SELECT GROUP_CONCAT(DISTINCT mc.lot_id)
                        FROM material_consumptions mc
                        WHERE mc.order_id = po.order_id
                    )
                ) AS material_lots,

                COALESCE(
                    s.supplier_name,
                    (
                        SELECT GROUP_CONCAT(DISTINCT sp.supplier_name)
                        FROM material_consumptions mc
                        JOIN material_lots lot
                            ON lot.lot_id = mc.lot_id
                        JOIN suppliers sp
                            ON sp.supplier_id = lot.supplier_id
                        WHERE mc.order_id = po.order_id
                    )
                ) AS suppliers,

                ca.capa_id,
                ca.root_cause,
                ca.corrective_action,
                ca.lifecycle_status AS capa_status,
                ca.verification_result

            FROM defects d

            JOIN inspection_results ir
                ON ir.inspection_id = d.inspection_id

            JOIN production_orders po
                ON po.order_id = d.order_id

            JOIN products p
                ON p.product_id = po.product_id

            LEFT JOIN order_machine_executions ome
                ON ome.execution_id = d.execution_id

            LEFT JOIN machines m
                ON m.machine_id = ome.machine_id

            LEFT JOIN material_lots ml
                ON ml.lot_id = d.lot_id

            LEFT JOIN suppliers s
                ON s.supplier_id = ml.supplier_id

            LEFT JOIN corrective_actions ca
                ON ca.defect_id = d.defect_id

            WHERE d.defect_id = ?
        """

        trace = load_parameterized_data(
            trace_query,
            (selected_defect,),
        )

        if not trace.empty:

            record = trace.iloc[0]

            st.subheader("Defect Information")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Defect ID", record["defect_id"])

            with c2:
                st.metric("Severity", record["severity"])

            with c3:
                st.metric("Defect Quantity", int(record["defect_quantity"]))

            st.write("**Category:**", record["defect_category"])
            st.write("**Description:**", record["defect_description"])
            st.write("**Status:**", record["defect_status"])

            st.divider()

            st.subheader("End-to-End Traceability Chain")

            trace_steps = [
                ("1. Inspection", record["inspection_id"]),
                ("2. Production Order", record["order_id"]),
                (
                    "3. Product",
                    f"{record['product_id']} — {record['product_name']}",
                ),
                ("4. Machine", record["machine_name"]),
                ("5. Material Lot(s)", record["material_lots"]),
                ("6. Supplier(s)", record["suppliers"]),
                ("7. Corrective Action", record["capa_id"]),
            ]

            for label, value in trace_steps:

                if pd.isna(value) or value is None:
                    display_value = "Not linked"
                else:
                    display_value = value

                st.markdown(
                    f"""
                    <div style="
                        background:#172338;
                        border:1px solid #263a56;
                        border-radius:9px;
                        padding:12px 16px;
                        margin-bottom:8px;
                    ">
                        <span style="color:#38bdf8;font-weight:700;">
                            {label}
                        </span>
                        <br>
                        <span style="color:#e5e7eb;">
                            {display_value}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.divider()

            st.subheader("Corrective Action Details")

            left, right = st.columns(2)

            with left:
                st.write("**Root Cause**")
                st.write(record["root_cause"])

                st.write("**Corrective Action**")
                st.write(record["corrective_action"])

            with right:
                st.write("**CAPA Status**")
                st.write(record["capa_status"])

                st.write("**Verification Result**")
                st.write(record["verification_result"])

            with st.expander("View Complete Traceability Record"):

                st.dataframe(
                    trace,
                    use_container_width=True,
                    hide_index=True,
                )


# =========================================================
# CAPA MANAGEMENT
# =========================================================

elif page == "CAPA Management":

    st.header("CAPA Management")

    st.caption(
        "Monitor corrective and preventive actions, ownership and lifecycle."
    )

    capa_summary = load_data("""
        SELECT lifecycle_status, COUNT(*) AS total
        FROM corrective_actions
        GROUP BY lifecycle_status
        ORDER BY total DESC
    """)

    if not capa_summary.empty:

        st.subheader("CAPA Status Summary")

        st.dataframe(
            capa_summary,
            use_container_width=True,
            hide_index=True,
        )

        fig = px.bar(
            capa_summary,
            x="lifecycle_status",
            y="total",
            title="Corrective Action Lifecycle",
            labels={
                "lifecycle_status": "CAPA Status",
                "total": "Number of CAPAs",
            },
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    st.divider()

    capa_records = load_data("""
        SELECT
            ca.capa_id,
            ca.defect_id,
            d.defect_category,
            ca.root_cause,
            ca.assigned_to,
            ca.opened_at,
            ca.due_date,
            ca.verified_at,
            ca.closed_at,
            ca.verification_result,
            ca.lifecycle_status
        FROM corrective_actions ca
        JOIN defects d
            ON d.defect_id = ca.defect_id
        ORDER BY ca.opened_at DESC
    """)

    st.subheader("CAPA Records")

    if not capa_records.empty:

        status_options = ["All"] + sorted(
            capa_records["lifecycle_status"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_status = st.selectbox(
            "Filter by CAPA Status",
            status_options,
        )

        filtered_records = capa_records.copy()

        if selected_status != "All":
            filtered_records = filtered_records[
                filtered_records["lifecycle_status"] == selected_status
            ]

        st.caption(f"Showing {len(filtered_records):,} CAPA records")

        st.dataframe(
            filtered_records,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇ Download CAPA Records as CSV",
            filtered_records.to_csv(index=False).encode("utf-8"),
            file_name="yottaflex_capa_records.csv",
            mime="text/csv",
        )

    else:
        st.info("No CAPA records found.")


# =========================================================
# ANOMALY MONITORING
# =========================================================

elif page == "Anomaly Monitoring":

    st.header("Anomaly Monitoring")

    st.caption(
        "Review synthetic ground-truth anomaly scenarios "
        "used to test data quality and traceability."
    )

    st.info(
        "These examples are maintained separately from the "
        "operational database. They are test scenarios, not "
        "a live production anomaly feed."
    )

    anomaly_file = (
        BASE_DIR
        / "data"
        / "ground_truth"
        / "anomaly_cases.json"
    )

    if anomaly_file.exists():

        try:

            with open(
                anomaly_file,
                "r",
                encoding="utf-8",
            ) as file:

                anomaly_data = json.load(file)

            if isinstance(anomaly_data, list):

                st.metric(
                    "Ground-Truth Anomaly Cases",
                    len(anomaly_data),
                )

                st.dataframe(
                    pd.json_normalize(anomaly_data),
                    use_container_width=True,
                    hide_index=True,
                )

            else:
                st.json(anomaly_data)

        except (json.JSONDecodeError, OSError) as error:

            st.error(
                f"Could not read anomaly file: {error}"
            )

    else:

        st.warning(
            f"Ground-truth file not found: {anomaly_file}"
        )

    st.divider()

    st.subheader("Anomaly Scenarios")

    anomaly_types = [
        "Nonexistent material lot",
        "BOM material not consumed",
        "CAPA closed before verification",
        "Defect quantity exceeds inspected quantity",
        "Broken traceability chain",
    ]

    for number, anomaly in enumerate(
        anomaly_types,
        start=1,
    ):

        st.markdown(
            f"""
            <div style="
                background:#172338;
                border:1px solid #263a56;
                border-radius:9px;
                padding:13px 16px;
                margin-bottom:9px;
            ">
                <span style="color:#38bdf8;font-weight:700;">
                    TEST CASE {number:02d}
                </span>
                <br>
                <span style="color:#e5e7eb;">
                    {anomaly}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

footer_left, footer_right = st.columns(2)

with footer_left:
    st.caption(
        "YottaFlex | Manufacturing Quality Intelligence"
    )

with footer_right:
    st.caption(
        "Synthetic dataset | SQLite | Read-only dashboard"
    )
