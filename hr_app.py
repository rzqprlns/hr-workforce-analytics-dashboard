import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Workforce Intelligence Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp { background:#F7F8FA; color:#18202B; }
.block-container {
    max-width:1280px; padding-top:5.8rem; padding-bottom:4rem;
    padding-left:2rem; padding-right:2rem;
}
[data-testid="stSidebar"] { background:#F0F3F7; border-right:1px solid #D8DDE5; }
.eyebrow {
    font-family:monospace; text-transform:uppercase; letter-spacing:.12em;
    font-size:.76rem; color:#5A57D6; margin-bottom:.7rem;
}
.hero {
    font-size:clamp(3.3rem,7vw,6rem); line-height:.94; font-weight:800;
    letter-spacing:-.055em; color:#18202B; margin-bottom:1.2rem;
}
.hero-copy { max-width:820px; font-size:1.05rem; line-height:1.7; color:#68717E; }
.section-label {
    font-family:monospace; text-transform:uppercase; letter-spacing:.1em;
    font-size:.74rem; color:#5A57D6; margin-top:2.8rem; margin-bottom:.45rem;
}
.section-title {
    font-size:clamp(1.9rem,4vw,2.55rem); line-height:1.08; font-weight:760;
    letter-spacing:-.035em; margin-bottom:1rem;
}
.kpi {
    background:white; border:1px solid #D9DEE6; padding:1rem;
    min-height:118px;
}
.kpi-label {
    font-family:monospace; text-transform:uppercase; letter-spacing:.07em;
    font-size:.67rem; color:#747C88; margin-bottom:.65rem;
}
.kpi-value { font-size:1.72rem; font-weight:800; letter-spacing:-.04em; }
.kpi-note { font-size:.77rem; color:#8A929D; margin-top:.35rem; }
.note {
    background:#E8F3EE; border:1px solid #B8D8C7; padding:1.1rem 1.2rem;
    line-height:1.6; margin:1rem 0 2rem 0;
}
.insight {
    background:#FFF1D2; border:1px solid #DFC574; padding:1.1rem 1.2rem;
    line-height:1.6; margin:1.2rem 0;
}
.method {
    background:white; border:1px solid #D9DEE6; padding:1.15rem; min-height:175px;
}
@media(max-width:768px){
    .block-container{padding-top:5.6rem!important;padding-left:1rem!important;padding-right:1rem!important;}
    .hero{font-size:3.15rem!important;line-height:.98!important;}
    .section-title{font-size:2rem!important;}
    .kpi{min-height:auto;}
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    emp = pd.read_csv("hr_workforce_employee_master.csv")
    rec = pd.read_csv("hr_recruitment_funnel.csv")
    att = pd.read_csv("hr_monthly_attendance.csv")

    emp["hire_date"] = pd.to_datetime(emp["hire_date"])
    emp["exit_date"] = pd.to_datetime(emp["exit_date"], errors="coerce")
    rec["month"] = pd.to_datetime(rec["month"])
    att["month"] = pd.to_datetime(att["month"])

    emp["tenure_days"] = (
        emp["exit_date"].fillna(pd.Timestamp("2025-12-31")) - emp["hire_date"]
    ).dt.days.clip(lower=0)
    emp["tenure_years"] = emp["tenure_days"] / 365.25
    emp["attrition_flag"] = (emp["employment_status"] == "Exited").astype(int)
    return emp, rec, att

emp, rec, att = load_data()

with st.sidebar:
    st.markdown("## Workforce Filters")
    depts = st.multiselect(
        "Department", sorted(emp["department"].unique()),
        default=sorted(emp["department"].unique())
    )
    locs = st.multiselect(
        "Location", sorted(emp["location"].unique()),
        default=sorted(emp["location"].unique())
    )
    levels = st.multiselect(
        "Job Level", sorted(emp["job_level"].unique()),
        default=sorted(emp["job_level"].unique())
    )
    etypes = st.multiselect(
        "Employment Type", sorted(emp["employment_type"].unique()),
        default=sorted(emp["employment_type"].unique())
    )
    st.markdown("---")
    st.caption("Synthetic workforce data created for portfolio demonstration.")

f = emp[
    emp["department"].isin(depts)
    & emp["location"].isin(locs)
    & emp["job_level"].isin(levels)
    & emp["employment_type"].isin(etypes)
].copy()

selected_ids = set(f["employee_id"])
att_f = att[att["employee_id"].isin(selected_ids)].copy()
rec_f = rec[rec["department"].isin(depts)].copy()

st.markdown("""
<div class="eyebrow">Rizqi / People Analytics Lab</div>
<div class="hero">Hiring is rising.<br>Why is turnover still high?</div>
<div class="hero-copy">
An interactive workforce analytics case study connecting headcount, attrition,
recruitment, attendance, engagement and employee characteristics to investigate
whether workforce growth is translating into stronger retention.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="note"><b>Portfolio case study.</b><br><br>
All employee IDs, salaries, hiring outcomes, attendance records and workforce
characteristics shown here are fully synthetic.
</div>
""", unsafe_allow_html=True)

# KPI
active = (f["employment_status"] == "Active").sum()
exited = (f["employment_status"] == "Exited").sum()
total = len(f)
attrition = exited / total if total else 0
avg_eng = f["engagement_score"].mean() if total else 0
avg_tth = f["time_to_hire_days"].mean() if total else 0
avg_abs = att_f["absence_days"].mean() if len(att_f) else 0

st.markdown('<div class="section-label">01 / Workforce Overview</div><div class="section-title">People metrics at a glance</div>', unsafe_allow_html=True)

cols = st.columns(6)
cards = [
    ("Active Employees", f"{active:,}", "current synthetic workforce"),
    ("Exited Employees", f"{exited:,}", "employees who left"),
    ("Attrition Rate", f"{attrition*100:.1f}%", "exits / employee records"),
    ("Engagement", f"{avg_eng:.1f}/5", "average score"),
    ("Time to Hire", f"{avg_tth:.0f} days", "average recruitment speed"),
    ("Absence", f"{avg_abs:.1f} days", "monthly average"),
]
for c, (lab,val,note) in zip(cols,cards):
    with c:
        st.markdown(f'<div class="kpi"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

# Hiring vs exits
st.markdown('<div class="section-label">02 / Workforce Movement</div><div class="section-title">Are we hiring faster than we are losing people?</div>', unsafe_allow_html=True)

hires = f.groupby(f["hire_date"].dt.to_period("M")).size().rename("Hires")
exits = f.dropna(subset=["exit_date"]).groupby(f.dropna(subset=["exit_date"])["exit_date"].dt.to_period("M")).size().rename("Exits")
movement = pd.concat([hires, exits], axis=1).fillna(0).reset_index()
movement["month"] = movement["index"].dt.to_timestamp()
movement = movement.drop(columns=["index"]).melt(id_vars="month", var_name="Movement", value_name="Employees")

fig = px.line(movement, x="month", y="Employees", color="Movement", markers=True, title="Monthly Hires vs Exits")
fig.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=55,b=20))
st.plotly_chart(fig, use_container_width=True)

# Attrition department
st.markdown('<div class="section-label">03 / Attrition</div><div class="section-title">Where is retention pressure concentrated?</div>', unsafe_allow_html=True)

dept = f.groupby("department").agg(
    employees=("employee_id","count"),
    exits=("attrition_flag","sum"),
    engagement=("engagement_score","mean"),
    overtime=("monthly_overtime_hours","mean")
).reset_index()
dept["attrition_rate"] = np.where(dept["employees"]>0, dept["exits"]/dept["employees"],0)

a1,a2=st.columns(2)
with a1:
    fig=px.bar(dept.sort_values("attrition_rate"),x="attrition_rate",y="department",orientation="h",text="attrition_rate",title="Attrition Rate by Department",labels={"attrition_rate":"Attrition Rate","department":""})
    fig.update_traces(texttemplate="%{text:.1%}",textposition="outside")
    fig.update_xaxes(tickformat=".0%")
    fig.update_layout(height=440,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=30,t=55,b=20))
    st.plotly_chart(fig,use_container_width=True)
with a2:
    fig=px.scatter(dept,x="overtime",y="attrition_rate",size="employees",color="department",hover_data={"engagement":":.2f"},title="Overtime vs Attrition",labels={"overtime":"Avg Monthly Overtime Hours","attrition_rate":"Attrition Rate","department":"Department","employees":"Employees","engagement":"Engagement"})
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(height=440,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=55,b=20))
    st.plotly_chart(fig,use_container_width=True)

# Risk factors
st.markdown('<div class="section-label">04 / Retention Diagnostic</div><div class="section-title">Which employee conditions are associated with exits?</div>', unsafe_allow_html=True)

r1,r2=st.columns(2)
with r1:
    type_sum=f.groupby("employment_type").agg(employees=("employee_id","count"),exits=("attrition_flag","sum")).reset_index()
    type_sum["attrition_rate"]=type_sum["exits"]/type_sum["employees"]
    fig=px.bar(type_sum,x="employment_type",y="attrition_rate",text="attrition_rate",title="Attrition by Employment Type",labels={"employment_type":"","attrition_rate":"Attrition Rate"})
    fig.update_traces(texttemplate="%{text:.1%}",textposition="outside")
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(height=390,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)
with r2:
    fig=px.scatter(f,x="monthly_overtime_hours",y="engagement_score",color="employment_status",hover_data=["department","commute_km"],title="Overtime, Engagement & Employment Status",labels={"monthly_overtime_hours":"Monthly Overtime Hours","engagement_score":"Engagement Score","employment_status":"Status"})
    fig.update_layout(height=390,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)

# Recruitment funnel
st.markdown('<div class="section-label">05 / Recruitment Funnel</div><div class="section-title">Where does candidate conversion narrow?</div>', unsafe_allow_html=True)

if len(rec_f):
    funnel_values = {
        "Applicants": rec_f["applicants"].sum(),
        "Interviews": rec_f["interviews"].sum(),
        "Offers": rec_f["offers"].sum(),
        "Hires": rec_f["hires"].sum(),
    }
    funnel_df=pd.DataFrame({"Stage":list(funnel_values.keys()),"Candidates":list(funnel_values.values())})
    fig=px.funnel(funnel_df,x="Candidates",y="Stage",title="Recruitment Conversion Funnel")
    fig.update_layout(height=430,paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=55,b=20))
    st.plotly_chart(fig,use_container_width=True)

# Hiring source
st.markdown('<div class="section-label">06 / Hiring Source</div><div class="section-title">Which sources combine speed and retention?</div>', unsafe_allow_html=True)

source=f.groupby("hiring_source").agg(
    employees=("employee_id","count"),
    avg_tth=("time_to_hire_days","mean"),
    exits=("attrition_flag","sum"),
    engagement=("engagement_score","mean")
).reset_index()
source["attrition_rate"]=source["exits"]/source["employees"]

fig=px.scatter(source,x="avg_tth",y="attrition_rate",size="employees",color="hiring_source",hover_data={"engagement":":.2f"},title="Time to Hire vs Attrition by Hiring Source",labels={"avg_tth":"Average Time to Hire (Days)","attrition_rate":"Attrition Rate","hiring_source":"Hiring Source","employees":"Employees","engagement":"Engagement"})
fig.update_yaxes(tickformat=".0%")
fig.update_layout(height=460,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig,use_container_width=True)

# Attendance
st.markdown('<div class="section-label">07 / Attendance</div><div class="section-title">How does attendance vary across teams?</div>', unsafe_allow_html=True)

if len(att_f):
    att_dept=att_f.groupby("department").agg(absence_days=("absence_days","mean"),late_days=("late_days","mean")).reset_index()
    att_long=att_dept.melt(id_vars="department",var_name="Metric",value_name="Days")
    fig=px.bar(att_long,x="department",y="Days",color="Metric",barmode="group",title="Average Monthly Absence & Late Days",labels={"department":"","Metric":""})
    fig.update_layout(height=430,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)

# Exit reasons
st.markdown('<div class="section-label">08 / Exit Reasons</div><div class="section-title">Why are employees leaving?</div>', unsafe_allow_html=True)

exit_reason=f[f["employment_status"]=="Exited"]["exit_reason"].value_counts().reset_index()
exit_reason.columns=["Exit Reason","Employees"]
if len(exit_reason):
    fig=px.bar(exit_reason.sort_values("Employees"),x="Employees",y="Exit Reason",orientation="h",text="Employees",title="Recorded Exit Reasons")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=420,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=30,t=55,b=20))
    st.plotly_chart(fig,use_container_width=True)

