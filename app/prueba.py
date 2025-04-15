import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import psycopg2
from sklearn.linear_model import LinearRegression
import numpy as np
import dash_bootstrap_components as dbc
import pandas as pd


cat_perfil_riesgo=pd.read_csv("app\cat_perfil_riesgo.csv")
catalogo_activos=pd.read_csv("app\catalogo_activos.csv")
catalogo_banca=pd.read_csv("app\catalogo_banca.csv")
historico_aba_macroactivos=pd.read_csv("app\historico_aba_macroactivos.csv")
print(historico_aba_macroactivos.dtypes)
tabDict= {"cat_perfil_riesgo" : cat_perfil_riesgo ,"catalogo_activos":catalogo_activos,"catalogo_banca":catalogo_banca,"historico_aba_macroactivos":historico_aba_macroactivos}
#Mapeo de los tipos de datos de pandas a PostgreSQL

type_map={
    
    "object":"TEXT",
    "int64":"INTEGER",
    "float64":"NUMERIC",
    "datetime64[ns]":"DATE"
    
    
}

#print(cat_perfil_riesgo)

conn= psycopg2.connect(
    
    host="localhost",
    database="postgres",
    user="postgres",
    password="4179"

)


cursor=conn.cursor()

print(tabDict)

for name,value in tabDict.items():
    columns=[]
    for col, dtype in value.dtypes.items():
        pg_type=type_map[str(dtype)]
        columns.append(f"{col} {pg_type}")
        
    create_table_query= f"""DROP TABLE IF EXISTS {name};
    CREATE TABLE {name} ({', '.join(columns)});"""
    #print(create_table_query)


    try: 
        
        cursor.execute(create_table_query)
        conn.commit()
        print(f"tabla {name} ha sido creada correctamente")
        
    except Exception as e:
        print(f"Error al crear la tabla {name}")
    
    try:
        for _, row in value.iterrows():
            values=', '.join(['%s'] * len(row))
            insert_query = f"INSERT INTO {name} VALUES ({values})"
            cursor.execute(insert_query,tuple(row))
        print(f"Datos de la tabla {name} importados correctamente")
        conn.commit()
    except Exception as e:
        print(f"Error al importar los datos de la tabla {name}")




