# app/main.py
#
# Riscos:
# 1. Falha de inicialização caso o arquivo do DuckDB (/app/data/northwind.duckdb) ainda não tenha sido criado pelo dbt.
# 2. Conflito de concorrência ao tentar ler o arquivo do DuckDB se o dbt-runner estiver executando uma materialização de escrita.
# 3. Consumo excessivo de memória no container se as consultas analíticas trouxerem milhões de registros brutos sem agregação prévia.
#
# Ambiguidades:
# 1. Se a interface gráfica deve exibir dados históricos completos ou se deve focar estritamente no último mês fechado por padrão.
# 2. Se a biblioteca Plotly Express gerará lentidão ao renderizar gráficos dinâmicos no navegador do host.

import os
import time
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da página e design
st.set_page_config(
    page_title="Northwind Traders Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para visual premium
st.markdown("""
<style>
    .main-header {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1D4ED8;
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Caminho do banco analítico DuckDB
db_path = os.getenv("DUCKDB_DATABASE_PATH", "/app/data/northwind.duckdb")

def run_query(query):
    """Executa consultas de forma segura e somente-leitura no DuckDB com lógica de Retry"""
    retries = 3
    delay = 0.5
    for i in range(retries):
        try:
            conn = duckdb.connect(db_path, read_only=True)
            df = conn.execute(query).df()
            conn.close()
            return df
        except Exception as e:
            # Se o erro indicar que o banco está bloqueado por escrita, tenta novamente
            if "locked" in str(e).lower() and i < retries - 1:
                time.sleep(delay)
                continue
            st.error(f"Erro ao acessar o banco DuckDB: {e}")
            return None

# Título Principal
st.markdown("<h1 class='main-header'>📊 Painel Analítico de Vendas & Logística - Northwind Traders</h1>", unsafe_allow_html=True)

# 2. Autenticação Básica (Portabilidade-First)
def check_password():
    """Retorna True se o usuário inseriu as credenciais corretas."""
    dashboard_user = os.getenv("DASHBOARD_USER")
    dashboard_password = os.getenv("DASHBOARD_PASSWORD")
    
    if not dashboard_user or not dashboard_password:
        st.warning("⚠️ Credenciais de acesso não configuradas no arquivo de ambiente (.env).")
        st.stop()
        
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        
    if st.session_state["authenticated"]:
        return True
        
    # Exibe interface de Login
    st.write("")
    col_login, _ = st.columns([1, 2])
    with col_login:
        st.subheader("🔑 Login de Acesso")
        user_input = st.text_input("Usuário", key="login_username")
        pass_input = st.text_input("Senha", type="password", key="login_password")
        if st.button("Acessar"):
            if user_input == dashboard_user and pass_input == dashboard_password:
                st.session_state["authenticated"] = True
                st.success("Acesso concedido!")
                st.rerun()
            else:
                st.error("⚠️ Usuário ou senha incorretos.")
    return False

if not check_password():
    st.stop()

if not os.path.exists(db_path):
    st.warning("⚠️ Banco de dados analítico local `northwind.duckdb` não localizado. Por favor, execute o pipeline de dados via terminal primeiro.")
    st.stop()

# 2. Tabs Principais para organização do Dashboard
tab_finance, tab_logistic, tab_shippers, tab_employees = st.tabs([
    "💰 Rentabilidade Financeira", 
    "🚚 Logística e Entregas", 
    "🚢 Transportadoras e Rotas", 
    "👥 Equipe e Produtividade"
])

# ==========================================
# TAB 1: RENTABILIDADE FINANCEIRA
# ==========================================
with tab_finance:
    st.subheader("Análise de Margem e Rentabilidade por Categoria (RF-02)")
    
    # Query de Rentabilidade Real
    query_fin = """
        select 
            p.category_name,
            sum(f.item_gross_value) as gross_revenue,
            sum(f.discount_value) as total_discounts,
            sum(f.allocated_freight) as allocated_freight,
            sum(f.net_revenue) as net_revenue,
            sum(f.net_profit) as net_profit,
            (sum(f.net_profit) / sum(f.item_gross_value)) * 100 as profit_margin_pct
        from fct_order_items f
        join dim_products p on f.product_id = p.product_id
        group by 1
        order by net_profit desc
    """
    df_fin = run_query(query_fin)
    
    if df_fin is not None and not df_fin.empty:
        # Indicadores Executivos em Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>R$ {df_fin['gross_revenue'].sum():,.2f}</div>
                <div class='metric-label'>Receita Bruta</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>R$ {df_fin['total_discounts'].sum():,.2f}</div>
                <div class='metric-label'>Descontos Concedidos</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>R$ {df_fin['allocated_freight'].sum():,.2f}</div>
                <div class='metric-label'>Custos de Frete Alocados</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            net_profit_total = df_fin['net_profit'].sum()
            margin_total = (net_profit_total / df_fin['gross_revenue'].sum()) * 100
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value' style='color:#10B981;'>R$ {net_profit_total:,.2f} ({margin_total:.1f}%)</div>
                <div class='metric-label'>Lucro Líquido Real</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        # Gráficos de Vendas
        col_g1, col_g2 = st.columns([3, 2])
        
        with col_g1:
            st.markdown("##### Comparativo de Receita Bruta vs Lucro Líquido Real por Categoria")
            fig_fin_bar = go.Figure(data=[
                go.Bar(name='Receita Bruta', x=df_fin['category_name'], y=df_fin['gross_revenue'], marker_color='#3B82F6'),
                go.Bar(name='Lucro Líquido Real', x=df_fin['category_name'], y=df_fin['net_profit'], marker_color='#10B981')
            ])
            fig_fin_bar.update_layout(barmode='group', height=400, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_fin_bar, use_container_width=True)
            
        with col_g2:
            st.markdown("##### Distribuição de Lucro Líquido por Categoria")
            fig_fin_pie = px.pie(
                df_fin, 
                values='net_profit', 
                names='category_name',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                height=400
            )
            fig_fin_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_fin_pie, use_container_width=True)
            
        st.markdown("##### Detalhamento Financeiro Consolidador")
        st.dataframe(
            df_fin.style.format({
                'gross_revenue': 'R$ {:,.2f}',
                'total_discounts': 'R$ {:,.2f}',
                'allocated_freight': 'R$ {:,.2f}',
                'net_revenue': 'R$ {:,.2f}',
                'net_profit': 'R$ {:,.2f}',
                'profit_margin_pct': '{:.2f}%'
            }),
            use_container_width=True
        )

# ==========================================
# TAB 2: LOGÍSTICA E ENTREGAS
# ==========================================
with tab_logistic:
    st.subheader("Eficiência Logística, Gargalos e Atrasos (RF-04, RF-05)")
    
    # Query de métricas de prazo
    query_log = """
        select 
            c.country as destination_country,
            c.region as destination_region,
            count(distinct f.order_id) as total_orders,
            avg(f.lead_time_days) as avg_lead_time_days,
            avg(f.delivery_deviation_days) as avg_deviation_days,
            count(distinct case when f.delivery_deviation_days > 0 then f.order_id end) as late_orders_count,
            count(distinct case when f.is_date_consistent = false then f.order_id end) as inconsistent_orders_count
        from fct_order_items f
        join dim_customers c on f.customer_id = c.customer_id
        group by 1, 2
        order by total_orders desc
    """
    df_log = run_query(query_log)
    
    if df_log is not None and not df_log.empty:
        total_orders = df_log['total_orders'].sum()
        late_orders = df_log['late_orders_count'].sum()
        late_rate = (late_orders / total_orders) * 100
        inconsistent_orders = df_log['inconsistent_orders_count'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{total_orders}</div>
                <div class='metric-label'>Volume Total de Pedidos</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value' style='color:#EF4444;'>{late_orders} ({late_rate:.1f}%)</div>
                <div class='metric-label'>Pedidos Entregues com Atraso</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_lead_time = df_log['avg_lead_time_days'].mean()
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{avg_lead_time:.1f} Dias</div>
                <div class='metric-label'>Tempo Médio de Envio (Lead Time)</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value' style='color:{"#F59E0B" if inconsistent_orders > 0 else "#1D4ED8"};'>{inconsistent_orders}</div>
                <div class='metric-label'>Pedidos com Inconsistência de Data</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        col_g1, col_g2 = st.columns([1, 1])
        
        with col_g1:
            st.markdown("##### Desempenho Logístico e Taxa de Atraso por País de Destino")
            # Agrupa dados por país
            df_country = df_log.groupby('destination_country').agg({
                'total_orders': 'sum',
                'late_orders_count': 'sum',
                'avg_lead_time_days': 'mean'
            }).reset_index()
            df_country['late_rate_pct'] = (df_country['late_orders_count'] / df_country['total_orders']) * 100
            
            fig_country = px.bar(
                df_country,
                x='destination_country',
                y='late_rate_pct',
                color='avg_lead_time_days',
                labels={'late_rate_pct': 'Taxa de Atraso (%)', 'destination_country': 'País de Destino', 'avg_lead_time_days': 'Lead Time Médio'},
                color_continuous_scale=px.colors.sequential.YlOrRd,
                height=350
            )
            fig_country.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_country, use_container_width=True)
            
        with col_g2:
            st.markdown("##### Desvios Médios de Entrega (Dias de Atraso) por Região")
            fig_deviation = px.bar(
                df_log,
                x='destination_region',
                y='avg_deviation_days',
                color='destination_country',
                labels={'avg_deviation_days': 'Desvio de Entrega (Dias)', 'destination_region': 'Região de Destino'},
                height=350
            )
            fig_deviation.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_deviation, use_container_width=True)

        st.markdown("##### Performance Geográfica Detalhada (Países e Regiões)")
        st.dataframe(
            df_log.style.format({
                'avg_lead_time_days': '{:.1f} dias',
                'avg_deviation_days': '{:.1f} dias'
            }),
            use_container_width=True
        )

# ==========================================
# TAB 3: TRANSPORTADORAS E ROTAS
# ==========================================
with tab_shippers:
    st.subheader("Análise de Custo-Benefício de Transportadoras (RF-06)")
    
    # Query de transportadoras
    query_ship = """
        select 
            s.shipper_name,
            c.country as destination_country,
            count(distinct f.order_id) as total_orders,
            sum(f.allocated_freight) as total_freight_cost,
            avg(f.allocated_freight) as avg_freight_per_order,
            avg(f.lead_time_days) as avg_lead_time_days,
            count(distinct case when f.delivery_deviation_days > 0 then f.order_id end) as late_orders_count
        from fct_order_items f
        join dim_shippers s on f.shipper_id = s.shipper_id
        join dim_customers c on f.customer_id = c.customer_id
        group by 1, 2
        order by total_orders desc
    """
    df_ship = run_query(query_ship)
    
    if df_ship is not None and not df_ship.empty:
        col_s1, col_s2 = st.columns([3, 2])
        
        with col_s1:
            st.markdown("##### Custo de Frete Médio vs Lead Time Médio por Transportadora")
            df_ship_agg = df_ship.groupby('shipper_name').agg({
                'total_orders': 'sum',
                'total_freight_cost': 'sum',
                'avg_lead_time_days': 'mean',
                'late_orders_count': 'sum'
            }).reset_index()
            df_ship_agg['avg_freight_cost'] = df_ship_agg['total_freight_cost'] / df_ship_agg['total_orders']
            df_ship_agg['late_rate_pct'] = (df_ship_agg['late_orders_count'] / df_ship_agg['total_orders']) * 100
            
            fig_bubble = px.scatter(
                df_ship_agg,
                x="avg_lead_time_days",
                y="avg_freight_cost",
                size="total_orders",
                color="shipper_name",
                hover_name="shipper_name",
                labels={'avg_lead_time_days': 'Prazo de Entrega Médio (Dias)', 'avg_freight_cost': 'Custo Médio de Frete (R$)'},
                size_max=60,
                height=400
            )
            st.plotly_chart(fig_bubble, use_container_width=True)
            
        with col_s2:
            st.markdown("##### Taxa de Entrega Atrasada (%) por Transportadora")
            fig_ship_late = px.bar(
                df_ship_agg,
                x='shipper_name',
                y='late_rate_pct',
                color='shipper_name',
                labels={'late_rate_pct': 'Taxa de Atraso (%)', 'shipper_name': 'Transportadora'},
                color_discrete_sequence=px.colors.qualitative.Set2,
                height=400
            )
            fig_ship_late.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_ship_late, use_container_width=True)
            
        st.markdown("##### Custos de Frete e Prazos por Rota Logística de Destino")
        st.dataframe(
            df_ship.style.format({
                'total_freight_cost': 'R$ {:,.2f}',
                'avg_freight_per_order': 'R$ {:,.2f}',
                'avg_lead_time_days': '{:.1f} dias'
            }),
            use_container_width=True
        )

# ==========================================
# TAB 4: EQUIPE E PRODUTIVIDADE
# ==========================================
with tab_employees:
    st.subheader("Correlação de Produtividade e Processamento por Funcionário (RF-07)")
    
    # Query de funcionários
    query_emp = """
        select 
            e.employee_name,
            e.job_title,
            count(distinct f.order_id) as total_orders_processed,
            avg(f.lead_time_days) as avg_processing_time_days,
            sum(f.net_profit) as total_profit_generated
        from fct_order_items f
        join dim_employees e on f.employee_id = e.employee_id
        group by 1, 2
        order by total_orders_processed desc
    """
    df_emp = run_query(query_emp)
    
    if df_emp is not None and not df_emp.empty:
        col_e1, col_e2 = st.columns([3, 2])
        
        with col_e1:
            st.markdown("##### Correlação: Volume de Pedidos vs Tempo Médio de Processamento")
            fig_emp_scatter = px.scatter(
                df_emp,
                x='avg_processing_time_days',
                y='total_orders_processed',
                color='job_title',
                size='total_profit_generated',
                hover_name='employee_name',
                labels={'avg_processing_time_days': 'Tempo Médio de Envio (Dias)', 'total_orders_processed': 'Pedidos Processados (Volume)', 'job_title': 'Cargo'},
                size_max=40,
                height=400
            )
            st.plotly_chart(fig_emp_scatter, use_container_width=True)
            
        with col_e2:
            st.markdown("##### Lucro Líquido Total Gerado por Funcionário")
            fig_emp_profit = px.bar(
                df_emp,
                y='employee_name',
                x='total_profit_generated',
                color='job_title',
                orientation='h',
                labels={'total_profit_generated': 'Lucro Gerado (R$)', 'employee_name': 'Funcionário'},
                color_discrete_sequence=px.colors.qualitative.Safe,
                height=400
            )
            fig_emp_profit.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_emp_profit, use_container_width=True)
            
        st.markdown("##### Performance Detalhada dos Funcionários")
        st.dataframe(
            df_emp.style.format({
                'avg_processing_time_days': '{:.1f} dias',
                'total_profit_generated': 'R$ {:,.2f}'
            }),
            use_container_width=True
        )
