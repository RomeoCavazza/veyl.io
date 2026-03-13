import streamlit as st
import os
import re

def parse_coverage(log_path):
    if not os.path.exists(log_path):
        return {}
    with open(log_path) as f:
        lines = f.readlines()
    coverage = {}
    pattern = re.compile(r'^(\S+\.py)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%')
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            file, stmts, miss, branch, brpart, percent = match.groups()
            coverage[file] = int(percent)
    return coverage

st.title('📊 Couverture des tests Revolvr AI Bot')

log_path = 'global_coverage.log'
coverage = parse_coverage(log_path)

if not coverage:
    st.warning("Aucun rapport coverage trouvé. Lancez d'abord la commande coverage CLI.")
else:
    for file, percent in coverage.items():
        st.metric(label=file, value=f"{percent}%")
        st.progress(percent / 100)
    st.write('---')
    st.write('Pour mettre à jour, relancez la commande coverage CLI.') 