sql_queries = [
    """
    


/*

ingestion_day corrección

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/




update public.historico_aba_macroactivos set ingestion_day = case
	WHEN historico_aba_macroactivos.ingestion_day > 31 THEN NULL
	ELSE ingestion_day
	END;

/*

id_sistema_cliente corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/
ALTER TABLE public.historico_aba_macroactivos 
ADD COLUMN id_sistema_cliente_correccion NUMERIC;


UPDATE historico_aba_macroactivos 
SET id_sistema_cliente_correccion = CASE 
    WHEN id_sistema_cliente ~ '^[0-9.E+-]+$' THEN id_sistema_cliente::NUMERIC 

	WHEN macroactivo ~ '^[0-9.E+-]+$' THEN  macroactivo::NUMERIC

	
    ELSE NULL 
END;










/*

cod_activo corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/

ALTER TABLE public.historico_aba_macroactivos 
ADD COLUMN cod_activo_correccion NUMERIC;



UPDATE public.historico_aba_macroactivos 
SET cod_activo_correccion = CASE
    WHEN cod_activo ~ '^[0-9]+(\.[0-9]+)?$' AND cod_activo::numeric IN (SELECT cod_activo::numeric FROM public.catalogo_activos) THEN cod_activo::NUMERIC

	WHEN aba::TEXT ~ '^[0-9]+(\.[0-9]+)?$' AND aba::numeric IN (SELECT cod_activo::numeric FROM public.catalogo_activos) THEN aba::numeric

	WHEN macroactivo::TEXT ~ '^[0-9]+(\.[0-9]+)?$' AND macroactivo::numeric IN (SELECT cod_activo::numeric FROM public.catalogo_activos) THEN macroactivo::numeric

	WHEN macroactivo::TEXT IN (SELECT activo::TEXT FROM public.catalogo_activos) THEN (SELECT catalogo_activos.cod_activo::numeric FROM catalogo_activos WHERE activo::TEXT = historico_aba_macroactivos.macroactivo::TEXT)

	WHEN  cod_activo ~ '^[0-9]+(\.[0-9]+)?$' AND RIGHT (cod_activo::TEXT, 2) IN ( SELECT RIGHT (cod_activo::TEXT, 2) FROM catalogo_activos) THEN (SELECT cod_activo::NUMERIC FROM catalogo_activos WHERE RIGHT (cod_activo::TEXT, 2)=RIGHT(historico_aba_macroactivos.cod_activo::TEXT, 2) ) 

	WHEN cod_activo !~ '^\d+$' AND RIGHT (aba::INTEGER::TEXT,2) IN ( SELECT RIGHT (cod_activo::TEXT, 2) FROM catalogo_activos) THEN (SELECT cod_activo::NUMERIC FROM catalogo_activos WHERE RIGHT (cod_activo::TEXT, 2)=RIGHT(historico_aba_macroactivos.aba::INTEGER::TEXT, 2) ) 
    
	ELSE NULL
END;


/*

macroactivo corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/

ALTER TABLE public.historico_aba_macroactivos 
ADD COLUMN macroactivo_correccion TEXT;


/* Existen 3 categorías Renta Variable, Renta Fija y FICs*/
SELECT DISTINCT macroactivo, historico_aba_macroactivos.cod_activo_correccion FROM public.historico_aba_macroactivos WHERE macroactivo='Renta Variable' ;
SELECT DISTINCT macroactivo, historico_aba_macroactivos.cod_activo_correccion FROM public.historico_aba_macroactivos WHERE macroactivo='Renta Fija' ;
SELECT DISTINCT macroactivo, historico_aba_macroactivos.cod_activo_correccion FROM public.historico_aba_macroactivos WHERE macroactivo='FICs' ;

SELECT DISTINCT historico_aba_macroactivos.cod_activo_correccion FROM public.historico_aba_macroactivos WHERE macroactivo='Renta Variable' ;
SELECT DISTINCT historico_aba_macroactivos.cod_activo_correccion FROM public.historico_aba_macroactivos WHERE macroactivo='Renta Fija' ;
SELECT DISTINCT historico_aba_macroactivos.cod_activo_correccion FROM public.historico_aba_macroactivos WHERE macroactivo='FICs' ;



SELECT DISTINCT macroactivo, catalogo_activos.activo
FROM public.historico_aba_macroactivos
JOIN catalogo_activos
ON historico_aba_macroactivos.cod_activo_correccion = catalogo_activos.cod_activo WHERE historico_aba_macroactivos.macroactivo ='Renta Variable';


SELECT DISTINCT macroactivo, catalogo_activos.activo
FROM public.historico_aba_macroactivos
JOIN catalogo_activos
ON historico_aba_macroactivos.cod_activo_correccion = catalogo_activos.cod_activo WHERE historico_aba_macroactivos.macroactivo ='Renta Fija';


SELECT DISTINCT historico_aba_macroactivos.cod_activo_correccion
FROM public.historico_aba_macroactivos
JOIN catalogo_activos
ON historico_aba_macroactivos.cod_activo_correccion = catalogo_activos.cod_activo WHERE historico_aba_macroactivos.macroactivo ='FICs';

SELECT * from historico_aba_macroactivos where historico_aba_macroactivos.macroactivo_correccion ='Renta Fija';

UPDATE public.historico_aba_macroactivos 
SET macroactivo_correccion = CASE

	WHEN cod_activo::TEXT IN ('Renta Variable','Renta Fija', 'FICs') THEN cod_activo::TEXT
	WHEN id_sistema_cliente::TEXT IN ('Renta Variable','Renta Fija', 'FICs') THEN id_sistema_cliente::TEXT
	WHEN macroactivo IN ('Renta Variable','Renta Fija', 'FICs') THEN macroactivo::TEXT


	WHEN cod_activo_correccion IN (SELECT DISTINCT historico_aba_macroactivos.cod_activo_correccion
		FROM public.historico_aba_macroactivos
		JOIN catalogo_activos
		ON historico_aba_macroactivos.cod_activo_correccion = catalogo_activos.cod_activo WHERE historico_aba_macroactivos.macroactivo ='FICs')
		THEN 'FICs'
	WHEN cod_activo_correccion IN(

		SELECT DISTINCT historico_aba_macroactivos.cod_activo_correccion
		FROM public.historico_aba_macroactivos
		JOIN catalogo_activos
		ON historico_aba_macroactivos.cod_activo_correccion = catalogo_activos.cod_activo WHERE historico_aba_macroactivos.macroactivo ='Renta Fija')
		THEN 'Renta Fija'

	WHEN cod_activo_correccion IN(SELECT DISTINCT historico_aba_macroactivos.cod_activo_correccion
		FROM public.historico_aba_macroactivos
		JOIN catalogo_activos
		ON historico_aba_macroactivos.cod_activo_correccion = catalogo_activos.cod_activo WHERE historico_aba_macroactivos.macroactivo ='Renta Variable') 
		THEN 'Renta Variable'
	WHEN macroactivo in ('FICs', 'Renta Variable', 'Renta Fija') THEN macroactivo
	ELSE NULL
	END;




/*

aba corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/

ALTER TABLE public.historico_aba_macroactivos 
ADD COLUMN aba_correccion NUMERIC;




UPDATE public.historico_aba_macroactivos 
SET aba_correccion = CASE
	WHEN cod_perfil_riesgo::TEXT !~ '^[0-9.E+-]+$' AND cod_perfil_riesgo::TEXT !~'NaN' AND RIGHT (cod_activo::TEXT,2) NOT IN (SELECT RIGHT (cod_activo::TEXT,2) FROM catalogo_activos)  THEN cod_activo::NUMERIC
	WHEN cod_activo::TEXT !~ '^[0-9.E+-]+$' AND cod_activo::TEXT !~'NaN' AND RIGHT (cod_perfil_riesgo::TEXT,2) NOT IN (SELECT RIGHT (cod_activo::TEXT,2) FROM catalogo_activos) THEN cod_perfil_riesgo::NUMERIC
	WHEN aba::TEXT ~ '^[0-9.E+-]+$' THEN aba::NUMERIC
	ELSE NULL
END;





/*

cod_perfil_riesgo corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/
ALTER TABLE public.historico_aba_macroactivos 
ADD COLUMN cod_perfil_riesgo_correccion NUMERIC;




/*Existen 4 perfiles de riesgo*/



UPDATE public.historico_aba_macroactivos 
SET cod_perfil_riesgo_correccion = CASE
	WHEN cod_perfil_riesgo::TEXT IN (SELECT DISTINCT cod_perfil_riesgo::TEXT from cat_perfil_riesgo) THEN cod_perfil_riesgo::NUMERIC
	WHEN aba::INTEGER::TEXT IN (SELECT DISTINCT cod_perfil_riesgo::TEXT from cat_perfil_riesgo) THEN aba::INTEGER::NUMERIC
	WHEN cod_banca::TEXT IN (SELECT DISTINCT cod_perfil_riesgo::TEXT from cat_perfil_riesgo) THEN aba::INTEGER::NUMERIC
	ELSE NULL
END;

/*

cod_banca corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/




ALTER TABLE public.historico_aba_macroactivos
ADD COLUMN cod_banca_correccion TEXT;



UPDATE public.historico_aba_macroactivos
SET cod_banca_correccion= CASE

	WHEN cod_banca::TEXT IN (SELECT cod_banca::TEXT FROM catalogo_banca) then cod_banca::TEXT
	WHEN cod_perfil_riesgo::TEXT IN (SELECT cod_banca::TEXT FROM catalogo_banca) then cod_perfil_riesgo::TEXT
	WHEN year::TEXT IN (SELECT cod_banca::TEXT FROM catalogo_banca) then year::TEXT
	ELSE NULL
END;



/*

year corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/

ALTER TABLE public.historico_aba_macroactivos 
ADD COLUMN year_correccion NUMERIC;
SELECT DISTINCT YEAR FROM public.historico_aba_macroactivos ;

UPDATE public.historico_aba_macroactivos 
SET year_correccion= CASE
	WHEN year::TEXT ~ '^[0-9.E+-]+$' AND year::NUMERIC >2000 THEN year::NUMERIC
	WHEN month::TEXT ~ '^[0-9.E+-]+$' AND month::TEXT !~ 'NaN' AND month >2000 THEN month::INTEGER::NUMERIC
	WHEN cod_banca::TEXT ~ '^[0-9.E+-]+$' AND cod_banca::TEXT !~ 'NaN' AND cod_banca::INTEGER >2000 THEN cod_banca::INTEGER::NUMERIC
	ELSE NULL
END;



/*

month corrección usando columna auxiliar

Para los datos que no concuerdan o no son claros en el ingestion_day se pondrá un valor nulo

*/
ALTER TABLE public.historico_aba_macroactivos 
ADD COLUMN month_correccion NUMERIC;


UPDATE public.historico_aba_macroactivos 
SET month_correccion = CASE
	WHEN month between 0 AND 12 THEN month
	WHEN year::TEXT ~ '^[0-9.E+-]+$' AND year::NUMERIC between 0 AND 12 THEN year::NUMERIC
	ELSE NULL
END;






/*

TRAER LOS DATOS A LA COLUMNA ORIGINAL
*/
UPDATE historico_aba_macroactivos SET id_sistema_cliente = NULL;
UPDATE historico_aba_macroactivos SET cod_activo = NULL;
UPDATE historico_aba_macroactivos SET macroactivo = NULL;
UPDATE historico_aba_macroactivos SET aba = NULL;
UPDATE historico_aba_macroactivos SET cod_perfil_riesgo = NULL;
UPDATE historico_aba_macroactivos SET cod_banca = NULL;
UPDATE historico_aba_macroactivos SET year = NULL;



ALTER TABLE historico_aba_macroactivos
ALTER COLUMN id_sistema_cliente TYPE BIGINT USING id_sistema_cliente_correccion::BIGINT,
ALTER COLUMN cod_activo TYPE INTEGER USING cod_activo_correccion::INTEGER,
ALTER COLUMN macroactivo TYPE TEXT USING macroactivo_correccion::TEXT,
ALTER COLUMN aba TYPE NUMERIC USING aba_correccion::NUMERIC,
ALTER COLUMN cod_perfil_riesgo TYPE INTEGER USING cod_perfil_riesgo_correccion::INTEGER,
ALTER COLUMN cod_banca TYPE TEXT USING cod_banca_correccion::TEXT,
ALTER COLUMN year TYPE INTEGER USING year_correccion::INTEGER,
ALTER COLUMN month TYPE INTEGER USING month_correccion::INTEGER;

ALTER TABLE historico_aba_macroactivos
DROP COLUMN id_sistema_cliente_correccion,
DROP COLUMN cod_activo_correccion,
DROP COLUMN macroactivo_correccion,
DROP COLUMN aba_correccion,
DROP COLUMN cod_perfil_riesgo_correccion,
DROP COLUMN cod_banca_correccion,
DROP COLUMN year_correccion,
DROP COLUMN month_correccion;




    
   


    
    
    """        
]