# Employee explorer
st.markdown('<div class="section-label">09 / Employee Explorer</div><div class="section-title">Inspect the workforce records</div>', unsafe_allow_html=True)

display_cols=["employee_id","department","location","job_level","employment_type","hiring_source","hire_date","employment_status","engagement_score","monthly_overtime_hours","time_to_hire_days"]
st.dataframe(f[display_cols],use_container_width=True,hide_index=True,height=420)

csv_data=f.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered workforce data",csv_data,"hr_workforce_filtered.csv","text/csv",use_container_width=True)

# Methodology/context
st.markdown('<div class="section-label">10 / Methodology</div><div class="section-title">From HR records to workforce decisions</div>', unsafe_allow_html=True)

m1,m2,m3=st.columns(3)
with m1:
    st.markdown('<div class="method"><b>01 · Workforce Monitoring</b><br><br>Track headcount movement, attrition, attendance and engagement across departments and employee groups.</div>',unsafe_allow_html=True)
with m2:
    st.markdown('<div class="method"><b>02 · Recruitment Analytics</b><br><br>Evaluate funnel conversion and compare hiring sources using recruitment speed and retention outcomes.</div>',unsafe_allow_html=True)
with m3:
    st.markdown('<div class="method"><b>03 · Retention Diagnostic</b><br><br>Explore relationships between overtime, engagement, employment type, commute and employee exits.</div>',unsafe_allow_html=True)

st.markdown("""
<div class="insight"><b>Important interpretation note.</b><br><br>
The dashboard shows descriptive associations in synthetic data. Relationships
between overtime, engagement, commute, employment type and attrition should not
be interpreted as causal effects or as a basis for automated employment decisions.
</div>
""",unsafe_allow_html=True)

st.markdown("""
<br><hr style="border:none;border-top:1px solid #D9DEE6;margin-top:2rem;margin-bottom:2rem;">
<div style="font-family:monospace;font-size:.76rem;letter-spacing:.08em;line-height:1.8;color:#7B838E;padding-bottom:2rem;">
RIZQI APRILIANES · PEOPLE ANALYTICS · WORKFORCE INTELLIGENCE · 2026<br>
PORTFOLIO PROJECT · SYNTHETIC DATA
</div>
""",unsafe_allow_html=True)
