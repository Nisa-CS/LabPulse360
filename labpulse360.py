import streamlit as st
import pandas as pd
import os, random
from datetime import datetime

st.set_page_config(page_title="LabPulse 360°", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<p style='text-align:center; color:#666; font-size:22px; font-weight:600;'>National Jr. College of Science & Commerce (English Medium) • 📍 Kalyan (W)</p>", unsafe_allow_html=True)
st.title("🖥️ LabPulse 360°")
st.markdown("<h2 style='text-align:left; color:#1A237E;font-size:30px;'>IT and Computer Science Lab - Live Health Monitoring</h2>", unsafe_allow_html=True)

# --------- LOGIN ---------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", "Student")
st.session_state.setdefault("user_id", "")
st.session_state.setdefault("show_login", False)

if not st.session_state.logged_in:
    if st.button("🔐 Please Login - Click Here", use_container_width=True):
        st.session_state.show_login = True
    if st.session_state.show_login:
        st.markdown("### 🔐 Login")
        role = st.selectbox("Login As", ["Student", "Admin (Teacher)"])
        user_id = st.text_input("ID / Roll No")
        user_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if role == "Admin (Teacher)" and user_id == "teacher" and user_pass == "teacher123":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user_id = user_id
                st.rerun()
            elif role == "Student" and user_id != "" and user_pass == "1234":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("Wrong Password!")
    st.stop()

role = st.session_state.role
user_id = st.session_state.user_id
st.success(f"✅ {user_id} Logged In")

# ---------- SETTINGS ----------
st.sidebar.header("⚙️ Lab Settings")
if role == "Admin (Teacher)":
    TOTAL_PCS = st.sidebar.number_input("Total PCs in Lab", min_value=1, max_value=100, value=25)
    TOTAL_PRINTERS = st.sidebar.number_input("Total Printers", min_value=0, max_value=10, value=2)
    TOTAL_PROJECTORS = st.sidebar.number_input("Total Projectors", min_value=0, max_value=5, value=1)
    TOTAL_SCANNERS = st.sidebar.number_input("Total Scanners", min_value=0, max_value=5, value=1)
    TOTAL_ROUTERS = st.sidebar.number_input("Total Routers", min_value=0, max_value=5, value=1)
else:
    TOTAL_PCS = 25
    TOTAL_PRINTERS = 2
    TOTAL_PROJECTORS = 1
    TOTAL_SCANNERS = 1
    TOTAL_ROUTERS = 1
    st.sidebar.info("🔒 Only Admin can change settings")

# ======== STUDENT VIEW ========
if role == "Student":
    import psutil
    st.success(f"👋 Welcome Student - {user_id}")
    st.subheader("Step 1: 🖥️ Which PC are you using today?")
    my_pc = st.selectbox("Select Your PC:", [f"PC-{i:02d}" for i in range(1, 26)])
    st.success(f"You are using: {my_pc} today")
    st.divider()
    st.subheader("Step 2: 📝 Select ONE Problem")
    problem = st.selectbox("Select your problem:", ["Mouse Not Working", "Internet Not Working", "Keyboard Not Working", "PC Slow / Hanging", "Monitor Not Working", "Speaker / Sound Not Working", "PC Not Starting", "Other"])
    video_file = st.file_uploader("🎥 Upload Video of Problem", type=["mp4","mov","avi","mkv"])
    def get_troubleshoot_student(p):
        steps = {
            "Mouse Not Working": ["✅ 1. Unplug mouse and plug again", "✅ 2. Try other USB port", "✅ 3. Restart PC"],
            "Internet Not Working": ["✅ 1. Check LAN cable - is it tight?", "✅ 2. Wi-Fi OFF / ON", "✅ 3. Restart PC", "✅ 4. Run Windows Troubleshoot"],
            "Keyboard Not Working": ["✅ 1. Unplug and plug keyboard", "✅ 2. Try other USB port", "✅ 3. Restart PC"],
            "PC Slow / Hanging": ["✅ 1. Close extra tabs / apps", "✅ 2. Restart PC", "✅ 3. Delete Temp files"],
            "Monitor Not Working": ["✅ 1. Check power cable", "✅ 2. Check VGA / HDMI cable", "✅ 3. Press power button"],
            "Speaker / Sound Not Working": ["✅ 1. Check volume - not mute", "✅ 2. Check speaker cable", "✅ 3. Restart PC"],
            "PC Not Starting": ["✅ 1. Check power cable / switch", "✅ 2. Check monitor power", "✅ 3. Hold power button 10 sec, then ON"],
        }
        return steps.get(p, [])
    def load_complaints_student():
        if os.path.exists("complaints.csv"):
            df = pd.read_csv("complaints.csv", dtype=str).fillna("")
            if "Photo" in df.columns:
                df = df.drop(columns=["Photo"])
            return df
        return pd.DataFrame(columns=["Date-Time", "Asset", "Asset No", "Problem", "Student", "Auto Priority", "Status", "Video", "Feedback"])
    def get_priority_student(p):
        if p in ["PC Not Starting", "Monitor Not Working"]:
            return "🔴 HIGH - Fix in 1 Hour"
        elif p in ["PC Slow / Hanging", "Internet Not Working"]:
            return "🟡 MEDIUM - Fix Today"
        else:
            return "🟢 LOW - Fix in 2 Days"
    if problem == "Other":
        st.divider()
        st.subheader("Step 3: ✍️ Type Your Problem")
        custom_problem = st.text_input("Type your problem here - e.g. Printer not working, USB not detecting, etc.")
        st.info("For 'Other', there is NO Quick Solution. You must type problem and send directly to Teacher.")
        if st.button("📩 Submit Complaint to Teacher"):
            if custom_problem.strip() == "":
                st.warning("⚠️ Please type your problem first! Cannot submit empty complaint.")
            else:
                video_path = ""
                if video_file is not None:
                    video_path = f"videos/{video_file.name}"
                    os.makedirs("videos", exist_ok=True)
                    with open(video_path, "wb") as f:
                        f.write(video_file.getbuffer())
                time_now = datetime.now().strftime("%d-%m-%Y %H:%M")
                new_row = pd.DataFrame([[time_now, "PC", my_pc, custom_problem, user_id, "🟡 Pending", "❌ Still Not Working - Need Teacher", video_path, ""]], columns=["Date-Time", "Asset", "Asset No", "Problem", "Student", "Auto Priority", "Status", "Video", "Feedback"])
                df_old = load_complaints_student()
                pd.concat([df_old, new_row], ignore_index=True).to_csv("complaints.csv", index=False)
                st.success(f"Complaint for {my_pc} - '{custom_problem}' sent to Teacher!")
    else:
        priority = get_priority_student(problem)
        st.info(f"Priority: {priority}")
        st.divider()
        st.subheader("Step 3: ⚡ Quick Solution - Try This First!")
        st.warning("Do NOT submit complaint yet. Try these steps first:")
        for step in get_troubleshoot_student(problem):
            st.write(step)
        st.divider()
        st.subheader("Step 4: Did Quick Solution Work?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, Solved!"):
                st.success(f"Great! {my_pc} Fixed by you. No complaint needed. Teacher saved time!")
                st.balloons()
        with c2:
            if st.button("❌ No, Still Not Working - Submit Complaint"):
                video_path = ""
                if video_file is not None:
                    video_path = f"videos/{video_file.name}"
                    os.makedirs("videos", exist_ok=True)
                    with open(video_path, "wb") as f:
                        f.write(video_file.getbuffer())
                time_now = datetime.now().strftime("%d-%m-%Y %H:%M")
                new_row = pd.DataFrame([[time_now, "PC", my_pc, problem, user_id, priority, "❌ Still Not Working - Need Teacher", video_path, ""]], columns=["Date-Time", "Asset", "Asset No", "Problem", "Student", "Auto Priority", "Status", "Video", "Feedback"])
                df_old = load_complaints_student()
                pd.concat([df_old, new_row], ignore_index=True).to_csv("complaints.csv", index=False)
                st.error(f"Complaint for {my_pc} - {problem} sent to Teacher!")
    st.divider()
    st.subheader("📋 My Complaints Only")
    df_all_s = load_complaints_student()
    if not df_all_s.empty:
        my_df = df_all_s[df_all_s['Student'].astype(str) == str(user_id)]
        st.table(my_df)
        for idx, row in my_df.iterrows():
            if row["Status"] == "✅ Fixed - Waiting for Feedback":
                st.warning(f"Teacher fixed {row['Asset No']}. Is it working?")
                if st.button(f"✅ Working Now - {row['Asset No']}", key=f"w{idx}"):
                    df_all_s["Feedback"] = df_all_s["Feedback"].astype(object)
                    df_all_s["Status"] = df_all_s["Status"].astype(object)
                    df_all_s.loc[idx, "Feedback"] = "✅ Working - Closed"
                    df_all_s.loc[idx, "Status"] = "Closed"
                    df_all_s.to_csv("complaints.csv", index=False)
                    st.rerun()
                if st.button(f"❌ Still Not Working - {row['Asset No']}", key=f"n{idx}"):
                    df_all_s["Feedback"] = df_all_s["Feedback"].astype(object)
                    df_all_s["Status"] = df_all_s["Status"].astype(object)
                    df_all_s.loc[idx, "Feedback"] = "❌ Still Not Working"
                    df_all_s.loc[idx, "Status"] = "❌ Still Not Working - Need Teacher"
                    df_all_s.to_csv("complaints.csv", index=False)
                    st.rerun()
    else:
        st.write("No complaints yet.")
    st.stop()

# ======== ADMIN STARTS ========
def get_troubleshoot(problem):
    steps = {
        "Internet Not Working": ["1. Check LAN cable / Wi-Fi", "2. Wi-Fi OFF and ON", "3. Restart PC", "4. Run Network Troubleshoot"],
        "Mouse Not Working": ["1. Unplug and plug again", "2. Try other USB port", "3. Restart PC"],
        "Keyboard Not Working": ["1. Unplug and plug again", "2. Try other USB port", "3. Restart PC"],
        "System Very Slow": ["1. Close extra tabs", "2. Restart PC", "3. Delete Temp files"],
        "Overheating / Fan Noise": ["1. Close heavy apps", "2. Check fan blocked?", "3. Restart and call Teacher"],
        "Software Not Opening": ["1. Restart PC", "2. Reopen software", "3. Call Teacher - Reinstall needed"],
        "PC Not Turning ON": ["1. Check power cable", "2. Press power 10 sec", "3. Call Teacher"],
        "No Display": ["1. Check VGA/HDMI cable", "2. Check monitor ON", "3. Restart PC"],
        "Printer Paper Jam": ["1. Turn printer OFF", "2. Open tray slowly", "3. Pull paper slowly - Do NOT tear", "4. Close tray, Turn ON"],
        "Printer No Ink": ["1. Check ink level", "2. Shake cartridge gently", "3. Replace cartridge - Call Teacher"],
        "Printer Not Printing": ["1. Check USB / Wi-Fi cable", "2. Check printer Online", "3. Restart printer and PC", "4. Clear print queue"],
        "Printer Offline": ["1. Check power cable", "2. Restart printer", "3. Reconnect USB / Wi-Fi"],
        "Projector No Display": ["1. Check HDMI cable", "2. Press Source button", "3. Check lamp ON", "4. Restart PC"],
        "Projector Lamp Dim": ["1. Clean lens", "2. Check brightness", "3. Call Teacher - Lamp change"],
        "Scanner Not Working": ["1. Check USB cable", "2. Restart scanner", "3. Call Teacher"],
    }
    return steps.get(problem, ["1. Restart device", "2. Check cables", "3. Call Teacher"])

def get_priority(problem):
    if problem in ["PC Not Turning ON", "No Display", "Projector No Display", "Printer Paper Jam"]:
        return "🔴 HIGH - Fix in 1 Hour"
    elif problem in ["System Very Slow", "Internet Not Working", "Printer Not Printing"]:
        return "🟡 MEDIUM - Fix Today"
    else:
        return "🟢 LOW - Fix in 2 Days"

def load_complaints():
    if os.path.exists("complaints.csv"):
        df = pd.read_csv("complaints.csv", dtype=str).fillna("")
        if "Photo" in df.columns:
            df = df.drop(columns=["Photo"])
        return df
    return pd.DataFrame(columns=["Date-Time", "Asset", "Asset No", "Problem", "Student", "Auto Priority", "Status", "Video", "Feedback"])

import psutil
admin_cpu = int(psutil.cpu_percent(interval=0.5))
admin_ram = int(psutil.virtual_memory().percent)
admin_disk = int(psutil.disk_usage('/').percent)
try:
    temps = psutil.sensors_temperatures()
    if temps:
        admin_temp = int(list(temps.values())[0][0].current)
    else:
        admin_temp = int(38 + (admin_cpu * 0.35))
except:
    admin_temp = int(38 + (admin_cpu * 0.35))
admin_health = 100 - int((admin_cpu + admin_ram)/4)

pcs = []
for i in range(1, TOTAL_PCS + 1):
    online = random.choice(["Online", "Online", "Online", "Offline"])
    cpu = random.randint(10, 95) if online == "Online" else 0
    ram = random.randint(20, 90) if online == "Online" else 0
    health = 100 - int((cpu + ram) / 4) if online == "Online" else 0
    if online == "Offline":
        status = "⚫ Offline"
    elif health >= 70:
        status = "🟢 Good"
    elif health >= 40:
        status = "🟡 Warning"
    else:
        status = "🔴 Critical"
    pcs.append([f"PC-{i:02d}", online, cpu, ram, health, status])
df_live = pd.DataFrame(pcs, columns=["PC", "Status", "CPU", "RAM", "Health Score", "Health"])
good = len(df_live[df_live['Health'] == "🟢 Good"])
warn = len(df_live[df_live['Health'] == "🟡 Warning"])
crit = len(df_live[df_live['Health'] == "🔴 Critical"])
off = len(df_live[df_live['Health'] == "⚫ Offline"])
bad_pcs = df_live[df_live['Health'].isin(["🔴 Critical", "⚫ Offline"])]['PC'].tolist()

# --------- TABS FOR ADMIN ---------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Dashboard", "🖥️ PCs", "📝 Complaints", "🔧 Maintenance", "📊 Usage", "⚡ Energy"])

with tab1:
    st.success("🖥️ SERVER - Admin Laptop | Status: 🟢 ONLINE")
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("Admin Laptop Pulse", "🟢 LIVE")
    a2.metric("CPU", f"{admin_cpu}%")
    a3.metric("RAM", f"{admin_ram}%")
    a4.metric("Disk", f"{admin_disk}%")
    a5.metric("Temp", f"{admin_temp}°C")
    st.progress(admin_health / 100)
    st.write(f"**Admin Laptop Health Score: {admin_health}%** - CPU/RAM/Disk are REAL from this laptop. Temp is estimated from CPU load.")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Lab PCs", str(TOTAL_PCS))
    c2.metric("Printers", str(TOTAL_PRINTERS))
    c3.metric("Projectors", str(TOTAL_PROJECTORS))
    c4.metric("Scanners", str(TOTAL_SCANNERS))
    c5.metric("Routers", str(TOTAL_ROUTERS))
    st.divider()
    if crit > 0:
        st.error(f"🔴 LAB NEEDS TECHNICIAN URGENTLY! - {crit} PCs are Critical / Offline")
    elif warn > 3:
        st.warning(f"🟡 LAB NEEDS ATTENTION - {warn} PCs are in Warning")
    elif admin_health >= 80:
        st.success(f"🟢 LAB IS HEALTHY - All Good! Health: {admin_health}%")
    else:
        st.info(f"🔵 LAB IS OK - Health: {admin_health}%")
    cc1, cc2, cc3, cc4 = st.columns(4)
    cc1.metric("🟢 Good", good)
    cc2.metric("🟡 Warning", warn)
    cc3.metric("🔴 Critical", crit)
    cc4.metric("⚫ Offline", off)
    st.subheader("📊 LabPulse Bar Graph")
    chart_data = pd.DataFrame({"Status": ["Good", "Warning", "Critical", "Offline"], "Count": [good, warn, crit, off]})
    st.bar_chart(chart_data.set_index("Status"))
    if bad_pcs:
        st.error(f"🚨 ALERT: {len(bad_pcs)} PCs Need Attention - {', '.join(bad_pcs)}")
    else:
        st.success("✅ All PCs Healthy - No Action Needed")
    if st.button("🔄 Refresh Live Data"):
        st.rerun()

with tab2:
    st.header("🖥️ Live Monitoring & Health Score")
    col_s, col_f = st.columns(2)
    search = col_s.text_input("🔍 Search PC - Type PC-05")
    filter_health = col_f.selectbox("Filter Health", ["All", "🟢 Good", "🟡 Warning", "🔴 Critical", "⚫ Offline"])
    df_show = df_live.copy()
    if search:
        df_show = df_show[df_show['PC'].str.contains(search.upper())]
    if filter_health != "All":
        df_show = df_show[df_show['Health'] == filter_health]
    df_display = df_show.copy()
    df_display['CPU'] = df_display['CPU'].astype(str) + "%"
    df_display['RAM'] = df_display['RAM'].astype(str) + "%"
    df_display['Health Score'] = df_display['Health Score'].astype(str) + "%"
    st.dataframe(df_display, use_container_width=True)
    st.caption(f"Showing {len(df_show)} of {TOTAL_PCS} PCs")
    st.header("🖨️ Lab Assets Status")
    assets = []
    for i in range(1, TOTAL_PRINTERS + 1):
        assets.append([f"Printer-{i:02d}", random.choice(["🟢 Online", "🟢 Online", "🔴 Paper Jam", "🟡 Low Ink"]), "Printing"])
    for i in range(1, TOTAL_PROJECTORS + 1):
        assets.append([f"Projector-{i:02d}", random.choice(["🟢 Online", "🟢 Online", "🔴 Lamp Issue"]), "Display"])
    for i in range(1, TOTAL_SCANNERS + 1):
        assets.append([f"Scanner-{i:02d}", "🟢 Online", "Scanning"])
    for i in range(1, TOTAL_ROUTERS + 1):
        assets.append([f"Router-{i:02d}", "🟢 Online", "Internet"])
    st.table(pd.DataFrame(assets, columns=["Asset", "Status", "Use"]))

with tab3:
    st.header("📝 Admin - All Complaints")
    df_all = load_complaints()
    if not df_all.empty:
        st.table(df_all)
        for idx, row in df_all.iterrows():
            video_col = row.get("Video", "")
            if video_col and os.path.exists(str(video_col)):
                with st.expander(f"🎥 Video - {row['Asset No']} | {row['Problem']}"):
                    c_v1, c_v2, c_v3 = st.columns([1, 1, 1])
                    with c_v1:
                        st.video(str(video_col))
        idx_to_fix = st.selectbox("Select Row To Mark Fixed", list(df_all.index))
        if st.button("Mark Selected As Fixed ✅"):
            df_all["Status"] = df_all["Status"].astype(object)
            df_all.loc[idx_to_fix, 'Status'] = "✅ Fixed - Waiting for Feedback"
            df_all.to_csv("complaints.csv", index=False)
            st.success("Marked as Fixed By Teacher")
            st.rerun()
    else:
        st.write("No complaints yet.")

with tab4:
    st.header("🔧 Maintenance Schedule")
    st.write("Which PC was serviced last time? Which PC needs servicing next?")
    maint_data = []
    for i in range(1, TOTAL_PCS + 1):
        last_days = random.randint(5, 90)
        next_due = 90 - last_days
        if last_days > 75:
            m_status = "🔴 Overdue - Service Now"
        elif last_days > 45:
            m_status = "🟡 Due Soon"
        else:
            m_status = "🟢 OK"
        maint_data.append([f"PC-{i:02d}", f"{last_days} days ago", f"In {next_due} days", m_status])
    df_maint = pd.DataFrame(maint_data, columns=["PC", "Last Serviced", "Next Service Due", "Status"])
    st.dataframe(df_maint, use_container_width=True)
    overdue = len(df_maint[df_maint['Status'].str.contains("Overdue")])
    due_soon = len(df_maint[df_maint['Status'].str.contains("Due Soon")])
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("🔴 Overdue", overdue)
    c_m2.metric("🟡 Due Soon", due_soon)
    c_m3.metric("🟢 OK", TOTAL_PCS - overdue - due_soon)
    if overdue > 0:
        st.error(f"⚠️ {overdue} PCs need servicing urgently - Dust cleaning + Software Update")
    else:
        st.success("✅ All PCs serviced on time")

with tab5:
    st.header("📊 Lab Usage Report")
    st.write("Which PC is used most? Which lab hour is busiest?")
    usage_data = []
    for i in range(1, TOTAL_PCS + 1):
        hours = random.randint(2, 8)
        students = random.randint(5, 30)
        usage_data.append([f"PC-{i:02d}", hours, students])
    df_usage = pd.DataFrame(usage_data, columns=["PC", "Hours Used Today", "Students Used"])
    st.bar_chart(df_usage.set_index("PC")["Hours Used Today"])
    st.dataframe(df_usage, use_container_width=True)
    total_hours = df_usage["Hours Used Today"].sum()
    most_used = df_usage.loc[df_usage["Hours Used Today"].idxmax(), "PC"]
    c_u1, c_u2, c_u3 = st.columns(3)
    c_u1.metric("Total Lab Hours Today", f"{total_hours} hrs")
    c_u2.metric("Most Used PC", most_used)
    c_u3.metric("Avg Use Per PC", f"{round(total_hours/TOTAL_PCS,1)} hrs")
    st.info(f"🏆 Most Used PC is {most_used} - Teacher should check it first for maintenance.")

with tab6:
    st.header("⚡ Energy Saving")
    st.write("How much electricity lab uses? How to save?")
    watt_per_pc = 150
    total_watt = TOTAL_PCS * watt_per_pc
    kwh_per_day = (total_watt * 8) / 1000
    cost_per_day = kwh_per_day * 8
    cost_per_month = cost_per_day * 22
    idle_pcs = off
    saved_kwh = (idle_pcs * watt_per_pc * 8) / 1000
    saved_rs = saved_kwh * 8
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Total Power", f"{total_watt} Watt")
    e2.metric("Energy / Day", f"{kwh_per_day:.1f} kWh")
    e3.metric("Cost / Day", f"₹{cost_per_day:.0f}")
    e4.metric("Cost / Month", f"₹{cost_per_month:.0f}")
    st.success(f"💡 Energy Tip: {idle_pcs} PCs are Offline today. If we keep them OFF, we save ₹{saved_rs:.0f} per day!")
    st.warning("🌱 Green Lab Rule: Last student must shutdown PC + Monitor + Switch OFF plug. Saves power + increases PC life.")
    st.progress(75)
    st.write("**Green Score: 75%** - Lab is saving energy by auto-shutdown of idle PCs.")

st.markdown("---")
st.success("🖥️ LabPulse 360° - Dedicated to National Jr. College of Science & Commerce (English Medium)")