try:
    for query in sql_queries:
        cursor.execute(query)
        conn.commit()
        print("Consulta ejecutada correctamente.")
except Exception as e:
    print(f"Error al ejecutar las consultas SQL: {e}")



# Función para conectar y traer los datos
def get_data():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="4179"
    )
    query = """
    SELECT 
        h.ingestion_year,
        h.ingestion_month,
        h.ingestion_day,
        h.id_sistema_cliente,
        h.aba,
        h.macroactivo,
        c.activo,
        p.perfil_riesgo,
        b.banca,
        h.year,
        h.month
    FROM historico_aba_macroactivos h
    LEFT JOIN catalogo_activos c ON h.cod_activo = c.cod_activo
    LEFT JOIN cat_perfil_riesgo p ON p.cod_perfil_riesgo::INTEGER = h.cod_perfil_riesgo::INTEGER
    LEFT JOIN catalogo_banca b ON b.cod_banca = h.cod_banca
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Carga inicial de datos
df = get_data()
df['fecha'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

# Instancia de Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard ABA - Bancolombia"

# Layout general con Tabs
app.layout = html.Div([
    html.H1("Dashboard ABA", style={"textAlign": "center"}),

    dcc.Tabs(id="tabs", value='tab-cliente', children=[
        dcc.Tab(label='Análisis por Cliente', value='tab-cliente'),
        dcc.Tab(label='Análisis por Banca', value='tab-banca')
    ]),

    html.Div(id='contenido-tab')
])

# Layout: Análisis por Cliente
def layout_tab_cliente():
    return html.Div([
        dcc.Dropdown(
            id='cliente-dropdown',
            options=[{"label": i, "value": i} for i in sorted(df["id_sistema_cliente"].dropna().unique())],
            placeholder="Selecciona un cliente",
            style={"width": "50%"}
        ),

        dcc.DatePickerRange(
            id='fecha-range',
            start_date=df['fecha'].min(),
            end_date=df['fecha'].max()
        ),

        dcc.Checklist(
            id='mostrar-proyeccion',
            options=[{'label': ' Mostrar proyección 6 meses', 'value': 'proyeccion'}],
            value=[]
        ),

        dcc.RadioItems(
            id='tipo-vista',
            options=[
                {'label': 'Macroactivo', 'value': 'macroactivo'},
                {'label': 'Activo', 'value': 'activo'}
            ],
            value='macroactivo',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        ),

        dcc.Graph(id='grafico-evolucion'),

        html.H3("Portafolio por perfil de riesgo"),
        dcc.Graph(id='grafico-portafolio-perfil-barras'),
        html.Div(id='grafico-portafolio-perfil-pie'),

        html.H3("Portafolio por banca"),
        dcc.Graph(id='grafico-portafolio-banca-barras'),
        html.Div(id='grafico-portafolio-banca-pie'),
    ])

# Layout: Análisis por Banca
def layout_tab_banca():
    return html.Div([
        dcc.Dropdown(
            id='banca-dropdown',
            options=[{"label": i, "value": i} for i in sorted(df["banca"].dropna().unique())],
            placeholder="Selecciona una banca",
            style={"width": "50%"}
        ),

        dcc.DatePickerRange(
            id='fecha-range-banca',
            start_date=df['fecha'].min(),
            end_date=df['fecha'].max()
        ),

        dcc.Checklist(
            id='mostrar-proyeccion-banca',
            options=[{'label': ' Mostrar proyección 6 meses', 'value': 'proyeccion'}],
            value=[]
        ),

        dcc.RadioItems(
            id='tipo-vista-banca',
            options=[
                {'label': 'Macroactivo', 'value': 'macroactivo'},
                {'label': 'Activo', 'value': 'activo'}
            ],
            value='macroactivo',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        ),

        dcc.Graph(id='grafico-evolucion-banca'),

        html.H3("Composición por perfil de riesgo"),
        dcc.Graph(id='grafico-perfil-banca-barras'),
        html.Div(id='grafico-perfil-banca-pie'),

        html.H3("Composición por activo/macroactivo"),
        dcc.Graph(id='grafico-activos-banca-barras'),
        html.Div(id='grafico-activos-banca-pie'),
    ])

# Callback para renderizar el contenido de cada tab
@app.callback(
    Output('contenido-tab', 'children'),
    Input('tabs', 'value')
)
def render_tab(tab):
    if tab == 'tab-cliente':
        return layout_tab_cliente()
    elif tab == 'tab-banca':
        return layout_tab_banca()

# Helper para proyectar 6 meses
def proyectar_aba(df_evol):
    df_evol = df_evol.copy()
    df_evol['mes_num'] = (df_evol['fecha'].dt.year - df_evol['fecha'].dt.year.min()) * 12 + df_evol['fecha'].dt.month
    X = df_evol['mes_num'].values.reshape(-1, 1)
    y = df_evol['aba'].values
    model = LinearRegression().fit(X, y)

    meses_extra = np.arange(X[-1][0] + 1, X[-1][0] + 7).reshape(-1, 1)
    fechas_extra = pd.date_range(start=df_evol['fecha'].max() + pd.DateOffset(months=1), periods=6, freq='MS')
    proy = model.predict(meses_extra)

    df_proy = pd.DataFrame({'fecha': fechas_extra, 'aba': proy})
    df_comb = pd.concat([df_evol, df_proy], ignore_index=True)
    return df_comb

# Callback: evolución ABA promedio con proyección
@app.callback(
    Output('grafico-evolucion', 'figure'),
    [Input('cliente-dropdown', 'value'),
     Input('fecha-range', 'start_date'),
     Input('fecha-range', 'end_date'),
     Input('mostrar-proyeccion', 'value')]
)
def update_evolucion(cliente, start, end, mostrar_proy):
    df_filtrado = df.copy()
    if cliente:
        df_filtrado = df_filtrado[df_filtrado['id_sistema_cliente'] == cliente]
    df_filtrado = df_filtrado[(df_filtrado['fecha'] >= start) & (df_filtrado['fecha'] <= end)]
    evolucion = df_filtrado.groupby('fecha')['aba'].mean().reset_index()

    if 'proyeccion' in mostrar_proy and len(evolucion) > 1:
        evolucion['mes_num'] = (evolucion['fecha'].dt.year - evolucion['fecha'].dt.year.min()) * 12 + evolucion['fecha'].dt.month
        X = evolucion['mes_num'].values.reshape(-1, 1)
        y = evolucion['aba'].values
        model = LinearRegression().fit(X, y)
        meses_extra = np.arange(X[-1][0] + 1, X[-1][0] + 7).reshape(-1, 1)
        fechas_extra = pd.date_range(start=evolucion['fecha'].max() + pd.DateOffset(months=1), periods=6, freq='MS')
        proy = model.predict(meses_extra)
        df_proy = pd.DataFrame({'fecha': fechas_extra, 'aba': proy})
        evolucion = pd.concat([evolucion, df_proy], ignore_index=True)

    return px.line(evolucion, x='fecha', y='aba', title='Evolución del ABA Promedio')

# Callback: barras por perfil de riesgo
@app.callback(
    Output('grafico-portafolio-perfil-barras', 'figure'),
    [Input('tipo-vista', 'value'),
     Input('fecha-range', 'end_date'),
     Input('cliente-dropdown', 'value')]
)
def update_barras_perfil(vista, fecha_max, cliente):
    df_f = df[df['fecha'] == fecha_max]
    if cliente:
        df_f = df_f[df_f['id_sistema_cliente'] == cliente]
    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    datos = df_f.groupby(['perfil_riesgo', col])['aba'].sum().reset_index()
    return px.bar(datos, x='perfil_riesgo', y='aba', color=col, barmode='stack', title='Portafolio por perfil de riesgo')

# Callback: barras por banca
@app.callback(
    Output('grafico-portafolio-banca-barras', 'figure'),
    [Input('tipo-vista', 'value'),
     Input('fecha-range', 'end_date'),
     Input('cliente-dropdown', 'value')]
)
def update_barras_banca(vista, fecha_max, cliente):
    df_f = df[df['fecha'] == fecha_max]
    if cliente:
        df_f = df_f[df_f['id_sistema_cliente'] == cliente]
    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    datos = df_f.groupby(['banca', col])['aba'].sum().reset_index()
    return px.bar(datos, x='banca', y='aba', color=col, barmode='stack', title='Portafolio por banca')

# Callbacks para cliente (composición de pie por perfil de riesgo)
@app.callback(
    Output('grafico-portafolio-perfil-pie', 'children'),
    [Input('tipo-vista', 'value'),
     Input('fecha-range', 'end_date'),
     Input('cliente-dropdown', 'value')]
)
def update_pie_perfil_multiples(vista, fecha_max, cliente):
    df_f = df[df['fecha'] == fecha_max]
    if cliente:
        df_f = df_f[df_f['id_sistema_cliente'] == cliente]

    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    perfiles = df_f['perfil_riesgo'].dropna().unique()
    figs = []

    for perfil in perfiles:
        sub_df = df_f[df_f['perfil_riesgo'] == perfil]
        resumen = sub_df.groupby(col)['aba'].sum().reset_index()
        fig_pie = px.pie(resumen, values='aba', names=col, title=f'Perfil de riesgo: {perfil}')
        figs.append(dcc.Graph(figure=fig_pie, style={"display": "inline-block", "width": f"{100 / len(perfiles)}%"}))

    if figs:
        return html.Div(figs, style={"display": "flex", "flexWrap": "wrap"})
    else:
        return html.Div("No hay datos disponibles para perfiles de riesgo.")

# Callbacks para cliente (composición de pie por banca)
@app.callback(
    Output('grafico-portafolio-banca-pie', 'children'),
    [Input('tipo-vista', 'value'),
     Input('fecha-range', 'end_date'),
     Input('cliente-dropdown', 'value')]
)
def update_pie_banca_multiples(vista, fecha_max, cliente):
    df_f = df[df['fecha'] == fecha_max]
    if cliente:
        df_f = df_f[df_f['id_sistema_cliente'] == cliente]

    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    bancas = df_f['banca'].dropna().unique()
    figs = []

    for banca in bancas:
        sub_df = df_f[df_f['banca'] == banca]
        resumen = sub_df.groupby(col)['aba'].sum().reset_index()
        fig_pie = px.pie(resumen, values='aba', names=col, title=f'Banca: {banca}')
        figs.append(dcc.Graph(figure=fig_pie, style={"display": "inline-block", "width": f"{100 / len(bancas)}%"}))

    if figs:
        return html.Div(figs, style={"display": "flex", "flexWrap": "wrap"})
    else:
        return html.Div("No hay datos disponibles para bancas.")



# Callbacks para análisis por banca

@app.callback(
    Output('grafico-evolucion-banca', 'figure'),
    [Input('banca-dropdown', 'value'),
     Input('fecha-range-banca', 'start_date'),
     Input('fecha-range-banca', 'end_date'),
     Input('mostrar-proyeccion-banca', 'value')]
)
def update_evolucion_banca(banca, start, end, mostrar_proy):
    df_f = df.copy()
    if banca:
        df_f = df_f[df_f['banca'] == banca]
    df_f = df_f[(df_f['fecha'] >= start) & (df_f['fecha'] <= end)]
    evolucion = df_f.groupby('fecha')['aba'].mean().reset_index()

    if 'proyeccion' in mostrar_proy and len(evolucion) > 1:
        evolucion['mes_num'] = (evolucion['fecha'].dt.year - evolucion['fecha'].dt.year.min()) * 12 + evolucion['fecha'].dt.month
        X = evolucion['mes_num'].values.reshape(-1, 1)
        y = evolucion['aba'].values
        model = LinearRegression().fit(X, y)
        meses_extra = np.arange(X[-1][0] + 1, X[-1][0] + 7).reshape(-1, 1)
        fechas_extra = pd.date_range(start=evolucion['fecha'].max() + pd.DateOffset(months=1), periods=6, freq='MS')
        proy = model.predict(meses_extra)
        df_proy = pd.DataFrame({'fecha': fechas_extra, 'aba': proy})
        evolucion = pd.concat([evolucion, df_proy], ignore_index=True)

    return px.line(evolucion, x='fecha', y='aba', title=f'Evolución ABA promedio - Banca: {banca}')

@app.callback(
    Output('grafico-perfil-banca-barras', 'figure'),
    [Input('banca-dropdown', 'value'),
     Input('fecha-range-banca', 'end_date'),
     Input('tipo-vista-banca', 'value')]
)
def update_perfil_banca_barras(banca, fecha_max, vista):
    df_f = df[df['fecha'] == fecha_max]
    if banca:
        df_f = df_f[df_f['banca'] == banca]
    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    datos = df_f.groupby(['perfil_riesgo', col])['aba'].sum().reset_index()
    return px.bar(datos, x='perfil_riesgo', y='aba', color=col, barmode='stack', title='Perfil de riesgo - banca')

@app.callback(
    Output('grafico-perfil-banca-pie', 'children'),
    [Input('banca-dropdown', 'value'),
     Input('fecha-range-banca', 'end_date'),
     Input('tipo-vista-banca', 'value')]
)
def update_perfil_banca_pie(banca, fecha_max, vista):
    df_f = df[df['fecha'] == fecha_max]
    if banca:
        df_f = df_f[df_f['banca'] == banca]
    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    perfiles = df_f['perfil_riesgo'].dropna().unique()
    figs = []

    for perfil in perfiles:
        sub_df = df_f[df_f['perfil_riesgo'] == perfil]
        resumen = sub_df.groupby(col)['aba'].sum().reset_index()
        fig_pie = px.pie(resumen, values='aba', names=col, title=f'Perfil: {perfil}')
        figs.append(dcc.Graph(figure=fig_pie, style={"display": "inline-block", "width": f"{100 / len(perfiles)}%"}))

    if figs:
        return html.Div(figs, style={"display": "flex", "flexWrap": "wrap"})
    else:
        return html.Div("No hay datos disponibles para perfiles de riesgo en esta banca.")

@app.callback(
    Output('grafico-activos-banca-barras', 'figure'),
    [Input('banca-dropdown', 'value'),
     Input('fecha-range-banca', 'end_date'),
     Input('tipo-vista-banca', 'value')]
)
def update_activos_banca_barras(banca, fecha_max, vista):
    df_f = df[df['fecha'] == fecha_max]
    if banca:
        df_f = df_f[df_f['banca'] == banca]
    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    datos = df_f.groupby(col)['aba'].sum().reset_index()
    return px.bar(datos, x=col, y='aba', title='Distribución total por activo/macroactivo')

@app.callback(
    Output('grafico-activos-banca-pie', 'children'),
    [Input('banca-dropdown', 'value'),
     Input('fecha-range-banca', 'end_date'),
     Input('tipo-vista-banca', 'value')]
)
def update_activos_banca_pie(banca, fecha_max, vista):
    df_f = df[df['fecha'] == fecha_max]
    if banca:
        df_f = df_f[df_f['banca'] == banca]
    col = 'macroactivo' if vista == 'macroactivo' else 'activo'
    datos = df_f.groupby(col)['aba'].sum().reset_index()
    fig = px.pie(datos, values='aba', names=col, title='Participación total por activo/macroactivo')
    return html.Div(dcc.Graph(figure=fig))






# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True)
